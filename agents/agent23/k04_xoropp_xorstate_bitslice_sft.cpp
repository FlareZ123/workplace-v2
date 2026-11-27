// Agent23: exact source-free xoroshiro128++ 1.0 inverse given t=a XOR b.
// Bitslice 64 independent candidate assignments to a's low 17 bits.
// All valid roots are independently replayed; source inputs not embedded.
#include <cstdint>
#include <cstdio>
#include <random>
#include <chrono>
#include <stdexcept>
using U=uint64_t;
constexpr U ALL=~U(0);
static inline U rot(U x,int n){return (x<<n)|(x>>(64-n));}
static inline U maj(U x,U y,U z){return (x&y)|(x&z)|(y&z);}
static inline U output(U a,U b){return rot(a+b,17)+a;}
static inline void step(U &a,U &b){U t=a^b;a=rot(a,49)^t^(t<<21);b=rot(t,28);}

template<class F> void invert(U y,U t,F&&f){
    U lowpattern[6]{};
    for(int j=0;j<6;j++)for(unsigned lane=0;lane<64;lane++)
        if((lane>>j)&1)lowpattern[j]|=U(1)<<lane;
    for(unsigned base=0;base<(1u<<17);base+=64){
        U a[64]{};
        for(int j=0;j<17;j++)
            a[j]=j<6?lowpattern[j]:((base>>j)&1?ALL:U(0));
        for(int v17=0;v17<2;v17++){
            U u[65]{};
            U v=v17?ALL:U(0);
            for(int j=17;j<64;j++){
                int k=j-17;
                U q=(t>>k)&1?~u[k]:u[k];
                a[j]=(((y>>j)&1)?ALL:U(0))^q^v;
                v=maj(q,a[j],v);
                u[k+1]=(t>>k)&1?u[k]:a[k];
            }
            for(int k=47;k<64;k++)
                u[k+1]=(t>>k)&1?u[k]:a[k];
            U valid=ALL; v=0;
            for(int j=0;j<17;j++){
                int k=j+47;
                U q=(t>>k)&1?~u[k]:u[k];
                U actual=q^a[j]^v;
                valid&=(y>>j)&1?actual:~actual;
                v=maj(q,a[j],v);
            }
            valid&=~(v^(v17?ALL:U(0)));
            while(valid){
                int lane=__builtin_ctzll(valid);
                U av=0;
                for(int j=0;j<64;j++)av|=((a[j]>>lane)&1)<<j;
                U bv=av^t;
                if(output(av,bv)!=y)throw std::runtime_error("full replay failed");
                f(av,bv);
                valid&=valid-1;
            }
        }
    }
}
int main(){
 std::mt19937_64 r(0x20261127);
 constexpr int N=200;
 uint64_t roots=0,pairs=0,planted=0;
 auto tic=std::chrono::steady_clock::now();
 for(int i=0;i<N;i++){
    U a=r(),b=r(),t=a^b,y0=output(a,b);
    U aa=a,bb=b; step(aa,bb);U y1=output(aa,bb);
    int truecount=0,paircount=0;
    invert(y0,t,[&](U ca,U cb){
        roots++;
        if(ca==a&&cb==b){planted++;truecount++;}
        step(ca,cb);
        if(output(ca,cb)==y1){pairs++;paircount++;}
    });
    if(truecount!=1||paircount!=1)throw std::runtime_error("state inverse planted control");
 }
 double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-tic).count();
 std::printf("synthetic=%d exact=%llu roots=%llu pair_hits=%llu seconds=%.6f\n",N,
 (unsigned long long)planted,(unsigned long long)roots,(unsigned long long)pairs,sec);
}
