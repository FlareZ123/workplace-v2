/* H17 first-original-intact-packet test: 32-bit scalar-seeded C++ mt19937_64,
   packet = first two 64bit native words, either byte-order. No selected K04 bytes.
   Source spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
*/
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <chrono>
#include <array>
#include <omp.h>
constexpr uint64_t M=6364136223846793005ULL,UM=0xFFFFFFFF80000000ULL,LM=0x7FFFFFFFULL;
constexpr uint64_t MAT=0xB5026F5AA96619E9ULL;
constexpr uint64_t TARGET_LE=0x583F485643C5BBFBULL,TARGET_BE=0xFBBBC54356483F58ULL;
constexpr uint64_t SECOND_LE=0xA5184579063FBB64ULL,SECOND_BE=0x64BB3F06794518A5ULL;
inline uint64_t t64(uint64_t x){
    x^=(x>>29)&0x5555555555555555ULL;
    x^=(x<<17)&0x71D67FFFEDA60000ULL;
    x^=(x<<37)&0xFFF7EEE000000000ULL;
    return x^(x>>43);
}
inline void first2(uint32_t seed,uint64_t &a,uint64_t &b){
    uint64_t x=seed,x0=x,x1=0,x2=0,x156=0,x157=0;
    for(uint64_t i=1;i<=157;i++){
        x=M*(x^(x>>62))+i;
        if(i==1)x1=x;
        if(i==2)x2=x;
        if(i==156)x156=x;
        if(i==157)x157=x;
    }
    uint64_t y=(x0&UM)|(x1&LM);
    a=t64(x156^(y>>1)^((y&1)?MAT:0));
    y=(x1&UM)|(x2&LM);
    b=t64(x157^(y>>1)^((y&1)?MAT:0));
}
int main(int argc,char **argv){
    const uint64_t count=argc>1?strtoull(argv[1],nullptr,10):1048576ull;
    const uint64_t start=argc>2?strtoull(argv[2],nullptr,10):0ull;
    if(start+count>4294967296ull)return 3;
    constexpr std::array<uint32_t,9> seeds{0u,1u,2u,5489u,8131u,0x12345678u,0x80000000u,0xDEADBEEFu,0xFFFFFFFFu};
    for(auto seed:seeds){
        uint64_t a,b;first2(seed,a,b);
        std::mt19937_64 rng(seed);
        if(a!=rng()||b!=rng()){
            printf("NATIVE_MT64_FAIL seed=%u got=%016llX/%016llX\n",seed,(unsigned long long)a,(unsigned long long)b);
            return 4;
        }
    }
    printf("NATIVE_MT64_POSITIVE_CONTROLS=9 PASS\n");fflush(stdout);
    uint64_t hits1=0,hits2=0; const auto t0=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(static) reduction(+:hits1,hits2)
    for(int64_t i=0;i<(int64_t)count;i++){
        const uint32_t seed=(uint32_t)(start+(uint64_t)i);
        uint64_t a,b;first2(seed,a,b);
        if(a==TARGET_LE||a==TARGET_BE){
            const bool le=a==TARGET_LE;hits1++;
            if((le && b==SECOND_LE)||(!le && b==SECOND_BE))hits2++;
#pragma omp critical
            {printf("FIRST64_HIT seed=%u endian=%s second=%016llX full=%d\n",seed,le?"LE":"BE",(unsigned long long)b,(le&&b==SECOND_LE)||(!le&&b==SECOND_BE));fflush(stdout);}
        }
    }
    const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    printf("START=%llu COUNT=%llu FIRST64_HITS=%llu FULL16_HITS=%llu SECONDS=%.3f RATE=%.0f/s THREADS=%d\n",
         (unsigned long long)start,(unsigned long long)count,(unsigned long long)hits1,(unsigned long long)hits2,sec,count/sec,omp_get_max_threads());
    return 0;
}
