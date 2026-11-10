/**
 * Full original H-17 K04 SHA256 acceptance search over original-source
 * affine MT19937 coupon spaces from k04_affine_source_sft.py.
 *
 * Reads 15 spaces on stdin, each carrying an already route-XORed component
 * base and independent 16-byte direction vectors. Every 2^rank candidate
 * is hashed using the exact one-block SHA256 compression.
 *
 * Optional arguments: number of OpenMP threads, maximum candidates per space.
 * Omit the maximum to run all 25,232,932,864 complete assignments.
 */
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>
#ifdef _OPENMP
#include <omp.h>
#endif

struct CouponSpace {
    int rank;
    int stage;
    std::array<unsigned char,16> base;
    std::vector<std::array<unsigned char,16>> deltas;
};

static std::array<unsigned char,16> parse_hex16(const std::string& text) {
    if(text.size()!=32) throw std::runtime_error("invalid 16-byte hex length");
    std::array<unsigned char,16> out{};
    for(int j=0;j<16;++j) {
        unsigned value=0;
        if(std::sscanf(text.substr(j*2,2).c_str(),"%2x",&value)!=1)
            throw std::runtime_error("bad hex");
        out[j]=static_cast<unsigned char>(value);
    }
    return out;
}

static std::vector<CouponSpace> read_spaces() {
    int n=0;
    if(!(std::cin>>n)||n!=15)
        throw std::runtime_error("expected all 15 original-source spaces");
    std::vector<CouponSpace> spaces;
    for(int i=0;i<n;++i) {
        CouponSpace s{};
        std::string hex;
        if(!(std::cin>>s.rank>>s.stage>>hex))
            throw std::runtime_error("missing source stage");
        if(s.rank!=29&&s.rank!=31&&s.rank!=32)
            throw std::runtime_error("invalid source rank");
        s.base=parse_hex16(hex);
        for(int j=0;j<s.rank;++j) {
            if(!(std::cin>>hex))
                throw std::runtime_error("truncated affine directions");
            s.deltas.push_back(parse_hex16(hex));
        }
        spaces.push_back(s);
    }
    if(std::cin>>n) throw std::runtime_error("trailing source data");
    return spaces;
}

static inline void xor16(unsigned char* a,const unsigned char* b) {
    for(int j=0;j<16;++j) a[j]^=b[j];
}

static std::array<unsigned char,32> original_digest() {
    constexpr char hex[]=
        "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
    std::array<unsigned char,32> out{};
    for(int j=0;j<32;++j) {
        unsigned value=0;
        if(std::sscanf(std::string(hex+j*2,2).c_str(),"%2x",&value)!=1)
            throw std::runtime_error("bad original K04 target");
        out[j]=static_cast<unsigned char>(value);
    }
    return out;
}

static uint64_t scan(const CouponSpace& space,
                     const std::array<unsigned char,32>& digest,
                     uint64_t limit,int threads,bool synthetic) {
    constexpr uint64_t CHUNK=1ULL<<21;
    const uint64_t parts=(limit+CHUNK-1)/CHUNK;
    const uint32_t iv[8]={
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19
    };
    uint32_t goal[8];
    for(int j=0;j<8;++j) {
        goal[j]=(uint32_t(digest[4*j])<<24)|(uint32_t(digest[4*j+1])<<16)
               |(uint32_t(digest[4*j+2])<<8)|digest[4*j+3];
    }
    uint64_t hits=0;
    #pragma omp parallel for num_threads(threads) schedule(dynamic,1) reduction(+:hits)
    for(uint64_t part=0;part<parts;++part) {
        uint64_t begin=part*CHUNK,end=std::min(begin+CHUNK,limit);
        unsigned char current[16];
        std::memcpy(current,space.base.data(),16);
        const uint64_t gray=begin^(begin>>1);
        for(int j=0;j<space.rank;++j)
            if((gray>>j)&1) xor16(current,space.deltas[j].data());
        SHA256_CTX ctx;
        unsigned char block[64]={};
        block[16]=0x80;
        block[63]=0x80; // correct bit length for a 16-byte input
        for(uint64_t idx=begin;idx<end;++idx) {
            if(idx!=begin) xor16(current,space.deltas[__builtin_ctzll(idx)].data());
            std::memcpy(block,current,16);
            std::memcpy(ctx.h,iv,sizeof(iv));
            SHA256_Transform(&ctx,block);
            if(ctx.h[0]==goal[0]&&std::memcmp(ctx.h,goal,sizeof(goal))==0) {
                #pragma omp critical
                {
                    std::printf("%s_MATCH stage=%d index=%llu K04=",
                        synthetic?"SYNTHETIC":"ORIGINAL",space.stage,
                        (unsigned long long)idx);
                    for(unsigned char x:current) std::printf("%02X",unsigned(x));
                    std::printf("\n");
                    std::fflush(stdout);
                }
                ++hits;
            }
        }
    }
    return hits;
}

int main(int argc,char** argv) {
    try {
        const int threads=(argc>1)?std::stoi(argv[1]):4;
        const uint64_t cap=(argc>2)?std::stoull(argv[2]):0;
        if(threads<1||threads>64) throw std::runtime_error("invalid thread count");
        const auto spaces=read_spaces();
        const auto digest=original_digest();
        uint64_t total=0,authentic_hits=0;
        for(const auto& space:spaces) {
            std::array<unsigned char,16> planted=space.base;
            const uint64_t i=1337,gray=i^(i>>1);
            for(int j=0;j<space.rank;++j)
                if((gray>>j)&1) xor16(planted.data(),space.deltas[j].data());
            std::array<unsigned char,32> synthetic{};
            SHA256(planted.data(),16,synthetic.data());
            if(scan(space,synthetic,65536,threads,true)!=1)
                throw std::runtime_error("full-coupon synthetic positive failed");
            const uint64_t limit=std::min(uint64_t(1)<<space.rank,
                cap?cap:(uint64_t(1)<<space.rank));
            auto start=std::chrono::steady_clock::now();
            const uint64_t hits=scan(space,digest,limit,threads,false);
            const double seconds=std::chrono::duration<double>(
                std::chrono::steady_clock::now()-start).count();
            std::printf(
                "ORIGINAL_COMPLETE stage=%d rank=%d checked=%llu hits=%llu time=%.3fs\n",
                space.stage,space.rank,(unsigned long long)limit,
                (unsigned long long)hits,seconds);
            std::fflush(stdout);
            total+=limit;
            authentic_hits+=hits;
        }
        std::printf("SUMMARY checked=%llu authentic_hits=%llu\n",
            (unsigned long long)total,(unsigned long long)authentic_hits);
        return authentic_hits?2:0;
    } catch(const std::exception& err) {
        std::cerr<<"ERROR "<<err.what()<<"\n";
        return 1;
    }
}
