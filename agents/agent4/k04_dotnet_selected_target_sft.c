/* H17 historical selected-only classic .NET Random(int).NextBytes(16).
 * Enumerates every absolute 31-bit scalar seed with immutable K04 mask/SHA.
 * Selected-event producer is hypothetical. No facility equipment interaction.
 * gcc -O3 -std=c11 FILE -lcrypto -o test
 * test START END [planted], END exclusive; supports sharded manual CI.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#define M 2147483647u
static const uint8_t masked[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint8_t target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static uint8_t desired[32];
static inline int32_t sub32(int32_t a,int32_t b){return (int32_t)((uint32_t)a-(uint32_t)b);}
static void from_seed(uint32_t seed,uint8_t dst[16]){
    int32_t a[56]={0},mj=161803398-(int32_t)seed,mk=1;
    a[55]=mj;
    for(int i=1;i<55;i++){
        int j=(21*i)%55;
        a[j]=mk;
        mk=sub32(mj,mk);
        if(mk<0)mk+=(int32_t)M;
        mj=a[j];
    }
    for(int k=0;k<4;k++)for(int i=1;i<56;i++){
        a[i]=sub32(a[i],a[1+(i+30)%55]);
        if(a[i]<0)a[i]+=(int32_t)M;
    }
    int ii=0,jj=21;
    for(int n=0;n<16;n++){
        ii=ii%55+1;jj=jj%55+1;
        int32_t v=sub32(a[ii],a[jj]);
        if(v==(int32_t)M)v--;
        if(v<0)v+=(int32_t)M;
        a[ii]=v;dst[n]=(uint8_t)v;
    }
}
static void test_seed(uint32_t seed,uint64_t *hits){
    uint8_t raw[16],coupon[16],digest[32];
    from_seed(seed,raw);
    for(unsigned orient=0;orient<2;orient++){
        for(unsigned i=0;i<16;i++)coupon[i]=raw[orient?15-i:i]^masked[i];
        SHA256(coupon,16,digest);
        if(!memcmp(digest,desired,32)){
            printf("TARGET HIT seed_abs=%u reverse=%u K04=",seed,orient);
            for(unsigned i=0;i<16;i++)printf("%02X",coupon[i]);
            putchar('\n');(*hits)++;
        }
    }
}
int main(int argc,char **argv){
    if(argc<3||argc>4){fputs("Requires START END and optional planted flag\n",stderr);return 2;}
    uint64_t start=strtoull(argv[1],NULL,10),end=strtoull(argv[2],NULL,10);
    if(start>end||end>(uint64_t)M+1)return 2;
    const struct{uint32_t seed;const char *hex;} controls[]={
        {0,"1A0C466F5D75E4D8AD6765D5F519DBC8"},
        {42,"3E17BA96AE04CD3B99869E56F0ADBF3A"},
        {1234567,"30E663CA5F4121481F8FFBE9DB201F70"},
        {2000000000u,"DFFFF954B410D83E664EA56F4D630F48"},
        {2147483647u,"1A0C4C6F5D73E4D8AD5B65D5E719DBC8"}
    };
    uint8_t raw[16],coupon[16];
    for(unsigned j=0;j<5;j++){
        char hex[33];
        from_seed(controls[j].seed,raw);
        for(unsigned i=0;i<16;i++)sprintf(hex+i*2,"%02X",raw[i]);
        if(strcmp(hex,controls[j].hex)){
            fprintf(stderr,"Generator vector failed seed %u\n",controls[j].seed);
            return 1;
        }
    }
    memcpy(desired,target,32);
    if(argc==4&&!strcmp(argv[3],"planted")){
        from_seed(1234567,raw);
        for(unsigned i=0;i<16;i++)coupon[i]=raw[15-i]^masked[i];
        SHA256(coupon,16,desired);
    }
    uint64_t hits=0;
    for(uint64_t seed=start;seed<end;seed++)test_seed((uint32_t)seed,&hits);
    printf("SHARD start=%llu end=%llu states=%llu checks=%llu hits=%llu\n",
           (unsigned long long)start,(unsigned long long)end,
           (unsigned long long)(end-start),
           (unsigned long long)(end-start)*2,(unsigned long long)hits);
    return 0;
}
