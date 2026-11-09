// Exhaustive H-17 K04 eight-bit error shell against unchanged historical commitment.
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
static const int planted_bits[8]={120,121,122,123,124,125,126,127};
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

int main(int argc,char **argv){
 if(argc!=3 && !(argc==2 && std::strcmp(argv[1],"--selftest")==0)){
  std::fprintf(stderr,"Usage: k04_exact8 <shard:0..63> 64, or --selftest\n");
  return 2;
 }
 uint8_t planted[16];std::memcpy(planted,baseline,16);
 for(int bit:planted_bits)planted[bit>>3]^=1u<<(bit&7);
 uint8_t actual[32];SHA256(planted,16,actual);
 uint32_t planted_hash[8];
 for(int i=0;i<8;i++)planted_hash[i]=uint32_t(actual[4*i])<<24|uint32_t(actual[4*i+1])<<16|uint32_t(actual[4*i+2])<<8|uint32_t(actual[4*i+3]);
 if(argc==2){
  ThreadState s(planted_hash);
  for(int bit:planted_bits)s.block[bit>>3]^=1u<<(bit&7);
  s.search(0,128);
  std::printf("SELFTEST checks=%llu original_hits=%llu planted_hits=%llu\n",
    (unsigned long long)s.checks,(unsigned long long)s.hits,(unsigned long long)s.planted);
  return s.checks==1 && s.planted==1?0:3;
 }
 const int shard=std::atoi(argv[1]),shards=std::atoi(argv[2]);
 if(shards!=64||shard<0||shard>=64)return 2;
 uint64_t expected=0;
 for(int a=0;a<=120;a++)for(int b=a+1;b<=121;b++)
  if((a*131+b*17)%shards==shard)expected+=choose(127-b,6);
 std::printf("START k04_exact8 shard=%d/64 expected=%llu threads=%d planted=",
   shard,(unsigned long long)expected,omp_get_max_threads());
 for(uint8_t x:planted)std::printf("%02X",x);
 std::puts("");std::fflush(stdout);
 uint64_t sum=0,hits=0,synthetic=0;
 std::atomic<unsigned> progress{0};
 const double begin=omp_get_wtime();
 #pragma omp parallel reduction(+:sum,hits,synthetic)
 {
  ThreadState s(planted_hash);
  #pragma omp for schedule(dynamic,1)
  for(int a=0;a<=120;a++){
   for(int b=a+1;b<=121;b++){
    if((a*131+b*17)%shards!=shard)continue;
    s.checks=0;s.hits=0;s.planted=0;
    s.block[a>>3]^=1u<<(a&7);
    s.block[b>>3]^=1u<<(b&7);
    s.search(6,b+1);
    s.block[b>>3]^=1u<<(b&7);
    s.block[a>>3]^=1u<<(a&7);
    const uint64_t count=choose(127-b,6);
    if(s.checks!=count){
     std::fprintf(stderr,"COUNT_MISMATCH a=%d b=%d have=%llu expected=%llu\n",
       a,b,(unsigned long long)s.checks,(unsigned long long)count);
     std::abort();
    }
    sum+=s.checks;hits+=s.hits;synthetic+=s.planted;
    unsigned done=++progress;
    if(done%10==0){
     #pragma omp critical
     {std::printf("PAIR_PROGRESS shard=%d pairs=%u a=%d b=%d elapsed=%.1f\n",
       shard,done,a,b,omp_get_wtime()-begin);std::fflush(stdout);}
    }
   }
  }
 }
 const unsigned expected_synthetic=((120*131+121*17)%64==shard)?1:0;
 std::printf("COMPLETE shard=%d/64 checked=%llu expected=%llu original_hits=%llu planted_hits=%llu expected_plant=%u elapsed=%.3f\n",
  shard,(unsigned long long)sum,(unsigned long long)expected,(unsigned long long)hits,
  (unsigned long long)synthetic,expected_synthetic,omp_get_wtime()-begin);
 return sum==expected&&synthetic==expected_synthetic?0:3;
}
