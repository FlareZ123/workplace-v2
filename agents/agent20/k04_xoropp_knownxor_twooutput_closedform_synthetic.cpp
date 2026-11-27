// Source-free exact known-XOR two-output inversion for xoroshiro128++ 1.0.
// Agent20, 2026-11-27. Composition of Agent12's rotadd17 Diophantine inverse
// with the genuine xoroshiro transition and Agent23/11's known-t problem.
// Neither this code nor its tests contain historical outputs or archive values.
// Build: g++ -std=c++17 -O3 -Wall -Wextra this_file.cpp -o inv && ./inv
#include <cstdint>
#include <cstddef>
#include <iostream>
#include <array>
#include <algorithm>
#include <random>
#include <chrono>
#include <cassert>
using U = uint64_t;
using I = __int128_t;
static inline U rl(U x, unsigned n) {return (x << n)|(x >> (64-n));}
static inline U rr(U x, unsigned n) {return (x >> n)|(x << (64-n));}
static inline U output(U a, U b) {return rl(a+b,17)+a;}
static inline void next(U &a, U &b) {
  U t=a^b;
  a=rl(a,49)^t^(t<<21);
  b=rl(t,28);
}

constexpr I P=((I)1<<17)+1, Q=((I)1<<47)+1;
constexpr I PR=P/3, QPR_INV=34956; // (Q/3)^(-1) mod (P/3)
// Enumerate all c for c+ROTL64(c,17)==z modulo 2^64.
// c=B+2^47*A, with 0<=A<2^17, 0<=B<2^47:
// z+k*2^64=(2^17+1)*B+(2^47+1)*A, k=0 or1.
// Since gcd(P,Q)=3, one residue A mod P/3 has up to three representatives.
static int inverse_rot_sum(U z, U *outc) {
  int n=0;
  for(int k=0;k<2;k++) {
    I rhs=(I)z+((I)k<<64);
    if(rhs%3)continue;
    I a0=((rhs/3)%PR*QPR_INV)%PR;
    for(int j=0;j<3;j++) {
      I A=a0+(I)j*PR;
      if(A>=((I)1<<17))continue;
      I d=rhs-Q*A;
      if(d<0 || d%P)continue;
      I B=d/P;
      if(B>=((I)1<<47))continue;
      U c=(U)(B+(A<<47));
      assert(c+rl(c,17)==z);
      outc[n++]=c;
      assert(n<=6);
    }
  }
  return n;
}

// For given y0,y1 and t=a0 XOR b0, b1=ROTL(t,28) is known.
// y1+b1=c1+ROTL(c1,17); invert this <=3-root relation first.
// a1=c1-b1, a0=ROTR(a1 XOR t XOR(t<<21),49), b0=a0 XOR t.
// Finally replay y0; every returned state exactly matches BOTH outputs.
static int inverse_pair_known_t(U y0,U y1,U t, U *oa,U *ob) {
  U b1=rl(t,28), roots[6];
  int nrot=inverse_rot_sum(y1+b1,roots), n=0;
  for(int i=0;i<nrot;i++) {
    U a1=roots[i]-b1;
    U a0=rr(a1^t^(t<<21),49), b0=a0^t;
    if(output(a0,b0)!=y0)continue;
    U a=a0,b=b0;next(a,b);
    assert(output(a,b)==y1);
    oa[n]=a0;ob[n]=b0;n++;
  }
  return n;
}
int main() {
  std::mt19937_64 rng(20261130);
  constexpr int N=1000000;
  auto start=std::chrono::steady_clock::now();
  int found=0, multiple=0, wrong_hits=0;
  std::array<int,7> root_counts{};
  for(int i=0;i<N;i++) {
    U a0=rng(),b0=rng(),t=a0^b0;
    U z=a0+rl(a0,17), roots[6];
    int nr=inverse_rot_sum(z,roots);
    root_counts[nr]++;
    assert(std::find(roots,roots+nr,a0)!=roots+nr);
    U a=a0,b=b0,y0=output(a,b);
    next(a,b);
    U y1=output(a,b), aa[6], bb[6];
    int n=inverse_pair_known_t(y0,y1,t,aa,bb);
    assert(n>0);
    bool includes_planted=false;
    for(int k=0;k<n;k++) {
      assert(output(aa[k],bb[k])==y0);
      U a2=aa[k],b2=bb[k];next(a2,b2);
      assert(output(a2,b2)==y1);
      includes_planted|=(aa[k]==a0 && bb[k]==b0);
    }
    assert(includes_planted);
    found++;
    multiple+=(n>1);
    U wrong=rng();
    if(wrong==t)wrong^=1;
    wrong_hits+=(inverse_pair_known_t(y0,y1,wrong,aa,bb)>0);
  }
  for(U z : std::array<U,4>{{U(0),U(1),U(UINT64_MAX),
                                  U(0x123456789ABCDEF0ULL)}}) {
    U rr[6];int n=inverse_rot_sum(z,rr);
    for(int k=0;k<n;k++)assert(rr[k]+rl(rr[k],17)==z);
  }
  double dt=std::chrono::duration<double>(
      std::chrono::steady_clock::now()-start).count();
  std::cout<<"source_free_planted "<<found<<"/"<<N
           <<" multiple_pair_roots "<<multiple
           <<" wrong_t_hits "<<wrong_hits
           <<" elapsed_seconds "<<dt<<"\nrot_sum_root_hist";
  for(size_t k=0;k<root_counts.size();k++)
    std::cout<<" "<<k<<":"<<root_counts[k];
  std::cout<<"\n";
}
