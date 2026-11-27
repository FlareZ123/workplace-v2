// Agent23: exact xoroshiro128++ 1.0 first-output inversion with known t=a^b.
// Pure synthetic mathematical test; zero original archive inputs or diagnostics.
// Enumerates all 2^17 low-a choices and two choices of the output-addition
// carry into bit 17. The remainder of a is computed deterministically.
#include <cstdint>
#include <cstdio>
#include <random>
#include <chrono>
#include <stdexcept>
using U=uint64_t;
static inline U rotl(U x,int r){return (x<<r)|(x>>(64-r));}
static inline int bit(U x,int k){return int((x>>k)&1);}
static inline int maj(int x,int y,int z){return (x&y)|(x&z)|(y&z);}
static inline U output(U a,U b){return rotl(a+b,17)+a;}
static inline void step(U&a,U&b){U t=a^b; a=rotl(a,49)^t^(t<<21); b=rotl(t,28);}

template<class F> static inline void invert_t(U y,U t,F&&accept){
    for(unsigned lo=0;lo<(1u<<17);lo++)for(unsigned v17=0;v17<2;v17++){
        U a=lo;
        int u=0,v=v17;
        for(int j=17;j<64;j++){
            int k=j-17;
            int q=bit(t,k)^u;  // c[k] = t[k] XOR first-add carry u
            int aj=bit(y,j)^q^v;
            a|=U(aj)<<j;
            v=maj(q,aj,v);
            u=bit(t,k)?u:bit(a,k); // first-add carry update
        }
        U b=a^t;
        if(output(a,b)==y)accept(a,b); // checks wrapped low 17 output bits
    }
}

int main(){
    std::mt19937_64 r(0x20261127);
    constexpr int N=200;
    uint64_t total_roots=0,total_pair=0;
    auto start=std::chrono::steady_clock::now();
    for(int i=0;i<N;i++){
        U true_a=r(),true_b=r();
        U y0=output(true_a,true_b),t=true_a^true_b;
        U na=true_a,nb=true_b;
        step(na,nb);
        U y1=output(na,nb);
        int planted=0,root_count=0,pair_count=0;
        invert_t(y0,t,[&](U a,U b){
            root_count++;
            if(a==true_a&&b==true_b)planted++;
            step(a,b);
            if(output(a,b)==y1)pair_count++;
        });
        if(planted!=1||pair_count<1)
            throw std::runtime_error("planted inversion failed");
        total_roots+=root_count;
        total_pair+=pair_count;
    }
    auto sec=std::chrono::duration<double>(
        std::chrono::steady_clock::now()-start).count();
    std::printf("synthetic_controls=%d PASS first_output_roots=%llu "
                "two_output_states=%llu seconds=%.3f\n",N,
                (unsigned long long)total_roots,
                (unsigned long long)total_pair,sec);
}
