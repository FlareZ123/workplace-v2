// RFC 8682 seeded TinyMT32 complete-packet original RECOVER source test.
// Source spool SHA-256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <array>
#include <atomic>
#include <chrono>
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <omp.h>
struct Tiny {
 uint32_t s[4];
 static constexpr uint32_t MAT1=0x8f7011ee, MAT2=0xfc78ff1f, TMAT=0x3793fdff;
 inline void advance(){
  uint32_t x=(s[0]&0x7fffffff)^s[1]^s[2];x^=x<<1;
  uint32_t y=s[3]^(s[3]>>1)^x;
  s[0]=s[1];s[1]=s[2];s[2]=x^(y<<10);s[3]=y;
  if(y&1){s[1]^=MAT1;s[2]^=MAT2;}
 }
 inline uint32_t next(){advance();const uint32_t t1=s[0]+(s[2]>>8);return s[3]^t1^((t1&1)?TMAT:0);}
 inline void init(uint32_t seed){
  s[0]=seed;s[1]=MAT1;s[2]=MAT2;s[3]=TMAT;
  for(uint32_t i=1;i<8;i++){const uint32_t q=s[(i-1)&3];s[i&3]^=i+1812433253U*(q^(q>>30));}
  for(int i=0;i<8;i++)advance();
 }
};
int main(int argc,char **argv){
 uint64_t begin=argc>1?strtoull(argv[1],nullptr,0):0;
 uint64_t count=argc>2?strtoull(argv[2],nullptr,0):1000000;
 if(count==0||begin+count>0x100000000ULL)return 2;
 // All three intact late RECOVER controls and one intact earlier RECOVER, target 18:02 excluded.
 constexpr uint32_t packet[4][4]={{0x234BE186,0xE97EE058,0x30909790,0xE336109E},
 {0x432475F7,0x2A62DB39,0xF3D5693E,0x2C937FA4},
 {0xF0DC2DDF,0x78FFE61C,0x33320BCB,0x94178480},
 {0xE3E47EC3,0xEA5183A7,0x83D7D8E0,0xA16C2F2E}};
 std::array<std::array<uint32_t,4>,16> targets{};
 for(int rec=0;rec<4;rec++)for(int endian=0;endian<2;endian++)for(int reversed=0;reversed<2;reversed++){
  int idx=rec*4+endian*2+reversed;
  for(int j=0;j<4;j++){
   uint32_t w=packet[rec][reversed?(3-j):j];
   if(endian)w=__builtin_bswap32(w);
   targets[idx][j]=w;
  }
 }
 // Reference official RFC8682 seed=1 first five words (including 5th).
 Tiny t;t.init(1);
 uint32_t reference[]={2545341989U,981918433U,3715302833U,2387538352U,3591001365U};
 for(uint32_t x:reference)if(t.next()!=x){puts("FAIL_RFC8682_REFERENCE");return 3;}
 // Synthetic seeded exact original-4-word positive control.
 Tiny synthetic;synthetic.init(0xA514F291);for(int i=0;i<3;i++)synthetic.next();
 uint32_t expected[4];for(int i=0;i<4;i++)expected[i]=synthetic.next();
 Tiny synthetic2;synthetic2.init(0xA514F291);uint32_t sample[12];
 for(int i=0;i<12;i++)sample[i]=synthetic2.next();
 for(int i=0;i<4;i++)if(sample[3+i]!=expected[i])return 4;
 uint16_t lookup[65536]={0};
 for(int k=0;k<16;k++)lookup[targets[k][0]&0xffff]|=(uint16_t)(1u<<k);
 std::atomic<unsigned long long> firstmatches(0), allmatches(0);
 const double start=omp_get_wtime();
 #pragma omp parallel
 {
  Tiny x;
  unsigned long long one=0,all=0;
  #pragma omp for schedule(dynamic,16384)
  for(uint64_t seed=begin;seed<begin+count;seed++){
   x.init(static_cast<uint32_t>(seed));uint32_t w[12];
   for(int i=0;i<12;i++)w[i]=x.next();
   for(int off=0;off<9;off++){
     uint16_t bits=lookup[w[off]&0xffff];
     while(bits){int k=__builtin_ctz((unsigned)bits);bits&=bits-1;
       if(w[off]!=targets[k][0])continue;
       one++;
       bool match=true;
       for(int i=1;i<4;i++)if(w[off+i]!=targets[k][i]){match=false;break;}
       if(match){all++;printf("FOUND seed=%" PRIu64 " target=%d offset=%d\n",seed,k,off);}
     }
   }
  }
  firstmatches.fetch_add(one,std::memory_order_relaxed);
  allmatches.fetch_add(all,std::memory_order_relaxed);
 }
 printf("RFC8682_POSITIVE_PASS source_tests=16 offsets=0..8 start=%" PRIu64 " count=%" PRIu64 " 32bit_firstword_matches=%llu exact16byte_matches=%llu elapsed=%.3f\n",begin,count,(unsigned long long)firstmatches.load(),(unsigned long long)allmatches.load(),omp_get_wtime()-start);
 return 0;
}
