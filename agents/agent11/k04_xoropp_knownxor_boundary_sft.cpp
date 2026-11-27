// Agent11: exact known-state-XOR xoroshiro128++ first-output inverse.
// Source-free synthetic controls. The first 17 rotated-sum bits depend on a small
// set of later predecessor bits; enumerate these, propagate all 64 output bits.
#include <cstdint>
#include <cstdio>
#include <vector>
#include <array>
#include <algorithm>
#include <random>
#include <chrono>
#include <stdexcept>
using U=std::uint64_t;
static inline U rol(U x,unsigned k){return(x<<k)|(x>>(64-k));}
static inline U output(U a,U b){return rol(a+b,17)+a;}
static inline void step(U &a,U&b){U t=a^b; a=rol(a,49)^t^(t<<21);b=rol(t,28);}
static inline int bit(U x,int j){return (x>>j)&1;}

struct InverseResult {U assignments=0, first_roots=0, pair_roots=0; unsigned boundary_unknown_bits=0; bool planted_found=false;};
InverseResult invert_known_xor(U y0,U t,U y1=0,bool second=false, U planted_a=0,U planted_b=0,bool verify_plant=false){
    std::array<int,64> pred;
    int prev=-1;
    for(int k=0;k<64;k++){
        pred[k]=prev;
        if(!bit(t,k))prev=k;
    }
    std::array<int,64> parent_to_id;parent_to_id.fill(-1);
    std::vector<int> unknown_parents;
    for(int j=0;j<17;j++){
       int p=pred[j+47];
       if(p>=0 && parent_to_id[p]<0){parent_to_id[p]=int(unknown_parents.size());unknown_parents.push_back(p);}
    }
    const unsigned d=unknown_parents.size();
    if(d>17)throw std::runtime_error("more than 17 boundary variables");
    InverseResult result;result.boundary_unknown_bits=d;
    const U count=U(1)<<d;
    for(U guess=0;guess<count;guess++){
        U a=0;
        int carry=0;
        for(int j=0;j<64;j++){
            int k=(j+47)%64;
            int p=pred[k];
            int u=0;
            if(p>=0){
                if(j<17){int i=parent_to_id[p];if(i<0)throw std::runtime_error("missing boundary id");u=int((guess>>i)&1);}
                else{if(p>=j)throw std::runtime_error("forward parent in main sweep");u=bit(a,p);}
            }
            int q=bit(t,k)^u;
            int y=bit(y0,j);
            int aj=y^q^carry;
            a|=U(aj)<<j;
            carry=y?(carry&q):(carry|q);
        }
        ++result.assignments;
        bool consistent=true;
        for(unsigned i=0;i<d;i++)if(bit(a,unknown_parents[i])!=int((guess>>i)&1)){consistent=false;break;}
        if(!consistent)continue;
        U b=a^t;
        if(output(a,b)!=y0)throw std::runtime_error("bit-propagation contradiction");
        ++result.first_roots;
        if(second){U aa=a,bb=b;step(aa,bb);if(output(aa,bb)==y1)++result.pair_roots;}
        if(verify_plant && a==planted_a && b==planted_b)result.planted_found=true;
    }
    return result;
}

// Independent 2^18 known-t reference implementation, controls only.
static inline int majority(int a,int b,int c){return(a&b)|(a&c)|(b&c);}
std::pair<U,U> reference_counts(U y0,U t,U y1){
 U roots=0,pairs=0;
 for(unsigned lo=0;lo<(1u<<17);lo++)for(int v17=0;v17<2;v17++){
  U a=lo;int u=0,v=v17;
  for(int j=17;j<64;j++){
   int k=j-17;
   int q=bit(t,k)^u;
   int aj=bit(y0,j)^q^v;
   a|=U(aj)<<j;
   v=majority(q,aj,v);
   u=bit(t,k)?u:bit(a,k);
  }
  U b=a^t;
  if(output(a,b)!=y0)continue;
  ++roots;
  U aa=a,bb=b;step(aa,bb);
  if(output(aa,bb)==y1)++pairs;
 }
 return {roots,pairs};
}

int main(int argc,char**argv){
  std::mt19937_64 rng(20261127);int N=argc>1?std::stoi(argv[1]):1000;
  U count=0,roots=0,pair=0;std::array<U,18> dcounts{};
  auto start=std::chrono::steady_clock::now();
  for(int i=0;i<N;i++){
     U a=rng(),b=rng(),t=a^b,y0=output(a,b);U aa=a,bb=b;step(aa,bb);U y1=output(aa,bb);
     auto r=invert_known_xor(y0,t,y1,true,a,b,true);
     if(!r.planted_found||r.pair_roots<1)throw std::runtime_error("planted state missed");
     if(i<64){auto ref=reference_counts(y0,t,y1);
       if(ref.first!=r.first_roots||ref.second!=r.pair_roots)throw std::runtime_error("independent exhaustive root enumeration disagrees");}
     count+=r.assignments;roots+=r.first_roots;pair+=r.pair_roots;
     ++dcounts[r.boundary_unknown_bits];
  }
  const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::printf("planted_states=%d PASS assignments=%llu first_output_roots=%llu pair_output_roots=%llu seconds=%.3f\n",
    N,(unsigned long long)count,(unsigned long long)roots,(unsigned long long)pair,elapsed);
  std::printf("boundary_unknown_bits_distribution=");
  for(unsigned i=0;i<18;i++)if(dcounts[i])std::printf(" %u:%llu",i,(unsigned long long)dcounts[i]);
  std::printf("\n");
  return 0;
}
