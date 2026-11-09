// Historical H-17 full 8+8 fragment assembly against original REC8 commitments.
// Build C++17 with -O3 -fopenmp -lcrypto; run after k04_k08_raw8_mosaic_prepare.py.
// Reads only generated fragment input. Neither acceptance nor archive is modified.
#define OPENSSL_API_COMPAT 0x10100000L
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
#include <omp.h>
#include <openssl/sha.h>

static const uint32_t target04[8] = {
    0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
    0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0
};
static const uint32_t target08[8] = {
    0x285eb6b4,0x196d21ea,0xf47e2514,0x49e61e0b,
    0xce287498,0x81ccc5a0,0x65ca733b,0x0c3fd747
};
static const unsigned char mask[16] = {
    0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
    0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c
};
static bool match(const SHA256_CTX &ctx, const uint32_t *target) {
    if (ctx.h[0] != target[0]) return false;
    for (int i=1; i<8; ++i) if (ctx.h[i] != target[i]) return false;
    return true;
}
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    std::ifstream f(argv[1], std::ios::binary);
    if (!f) return 2;
    std::vector<char> raw(
        (std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    if (raw.size() % 8 != 0) return 2;
    const size_t n = raw.size()/8;
    if (n <= 42) return 2;
    SHA256_CTX initial;
    SHA256_Init(&initial);
    unsigned char packet[16], digest[32], block[64]{};
    block[16]=0x80; block[63]=0x80;
    for (int k=0; k<10; ++k) {
        for (int z=0; z<16; ++z) packet[z]=(unsigned char)(k*17+z*13);
        memcpy(block,packet,16);
        SHA256(packet,16,digest);
        SHA256_CTX ctx=initial;
        SHA256_Transform(&ctx,block);
        for (int w=0; w<8; ++w) {
            unsigned v=((unsigned)digest[w*4]<<24)
                |((unsigned)digest[w*4+1]<<16)
                |((unsigned)digest[w*4+2]<<8)
                |digest[w*4+3];
            if (ctx.h[w]!=v) {
                puts("HASH_DIAGNOSTIC_FAILED");
                return 3;
            }
        }
    }
    memcpy(packet,raw.data()+7*8,8);
    memcpy(packet+8,raw.data()+42*8,8);
    SHA256(packet,16,digest);
    uint32_t planted[8];
    for (int w=0; w<8; ++w) {
        planted[w]=((unsigned)digest[w*4]<<24)
            |((unsigned)digest[w*4+1]<<16)
            |((unsigned)digest[w*4+2]<<8)
            |digest[w*4+3];
    }
    uint64_t hits04=0,hits08=0,hitsplant=0;
    std::atomic<size_t> progress{0};
    double start=omp_get_wtime();
    #pragma omp parallel reduction(+:hits04,hits08,hitsplant)
    {
        unsigned char b8[64]{},b4[64]{};
        b8[16]=b4[16]=0x80;
        b8[63]=b4[63]=0x80;
        SHA256_CTX ctx;
        #pragma omp for schedule(dynamic,32)
        for (size_t i=0; i<n; ++i) {
            const unsigned char *a=(const unsigned char*)(raw.data()+i*8);
            memcpy(b8,a,8);
            for (int x=0; x<8; ++x) b4[x]=a[x]^mask[x];
            for (size_t j=0; j<n; ++j) {
                const unsigned char *b=(const unsigned char*)(raw.data()+j*8);
                memcpy(b8+8,b,8);
                ctx=initial;
                SHA256_Transform(&ctx,b8);
                if (match(ctx,target08)) {
                    ++hits08;
                    #pragma omp critical
                    {printf("ORIGINAL_K08_HIT i=%zu j=%zu\n",i,j);fflush(stdout);}
                }
                if (match(ctx,planted)) ++hitsplant;
                for (int x=0; x<8; ++x) b4[8+x]=b[x]^mask[8+x];
                ctx=initial;
                SHA256_Transform(&ctx,b4);
                if (match(ctx,target04)) {
                    ++hits04;
                    #pragma omp critical
                    {printf("ORIGINAL_K04_HIT i=%zu j=%zu\n",i,j);fflush(stdout);}
                }
            }
            size_t v=++progress;
            if (v%2048==0) {
                #pragma omp critical
                {printf("PROGRESS %zu/%zu elapsed=%.2f\n",v,n,omp_get_wtime()-start);fflush(stdout);}
            }
        }
    }
    printf("COMPLETE fragments=%zu pairs=%llu k04_hits=%llu k08_hits=%llu planted_hits=%llu elapsed=%.3f\n",
        n,(unsigned long long)n*n,(unsigned long long)hits04,
        (unsigned long long)hits08,(unsigned long long)hitsplant,omp_get_wtime()-start);
    return hitsplant==1?0:4;
}
