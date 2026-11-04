#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static const unsigned char copied[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char expected[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static const unsigned char source_pin[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static inline uint32_t rot(uint32_t x, unsigned r){r&=31; return r ? (x<<r)|(x>>(32-r)): x;}
static inline uint32_t xorshift(uint32_t x){x^=x<<13; x^=x>>17; x^=x<<5; return x;}

static inline uint32_t word(unsigned mode, uint32_t key, unsigned idx){
    switch(mode){
      case 0: return rot(key, idx*8); /* rotating byte-lane mask */
      case 1: return rot(key, idx*16); /* alternating halfword-lane mask */
      case 2: {uint32_t a=key; for(unsigned j=0;j<idx;j++)a=xorshift(a); return a;}
      case 3: return key+idx; /* 32-bit counter-XOR word mask */
      default:return key-idx;
    }
}
static inline void coupon(unsigned char out[16], unsigned mode, uint32_t key, int reverse){
    for(unsigned i=0;i<4;i++){
        uint32_t w=word(mode,key,i);
        for(unsigned j=0;j<4;j++){
            unsigned s=reverse ? 24-8*j : 8*j;
            out[4*i+j]=copied[4*i+j]^mask[4*i+j]^((w>>s)&255);
        }
    }
}
static inline void sha_compress16(const unsigned char in[16],SHA256_CTX *ctx){
    static const uint32_t iv[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    unsigned char block[64]={0};memcpy(block,in,16);block[16]=0x80;block[63]=128;
    memcpy(ctx->h,iv,sizeof(iv));SHA256_Transform(ctx,block);
}
static inline int sha_equal(const SHA256_CTX *ctx,const unsigned char target[32]){
    for(unsigned i=0;i<8;i++){
       uint32_t z=ctx->h[i];
       if((unsigned char)(z>>24)!=target[4*i]||(unsigned char)(z>>16)!=target[4*i+1]||
          (unsigned char)(z>>8)!=target[4*i+2]||(unsigned char)z!=target[4*i+3])return 0;
    }
    return 1;
}
static int source_assert(const char *path){
    FILE *f=fopen(path,"rb"); if(!f){perror(path);return 0;}
    unsigned char buf[8192],sha[32];SHA256_CTX c;SHA256_Init(&c);
    size_t n,sz=0;char data[30000];
    while((n=fread(buf,1,sizeof(buf),f))){SHA256_Update(&c,buf,n);if(sz+n>=sizeof(data)){fclose(f);return 0;}memcpy(data+sz,buf,n);sz+=n;}
    fclose(f);SHA256_Final(sha,&c);data[sz]=0;
    const char *line=strstr(data,"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER");
    if(!line||!strstr(line,"PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5"))return 0;
    return memcmp(sha,source_pin,32)==0;
}
int main(int argc,char**argv){
    if(argc!=4){fprintf(stderr,"usage: %s printer-log start-32bit range-count\n",argv[0]);return 2;}
    if(!source_assert(argv[1])){fprintf(stderr,"Original source pin/selector failure\n");return 3;}
    uint64_t start=strtoull(argv[2],0,0),count=strtoull(argv[3],0,0);
    if(start>UINT32_MAX||count==0||count>UINT64_C(4294967296)-start)return 2;
    const uint32_t plant=0xA13F70C5;
    unsigned long long observed=0,positives=0;unsigned char known[16],target[32];SHA256_CTX test;
    SHA256_Init(&test);
    for(unsigned m=0;m<5;m++)for(int rv=0;rv<2;rv++){
      coupon(known,m,plant,rv);SHA256(known,16,target);
      sha_compress16(known,&test);if(!sha_equal(&test,target)){fprintf(stderr,"planted fast SHA mismatch mode %u view %d\n",m,rv);return 4;}
      for(unsigned i=0;i<64;i++){
        uint32_t k=(uint32_t)(i*0x1234567u+m*0x100211u+rv);
        coupon(known,m,k,rv);SHA256(known,16,target);
        sha_compress16(known,&test);if(!sha_equal(&test,target)){fprintf(stderr,"fast SHA mismatch random\n");return 5;}
      }
    }
    uint32_t found_seed=0;unsigned found_mode=0,found_view=0;
    #pragma omp parallel reduction(+:observed,positives)
    {
      SHA256_CTX ctx;SHA256_Init(&ctx);unsigned char comp[16],tmp[16],plant_digest[5][2][32];
      for(unsigned m=0;m<5;m++)for(int rv=0;rv<2;rv++){
        coupon(tmp,m,plant,rv);SHA256(tmp,16,plant_digest[m][rv]);
      }
      #pragma omp for schedule(static)
      for(uint64_t off=0;off<count;off++){
        uint32_t k=(uint32_t)(start+off);
        for(unsigned m=0;m<5;m++)for(int rv=0;rv<2;rv++){
          coupon(comp,m,k,rv);
          sha_compress16(comp,&ctx);
          int authentic=sha_equal(&ctx,expected);
          observed += authentic;
          if(sha_equal(&ctx,plant_digest[m][rv]))positives++;
          if(authentic){
            #pragma omp critical
            {found_seed=k;found_mode=m;found_view=rv;}
          }
        }
      }
    }
    unsigned long long expected_positives=(plant>=start&&plant<start+count)?10:0;
    printf("SHARD_COMPLETE start=%" PRIu64 " count=%" PRIu64 " modes=10 checks=%" PRIu64 " original_hits=%llu planted_hits=%llu expected_plants=%llu\n",start,count,count*10ULL,observed,positives,expected_positives);
    if(observed){printf("MATCH seed=%08X mode=%u endian=%u\n",found_seed,found_mode,found_view);return 10;}
    if(positives!=expected_positives)return 6;
    return 0;
}
