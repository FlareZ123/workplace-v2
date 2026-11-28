// Exact xoroshiro128++ (49,21,28) 2-output inverse with 32 anchored bits
// of FIRST state word a0. Source-free reproducible control, 2026-11-28.
// The source-linked runner must be run LOCALLY; no archive bits are embedded.
// Build: g++ -O3 -std=c++17 -fopenmp k04_xoropp_firsta32_synthetic.cpp -o a32
// Run without arguments for complete planted 2^32 positive and wrong-anchor
// negative. Optional CLI y0 y1 anchor32 known_half_high 4294967296 prints
// only match COUNTS (hex first four, decimal final; never source state bytes).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <chrono>
#include <cstring>
using U=uint64_t;
static U rol(U x,unsigned n){return (x<<n)|(x>>(64-n));}
static U ror(U x,unsigned n){return (x>>n)|(x<<(64-n));}
static U out(U a,U b){return rol(a+b,17)+a;}
static void advance(U& a,U& b) {
  U t=a^b; a=rol(a,49)^t^(t<<21); b=rol(t,28);
}
struct Result {U hits,first_a,first_b;};
static Result run(U y0,U y1,U fixed,bool high,U end) {
  U hits=0, first_a=0,first_b=0;
  bool first_seen=false;
  #pragma omp parallel for reduction(+:hits) schedule(static)
  for(U suffix=0;suffix<end;suffix++) {
    U a=high?((fixed<<32)|suffix):((suffix<<32)|fixed);
    // Exact inverse of output0: b=ROTR(y0-a,17)-a.
    U b=ror(y0-a,17)-a,t=a^b;
    U a1=rol(a,49)^t^(t<<21),b1=rol(t,28);
    if(rol(a1+b1,17)+a1 == y1) {
      ++hits;
      #pragma omp critical
      {
        if(!first_seen) {first_seen=true;first_a=a;first_b=b;}
      }
    }
  }
  return {hits,first_a,first_b};
}
static void selftest(bool full) {
  U a0=(U(0xF1234567)<<32)|U(0x89ABCDEF);
  U b0=0x3141592653589793ULL;
  U a=a0,b=b0,y0=out(a,b);advance(a,b);U y1=out(a,b);
  if(full) {
    Result r=run(y0,y1,0x89ABCDEF,false,U(1)<<32);
    assert(r.hits==1 && r.first_a==a0 && r.first_b==b0);
    Result miss=run(y0,y1,0x89ABCDEE,false,U(1)<<32);
    assert(miss.hits==0);
    std::puts("full 2^32 planted state + wrong-anchor negative: PASS");
  } else {
    // A separate planted state with unknown high portion inside 2^20.
    a0=(U(0x000ABCDE)<<32)|U(0x89ABCDEF);
    a=a0;b=b0;y0=out(a,b);advance(a,b);y1=out(a,b);
    Result r=run(y0,y1,0x89ABCDEF,false,U(1)<<20);
    assert(r.hits==1 && r.first_a==a0 && r.first_b==b0);
  }
}
int main(int argc,char**argv) {
  if(argc==1){selftest(true);return 0;}
  if(argc!=6){std::fprintf(stderr,"usage: a32 y0hex y1hex known32hex high(0/1) 4294967296\\n");return 2;}
  selftest(false);
  U y0=std::strtoull(argv[1],nullptr,16),y1=std::strtoull(argv[2],nullptr,16);
  U anchor=std::strtoull(argv[3],nullptr,16);
  int high=std::atoi(argv[4]);U count=std::strtoull(argv[5],nullptr,10);
  if(anchor>0xffffffffULL || (high!=0 && high!=1) || count>(U(1)<<32))return 3;
  auto st=std::chrono::steady_clock::now();
  Result result=run(y0,y1,anchor,high,count);
  double sec=std::chrono::duration<double>(
   std::chrono::steady_clock::now()-st).count();
  std::printf("synthetic_positive PASS source_pair_full_match=%llu exhaustive_unknown32=%d seconds=%.3f\\n",
   (unsigned long long)result.hits,int(count==(U(1)<<32)),sec);
  return 0;
}
