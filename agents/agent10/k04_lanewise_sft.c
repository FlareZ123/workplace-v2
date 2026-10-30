/* K04 four-word independent same-byte-lane corruption pilot.
 * Replaces byte offsets j, j+4, j+8, j+12 for j=0..3.
 * Original ESC-N ACK2 / 16-byte route mask, fixed SHA256.
 * This hypothesized source format is not historically authenticated.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include <openssl/sha.h>

static const unsigned char original[16] = {0x2C,0xFF,0x14,0x9C,0x50,0xE5,0x45,0x57,0x22,0x8E,0x7D,0xE6,0x0B,0x3E,0xB7,0xC9};
static const unsigned char expected[32] = {0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static const unsigned char baseline_hash[32] = {0x11,0xA7,0xF6,0x06,0x47,0x81,0xA6,0xAC,0x76,0x78,0xDC,0x6D,0xD2,0x47,0x59,0xAF,0x95,0x98,0x1C,0x8A,0x92,0x7F,0x8D,0xA4,0x43,0x65,0x15,0x35,0x4D,0x34,0x54,0x9B};
static uint32_t target[8];
static void format_target(const unsigned char digest[32], uint32_t out[8]) {
    for (int i=0;i<8;i++) out[i]=((uint32_t)digest[4*i]<<24)|((uint32_t)digest[4*i+1]<<16)|((uint32_t)digest[4*i+2]<<8)|digest[4*i+3];
}
static int scan(unsigned lane, unsigned lo, unsigned hi, const unsigned char digest[32], int synthetic) {
    format_target(digest,target);
    uint64_t total=0;
    int found_count=0;
    double start=omp_get_wtime();
    #pragma omp parallel reduction(+:total,found_count)
    {
        SHA256_CTX init;
        SHA256_Init(&init);
        unsigned char block[64]={0};
        memcpy(block,original,16);
        block[16]=0x80;
        block[63]=0x80; /* 16 bytes = 128 message bits */
        #pragma omp for schedule(dynamic,16)
        for(unsigned high=lo; high<hi; high++) {
            block[lane]=(unsigned char)(high>>8);
            block[lane+4]=(unsigned char)high;
            for (unsigned low=0; low<65536; low++) {
                block[lane+8]=(unsigned char)(low>>8);
                block[lane+12]=(unsigned char)low;
                SHA256_CTX ctx=init;
                SHA256_Transform(&ctx,block);
                total++;
                if(ctx.h[0] == target[0] && ctx.h[1] == target[1]
                   && ctx.h[2] == target[2] && ctx.h[3] == target[3]
                   && ctx.h[4] == target[4] && ctx.h[5] == target[5]
                   && ctx.h[6] == target[6] && ctx.h[7] == target[7]) {
                    #pragma omp critical
                    {
                        printf("FOUND synthetic=%d high=%u low=%u candidate=",synthetic,high,low);
                        for(int i=0;i<16;i++) printf("%02X",block[i]);
                        putchar('\n'); fflush(stdout);
                    }
                    found_count++;
                }
            }
        }
    }
    printf("COMPLETE %s lane=%u high=[%u,%u) tested=%llu found=%d sec=%.3f\n",synthetic?"SYNTHETIC":"ORIGINAL",lane,lo,hi,(unsigned long long)total,found_count,omp_get_wtime()-start);
    fflush(stdout);
    return found_count;
}
int main(int argc,char **argv) {
    if(argc!=4) {fprintf(stderr,"usage: %s lane high16_lo high16_hi\n",argv[0]);return 2;}
    unsigned lane=(unsigned)strtoul(argv[1],NULL,10);
    unsigned lo=(unsigned)strtoul(argv[2],NULL,10);
    unsigned hi=(unsigned)strtoul(argv[3],NULL,10);
    if(lane>3 || lo>=hi || hi>65536) return 2;
    unsigned char check[32]; SHA256(original,16,check);
    if(memcmp(check,baseline_hash,32)) {fputs("ERROR baseline input hash mismatch\n",stderr);return 3;}
    unsigned char altered[16]; memcpy(altered,original,16);
    altered[lane]=0xAB; altered[lane+4]=0xCD; altered[lane+8]=0x12; altered[lane+12]=0x34;
    SHA256(altered,16,check);
    if(scan(lane,0xABCD,0xABCE,check,1)!=1) {fputs("ERROR synthetic positive failed\n",stderr);return 4;}
    if(scan(lane,lo,hi,expected,0)>0) return 0;
    return 1; /* no match, expected for a negative search */
}
