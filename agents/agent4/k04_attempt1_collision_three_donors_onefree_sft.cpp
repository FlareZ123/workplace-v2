/* H17 K04: earlier same JOB+ATTEMPT1 class-collision mixed three-word cache.
   Prior (16:45) LABEL1 ACK and (18:01) RECOVER REQUESTED1 share
   (JOB=PS-261003-0417,ATTEMPT=1) but have different 16byte payloads.
   A hypothetical stale per-word copier could take 3 of 4 32bit lanes
   from either earlier buffer, with fourth newly issued/wholly unknown.
   Exhaust all 4 missing lane choices * 8 earlier-donor lane selections *
   2^32 free complete lanes; 128 disjoint (case, high-2-bit shard) jobs.
   This is an unproven copy-stage reconstruction model, not paper evidence.

   Build: g++ -O3 -std=c++17 -fopenmp -Wno-deprecated-declarations
           k04_job_attempt1_collision_onefree_word_sft.cpp -lcrypto -o k04_mix
   Usage: k04_mix RESOURCES_ROOT CASE_0_TO_31 SHARD_0_TO_3 [--smoke]
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint8_t src_label[16]={
  0xe1,0xe6,0x0d,0x5f,0x6b,0x6d,0xd2,0x22,
  0x5f,0xa6,0xd5,0xa2,0xa6,0x3a,0xd9,0x32};
static const uint8_t src_req[16]={
  0xcd,0x3e,0x4f,0x21,0x6a,0xdb,0x2f,0xb1,
  0x80,0xda,0x2a,0xa9,0x0b,0x33,0xf7,0xa4};
static const uint8_t route[16]={
  0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
  0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const unsigned target[8]={
  0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,
  0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U};
static const char *sha_spool="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *row_label="2026-10-03T16:45:00+00:00 JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=E1E60D5F6B6DD2225FA6D5A2A63AD932 DEST=bench";
static const char *row_req="2026-10-03T18:01:00Z JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER PAYLOAD=CD3E4F216ADB2FB180DA2AA90B33F7A4 DEST=bench";
static const char *row_ack2="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static void fail(const char *what){fprintf(stderr,"ERROR: %s\n",what);exit(2);}
static void source_check(const char *root,const char *relative,const char *line,const char *fingerprint){
  char path[4096];
  if(snprintf(path,sizeof(path),"%s/%s",root,relative)>=(int)sizeof(path))fail("path");
  FILE *f=fopen(path,"rb");if(!f)fail("missing original source");
  if(fseek(f,0,SEEK_END))fail("seek");
  long n=ftell(f);if(n<0||n>1000000)fail("source size");
  rewind(f);char *contents=(char*)malloc((size_t)n+1);if(!contents)fail("memory");
  if(fread(contents,1,(size_t)n,f)!=(size_t)n)fail("read");
  fclose(f);contents[n]=0;
  if(line){
    char *p=strstr(contents,line);
    if(!p||strstr(p+strlen(line),line))fail("source literal absent or duplicate");
  }
  if(fingerprint){
    uint8_t digest[32];char actual[65];
    SHA256((uint8_t*)contents,(size_t)n,digest);
    for(int i=0;i<32;i++)sprintf(actual+2*i,"%02x",digest[i]);
    if(strcmp(actual,fingerprint))fail("original source SHA256");
  }
  free(contents);
}
static void prep(uint8_t block[64],int which){
  memset(block,0,64);
  int missing=which/8, donor_choice=which%8, donor_index=0;
  for(int lane=0;lane<4;lane++){
    if(lane==missing)continue;
    const uint8_t *parent=((donor_choice>>donor_index++)&1)?src_req:src_label;
    memcpy(block+4*lane,parent+4*lane,4);
  }
  for(int k=0;k<16;k++)block[k]^=route[k];
  block[16]=0x80;block[63]=0x80;
}
static unsigned parseword(const uint8_t raw[32],int k){
  return ((unsigned)raw[4*k]<<24)|((unsigned)raw[4*k+1]<<16)
        |((unsigned)raw[4*k+2]<<8)|raw[4*k+3];
}
static int same_hash(const SHA256_CTX &initial,const uint8_t block[64],const unsigned digest[8]){
  SHA256_CTX c=initial;SHA256_Transform(&c,block);
  if(c.h[0]!=digest[0])return 0;
  for(int k=1;k<8;k++)if(c.h[k]!=digest[k])return 0;
  return 1;
}
int main(int argc,char **argv){
  if(argc!=4&&argc!=5)fail("usage ROOT CASE_0_TO_31 SHARD_0_TO_3 [--smoke]");
  char *end=nullptr;long which=strtol(argv[2],&end,10);
  if(!*argv[2]||*end||which<0||which>31)fail("case");
  long shard=strtol(argv[3],&end,10);
  if(!*argv[3]||*end||shard<0||shard>3)fail("shard");
  int smoke=argc==5&&!strcmp(argv[4],"--smoke");
  if(argc==5&&!smoke)fail("mode");
  source_check(argv[1],"evidence/print/spool-reconstruction.log",row_label,sha_spool);
  source_check(argv[1],"evidence/print/spool-reconstruction.log",row_req,sha_spool);
  source_check(argv[1],"evidence/print/spool-reconstruction.log",row_ack2,sha_spool);
  source_check(argv[1],"evidence/recovery-routing.json","8556C8CB6140A7F9A5123AC7571BEE1C",nullptr);
  source_check(argv[1],"acceptance.json","930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",nullptr);
  const int off=4*((int)which/8);
  SHA256_CTX initial;SHA256_Init(&initial);
  uint8_t block[64],raw[32];prep(block,(int)which);
  uint32_t planted=(uint32_t(shard)<<30)|0x01234567U;
  for(int k=0;k<4;k++)block[off+k]=(uint8_t)(planted>>(24-8*k))^route[off+k];
  SHA256(block,16,raw);unsigned plant[8];
  for(int i=0;i<8;i++)plant[i]=parseword(raw,i);
  if(!same_hash(initial,block,plant))fail("planted full Sha mismatch");
  for(uint32_t k=0;k<1024;k++){
    prep(block,(int)which);
    uint32_t v=k*2654435761U+0xABCDFU;
    for(int j=0;j<4;j++)block[off+j]=(uint8_t)(v>>(24-8*j))^route[off+j];
    SHA256(block,16,raw);unsigned hash[8];
    for(int j=0;j<8;j++)hash[j]=parseword(raw,j);
    if(!same_hash(initial,block,hash))fail("SHA256 differential whole 16byte");
  }
  printf("SOURCE_AND_SHA_CONTROLS_PASS case=%ld shard=%ld\n",which,shard);fflush(stdout);
  if(smoke)return 0;
  uint64_t hits=0,plants=0;
  const double start=omp_get_wtime();
  #pragma omp parallel for schedule(dynamic,1) reduction(+:hits,plants)
  for(int hi=0;hi<256;hi++){
    uint8_t b[64];prep(b,(int)which);
    SHA256_CTX ctx;
    uint32_t prefix=(uint32_t(shard)<<30)|((uint32_t)hi<<22);
    for(uint32_t lo=0;lo<(1U<<22);lo++){
      uint32_t word=prefix|lo;
      for(int j=0;j<4;j++)b[off+j]=(uint8_t)(word>>(24-8*j))^route[off+j];
      ctx=initial;SHA256_Transform(&ctx,b);
      if(ctx.h[0]==target[0]){
        int ok=1;for(int j=1;j<8;j++)ok&=(ctx.h[j]==target[j]);
        if(ok){
          hits++;
          #pragma omp critical
          {printf("ORIGINAL_K04_MATCH case=%ld shard=%ld component=",which,shard);
           for(int j=0;j<16;j++)printf("%02X",b[j]);puts("");fflush(stdout);}
        }
      }
      if(ctx.h[0]==plant[0]){
        int ok=1;for(int j=1;j<8;j++)ok&=(ctx.h[j]==plant[j]);
        if(ok)plants++;
      }
    }
  }
  printf("SHARD_COMPLETE case=%ld shard=%ld checks=%llu original_hits=%llu plant_hits=%llu elapsed_sec=%.3f\n",
         which,shard,(unsigned long long)(1ULL<<30),
         (unsigned long long)hits,(unsigned long long)plants,omp_get_wtime()-start);
  fflush(stdout);
  if(plants!=1)fail("planted full-coupon original loop miss");
  return hits?9:0;
}
