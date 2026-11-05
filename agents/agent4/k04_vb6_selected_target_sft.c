/* Selected-only VB6 Rnd 24-bit output model for H-17 historical recovery.
 * SHA256(16-byte coupon XOR original mask) checked against original K04 hash.
 * This is a speculative exceptional producer model, not an equipment operation.
 * Compile: cc -O3 -std=c11 FILE -lcrypto -o test
 * Invoke: test START END [planted], with 0 <= START <= END <= 16777216.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/sha.h>
#define N 16777216u
#define A 1140671485u
#define C 12820163u
static const uint8_t masked[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint8_t target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static uint8_t comparison_target[32];
static uint32_t advance(uint32_t x){return (x*A+C)&(N-1);}
static void check(uint8_t *raw,uint32_t state,unsigned variant,unsigned *hits){
    uint8_t coupon[16],hash[32];
    for(unsigned orient=0;orient<2;orient++){
        for(unsigned i=0;i<16;i++)coupon[i]=raw[orient?15-i:i]^masked[i];
        SHA256(coupon,16,hash);
        if(!memcmp(hash,comparison_target,32)){
            printf("TARGET HIT firststate=%u variant=%u byteorder=%u K04=",state,variant,orient);
            for(unsigned i=0;i<16;i++)printf("%02X",coupon[i]);
            putchar('\n');(*hits)++;
        }
    }
}
static void make_byte(uint32_t x,unsigned lane,uint8_t *raw){
    for(unsigned i=0;i<16;i++){raw[i]=(uint8_t)(x>>(8*lane));x=advance(x);}
}
static void make_pack(uint32_t x,unsigned endian,unsigned phase,uint8_t *raw){
    uint8_t ext[18];
    for(unsigned j=0;j<6;j++){
        for(unsigned k=0;k<3;k++)ext[j*3+k]=(uint8_t)(x>>(8*(endian?k:2-k)));
        x=advance(x);
    }
    memcpy(raw,ext+phase,16);
}
int main(int argc,char**argv){
    if(argc!=3&&argc!=4){fputs("Require shard start/end and optional planted flag\n",stderr);return 2;}
    uint32_t start=(uint32_t)strtoul(argv[1],NULL,10),end=(uint32_t)strtoul(argv[2],NULL,10);
    if(start>end||end>N)return 2;
    unsigned hits=0;uint8_t raw[16],coupon[16],digest[32];
    memcpy(comparison_target,target,32);
    if(argc==4&&!strcmp(argv[3],"planted")){
        make_pack(0x123456,1,2,raw);
        for(unsigned i=0;i<16;i++)coupon[i]=raw[15-i]^masked[i];
        SHA256(coupon,16,comparison_target);
    }
    make_byte(123456,2,raw);
    for(unsigned i=0;i<16;i++)coupon[i]=raw[i]^masked[i];
    SHA256(coupon,16,digest);
    if(digest[0]==0&&digest[1]==0)return 3;
    for(uint32_t state=start;state<end;state++){
        for(unsigned lane=0;lane<3;lane++){make_byte(state,lane,raw);check(raw,state,lane,&hits);}
        for(unsigned endian=0;endian<2;endian++)
            for(unsigned phase=0;phase<3;phase++){
                make_pack(state,endian,phase,raw);
                check(raw,state,3+endian*3+phase,&hits);
            }
    }
    printf("SHARD start=%u end=%u states=%u candidateChecks=%llu originalMatches=%u\n",
           start,end,end-start,(unsigned long long)(end-start)*18,hits);
    return 0;
}
