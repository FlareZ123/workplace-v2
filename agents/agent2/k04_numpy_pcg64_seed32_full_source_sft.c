/*
 * H17 source-only NumPy PCG64 SeedSequence(uint32 seed) exhaustive test.
 * Reproduces NumPy 2.3.5 SeedSequence pool4 and PCG XSL-RR 128/64.
 * Requires GCC/Clang and OpenSSL libcrypto; execute from repository root.
 * Run eight nonoverlapping shards, [0,2^29),...,[7*2^29,2^32).
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

typedef unsigned __int128 u128;
#define MUL_A ((((u128)2549297995355413924ULL)<<64)|4865540595714422341ULL)
static uint32_t hashmix(uint32_t x, uint32_t *hc) {
    x ^= *hc;
    *hc *= UINT32_C(0x931e8875);
    x *= *hc;
    return x ^ (x >> 16);
}
static uint32_t mix(uint32_t x, uint32_t y) {
    uint32_t v = UINT32_C(0xca01f9dd)*x - UINT32_C(0x4973f715)*y;
    return v ^ (v >> 16);
}
static void seeded(uint32_t seed, u128 *state, u128 *inc) {
    uint32_t p[4], hc=UINT32_C(0x43b0d7e5), g[8];
    p[0]=hashmix(seed,&hc);
    for(int j=1;j<4;j++)p[j]=hashmix(0,&hc);
    for(int i=0;i<4;i++)for(int j=0;j<4;j++)
        if(i!=j)p[j]=mix(p[j],hashmix(p[i],&hc));
    hc=UINT32_C(0x8b51f9dd);
    for(int j=0;j<8;j++){
        uint32_t v=p[j%4]^hc;
        hc*=UINT32_C(0x58f38ded);
        v*=hc;
        g[j]=v^(v>>16);
    }
    uint64_t w[4];
    for(int j=0;j<4;j++)w[j]=(uint64_t)g[2*j]|((uint64_t)g[2*j+1]<<32);
    u128 initstate=((u128)w[0]<<64)|w[1];
    u128 initseq=((u128)w[2]<<64)|w[3];
    *inc=(initseq<<1)|1;
    *state=*inc;
    *state+=initstate;
    *state=*state*MUL_A+*inc;
}
static uint64_t draw(u128 *state, u128 inc) {
    *state=*state*MUL_A+inc;
    uint64_t h=(uint64_t)(*state>>64), l=(uint64_t)*state;
    unsigned r=(unsigned)(h>>58);
    uint64_t x=h^l;
    return (x>>r)|(x<<((-r)&63));
}
static uint64_t bytes64(const unsigned char *p, int big) {
    uint64_t result=0;
    for(int i=0;i<8;i++)result=(result<<8)|p[big?i:7-i];
    return result;
}
static int get_source(unsigned char original[16]) {
    const char *path="resources/evidence/print/spool-reconstruction.log";
    FILE *f=fopen(path,"rb");
    if(!f){perror(path);return 0;}
    if(fseek(f,0,SEEK_END)){fclose(f);return 0;}
    long n=ftell(f);
    if(n<=0){fclose(f);return 0;}
    rewind(f);
    unsigned char *b=malloc((size_t)n+1);
    if(!b){fclose(f);return 0;}
    size_t got=fread(b,1,(size_t)n,f);
    fclose(f);
    if(got!=(size_t)n){free(b);return 0;}
    b[n]=0;
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(b,(size_t)n,digest);
    static const unsigned char expected[SHA256_DIGEST_LENGTH]={
        0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,
        0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,
        0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,
        0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
    if(memcmp(digest,expected,sizeof(expected))){
        fprintf(stderr,"original source SHA mismatch\n");free(b);return 0;
    }
    char *start=strchr((char *)b,'\n');
    if(!start){free(b);return 0;}
    char *payload=strstr(start+1,"PAYLOAD=");
    if(!payload){free(b);return 0;}
    payload+=8;
    for(int j=0;j<16;j++){
        unsigned n;
        if(sscanf(payload+2*j,"%2x",&n)!=1){free(b);return 0;}
        original[j]=(unsigned char)n;
    }
    static const unsigned char first[16]={0xfb,0xbb,0xc5,0x43,0x56,0x48,0x3f,0x58,
                                          0x64,0xbb,0x3f,0x06,0x79,0x45,0x18,0xa5};
    int good=memcmp(first,original,16)==0;
    free(b);return good;
}
int main(int argc,char **argv) {
    if(argc!=3){fprintf(stderr,"usage: test SEED_START SEED_COUNT\n");return 2;}
    uint64_t first=strtoull(argv[1],NULL,0),count=strtoull(argv[2],NULL,0);
    if(count==0 || first+count>UINT64_C(4294967296))return 2;
    unsigned char source[16];
    if(!get_source(source)){fprintf(stderr,"source validation failed\n");return 3;}
    u128 state,inc;
    seeded(42,&state,&inc);
    if(state!=((((u128)UINT64_C(0xcea44f6798798f2a))<<64)|UINT64_C(0xacbc7c9d68860ac8)) ||
       inc!=((((u128)UINT64_C(0xfa505436c9a8416e))<<64)|UINT64_C(0x66caf2e28d25abff)) ||
       draw(&state,inc)!=UINT64_C(0xc621fbcd16d92688) ||
       draw(&state,inc)!=UINT64_C(0x705a5661a791ffc1)){
        fprintf(stderr,"NumPy seed42 positive control failed\n");return 4;
    }
    uint64_t le0=bytes64(source,0),be0=bytes64(source,1);
    uint64_t le1=bytes64(source+8,0),be1=bytes64(source+8,1);
    uint64_t digest=0,hits=0,whole=0;
    for(uint64_t k=first;k<first+count;k++){
        seeded((uint32_t)k,&state,&inc);
        uint64_t x=draw(&state,inc);
        digest^=x;
        if(x==le0 || x==be0){
            hits++;
            uint64_t y=draw(&state,inc);
            if((x==le0 && y==le1)||(x==be0 && y==be1))whole++;
            fprintf(stderr,"first-word collision seed=%" PRIu64 " x=%016" PRIx64 " y=%016" PRIx64 "\n",k,x,y);
        }
    }
    printf("begin=%" PRIu64 " count=%" PRIu64 " half_hits=%" PRIu64 " whole_hits=%" PRIu64 " xor=%016" PRIx64 "\n",first,count,hits,whole,digest);
    return 0;
}
