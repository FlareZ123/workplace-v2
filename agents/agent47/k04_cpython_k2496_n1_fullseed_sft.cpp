/* Read-only target-reaching source discriminator for H-17 K04.
 * Frozen source values S6/S7 reproduced by Python projector and positive.
 * Exhaustive CPython one-integer-word seed domain at actual k=2496 prior
 * outputs under conditional p951 native-printer chronology.
 */
#include <array>
#include <cstdint>
#include <cstdio>
#include <omp.h>

constexpr uint32_t U32_MASK=0xffffffffu;
constexpr uint32_t S6_SOURCE=0xE403BB7Du;
constexpr uint32_t S7_SOURCE=0x1F7B301Fu;
constexpr uint32_t A7_SOURCE=0x2AED5290u;
constexpr uint32_t F1=1664525u, F2=1566083941u;
constexpr uint32_t GREC=1812433253u;

using Register=std::array<uint32_t,624>;
static uint32_t mix(uint32_t mul,uint32_t x){return mul*(x^(x>>30));}
static Register initial_state(uint32_t seed){
  Register s{};s[0]=19650218u;
  for(unsigned i=1;i<624;i++)s[i]=mix(GREC,s[i-1])+i;
  unsigned i=1;
  for(unsigned k=624;k;k--){
    s[i]=(s[i]^mix(F1,s[i-1]))+seed;
    ++i;
    if(i>=624){s[0]=s[623];i=1;}
  }
  for(unsigned k=623;k;k--){
    s[i]=(s[i]^mix(F2,s[i-1]))-i;
    ++i;
    if(i>=624){s[0]=s[623];i=1;}
  }
  s[0]=0x80000000u;
  return s;
}

static std::array<uint32_t,8> g_prefix(){
  std::array<uint32_t,8> g{};
  g[0]=19650218u;
  for(unsigned i=1;i<8;i++)g[i]=mix(GREC,g[i-1])+i;
  return g;
}
static uint32_t a7_from_seed(uint32_t seed,const std::array<uint32_t,8>& g){
  uint32_t x=g[0];
  for(unsigned i=1;i<8;i++)x=(g[i]^mix(F1,x))+seed;
  return x;
}
static uint32_t a7_from_final(uint32_t s6,uint32_t s7){
  return (s7+7u)^mix(F2,s6);
}
int main(){
  const auto g=g_prefix();
  if(a7_from_final(S6_SOURCE,S7_SOURCE)!=A7_SOURCE)return 2;
  for(const auto [seed,a7,s6,s7]:{
      std::array<uint32_t,4>{0u,0x076FB8FBu,0xB8C84335u,0xBE06D941u},
      {1u,0x91AA5D5Du,0x51AAB1E2u,0x125C32CBu},
      {8131u,0xC8177294u,0x126F6A3Au,0x9285146Fu},
      {0x12345678u,0x0u,0xD253A7B2u,0x5732B664u},
      {0xFFFFFFFFu,0xD8F8BE0Au,0xF6A9E41Eu,0x5A220074u}}){
    const auto st=initial_state(seed);
    if((a7!=0u&&a7_from_seed(seed,g)!=a7)||st[6]!=s6||st[7]!=s7||
       a7_from_final(st[6],st[7])!=a7_from_seed(seed,g)){
      std::printf("SYNTHETIC_REFERENCE_FAIL seed=%08X\n",seed);return 3;
    }
  }
  std::printf("CPYTHON_SEED_POSITIVE_CONTROLS=5 PASS\n");std::fflush(stdout);
  uint64_t a7_survivors=0,full_survivors=0;
  #pragma omp parallel for schedule(static) reduction(+:a7_survivors,full_survivors)
  for(int64_t k=0;k<static_cast<int64_t>(1ull<<32);k++){
    uint32_t seed=static_cast<uint32_t>(k);
    if(a7_from_seed(seed,g)!=A7_SOURCE)continue;
    ++a7_survivors;
    auto s=initial_state(seed);
    if(s[6]==S6_SOURCE&&s[7]==S7_SOURCE)++full_survivors;
    #pragma omp critical
    {std::printf("A7_SURVIVOR seed=%08X predicted_S6=%08X predicted_S7=%08X full=%d\n",
     seed,s[6],s[7],s[6]==S6_SOURCE&&s[7]==S7_SOURCE);std::fflush(stdout);}
  }
  std::printf("COMPLETE_32BIT_DOMAIN=%llu A7_SURVIVORS=%llu HISTORICAL_PAIR_MATCHES=%llu\n",
        1ull<<32,(unsigned long long)a7_survivors,(unsigned long long)full_survivors);
  return !(a7_survivors==1u&&full_survivors==0u);
}
