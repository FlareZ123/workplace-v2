/* H17 K04 original-source pinned 32-bit repeating wordpad copier model.
 * The four serialized 32-bit coupon words share one hypothetical XOR error pad.
 * This is not an attested printer fault; selected source and commitments are read-only.
 * cc -O3 -std=c11 -Wno-deprecated-declarations -lcrypto -o k04pad agents/agent42/k04_repeated_32bit_buspad_sft.c
 * k04pad RESOURCES SHARD SHARDS (SHARDS a power of 2).
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const unsigned char PAPER[16] = {0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,
                                        0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const unsigned char MASK[16] = {0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
                                       0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint32_t TARGET[8] = {0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
                                   0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const char *PATHS[3] = {"evidence/print/spool-reconstruction.log",
 "evidence/recovery-routing.json", "acceptance.json"};
static const char *PINS[3] = {
 "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
 "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
 "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"};
static void hexprint(const unsigned char *p, int n) {
 for (int i=0;i<n;i++) printf("%02X",p[i]);
}
static int verify(const char *root) {
 for (int i=0;i<3;i++) {
  char path[4096],actual[65]; unsigned char buf[32768],digest[32]; size_t n;
  snprintf(path,sizeof(path),"%s/%s",root,PATHS[i]);
  FILE *f=fopen(path,"rb"); if(!f) {perror(path);return 0;}
  SHA256_CTX c;SHA256_Init(&c);
  while ((n=fread(buf,1,sizeof(buf),f))!=0) SHA256_Update(&c,buf,n);
  int failed=ferror(f);fclose(f);if(failed)return 0;
  SHA256_Final(digest,&c);
  for (int j=0;j<32;j++) snprintf(actual+2*j,3,"%02x",digest[j]);
  if(strcmp(actual,PINS[i])) {fprintf(stderr,"Original SHA mismatch %s\n",path);return 0;}
 }
 return 1;
}
static void candidate(unsigned char out[16], uint32_t pad) {
 for (int i=0;i<16;i++) out[i] = PAPER[i] ^ MASK[i] ^ (unsigned char)(pad >> (8*(i%4)));
}
static void expected_wordhash(const unsigned char out[16], uint32_t words[8]) {
 unsigned char digest[32];SHA256(out,16,digest);
 for (int j=0;j<8;j++)words[j]=((uint32_t)digest[4*j]<<24)
   |((uint32_t)digest[4*j+1]<<16)|((uint32_t)digest[4*j+2]<<8)|digest[4*j+3];
}
static int equal(const uint32_t a[8],const uint32_t b[8]) {
 return a[0]==b[0] && memcmp(a,b,8*sizeof(uint32_t))==0;
}
int main(int argc,char **argv) {
 if(argc!=4) {fprintf(stderr,"Usage: program RESOURCES SHARD SHARDS\n");return 2;}
 if(!verify(argv[1]))return 3;
 char *end; unsigned long shard=strtoul(argv[2],&end,10);if(*end)return 2;
 unsigned long shards=strtoul(argv[3],&end,10);if(*end||shards<1||shards>128||(shards&(shards-1))||shard>=shards)return 2;
 const uint64_t total=UINT64_C(1)<<32;
 const uint64_t count=total/shards, begin=shard*count, finish=begin+count;
 const uint32_t plant=0xA17F35E4;
 unsigned char payload[16],block[64]={0};uint32_t planted[8],baseline[8];
 candidate(payload,plant);expected_wordhash(payload,planted);
 candidate(payload,0);expected_wordhash(payload,baseline);
 SHA256_CTX base,test;SHA256_Init(&base);
 memcpy(block,payload,16);block[16]=0x80;block[63]=0x80;
 test=base;SHA256_Transform(&test,block);
 if(!equal(test.h,baseline)) {fprintf(stderr,"SHA256 block verification failed\n");return 3;}
 uint64_t controls=0,hits=0;
 for (uint64_t x=begin;x<finish;x++) {
  uint32_t v=(uint32_t)x;
  for (int j=0;j<16;j++)block[j]=PAPER[j]^MASK[j]^(unsigned char)(v>>(8*(j%4)));
  test=base;SHA256_Transform(&test,block);
  if(equal(test.h,TARGET)) {
   ++hits;printf("ORIGINAL K04 HIT buspad=%08X component=",v);
   hexprint(block,16);puts("");fflush(stdout);
  }
  if(equal(test.h,planted)) {
   ++controls;printf("PLANTED CONTROL buspad=%08X\n",v);fflush(stdout);
  }
 }
 uint64_t expected=(begin<=plant&&plant<finish)?1:0;
 printf("SHARD %lu/%lu RANGE %llu..%llu checked=%llu original_hits=%llu planted=%llu expected=%llu\n",
  shard,shards,(unsigned long long)begin,(unsigned long long)finish,
  (unsigned long long)count,(unsigned long long)hits,(unsigned long long)controls,(unsigned long long)expected);
 return controls!=expected?4:(hits?10:0);
}
