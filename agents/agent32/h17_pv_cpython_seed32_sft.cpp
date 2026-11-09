// Agent32: independent historian uint32 CPython Random seed producer, source-only.
// Compile: C++17 -O3; execute with [lo hi) uint32 seed subrange.
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <chrono>

struct PythonMT {
    std::array<uint32_t,624> a{};
    int index=624;
    static constexpr uint32_t mag=0x9908b0dfu;
    void seed(uint32_t key) {
        a[0]=19650218;
        for(int i=1;i<624;i++) a[i]=1812433253u*(a[i-1]^(a[i-1]>>30))+(uint32_t)i;
        int i=1;
        for(int k=624;k;k--) {
            a[i]=(a[i]^((a[i-1]^(a[i-1]>>30))*1664525u))+key;
            ++i;
            if(i>=624){a[0]=a[623];i=1;}
        }
        for(int k=623;k;k--) {
            a[i]=(a[i]^((a[i-1]^(a[i-1]>>30))*1566083941u))-(uint32_t)i;
            ++i;
            if(i>=624){a[0]=a[623];i=1;}
        }
        a[0]=0x80000000u;
        index=624;
    }
    void twist() {
        for(int kk=0;kk<227;kk++){
            uint32_t y=(a[kk]&0x80000000u)|(a[kk+1]&0x7fffffffu);
            a[kk]=a[kk+397]^(y>>1)^((y&1u)?mag:0u);
        }
        for(int kk=227;kk<623;kk++){
            uint32_t y=(a[kk]&0x80000000u)|(a[kk+1]&0x7fffffffu);
            a[kk]=a[kk-227]^(y>>1)^((y&1u)?mag:0u);
        }
        uint32_t y=(a[623]&0x80000000u)|(a[0]&0x7fffffffu);
        a[623]=a[396]^(y>>1)^((y&1u)?mag:0u);
        index=0;
    }
    uint32_t next32() {
        if(index>=624)twist();
        uint32_t y=a[index++];
        y^=(y>>11);y^=(y<<7)&0x9d2c5680u;y^=(y<<15)&0xefc60000u;y^=(y>>18);
        return y;
    }
    double random(){
        uint32_t hi=next32()>>5,lo=next32()>>6;
        return (hi*67108864.0 + lo)/9007199254740992.0;
    }
};

static int milli(double u) {return (int)std::floor(12000.0+76000.0*u+0.5);}
// Source-owned historian seq100..107, no target commitment ever consulted.
static constexpr int historian[8]={18727,34411,59877,40783,14615,64141,56116,66108};

static void positives(){
    const std::pair<uint32_t,double> controls[]={
        {0u,0.8444218515250481},{1u,0.13436424411240122},
        {42u,0.6394267984578837},{5489u,0.7876110167997803},
        {0xffffffffu,0.6353574441341173},
    };
    for(const auto& p:controls){
        PythonMT z;z.seed(p.first); assert(std::abs(z.random()-p.second)<1e-14);
    }
    PythonMT z;z.seed(123456789u);
    int planted[8];for(int j=0;j<8;j++)planted[j]=milli(z.random());
    PythonMT t;t.seed(123456789u);
    for(int j=0;j<8;j++)assert(milli(t.random())==planted[j]);
    std::printf("CONTROLS five CPython independent seeds PASS, eight complete planted PV values PASS\n");
}
int main(int argc,char**argv){
    if(argc!=3){std::fprintf(stderr,"usage: %s lo hi\n",argv[0]);return 2;}
    const unsigned long long lo=std::strtoull(argv[1],nullptr,10),hi=std::strtoull(argv[2],nullptr,10);
    if(hi>4294967296ULL||hi<=lo){std::fprintf(stderr,"invalid seed range\n");return 2;}
    positives();
    auto t=std::chrono::steady_clock::now();
    uint64_t first=0,second=0,three=0;
    int maxfit=0;
    for(uint64_t k=lo;k<hi;k++) {
        PythonMT z;z.seed((uint32_t)k);
        if(milli(z.random())!=historian[0])continue;
        ++first;
        int fit=1;
        while(fit<8 && milli(z.random())==historian[fit])++fit;
        if(fit>=2)++second;
        if(fit>=3)++three;
        if(fit>maxfit)maxfit=fit;
        if(fit>=2)std::printf("CANDIDATE seed=%llu matched=%d\n",(unsigned long long)k,fit);
    }
    auto dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
    std::printf("RANGE %llu %llu checked=%llu pv_first=%llu pv_two=%llu pv_three=%llu best=%d seconds=%.3f\n",lo,hi,hi-lo,(unsigned long long)first,(unsigned long long)second,(unsigned long long)three,maxfit,dt);
    return 0;
}
