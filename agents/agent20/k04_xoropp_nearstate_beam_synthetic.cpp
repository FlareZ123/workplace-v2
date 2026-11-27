// Synthetic-only near-state repair feasibility for xoroshiro128++ 1.0.
// This file contains NO historical archive values, masks, targets or commitments.
// A beam can repair a near-c sum-state guess; it cannot produce a near guess.
// Build: g++ -O3 -std=c++17 k04_xoropp_nearstate_beam_synthetic.cpp -o beam && ./beam
#include <cstdint>
#include <iostream>
#include <random>
#include <algorithm>
#include <unordered_map>
#include <vector>
#include <utility>
#include <chrono>
using U=uint64_t;
static inline U rot(U a,unsigned r){return (a<<r)|(a>>(64-r));}
static inline U f(U c,U y0){U a=y0-rot(c,17),b=c-a,t=a^b,ap=rot(a,49)^t^(t<<21),bp=rot(t,28);return rot(ap+bp,17)+ap;}
static inline int e(U c,U y0,U y1){return __builtin_popcountll(f(c,y0)^y1);}
U beam(U start,U y0,U y1,int width,int depth){
 std::vector<std::pair<int,U>> frontier={{e(start,y0,y1),start}};
 if(frontier[0].first==0)return start;
 std::unordered_map<U,int> seen;seen.reserve(width*depth*65);seen[start]=0;
 for(int step=1;step<=depth;step++){
  std::vector<std::pair<int,U>> candidates;candidates.reserve(width*64);
  for(auto [prev,x]:frontier)for(int j=0;j<64;j++){
   U z=x^(U(1)<<j);if(!seen.emplace(z,step).second)continue;
   int q=e(z,y0,y1);if(q==0)return z;
   candidates.emplace_back(q,z);
  }
  if(candidates.empty())break;
  int keep=std::min(width,(int)candidates.size());
  std::partial_sort(candidates.begin(),candidates.begin()+keep,candidates.end(),
                    [](auto l,auto r){return l<r;});
  frontier.assign(candidates.begin(),candidates.begin()+keep);
 }
 return 0;
}
int main(){
 std::mt19937_64 rng(20261129);const int n=96;
 for(int width:{16,64,256})for(int k=2;k<=10;k+=2){
  int ok=0;auto st=std::chrono::steady_clock::now();
  for(int trial=0;trial<n;trial++){
   U truth=rng(),y0=rng(),y1=f(truth,y0),x=truth;int ix[64];
   for(int i=0;i<64;i++)ix[i]=i;
   for(int j=0;j<k;j++){int z=j+rng()%(64-j);std::swap(ix[z],ix[j]);x^=U(1)<<ix[j];}
   U ans=beam(x,y0,y1,width,8);if(ans==truth)ok++;
  }
  auto t=std::chrono::duration<double>(std::chrono::steady_clock::now()-st).count();
  std::cout<<"width="<<width<<" corruption="<<k<<" n="<<n
           <<" exact_true_state="<<ok<<" seconds="<<t<<"\n";
 }
}
