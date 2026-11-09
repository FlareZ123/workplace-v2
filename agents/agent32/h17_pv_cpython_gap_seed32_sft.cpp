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
#include <vector>
#include <utility>

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
// Reconstruct a Python random.random() float from any adjacent pair of native words.
static double from_words(uint32_t a,uint32_t b) {
    return ((double)(a>>5)*67108864.0+(double)(b>>6))/9007199254740992.0;
}

// State and value production are exactly CPython; unknown metadata draws may
// consume one or more native 32-bit words between readings.
static int search_path(const uint32_t* w, const int values[8],std::vector<int>& final_starts){
    std::vector<int> starts;
    for(int i=0;i<=32;i++)if(milli(from_words(w[i],w[i+1]))==values[0])starts.push_back(i);
    if(starts.empty()){final_starts.clear();return 0;}
    int matched=1;
    for(int step=1;step<8;step++){
        std::array<bool,315> seen{};
        std::vector<int> next;
        for(int old:starts)for(int at=old+2;at<=old+40 && at<314;at++){
            if(!seen[at] && milli(from_words(w[at],w[at+1]))==values[step]){
                seen[at]=true;next.push_back(at);
            }
        }
        if(next.empty())break;
        starts.swap(next);
        matched=step+1;
    }
    final_starts.swap(starts);
    return matched;
}

static void gap_positives(){
    PythonMT z;z.seed(123456789u);
    std::array<uint32_t,315> w{};
    for(auto& a:w)a=z.next32();
    const std::array<int,8> stages={7,12,21,30,38,59,76,84};
    int values[8];
    for(int k=0;k<8;k++)values[k]=milli(from_words(w[stages[k]],w[stages[k]+1]));
    std::vector<int> starts;
    const int fit=search_path(w.data(),values,starts);
    assert(fit==8);
    assert(!starts.empty());
    std::printf("GAP_SYNTHETIC seeded native-word gaps and complete eight-value reconstruction PASS\n");
}

int main(int argc,char**argv){
    if(argc!=3){std::fprintf(stderr,"usage: %s lo hi\n",argv[0]);return 2;}
    const uint64_t lo=std::strtoull(argv[1],nullptr,10),hi=std::strtoull(argv[2],nullptr,10);
    if(hi>4294967296ULL || hi<=lo){std::fprintf(stderr,"invalid seed range\n");return 2;}
    positives();gap_positives();
    uint64_t first=0,second=0,third=0,four=0,full=0;
    int maxfit=0;
    const auto t=std::chrono::steady_clock::now();
    for(uint64_t k=lo;k<hi;k++){
        PythonMT z;z.seed((uint32_t)k);
        std::array<uint32_t,315> w{};
        for(int j=0;j<35;j++)w[j]=z.next32();
        bool found=false;
        for(int j=0;j<=32;j++){
           if(milli(from_words(w[j],w[j+1]))==historian[0]){found=true;break;}
        }
        if(!found)continue;
        ++first;
        for(int j=35;j<315;j++)w[j]=z.next32();
        std::vector<int> positions;
        const int fit=search_path(w.data(),historian,positions);
        if(fit>=2)second++;
        if(fit>=3)third++;
        if(fit>=4)four++;
        if(fit>=8)full++;
        if(fit>maxfit)maxfit=fit;
        if(fit>=3)std::printf("SURVIVING_SEED seed=%llu first_eight_prefix=%d candidate_last_positions=%zu\n",(unsigned long long)k,fit,positions.size());
    }
    const auto dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
    std::printf("GAPPED_RANGE %llu %llu checked=%llu first=%llu two=%llu three=%llu four=%llu full8=%llu maxfit=%d seconds=%.3f\n",
      (unsigned long long)lo,(unsigned long long)hi,(unsigned long long)(hi-lo),
      (unsigned long long)first,(unsigned long long)second,(unsigned long long)third,
      (unsigned long long)four,(unsigned long long)full,maxfit,dt);
    return 0;
}
