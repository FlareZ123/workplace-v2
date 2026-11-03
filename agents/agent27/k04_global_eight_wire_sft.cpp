// Agent 27 | H-17 K04 | global 8-bit wire-permutation copier SFT.
// Read-only original source; C++17 with OpenSSL libcrypto.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>

using Coupon = std::array<uint8_t,16>;
using Hash = std::array<uint8_t,32>;

template<size_t N> static std::array<uint8_t,N> decode(const char* s) {
    std::array<uint8_t,N> x{};
    if(std::char_traits<char>::length(s)!=2*N)std::abort();
    for(size_t i=0;i<N;++i) {
        unsigned v=0;
        if(std::sscanf(std::string(s+2*i,2).c_str(),"%02x",&v)!=1)std::abort();
        x[i]=static_cast<uint8_t>(v);
    }
    return x;
}
static Hash sha(const uint8_t* x,size_t n) {
    Hash h{};SHA256(x,n,h.data());return h;
}
static bool accepted(const Coupon& c,const Hash& h) {
    return sha(c.data(),c.size())==h;
}
static uint8_t mapBits(uint8_t x,const std::array<int,8>& p) {
    uint8_t y=0;
    for(int i=0;i<8;i++)y|=static_cast<uint8_t>(((x>>p[i])&1)<<i);
    return y;
}
int main(int argc,char** argv) {
    const char* sourcePath=argc>1?argv[1]:"resources/evidence/print/spool-reconstruction.log";
    std::ifstream file(sourcePath,std::ios::binary);
    if(!file){std::fprintf(stderr,"Source absent\n");return 2;}
    const std::string spool((std::istreambuf_iterator<char>(file)),{});
    const Hash spoolHash=decode<32>("7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
    if(sha(reinterpret_cast<const uint8_t*>(spool.data()),spool.size())!=spoolHash)return 3;
    const std::string stamp="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
    size_t pos=spool.find(stamp);
    if(pos==std::string::npos)return 4;
    const Coupon payload=decode<16>("A9A9DC5731A5E2AE879C47215C2559D5");
    if(spool.substr(pos+stamp.size(),32)!="A9A9DC5731A5E2AE879C47215C2559D5")return 5;
    const Coupon mask=decode<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
    const Hash target=decode<32>("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
    Coupon component{};for(int i=0;i<16;i++)component[i]=payload[i]^mask[i];
    if(accepted(component,target))return 6;

    const std::array<int,8> positiveMap{2,0,5,7,3,4,1,6};
    const Coupon positive=decode<16>("AC7F461F70785C93D91CCEF6D12B6B80");
    const Hash positiveTarget=decode<32>("5773e85231dac63331f9a1046db27a804d7c5fa68b819d799fe380d82824b267");
    Coupon check{};for(int i=0;i<16;i++)check[i]=mapBits(payload[i],positiveMap)^0x37^mask[i];
    if(check!=positive||!accepted(check,positiveTarget))return 7;

    std::array<int,8> permutation{0,1,2,3,4,5,6,7};
    uint64_t checks[3]={},hits[3]={},positiveHits=0;
    auto start=std::chrono::steady_clock::now();
    do {
        std::array<Coupon,3> base{};
        for(int i=0;i<16;i++) {
            base[0][i]=mapBits(payload[i],permutation)^mask[i];
            base[1][i]=mapBits(mask[i],permutation)^payload[i];
            base[2][i]=mapBits(component[i],permutation);
        }
        for(int stage=0;stage<3;stage++)
        for(int offset=0;offset<256;offset++) {
            Coupon candidate=base[stage];
            for(uint8_t& byte:candidate)byte^=static_cast<uint8_t>(offset);
            ++checks[stage];
            if(accepted(candidate,target)) {
                ++hits[stage];std::printf("ORIGINAL_HIT stage=%d offset=%d bits=",stage,offset);
                for(int x:permutation)std::printf("%d",x);
                std::printf(" component=");
                for(uint8_t x:candidate)std::printf("%02X",x);
                std::puts("");
            }
            if(stage==0 && accepted(candidate,positiveTarget)) {
                if(permutation!=positiveMap||offset!=0x37)return 8;
                ++positiveHits;
            }
        }
    } while(std::next_permutation(permutation.begin(),permutation.end()));
    double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    for(int i=0;i<3;i++)std::printf("stage%d_checks=%llu original_hits=%llu\n",i,
        static_cast<unsigned long long>(checks[i]),static_cast<unsigned long long>(hits[i]));
    std::printf("planted_positive=%llu elapsed_seconds=%.3f\n",
        static_cast<unsigned long long>(positiveHits),seconds);
    if(positiveHits!=1)return 9;
    for(int i=0;i<3;i++)if(checks[i]!=10321920)return 10;
    return 0;
}
