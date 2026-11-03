/* H-17 K04: exhaustive global hex-symbol map with one 3-cycle and
 * disjoint fixed points / transpositions on the other 13 symbols.
 * Read-only source-pinned shardable SFT; compile C++17 with OpenSSL and OpenMP.
 * Example: g++ -O3 -fopenmp agents/agent1/k04_threecycle_copier_sft.cpp -lcrypto -o cycle
 * Run from repo root: ./cycle 0 32; ./cycle 32 64; ...; ./cycle 544 560.
 */
#include <openssl/sha.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <array>
#include <vector>
#include <algorithm>
#include <chrono>
#include <atomic>
#include <fstream>
#include <string>
#include <iterator>
#ifdef _OPENMP
#include <omp.h>
#endif
using Bytes=std::array<uint8_t,16>;
static const char *ORIG_PAY="A9A9DC5731A5E2AE879C47215C2559D5";
static const char *ORIG_MASK="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *ORIG_TARGET="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static inline int hval(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;if(c>='a'&&c<='f')return c-'a'+10;std::abort();}
static Bytes decode(const char *p){Bytes out{};for(int i=0;i<16;i++)out[i]=(hval(p[2*i])<<4)|hval(p[2*i+1]);return out;}
static void hex32(const uint8_t* bytes,char* o,int n){const char* alphabet="0123456789ABCDEF";for(int i=0;i<n;i++){o[i*2]=alphabet[bytes[i]>>4];o[i*2+1]=alphabet[bytes[i]&15];}o[n*2]=0;}
struct Search {
 Bytes payload,mask,base;std::array<uint8_t,32> hexpay,hexmask,hexbase;std::array<uint8_t,SHA256_DIGEST_LENGTH> target,synth;
 std::atomic<uint64_t> matches{0},synthetic_hits{0};
 Search(){
  payload=decode(ORIG_PAY);mask=decode(ORIG_MASK);
  for(int i=0;i<16;i++)base[i]=payload[i]^mask[i];
  for(int i=0;i<32;i++){hexpay[i]=hval(ORIG_PAY[i]);hexmask[i]=hval(ORIG_MASK[i]);hexbase[i]=(i&1)?(base[i/2]&15):(base[i/2]>>4);}
  for(int i=0;i<32;i++)target[i]=(hval(ORIG_TARGET[2*i])<<4)|hval(ORIG_TARGET[2*i+1]);
  uint8_t planted[16]{};int map[16];for(int i=0;i<16;i++)map[i]=i;
  map[1]=4;map[4]=7;map[7]=1;map[2]=12;map[12]=2;
  mapped(map,0,planted);SHA256(planted,16,synth.data());
 }
 void mapped(const int *f,int stage,uint8_t* out)const{
  const auto& h=stage==0?hexpay:(stage==1?hexmask:hexbase);
  for(int i=0;i<16;i++){
   uint8_t c=(f[h[2*i]]<<4)|f[h[2*i+1]];
   out[i]=stage==0?(c^mask[i]):(stage==1?(c^payload[i]):c);
  }
 }
 uint64_t run(int start,int end){
  const auto t0=std::chrono::steady_clock::now();uint64_t total=0;
 #pragma omp parallel for reduction(+:total) schedule(dynamic,1)
  for(int idx=start;idx<end;idx++){
   int ia=0,ib=0,ic=0,k=0;
   for(int a=0;a<16;a++)for(int b=a+1;b<16;b++)for(int c=b+1;c<16;c++){
    if(k++==idx){ia=a;ib=b;ic=c;}
   }
   int remaining[13],m=0;for(int i=0;i<16;i++)if(i!=ia&&i!=ib&&i!=ic)remaining[m++]=i;
   for(int orient=0;orient<2;orient++){
    int f[16];for(int i=0;i<16;i++)f[i]=i;
    f[ia]=orient?ic:ib;f[ib]=orient?ia:ic;f[ic]=orient?ib:ia;
    auto visit=[&](auto&& self,int pos)->void{
     if(pos==13){
      uint8_t cand[16];unsigned char hash[32];
      for(int stage=0;stage<3;stage++){
       mapped(f,stage,cand);SHA256(cand,16,hash);
       if(!memcmp(hash,target.data(),32)){
        char h[33];hex32(cand,h,16);
        fprintf(stderr,"K04 MATCH stage%d map3(%X,%X,%X) component=%s\n",stage,ia,ib,ic,h);
        matches++;
       }
       if(stage==0 && !memcmp(hash,synth.data(),32))synthetic_hits++;
      }
      total++;return;
     }
     int a=remaining[pos];if(f[a]!=a)return self(self,pos+1);
     self(self,pos+1);
     for(int j=pos+1;j<13;j++){
      int b=remaining[j];if(f[b]!=b)continue;
      f[a]=b;f[b]=a;self(self,pos+1);f[a]=a;f[b]=b;
     }
    };
    visit(visit,0);
   }
  }
  double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
  fprintf(stderr,"completed idx %d..%d maps=%llu checks=%llu original=%llu synthetic=%llu seconds=%.3f\n",
   start,end,(unsigned long long)total,(unsigned long long)(total*3),
   (unsigned long long)matches.load(),(unsigned long long)synthetic_hits.load(),sec);
  return total;
 }
};
int main(int argc,char**argv){
 std::ifstream in("resources/evidence/print/spool-reconstruction.log",std::ios::binary);
 if(!in){fprintf(stderr,"source missing; run from repository root\n");return 4;}
 std::string raw((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
 unsigned char source_digest[32];SHA256(reinterpret_cast<const unsigned char*>(raw.data()),raw.size(),source_digest);
 char source_hex[65];hex32(source_digest,source_hex,32);
 if(std::strcmp(source_hex,"7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083")!=0 ||
    raw.find("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5") == std::string::npos){
   fprintf(stderr,"original source checksum or selector mismatch\n");return 5;
 }
 int start=argc>1?std::atoi(argv[1]):0;
 int end=argc>2?std::atoi(argv[2]):560;
 if(start<0||end>560||end<start)std::abort();
 Search s;auto total=s.run(start,end);
 if(start==0&&end==560){
  if(total!=636724480ULL){fprintf(stderr,"count mismatch\n");return 2;}
  if(s.synthetic_hits.load()==0){fprintf(stderr,"synthetic missed\n");return 3;}
 }
 return 0;
}
