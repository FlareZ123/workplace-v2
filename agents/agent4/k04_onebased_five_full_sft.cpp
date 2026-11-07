/* Agent 4: H-17 K04 one-based cassette-ticket five-byte exhaustive repair.
   Source-selected five-byte positions from the L-29/N ticket IDs, relative to
   the copied 18:02 ACK2. This is speculative physical repair, not an original
   coupon witness. No official resource is modified.

   Build: g++ -O3 -std=c++17 -fopenmp -Wno-deprecated-declarations
            k04_onebased_five_full_sft.cpp -lcrypto -o k04_five
   Usage: k04_five RESOURCES_ROOT SHARD_0_TO_127 [--smoke]
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t copied[16]={
  0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
  0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={
  0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
  0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const int pos[5]={0,2,9,13,15};
static const unsigned target[8]={
  0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,
  0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U};
static const char *spool_sha="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *retirement_sha="10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf";
static const char *selected="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static void fail(const char *s){fprintf(stderr,"ERROR: %s\n",s);exit(2);}
static void verify_source(const char *root,const char *path,const char *needle,const char *sha){
  char name[4096];
  if(snprintf(name,sizeof(name),"%s/%s",root,path)>=(int)sizeof(name))fail("path too long");
  FILE *f=fopen(name,"rb");if(!f)fail("missing source");
  if(fseek(f,0,SEEK_END)!=0)fail("seek");
  long n=ftell(f);if(n<0||n>1000000)fail("source length");rewind(f);
  char *s=(char*)malloc((size_t)n+1);if(!s)fail("memory");
  if(fread(s,1,(size_t)n,f)!=(size_t)n)fail("source read");fclose(f);s[n]=0;
  if(needle&&!strstr(s,needle))fail("source literal mismatch");
  if(sha){uint8_t d[32];char h[65];SHA256((const uint8_t*)s,(size_t)n,d);
    for(int i=0;i<32;i++)sprintf(h+2*i,"%02x",d[i]);
    if(strcmp(h,sha))fail("source SHA mismatch");}
  free(s);
}
static void prep(uint8_t block[64]){
  memset(block,0,64);
  for(int i=0;i<16;i++)block[i]=copied[i]^mask[i];
  block[16]=0x80;block[63]=0x80; // 128-bit message length
}
static unsigned word32(const uint8_t *d,int j){
  return ((unsigned)d[4*j]<<24)|((unsigned)d[4*j+1]<<16)|((unsigned)d[4*j+2]<<8)|d[4*j+3];
}
static void hash256_oneblock(const SHA256_CTX &init,const uint8_t block[64],unsigned d[8]){
  SHA256_CTX h=init;SHA256_Transform(&h,block);
  for(int i=0;i<8;i++)d[i]=h.h[i];
}
static int full_match(const unsigned a[8],const unsigned b[8]){
  if(a[0]!=b[0])return 0;
  for(int i=1;i<8;i++)if(a[i]!=b[i])return 0;
  return 1;
}
int main(int argc,char **argv){
  if(argc!=3&&argc!=4)fail("usage ROOT SHARD_0_TO_127 [--smoke]");
  const int smoke=argc==4&&!strcmp(argv[3],"--smoke");
  if(argc==4&&!smoke)fail("unrecognized mode");
  char *end=0;long sh=strtol(argv[2],&end,10);
  if(!*argv[2]||*end||sh<0||sh>127)fail("invalid shard");
  verify_source(argv[1],"evidence/print/spool-reconstruction.log",selected,spool_sha);
  verify_source(argv[1],"evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt","L-29/N    05     ST-112",retirement_sha);
  verify_source(argv[1],"evidence/recovery-routing.json","8556C8CB6140A7F9A5123AC7571BEE1C",nullptr);
  verify_source(argv[1],"acceptance.json","930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",nullptr);
  SHA256_CTX init;SHA256_Init(&init);
  uint8_t planted_block[64],std[32];prep(planted_block);
  int witness[5]={(int)sh*2+1,0x57,0x3c,0xa5,0xe7};
  for(int i=0;i<5;i++)planted_block[pos[i]]=(uint8_t)witness[i];
  SHA256(planted_block,16,std);
  unsigned plant_target[8],digest[8];
  for(int i=0;i<8;i++)plant_target[i]=word32(std,i);
  hash256_oneblock(init,planted_block,digest);
  if(!full_match(digest,plant_target))fail("planted direct SHA disagrees with one-block hash");
  // Validate the shortcut at 1,024 deterministic whole messages per shard.
  for(uint32_t i=0;i<1024;i++){
    uint8_t b[64],actual[32];prep(b);
    for(int j=0;j<5;j++)b[pos[j]]=(uint8_t)((i*2654435761U+j*0x9e37U)>>((j&3)*8));
    SHA256(b,16,actual);hash256_oneblock(init,b,digest);
    for(int k=0;k<8;k++)if(digest[k]!=word32(actual,k))fail("SHA control mismatch");
  }
  puts("SOURCE_SHA_AND_1024_WHOLE_MESSAGE_CONTROLS_PASS");fflush(stdout);
  if(smoke){printf("PLANTED_SELECTED_SHARD_CONTROL_PASS shard=%ld\n",sh);return 0;}
  unsigned long long found=0,plant=0;
  double t0=omp_get_wtime();
  // 128 nonoverlapping shards partition the high seven bits of component byte0.
  // Each shard tests 2 * 256 * 256 * 65536 = 2^33 *complete* components.
  #pragma omp parallel for collapse(2) schedule(dynamic,1) reduction(+:found,plant)
  for(int low=0;low<2;low++)for(int v1=0;v1<256;v1++){
    uint8_t b[64];prep(b);b[pos[0]]=(uint8_t)(sh*2+low);b[pos[1]]=(uint8_t)v1;
    SHA256_CTX h;
    for(int v2=0;v2<256;v2++){
      b[pos[2]]=(uint8_t)v2;
      for(uint32_t tail=0;tail<65536;tail++){
        b[pos[3]]=(uint8_t)(tail>>8);b[pos[4]]=(uint8_t)tail;
        h=init;SHA256_Transform(&h,b);
        if(h.h[0]==target[0]){
          int ok=1;for(int k=1;k<8;k++)ok&=h.h[k]==target[k];
          if(ok){found++;
            #pragma omp critical
            {printf("ORIGINAL_K04_MATCH shard=%ld component=",sh);
             for(int k=0;k<16;k++)printf("%02X",b[k]);puts("");fflush(stdout);}
          }
        }
        if(h.h[0]==plant_target[0]){
          int ok=1;for(int k=1;k<8;k++)ok&=h.h[k]==plant_target[k];
          if(ok)plant++;
        }
      }
    }
  }
  const unsigned long long expected=8589934592ULL;
  printf("SHARD_COMPLETE shard=%ld component_byte0=[%ld,%ld] checks=%llu original_hits=%llu plant_hits=%llu elapsed_sec=%.3f\n",
         sh,sh*2,sh*2+1,expected,found,plant,omp_get_wtime()-t0);fflush(stdout);
  if(plant!=1)fail("exact planted full-component count mismatch");
  return found?9:0;
}
