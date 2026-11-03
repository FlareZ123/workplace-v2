/* Explore two damaged 8-byte segment headers: bytes {0,1,8,9}. Original archive read-only.
 * Full 2^32 replacement assignment per source-inferred 8-byte half-boundary, XOR mask fixed.
 * Earlier 4-contiguous-byte and two-ended 4-byte tests do not cover this geometry.
 * Hypothetical artifact corruption, not an authenticated device failure mechanism.
 */
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdatomic.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static const unsigned char baseline[16]={0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static const unsigned char original_target[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static void prepare(unsigned char block[64]){memset(block,0,64);memcpy(block,baseline,16);block[16]=0x80;block[63]=0x80;}
static void hash_block(const unsigned char block[64],unsigned char digest[32]){
  SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,block);
  for(int i=0;i<8;i++){
    uint32_t word=(uint32_t)ctx.h[i];
    digest[4*i]=(unsigned char)(word>>24);digest[4*i+1]=(unsigned char)(word>>16);
    digest[4*i+2]=(unsigned char)(word>>8);digest[4*i+3]=(unsigned char)word;
  }
}
static void target_for(uint16_t a,uint16_t b,unsigned char out[32]){
  unsigned char block[64];prepare(block);
  block[0]=(unsigned char)(a>>8);block[1]=(unsigned char)a;
  block[8]=(unsigned char)(b>>8);block[9]=(unsigned char)b;
  hash_block(block,out);
}
static int run(uint32_t begin,uint32_t end,const unsigned char target[32],int report){
   atomic_int found=0;
   uint16_t founda=0,foundb=0;
   #pragma omp parallel for schedule(dynamic,256)
   for(uint64_t a=begin;a<end;a++){
       unsigned char block[64],digest[32];prepare(block);
       block[0]=(unsigned char)(a>>8);block[1]=(unsigned char)a;
       for(uint32_t b=0;b<65536&&!atomic_load_explicit(&found,memory_order_relaxed);b++){
           block[8]=(unsigned char)(b>>8);block[9]=(unsigned char)b;
           hash_block(block,digest);
           if(!memcmp(target,digest,32)){
             #pragma omp critical
             {founda=(uint16_t)a;foundb=(uint16_t)b;atomic_store_explicit(&found,1,memory_order_relaxed);}
             break;
           }
       }
   }
   if(report)printf("SCAN [%u,%u) pairs=%llu result=%s",begin,end,
      (unsigned long long)((uint64_t)(end-begin)*65536ULL),found?"HIT":"NO_MATCH");
   if(found&&report)printf(" a=%04X b=%04X",founda,foundb);
   if(report)printf("\n");
   return found;
}
int main(int argc,char **argv){
   unsigned char known[32], digest[32],block[64];
   prepare(block);hash_block(block,digest);
   SHA256(baseline,16,known);
   if(memcmp(known,digest,32)){fputs("SHA256 single-block equivalence failed\n",stderr);return 2;}
   target_for(0xBEEF,0xC0DE,known);
   if(!run(0xBEEF,0xBEF0,known,1)){fputs("Synthetic control failed\n",stderr);return 3;}
   uint32_t begin=0,end=65536;
   if(argc>1)begin=(uint32_t)strtoul(argv[1],0,0);
   if(argc>2)end=(uint32_t)strtoul(argv[2],0,0);
   if(end>65536||begin>=end){fputs("Range must be 0 <= begin < end <= 65536\n",stderr);return 4;}
   int found=run(begin,end,original_target,1);
   return found?0:1;
}
