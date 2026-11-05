// H-17 K04 original-source scalar-MT deep-prefix producer test.
// FULL 2^32 uint32 seeds x 8192 unseen prefix draw positions, with a complete
// 16-byte intact first packet as filter. The disputed selected ACK is omitted.
// Compile: g++ -O3 -std=c++17 -march=native k04_scalar_deepprefix_sft.cpp -o deep
// Run: deep 0 1000 8191
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>

using Words = std::array<uint32_t,4>;
struct Counts {
    uint64_t prefix_le=0, prefix_be=0, full_le=0, full_be=0;
};
static constexpr Words source_le{{0x43C5BBFBu,0x583F4856u,0x063FBB64u,0xA5184579u}};
static constexpr Words source_be{{0xFBBBC543u,0x56483F58u,0x64BB3F06u,0x794518A5u}};

static Words at(uint32_t seed,uint32_t offset) {
    std::mt19937 mt(seed);
    for(uint32_t j=0;j<offset;j++) (void)mt();
    return {{static_cast<uint32_t>(mt()),static_cast<uint32_t>(mt()),
             static_cast<uint32_t>(mt()),static_cast<uint32_t>(mt())}};
}

static Counts scan(uint64_t begin,uint64_t end,uint32_t last,
                   const Words& le,const Words& be,bool report){
    Counts out;
    for(uint64_t i=begin;i<end;i++){
        std::mt19937 mt(static_cast<uint32_t>(i));
        uint32_t a=mt(),b=mt(),c=mt();
        for(uint32_t offset=0;offset<=last;offset++){
            const uint32_t d=mt();
            if(a==le[0]) {
                ++out.prefix_le;
                if(b==le[1]&&c==le[2]&&d==le[3]) {
                    ++out.full_le;
                    if(report) std::cout<<"SOURCE_FULL_LE seed="<<i<<" offset="<<offset<<"\n";
                }
            }
            if(a==be[0]){
                ++out.prefix_be;
                if(b==be[1]&&c==be[2]&&d==be[3]){
                    ++out.full_be;
                    if(report) std::cout<<"SOURCE_FULL_BE seed="<<i<<" offset="<<offset<<"\n";
                }
            }
            a=b;b=c;c=d;
        }
    }
    return out;
}
static void selftest(uint32_t last) {
    std::mt19937 ref(5489u);
    if(ref()!=3499211612u||ref()!=581869302u) throw std::runtime_error("MT reference failed");
    for(uint32_t seed: {0u,0x5A1704A2u,0xDEADBEEFu}) {
        for(uint32_t phase: {0u,last/2,last}){
            const Words planted=at(seed,phase);
            const Counts pos=scan(seed,uint64_t(seed)+1,last,planted,planted,false);
            if(pos.full_le!=1||pos.full_be!=1)
                throw std::runtime_error("full 16-byte seeded positive failed");
            const Counts bad=scan(seed,uint64_t(seed)+1,last,Words{{0,0,0,0}},
                                  Words{{0,0,0,0}},false);
            if(bad.full_le||bad.full_be) throw std::runtime_error("negative failed");
        }
    }
}
int main(int argc,char** argv){
    try {
        if(argc!=4) throw std::runtime_error("usage: <seed_start> <seed_end> <last_offset>");
        const uint64_t begin=std::stoull(argv[1]),end=std::stoull(argv[2]);
        const uint32_t last=static_cast<uint32_t>(std::stoul(argv[3]));
        if(begin>=end||end>4294967296ULL||last>8191u)
            throw std::runtime_error("unsupported interval");
        selftest(last);
        const auto t=std::chrono::steady_clock::now();
        const Counts c=scan(begin,end,last,source_le,source_be,true);
        const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
        std::cout<<std::fixed<<std::setprecision(4)
                 <<"RESULT seed_begin="<<begin<<" seed_end="<<end<<" last_offset="<<last
                 <<" tested="<<(end-begin)*(uint64_t(last)+1)
                 <<" prefix_le="<<c.prefix_le<<" prefix_be="<<c.prefix_be
                 <<" full_le="<<c.full_le<<" full_be="<<c.full_be
                 <<" seconds="<<seconds<<"\n";
        return (c.full_le || c.full_be) ? 10 : 0;
    }catch(const std::exception& e){
        std::cerr<<"ERROR "<<e.what()<<"\n";return 2;
    }
}
