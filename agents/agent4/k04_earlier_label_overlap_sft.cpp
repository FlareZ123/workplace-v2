/* H17 K04: earlier same-job LABEL ACK1 partial-source cache and one-native-word
   shift. Four-byte unknown is unrestricted; three preserved four-byte words
   come from genuinely earlier 16:45 LABEL1 record for the exact selected job.
   Physical/copy mechanism is hypothetical. Exact full K04 SHA256 only.
   Build: g++ -O3 -std=c++17 -fopenmp -Wno-deprecated-declarations
          k04_earlier_label_overlap_sft.cpp -lcrypto -o k04_label
   Usage: k04_label RESOURCES_ROOT SIDE_0_OR_1 SHARD_0_TO_15 [--smoke]
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t label1[16]={
  0xe1,0xe6,0x0d,0x5f,0x6b,0x6d,0xd2,0x22,
  0x5f,0xa6,0xd5,0xa2,0xa6,0x3a,0xd9,0x32};
static const uint8_t mask[16]={
  0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
  0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const unsigned target[8]={
  0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,
  0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U};
static const char *source_sha="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *label_row="2026-10-03T16:45:00+00:00 JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=E1E60D5F6B6DD2225FA6D5A2A63AD932 DEST=bench";
static const char *selected_row="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static void fail(const char *message){fprintf(stderr,"ERROR: %s\n",message);exit(2);}
static void check(const char *root,const char *rel,const char *needle,const char *digest){
  char filename[4096];
  if(snprintf(filename,sizeof(filename),"%s/%s",root,rel)>=(int)sizeof(filename))fail("path");
  FILE*f=fopen(filename,"rb");if(!f)fail("source file");
  if(fseek(f,0,SEEK_END)!=0)fail("seek");
  long n=ftell(f);if(n<0||n>1000000)fail("source size");
  rewind(f);
  char *buffer=(char*)malloc((size_t)n+1);if(!buffer)fail("allocation");
  if(fread(buffer,1,(size_t)n,f)!=(size_t)n)fail("read");
  fclose(f);buffer[n]=0;
  if(needle&&(!strstr(buffer,needle)||strstr(strstr(buffer,needle)+strlen(needle),needle)))
    fail("source literal absent or repeated");
  if(digest){
    uint8_t raw[32];char hex[65];SHA256((const uint8_t*)buffer,(size_t)n,raw);
    for(int j=0;j<32;j++)sprintf(hex+j*2,"%02x",raw[j]);
    if(strcmp(hex,digest))fail("source digest");
  }
  free(buffer);
}
static void prepare(uint8_t block[64],int side){
  memset(block,0,64);
  if(side==0){ // Three known first words of prior LABEL1 now follow new word.
    memcpy(block+4,label1,12);
  }else{ // Prior LABEL1 last three known words precede missing word.
    memcpy(block,label1+4,12);
  }
  for(int k=0;k<16;k++)block[k]^=mask[k];
  block[16]=0x80;block[63]=0x80; // Original message is 16 bytes.
}
static int digest_match(const SHA256_CTX &initial,const uint8_t block[64],
                       const unsigned digest[8]){
  SHA256_CTX x=initial;SHA256_Transform(&x,block);
  if(x.h[0]!=digest[0])return 0;
  for(int k=1;k<8;k++)if(x.h[k]!=digest[k])return 0;
  return 1;
}
static unsigned digest_word(const uint8_t d[32],int k){
  return ((unsigned)d[4*k]<<24)|((unsigned)d[4*k+1]<<16)|((unsigned)d[4*k+2]<<8)|d[4*k+3];
}
int main(int argc,char **argv){
  if(argc!=4&&argc!=5)fail("usage ROOT SIDE_0_OR_1 SHARD_0_TO_15 [--smoke]");
  char *end=nullptr;long side=strtol(argv[2],&end,10);
  if(*end||!*argv[2]||side<0||side>1)fail("side");
  long shard=strtol(argv[3],&end,10);
  if(*end||!*argv[3]||shard<0||shard>15)fail("shard");
  const int smoke=argc==5&&!strcmp(argv[4],"--smoke");
  if(argc==5&&!smoke)fail("mode");
  check(argv[1],"evidence/print/spool-reconstruction.log",label_row,source_sha);
  check(argv[1],"evidence/print/spool-reconstruction.log",selected_row,source_sha);
  check(argv[1],"evidence/recovery-routing.json","8556C8CB6140A7F9A5123AC7571BEE1C",nullptr);
  check(argv[1],"acceptance.json","930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",nullptr);
  SHA256_CTX initial;SHA256_Init(&initial);
  uint8_t block[64],d[32];prepare(block,(int)side);
  const int p=(side==0?0:12);
  const uint32_t planted_word=(uint32_t(shard)<<28)|0x01234567U;
  for(int k=0;k<4;k++)block[p+k]=(uint8_t)(planted_word>>(24-8*k))^mask[p+k];
  SHA256(block,16,d);
  unsigned planted[8];
  for(int k=0;k<8;k++)planted[k]=digest_word(d,k);
  if(!digest_match(initial,block,planted))fail("planted whole-component SHA mismatch");
  for(int k=0;k<1024;k++){
    prepare(block,(int)side);
    uint32_t value=uint32_t(k)*2654435761U+0x456789U;
    for(int j=0;j<4;j++)block[p+j]=uint8_t(value>>(24-8*j))^mask[p+j];
    SHA256(block,16,d);
    unsigned known[8];for(int j=0;j<8;j++)known[j]=digest_word(d,j);
    if(!digest_match(initial,block,known))fail("differential SHA256");
  }
  printf("SOURCE_SHA_AND_1024_COMPLETE_MESSAGE_CONTROLS_PASS side=%ld shard=%ld\n",side,shard);
  fflush(stdout);
  if(smoke)return 0;
  uint64_t found=0,positive=0;
  const double start=omp_get_wtime();
  #pragma omp parallel for schedule(dynamic,1) reduction(+:found,positive)
  for(int high=0;high<256;high++){
    uint8_t b[64];prepare(b,(int)side);
    SHA256_CTX state;
    uint32_t begin=(uint32_t(shard)<<28)|((uint32_t)high<<20);
    for(uint32_t tail=0;tail<(1U<<20);tail++){
      uint32_t x=begin|tail;
      for(int j=0;j<4;j++)b[p+j]=(uint8_t)(x>>(24-8*j))^mask[p+j];
      state=initial;SHA256_Transform(&state,b);
      if(state.h[0]==target[0]){
        int full=1;for(int j=1;j<8;j++)full&=(state.h[j]==target[j]);
        if(full){
          found++;
          #pragma omp critical
          {printf("ORIGINAL_K04_MATCH side=%ld shard=%ld component=",side,shard);
           for(int j=0;j<16;j++)printf("%02X",b[j]);
           puts("");fflush(stdout);}
        }
      }
      if(state.h[0]==planted[0]){
        int full=1;for(int j=1;j<8;j++)full&=(state.h[j]==planted[j]);
        if(full)positive++;
      }
    }
  }
  printf("SHARD_COMPLETE side=%ld shard=%ld checks=%llu original_hits=%llu planted_hits=%llu elapsed_sec=%.3f\n",
         side,shard,(unsigned long long)(1ULL<<28),
         (unsigned long long)found,(unsigned long long)positive,omp_get_wtime()-start);
  fflush(stdout);
  if(positive!=1)fail("planted witness count");
  return found?9:0;
}
