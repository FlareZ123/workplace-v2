/* H-17 original K04 RomuQuad32 reverse-source candidate search.
 * C++17, OpenMP, OpenSSL SHA256. The intact 18:03 REQUESTED3 packet
 * determines full 128bit states up to a bounded 32bit variable z0;
 * rewind the invertible recurrence to predict missing 18:02 ACK2.
 * The disputed copied ACK2 bytes are never used as input.
 */
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <openssl/sha.h>

constexpr uint32_t C=3323815723u, CI=0x33621f83u;
uint32_t rol(uint32_t x,int n){return (x<<n)|(x>>(32-n));}
uint32_t ror(uint32_t x,int n){return (x>>n)|(x<<(32-n));}
struct State{uint32_t w,x,y,z;};
uint32_t next(State& s){auto [w,x,y,z]=s;s={C*z,z+rol(w,26),y-x,rol(y+w,9)};return x;}
void previous(State& s){
 auto [w,x,y,z]=s;
 uint32_t z0=CI*w,w0=ror(x-z0,26),y0=ror(z,9)-w0;
 s={w0,y0-y,y0,z0};
}
uint32_t predicted4(uint32_t a,uint32_t b,uint32_t c,uint32_t z){
 uint32_t w0=ror(b-z,26),z1=c-rol(C*z,26),y0=ror(z1,9)-w0;
 return rol(y0-a+C*z,9)+rol(C*z1,26);
}
State inverse(uint32_t a,uint32_t b,uint32_t c,uint32_t z){
 uint32_t w0=ror(b-z,26),z1=c-rol(C*z,26),y0=ror(z1,9)-w0;
 return {w0,a,y0,z};
}
void fromhex(const char* s,uint8_t* out,int n){
 for(int i=0;i<n;i++){unsigned x;std::sscanf(s+2*i,"%2x",&x);out[i]=uint8_t(x);}
}
void pack(const uint32_t* words,int le,int reverse,uint8_t* out){
 for(int i=0;i<4;i++){uint32_t w=words[reverse?3-i:i];
  for(int j=0;j<4;j++)out[i*4+j]=uint8_t(w>>(8*(le?j:3-j))); }
}
void unpack(const uint8_t* in,int le,int reverse,uint32_t* out){
 for(int i=0;i<4;i++){uint32_t w=0;
  for(int j=0;j<4;j++)w|=uint32_t(in[i*4+j])<<(8*(le?j:3-j));
  out[reverse?3-i:i]=w;}
}
void planted(){
 for(uint32_t i=0;i<1000;i++){
  State s{0x12345678u+i,0x9abcdef0u-i,0xa55a5aa5u+i,0xf0e1d2c3u-i},initial=s;
  for(int j=0;j<64;j++)next(s);
  for(int j=0;j<64;j++)previous(s);
  if(std::memcmp(&s,&initial,sizeof(s)))std::abort();
 }
 std::puts("Planted 1000 forward/backward 64-step state round-trips: PASS");
}
int main(){
 planted();
 uint8_t late[16],early[16],mask[16],wanted[32];
 fromhex("44D53DFC29D7943A95D89371DA58EC64",late,16);
 fromhex("CD3E4F216ADB2FB180DA2AA90B33F7A4",early,16);
 fromhex("8556C8CB6140A7F9A5123AC7571BEE1C",mask,16);
 fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",wanted,32);
 uint64_t solutions=0,hits=0,prior_hits=0,window_count=0,window_hits=0;
 for(int endian=0;endian<2;endian++)for(int reverse=0;reverse<2;reverse++){
  uint32_t observed[4];unpack(late,endian,reverse,observed);
  std::vector<uint32_t> states;
  #pragma omp parallel
  {std::vector<uint32_t> local;
   #pragma omp for schedule(static)
   for(uint64_t n=0;n<(uint64_t(1)<<32);n++)
    if(predicted4(observed[0],observed[1],observed[2],uint32_t(n))==observed[3])
     local.push_back(uint32_t(n));
   #pragma omp critical
   states.insert(states.end(),local.begin(),local.end());
  }
  solutions+=states.size();
  std::printf("%s %s: %zu complete initial states\n",endian?"LE":"BE",reverse?"rev":"normal",states.size());
  for(uint32_t z0:states){
   State checkpoint=inverse(observed[0],observed[1],observed[2],z0),replay=checkpoint;
   for(int i=0;i<4;i++)if(next(replay)!=observed[i])std::abort();
   State intermediate=checkpoint;
   for(int i=0;i<4;i++)previous(intermediate);
   State first=intermediate;
   for(int i=0;i<4;i++)previous(first);
   uint32_t selected[4],original[4];
   for(int i=0;i<4;i++)selected[i]=next(intermediate);
   for(int i=0;i<4;i++)original[i]=next(first);
   uint8_t physical[16],before[16],component[16],digest[32];
   pack(selected,endian,reverse,physical);
   pack(original,endian,reverse,before);
   for(int i=0;i<16;i++)component[i]=physical[i]^mask[i];
   SHA256(component,16,digest);
   hits+=!std::memcmp(digest,wanted,32);
   prior_hits+=!std::memcmp(before,early,16);
   std::printf("  candidate=");
   for(uint8_t byte:component)std::printf("%02X",byte);
   std::printf("\n");
   constexpr int N=131072;
   State rewind=inverse(observed[0],observed[1],observed[2],z0);
   std::vector<uint32_t> past(N+7);
   for(uint32_t& v:past){previous(rewind);v=rewind.x;}
   for(int offset=4;offset<4+N;offset++){
    uint32_t chronological[4]={past[offset-1],past[offset-2],past[offset-3],past[offset-4]};
    uint8_t packet[16],hyp[16],sha[32];pack(chronological,endian,reverse,packet);
    for(int j=0;j<16;j++)hyp[j]=packet[j]^mask[j];
    SHA256(hyp,16,sha);window_count++;
    if(!std::memcmp(sha,wanted,32)){window_hits++;std::printf("FOUND K04 at backward offset=%d\n",offset);}
   }
  }
 }
 std::printf("states=%llu direct_K04=%llu previous_18:01=%llu windows=%llu window_K04=%llu\n",
  (unsigned long long)solutions,(unsigned long long)hits,(unsigned long long)prior_hits,
  (unsigned long long)window_count,(unsigned long long)window_hits);
 return (solutions==2 && !hits && !prior_hits && window_count==262144 && !window_hits)?0:2;
}