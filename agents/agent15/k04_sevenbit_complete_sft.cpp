// Exhaustive H-17 K04 seven-bit error shell against unchanged historical commitment.
// C++17, OpenSSL libcrypto and OpenMP. Compile with -O3 -fopenmp -lcrypto.
#define OPENSSL_API_COMPAT 0x10100000L
#include <array>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <omp.h>
#include <openssl/sha.h>
static const unsigned char baseline[16]={0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static const uint32_t target[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const int planted_bits[7]={121,122,123,124,125,126,127};
static const SHA256_CTX initial=[](){SHA256_CTX c;SHA256_Init(&c);return c;}();
struct ThreadState {
 uint8_t block[64]{};
 SHA256_CTX ctx{};
 uint64_t checks=0,hits=0,planted=0;
 uint32_t planted_hash[8]{};
 explicit ThreadState(const uint32_t *p){
  std::memcpy(block,baseline,16);block[16]=0x80;block[63]=0x80;
  std::memcpy(planted_hash,p,sizeof(planted_hash));
 }
 static bool match(const SHA256_CTX &c,const uint32_t *h){
  if(c.h[0]!=h[0])return false;
  for(int i=1;i<8;i++)if(c.h[i]!=h[i])return false;
  return true;
 }
 void search(int left,int next){
  if(!left){
   ctx=initial;
   SHA256_Transform(&ctx,block);
   checks++;
   if(match(ctx,target)){
    hits++;
    #pragma omp critical
    {std::printf("REAL_ORIGINAL_K04_HIT ");for(int i=0;i<16;i++)std::printf("%02X",block[i]);std::printf("\n");std::fflush(stdout);}
   }
   if(match(ctx,planted_hash))planted++;
   return;
  }
  for(int pos=next;pos<=128-left;pos++){
   block[pos>>3]^=(1u<<(pos&7));
   search(left-1,pos+1);
   block[pos>>3]^=(1u<<(pos&7));
  }
 }
};
static uint64_t choose(unsigned n,unsigned k){
 if(k>n)return 0;
 uint64_t v=1;
 for(unsigned i=1;i<=k;i++)v=v*(n-k+i)/i;
 return v;
}
int main(){
 uint8_t planted[16];std::memcpy(planted,baseline,16);
 for(int bit:planted_bits)planted[bit>>3]^=1u<<(bit&7);
 uint8_t actual[32];SHA256(planted,16,actual);
 uint32_t planted_hash[8];
 for(int i=0;i<8;i++)planted_hash[i]=uint32_t(actual[4*i])<<24|uint32_t(actual[4*i+1])<<16|uint32_t(actual[4*i+2])<<8|uint32_t(actual[4*i+3]);
 printf("START k04_exact7 expected=%llu threads=%d planted=",(unsigned long long)choose(128,7),omp_get_max_threads());
 for(uint8_t x:planted)printf("%02X",x);puts("");fflush(stdout);
 std::atomic<uint64_t> progress{0};uint64_t sum=0,hits=0,synthetic=0;
 const double begin=omp_get_wtime();
 #pragma omp parallel reduction(+:sum,hits,synthetic)
 {
  ThreadState s(planted_hash);
  #pragma omp for schedule(dynamic,1)
  for(int low=0;low<=121;low++){
   s.checks=0;s.hits=0;s.planted=0;
   s.block[low>>3]^=1u<<(low&7);
   s.search(6,low+1);
   s.block[low>>3]^=1u<<(low&7);
   uint64_t expected=choose(127-low,6);
   if(s.checks!=expected){fprintf(stderr,"COUNT_MISMATCH low=%d have=%llu expect=%llu\n",low,(unsigned long long)s.checks,(unsigned long long)expected);abort();}
   sum+=s.checks;hits+=s.hits;synthetic+=s.planted;
   unsigned done=++progress;
   #pragma omp critical
   {printf("LOW_DONE %d/%d low=%d checks=%llu original_hits=%llu synthetic_hits=%llu elapsed=%.1f\n",done,122,low,(unsigned long long)s.checks,(unsigned long long)s.hits,(unsigned long long)s.planted,omp_get_wtime()-begin);fflush(stdout);}
  }
 }
 printf("COMPLETE checked=%llu expected=%llu original_hits=%llu planted_hits=%llu elapsed=%.3f\n",(unsigned long long)sum,(unsigned long long)choose(128,7),(unsigned long long)hits,(unsigned long long)synthetic,omp_get_wtime()-begin);
 return (sum==choose(128,7)&&synthetic==1)?0:3;
}
