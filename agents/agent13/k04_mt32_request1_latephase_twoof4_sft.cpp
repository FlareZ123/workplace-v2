// Original PS-0417 REQUESTED1 late-stage native scalar MT32 whole-source gate; ≥2 of4 complete words.
// Selected PS-0417 ACK2 never read; planted native seed12345 phase951 2word-loss control.
// H-17 full native MT32 unsigned scalar-seed and late selected-job source-stage producer test.
// Original input: PS-261003-0417 ATTEMPT=1 STATE=REQUESTED raw CD3E4F216ADB2FB180DA2AA90B33F7A4.
// Original PS-0417 ATTEMPT=2 selected ACK2 and K04 commitment are excluded entirely.
// g++ -O3 -mavx512f -mavx512dq -std=c++17 -pthread k04_mt32_fullseed_cycle_sft.cpp -o scan
// ./scan planted 12336 12352 1
// ./scan tampered 12336 12352 1
// ./scan original 0 268435456 4   (16 disjoint shards of 2^28 each)
// ./scan request1 0 268435456 4  (same shard schedule, selected job original flank)
#include <immintrin.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <thread>
#include <vector>
using U=uint32_t;using V=__m512i;
constexpr U N=624u,MAG=0x9908b0dfu,UPPER=0x80000000u,LOWER=0x7fffffffu;
constexpr U PLANT_SEED=12345u,PLANT_PHASE=951u;
struct Source{std::array<std::array<U,2>,4> possible;};
inline V shr(V x,int s){return _mm512_srli_epi32(x,s);}
static U undo_right(U y,int s){U x=y;for(int k=0;k<6;++k)x=y^(x>>s);return x;}
static U undo_left(U y,int s,U m){U x=y;for(int k=0;k<6;++k)x=y^((x<<s)&m);return x;}
static U untemper(U y){
  y=undo_right(y,18);y=undo_left(y,15,0xefc60000u);
  y=undo_left(y,7,0x9d2c5680u);return undo_right(y,11);
}
static U swap32(U x){return __builtin_bswap32(x);}
static Source make_target(const std::string& mode){
  U original[4]={0x43c5bbfbu,0x583f4856u,0x063fbb64u,0xa5184579u};
  if(mode=="request1"||mode=="original"){
    const U request[4]={0x214F3ECDu,0xB12FDB6Au,0xA92ADA80u,0xA4F7330Bu};
    std::copy(std::begin(request),std::end(request),std::begin(original));
  }else if(mode=="request3"){
    const U request[4]={0xFC3DD544u,0x3A94D729u,0x7193D895u,0x64EC58DAu};
    std::copy(std::begin(request),std::end(request),std::begin(original));
  }else if(mode!="original"){
    std::mt19937 rng(PLANT_SEED);
    for(U k=0;k<PLANT_PHASE;++k)(void)rng();
    const U words[4]={U(rng()),U(rng()),U(rng()),U(rng())};
    const int perm[4]={2,0,3,1};
    for(int j=0;j<4;++j)original[j]=(j%2==0)?words[perm[j]]:swap32(words[perm[j]]);
    if(mode=="tampered"||mode=="planted2"||mode=="planted3")original[0]^=1u;
    if(mode=="tampered"||mode=="planted2"||mode=="planted3")original[1]^=1u;
    if(mode=="tampered"||mode=="planted3")original[2]^=1u;
  }
  Source t{};
  for(int i=0;i<4;++i){
    t.possible[i][0]=untemper(original[i]);
    t.possible[i][1]=untemper(swap32(original[i]));
  }
  return t;
}
static int match_count(const U* words,const Source& source){
  std::array<int,4> p{0,1,2,3};int best=0;
  do{
    int score=0;
    for(int i=0;i<4;++i){
      const auto& opt=source.possible[p[i]];
      if(words[i]==opt[0]||words[i]==opt[1])++score;
    }
    best=std::max(best,score);
  }while(std::next_permutation(p.begin(),p.end()));
  return best;
}
static V twist0(V x,V next,V other){
  V y=_mm512_or_si512(_mm512_and_si512(x,_mm512_set1_epi32(UPPER)),_mm512_and_si512(next,_mm512_set1_epi32(LOWER)));
  V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,_mm512_set1_epi32(1)),_mm512_set1_epi32(MAG));
  return _mm512_xor_si512(_mm512_xor_si512(other,shr(y,1)),magic);
}
struct Match{U seed;unsigned phase;};
struct Result{std::vector<Match> matches;std::uint64_t first=0;};
static Result scan(std::uint64_t start,std::uint64_t end,Source target,int thread){
  alignas(64) V s[624];alignas(64) U seeds[16];
  const V mul=_mm512_set1_epi32(1812433253u);
  const V upper=_mm512_set1_epi32(UPPER),lower=_mm512_set1_epi32(LOWER),mag=_mm512_set1_epi32(MAG),one=_mm512_set1_epi32(1u);
  V candidates[8];for(int i=0;i<4;++i)for(int j=0;j<2;++j)candidates[i*2+j]=_mm512_set1_epi32(target.possible[i][j]);
  Result result;
  for(std::uint64_t base=start;base<end;base+=16){
    for(int lane=0;lane<16;++lane)seeds[lane]=U(base+lane);
    s[0]=_mm512_load_si512((V*)seeds);
    for(int i=1;i<624;++i){
      V prev=s[i-1];
      s[i]=_mm512_add_epi32(_mm512_mullo_epi32(_mm512_xor_si512(prev,shr(prev,30)),mul),_mm512_set1_epi32(i));
    }
    for(int i=0;i<227;++i){
      V y=_mm512_or_si512(_mm512_and_si512(s[i],upper),_mm512_and_si512(s[i+1],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i+397],shr(y,1)),magic);
    }
    for(int i=227;i<623;++i){
      V y=_mm512_or_si512(_mm512_and_si512(s[i],upper),_mm512_and_si512(s[i+1],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i-227],shr(y,1)),magic);
    }
    {
      V y=_mm512_or_si512(_mm512_and_si512(s[623],upper),_mm512_and_si512(s[0],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[623]=_mm512_xor_si512(_mm512_xor_si512(s[396],shr(y,1)),magic);
    }
    // A second complete native twist exposes source stages 624..1247.
    // The original PS-0417 REQUESTED1 packet is tested at stages 900..980.
    for(int i=0;i<227;++i){
      V y=_mm512_or_si512(_mm512_and_si512(s[i],upper),_mm512_and_si512(s[i+1],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i+397],shr(y,1)),magic);
    }
    for(int i=227;i<623;++i){
      V y=_mm512_or_si512(_mm512_and_si512(s[i],upper),_mm512_and_si512(s[i+1],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[i]=_mm512_xor_si512(_mm512_xor_si512(s[i-227],shr(y,1)),magic);
    }
    {
      V y=_mm512_or_si512(_mm512_and_si512(s[623],upper),_mm512_and_si512(s[0],lower));
      V magic=_mm512_maskz_mov_epi32(_mm512_test_epi32_mask(y,one),mag);
      s[623]=_mm512_xor_si512(_mm512_xor_si512(s[396],shr(y,1)),magic);
    }
    // Probe all four possible source-word anchors, preserving packet-start range 900..980.
    constexpr unsigned PHASE_LO=900,PHASE_HI=980;
    for(unsigned probe=PHASE_LO;probe<=PHASE_HI+3;++probe){
      const unsigned i=probe-624;
      __mmask16 mask=0;
      for(const V& candidate:candidates)mask|=_mm512_cmpeq_epi32_mask(s[i],candidate);
      while(mask){
        int lane=__builtin_ctz(mask);mask&=mask-1;
        ++result.first;
        for(int back=0;back<4;++back){
          if(probe<PHASE_LO+static_cast<unsigned>(back))continue;
          const unsigned phase=probe-back;
          if(phase<PHASE_LO||phase>PHASE_HI)continue;
          U w[4];
          for(unsigned j=0;j<4;++j)w[j]=((U*)&s[phase-624+j])[lane];
          const int score=match_count(w,target);
          if(score>=2){
            std::printf("THREAD%d SOURCE_MATCH score=%d seed=%u phase=%u native=%08X,%08X,%08X,%08X\n",thread,score,seeds[lane],phase,w[0],w[1],w[2],w[3]);
            result.matches.push_back({seeds[lane],phase});
          }
        }
      }
    }
  }
  return result;
}
int main(int argc,char** argv){
  if(argc!=5){std::fprintf(stderr,"Usage: scan original|request1|request3|planted|tampered start end threads\n");return 2;}
  const std::string mode(argv[1]);
  if(mode!="original"&&mode!="request1"&&mode!="request3"&&mode!="planted"&&mode!="planted2"&&mode!="planted3"&&mode!="tampered")return 2;
  const std::uint64_t start=std::strtoull(argv[2],nullptr,0),end=std::strtoull(argv[3],nullptr,0);
  const int threads=std::atoi(argv[4]);
  if(start>=end||end>4294967296ull||start%16||end%16||threads<1||threads>8)return 2;
  const Source target=make_target(mode);
  const auto t0=std::chrono::steady_clock::now();
  std::vector<std::thread> jobs;std::vector<Result> results(threads);
  const std::uint64_t partition=(((end-start+threads-1)/threads)+15)/16*16;
  for(int i=0;i<threads;++i){
    const std::uint64_t lo=std::min(end,start+i*partition),hi=std::min(end,lo+partition);
    jobs.emplace_back([&,i,lo,hi]{results[i]=scan(lo,hi,target,i);});
  }
  for(auto& job:jobs)job.join();
  std::uint64_t first=0;std::size_t full=0;
  for(const auto& r:results){first+=r.first;full+=r.matches.size();}
  if(mode=="planted"||mode=="tampered"||mode=="planted2"||mode=="planted3"){
    if((mode=="planted3"||mode=="tampered")&&full!=0)return 3;
    if((mode=="planted"||mode=="planted2")&&full==0)return 3;
    if(mode=="planted"||mode=="planted2"){
      bool found=false;
      for(const auto& r:results)for(const auto& m:r.matches)
        if(m.seed==PLANT_SEED&&m.phase==PLANT_PHASE)found=true;
      if(!found)return 4;
    }
    std::printf("CONTROL %s PASS\n",mode.c_str());
  }
  const auto ms=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-t0).count();
  std::printf("SUMMARY mode=%s begin=%llu end=%llu seeds=%llu firstword_hits=%llu two_word_preservation_matches=%zu elapsed_ms=%lld\n",mode.c_str(),(unsigned long long)start,(unsigned long long)end,(unsigned long long)(end-start),(unsigned long long)first,full,(long long)ms);
  return 0;
}
