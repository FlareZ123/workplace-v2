// H-17 K04: exhaustive four full-16byte coupons with 32 unknown bits each.
// The four fixed component templates are derived independently and source-pinned
// in k04_mt_threeword_free32_sft.py. This worker only hashes full 16-byte
// candidates against the unchanged official K04 target SHA256.
//
// Build with C++17, OpenSSL libcrypto and OpenMP.
#define OPENSSL_API_COMPAT 0x10100000L
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <omp.h>
#include <openssl/sha.h>

struct Template {
    const char* description;
    int free_word;
    std::array<unsigned char, 16> fixed;
};
static const Template samples[]={
    {"r45_k98_q0_i0",3,{0x9B,0x12,0x22,0xB4,0x32,0xAD,0x70,0x51,0x2F,0x49,0x79,0x95,0,0,0,0}},
    {"r45_k98_q0_i1",3,{0x9E,0x34,0x99,0xEA,0xD0,0x38,0xB4,0x88,0xFA,0x2D,0x93,0xC9,0,0,0,0}},
    {"r45_k98_q1_i0",0,{0,0,0,0,0x7F,0x04,0x4D,0x86,0xF6,0xFF,0xED,0x6F,0xDD,0x40,0xAD,0x4E}},
    {"r45_k98_q1_i1",0,{0,0,0,0,0x7A,0x22,0xF6,0xD8,0x14,0x6A,0x29,0xB6,0x08,0x24,0x47,0x12}},
};
static const uint32_t TARGET[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const unsigned char ROUTE_MASK[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint32_t PLANT=0x17C0FFEE;

void encode(unsigned char* p, uint32_t x) {
    p[0]=static_cast<unsigned char>(x);
    p[1]=static_cast<unsigned char>(x>>8);
    p[2]=static_cast<unsigned char>(x>>16);
    p[3]=static_cast<unsigned char>(x>>24);
}
void print_hex(const unsigned char* p,size_t n){for(size_t i=0;i<n;i++)std::printf("%02X",p[i]);}
bool match(const SHA256_CTX& c,const uint32_t* digest){
    if(c.h[0]!=digest[0])return false;
    for(int i=1;i<8;i++)if(c.h[i]!=digest[i])return false;
    return true;
}
int main(int argc,char** argv){
    int only=-1;
    if(argc==2) only=std::atoi(argv[1]);
    if(only>=static_cast<int>(std::size(samples))) return 2;
    SHA256_CTX initial;
    SHA256_Init(&initial);
    unsigned long long total=0,realhits=0;
    for(int si=0;si<static_cast<int>(std::size(samples));si++){
        if(only>=0 && si!=only)continue;
        const Template& s=samples[si];
        unsigned char plantbuf[16];std::memcpy(plantbuf,s.fixed.data(),16);
        encode(plantbuf+4*s.free_word,PLANT);
        unsigned char plant_hash[32];SHA256(plantbuf,16,plant_hash);
        uint32_t plant_target[8];
        for(int k=0;k<8;k++)plant_target[k]=(uint32_t(plant_hash[4*k])<<24)|(uint32_t(plant_hash[4*k+1])<<16)|(uint32_t(plant_hash[4*k+2])<<8)|uint32_t(plant_hash[4*k+3]);
        unsigned long long plant_hits=0,real_hits=0,checks=0;
        double started=omp_get_wtime();
        std::printf("START %d %s missing_word=%d search=4294967296 plant=%08X threads=%d\n",si,s.description,s.free_word,PLANT,omp_get_max_threads());
        std::fflush(stdout);
        #pragma omp parallel reduction(+:plant_hits,real_hits,checks)
        {
            unsigned char block[64]{};
            std::memcpy(block,s.fixed.data(),16);
            block[16]=0x80;block[63]=0x80;
            SHA256_CTX ctx{};
            #pragma omp for schedule(dynamic,1)
            for(int shard=0;shard<4096;shard++){
                uint64_t lo=uint64_t(shard)<<20;
                uint64_t hi=lo+(1ULL<<20);
                for(uint64_t val=lo;val<hi;val++){
                    encode(block+4*s.free_word,static_cast<uint32_t>(val));
                    ctx=initial;
                    SHA256_Transform(&ctx,block);
                    checks++;
                    if(match(ctx,TARGET)){
                        real_hits++;
                        #pragma omp critical
                        {
                            std::printf("ORIGINAL_K04_HIT template=%s component=",s.description);
                            print_hex(block,16);
                            std::printf(" coupon=");
                            for(int b=0;b<16;b++)std::printf("%02X",block[b]^ROUTE_MASK[b]);
                            std::puts("");std::fflush(stdout);
                        }
                    }
                    if(match(ctx,plant_target))plant_hits++;
                }
            }
        }
        double elapsed=omp_get_wtime()-started;
        std::printf("COMPLETE %d %s checks=%llu planted_hits=%llu original_hits=%llu elapsed=%.3f\n",si,s.description,checks,plant_hits,real_hits,elapsed);
        std::fflush(stdout);
        if(checks!=4294967296ULL||plant_hits!=1ULL)return 3;
        total+=checks;realhits+=real_hits;
    }
    std::printf("SUMMARY full_candidates=%llu original_hits=%llu\n",total,realhits);
    return 0;
}
