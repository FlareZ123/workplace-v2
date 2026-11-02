/*
 * Original H-17 K04: four independent unknown byte values in one fixed
 * byte lane across four serialized 32-bit printer words. A genuinely
 * distinct source-cued hypothesis from contiguous four-byte faults and
 * periodic word XOR. Source selected ACK2: A9A9DC5731A5E2AE879C47215C2559D5.
 * Original ESC-N mask: 8556C8CB6140A7F9A5123AC7571BEE1C.
 * Baseline derived key: 2CFF149C50E54557228E7DE60B3EB7C9.
 * Original K04 SHA256 commitment: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.
 * Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
 * This is a source-specific finite error model, not an authentic fault diagnosis.
 * Build: C compiler with libcrypto and OpenMP. Positive controls execute
 * before every original-range scan. Fully cover lanes 0,1,2,3 with
 * arguments <lane> 0 4294967296, one invocation per lane.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
static const unsigned char original[16] = {
    0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,
    0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9
};
static const uint32_t real_target[8] = {
    0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
    0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0
};
static int digest_equal(const uint32_t a[8], const uint32_t b[8]) {
    for (int i=0; i<8; ++i) if (a[i]!=b[i]) return 0;
    return 1;
}
static void one_block(const SHA256_CTX *base,
                      const unsigned char block[64], uint32_t out[8]) {
    SHA256_CTX ctx=*base;
    SHA256_Transform(&ctx,block);
    memcpy(out,ctx.h,32);
}
int main(int argc,char **argv) {
    if (argc!=4 && argc!=5) {
        fprintf(stderr,"Usage: program lane[0..3] low32 high32 [synthetic]\n");
        return 2;
    }
    int lane=atoi(argv[1]);
    uint64_t from=strtoull(argv[2],NULL,10);
    uint64_t to=strtoull(argv[3],NULL,10);
    if (lane<0 || lane>3 || to>UINT64_C(4294967296) || from>=to) {
        fprintf(stderr,"Invalid lane or half-open range\n");
        return 2;
    }
    SHA256_CTX base;
    SHA256_Init(&base);
    unsigned char block[64]={0};
    memcpy(block,original,16);
    block[16]=0x80;
    block[63]=0x80; /* 16-byte message is 128 bits long */
    uint32_t check[8];
    one_block(&base,block,check);
    static const uint32_t baseline_sha[8] = {
        0x11a7f606,0x4781a6ac,0x7678dc6d,0xd24759af,
        0x95981c8a,0x927f8da4,0x43651535,0x4d34549b
    };
    if (!digest_equal(check,baseline_sha)) {
        fprintf(stderr,"Original source baseline SHA positive failed\n");
        return 3;
    }
    block[lane]=0x12;
    block[lane+4]=0x34;
    block[lane+8]=0x56;
    block[lane+12]=0x78;
    one_block(&base,block,check);
    unsigned char standard[32];
    SHA256(block,16,standard);
    for (int i=0;i<8;i++) {
        uint32_t x=((uint32_t)standard[i*4]<<24)
                  |((uint32_t)standard[i*4+1]<<16)
                  |((uint32_t)standard[i*4+2]<<8)
                  |(uint32_t)standard[i*4+3];
        if (check[i]!=x) {
            fprintf(stderr,"Synthetic SHA256 transform positive failed\n");
            return 4;
        }
    }
    const uint32_t *goal=(argc==5 && strcmp(argv[4],"synthetic")==0)
                         ?check:real_target;
    int matches=0;
    double start=omp_get_wtime();
    #pragma omp parallel reduction(+:matches)
    {
        unsigned char msg[64]={0};
        memcpy(msg,original,16);
        msg[16]=0x80;
        msg[63]=0x80;
        SHA256_CTX ctx;
        #pragma omp for schedule(static)
        for (uint64_t x=from; x<to; ++x) {
            msg[lane]=(unsigned char)(x>>24);
            msg[lane+4]=(unsigned char)(x>>16);
            msg[lane+8]=(unsigned char)(x>>8);
            msg[lane+12]=(unsigned char)x;
            ctx=base;
            SHA256_Transform(&ctx,msg);
            if (ctx.h[0]==goal[0] && digest_equal(ctx.h,goal)) {
                ++matches;
                #pragma omp critical
                {
                    printf("FOUND K04 ");
                    for (int i=0;i<16;i++) printf("%02X",msg[i]);
                    printf(" lane %d assignment %08X\n",lane,(unsigned)x);
                }
            }
        }
    }
    printf("LANE %d RANGE [%llu,%llu) count %llu matches %d seconds %.3f\n",
        lane,(unsigned long long)from,(unsigned long long)to,
        (unsigned long long)(to-from),matches,omp_get_wtime()-start);
    if (goal==check && matches!=1) return 5;
    return 0;
}
