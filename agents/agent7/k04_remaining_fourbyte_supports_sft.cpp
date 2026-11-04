/* H-17 K04 selected coupon: two disjoint unknown two-byte edge fragments.
   Original evidence, mask, and acceptance are read-only.
   Build as C++17 with OpenSSL libcrypto and OpenMP.
   Accept repository resources root, optional first byte 0..255 for sharding.
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const unsigned target[8] = {
  0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
  0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0
};
static const uint8_t component[16] = {
  0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,
  0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9
};
static const char *spool_sha = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *selected_row = "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static const char *mask_hex = "8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *target_hex = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static void quit(const char *s) {fprintf(stderr,"ERROR: %s\n",s);exit(2);}
static size_t read_file(const char *root,const char *relative,unsigned char **out) {
  char path[4096];
  if(snprintf(path,sizeof(path),"%s/%s",root,relative)>=(int)sizeof(path))quit("path too long");
  FILE *f=fopen(path,"rb");if(!f)quit("cannot open original source");
  if(fseek(f,0,SEEK_END)!=0)quit("fseek source");
  long n=ftell(f);if(n<0||n>1000000L)quit("source length");
  rewind(f);unsigned char *a=(unsigned char*)malloc((size_t)n+1);
  if(!a)quit("allocation");
  if(fread(a,1,(size_t)n,f)!=(size_t)n)quit("source short read");
  fclose(f);a[n]=0;*out=a;return (size_t)n;
}
static void check_sources(const char *root) {
  unsigned char *x;size_t n=read_file(root,"evidence/print/spool-reconstruction.log",&x);
  uint8_t digest[32];SHA256(x,n,digest);
  char hex[65];for(int i=0;i<32;i++)sprintf(hex+2*i,"%02x",digest[i]);
  if(strcmp(hex,spool_sha)!=0)quit("original spool SHA256 mismatch");
  char *p=strstr((char*)x,selected_row);
  if(!p||strstr(p+strlen(selected_row),selected_row))quit("selected ACK2 record missing/duplicated");
  free(x);
  read_file(root,"evidence/recovery-routing.json",&x);
  if(!strstr((char*)x,mask_hex))quit("original K04 mask mismatch");
  free(x);
  read_file(root,"acceptance.json",&x);
  if(!strstr((char*)x,target_hex))quit("original K04 slot commitment mismatch");
  free(x);
}
static void prepare(uint8_t block[64]) {
  memset(block,0,64);memcpy(block,component,16);
  block[16]=0x80;block[63]=0x80;
}
static void check_hash_controls(const SHA256_CTX *initial, unsigned planted[8]) {
  uint8_t block[64], full[32];SHA256_CTX ctx;
  prepare(block);
  for(int i=0;i<1000;i++) {
    uint32_t z=((uint32_t)i*2654435761U)^0x78ACD115U;
    block[0]=(uint8_t)(z>>24);block[1]=(uint8_t)(z>>16);
    block[14]=(uint8_t)(z>>8);block[15]=(uint8_t)z;
    SHA256(block,16,full);ctx=*initial;SHA256_Transform(&ctx,block);
    for(int j=0;j<8;j++) {
      unsigned word=((unsigned)full[j*4]<<24)|((unsigned)full[j*4+1]<<16)
          |((unsigned)full[j*4+2]<<8)|full[j*4+3];
      if(ctx.h[j]!=word)quit("one-block SHA256 disagrees with ordinary SHA256");
    }
  }
  block[0]=0x42;block[1]=0xb7;block[14]=0xcc;block[15]=0x39;
  SHA256(block,16,full);
  for(int j=0;j<8;j++)planted[j]=((unsigned)full[j*4]<<24)|((unsigned)full[j*4+1]<<16)
          |((unsigned)full[j*4+2]<<8)|full[j*4+3];
  ctx=*initial;SHA256_Transform(&ctx,block);
  for(int j=0;j<8;j++)if(ctx.h[j]!=planted[j])quit("planted positive digest inconsistent");
}

/* Complete the four whole-byte replacement frontier of original K04 ACK2.

   Previously exhausted supports:
   - 91 supports {0,1,i,j}, i<j in 2..15, conditional on the new 78-pair
     workflow completing, and prior adjacent-pair/edge/contiguous studies.
   - 12 remaining contiguous windows of four bytes.
   - four four-word same-byte-lane supports.

   Here each of the other 1713 unordered byte quartets receives every
   independent four-byte assignment. Every outcome is checked against the
   original unchanged 256-bit K04 SHA256 commitment, with exact controls.
*/
static unsigned digest_word(const uint8_t d[32],int k){
  return ((unsigned)d[4*k]<<24)|((unsigned)d[4*k+1]<<16)
    |((unsigned)d[4*k+2]<<8)|d[4*k+3];
}
static void planted_for_quartet(const SHA256_CTX *initial,
                               const int q[4],unsigned digest[8]){
  uint8_t block[64],full[32];SHA256_CTX state;
  prepare(block);
  block[q[0]]=0xde;block[q[1]]=0xad;block[q[2]]=0xbe;block[q[3]]=0xef;
  SHA256(block,16,full);
  state=*initial;SHA256_Transform(&state,block);
  for(int k=0;k<8;k++){
    digest[k]=digest_word(full,k);
    if(state.h[k]!=digest[k])quit("quartet planted SHA256 discrepancy");
  }
}
static int excluded_quartet(int a,int b,int c,int d) {
  if(a==0 && b==1)return 1; /* completed first A9A9 family */
  if(d==a+3)return 1; /* four contiguous bytes */
  if(a%4==b%4 && a%4==c%4 && a%4==d%4)return 1; /* common lane */
  return 0;
}
int main(int argc,char **argv) {
  if(argc<3||argc>4)quit("usage: fourbyte ROOT SHARD_0_TO_127 [--smoke]");
  if(argc==4&&strcmp(argv[3],"--smoke")!=0)quit("bad mode");
  const int smoke=argc==4;
  char *end=0;long shard=strtol(argv[2],&end,10);
  if(!*argv[2]||*end||shard<0||shard>=128)quit("bad shard");
  check_sources(argv[1]);
  SHA256_CTX initial;SHA256_Init(&initial);
  unsigned inherited[8];check_hash_controls(&initial,inherited);
  int q[1713][4],n=0;
  for(int a=0;a<16;a++)for(int b=a+1;b<16;b++)
  for(int c=b+1;c<16;c++)for(int d=c+1;d<16;d++){
    if(excluded_quartet(a,b,c,d))continue;
    if(n>=1713)quit("enumeration exceeded quartet boundary");
    q[n][0]=a;q[n][1]=b;q[n][2]=c;q[n][3]=d;n++;
  }
  if(n!=1713)quit("incorrect remaining quartet count");
  printf("ORIGINAL_SOURCE_SHA_AND_CANDIDATE_CONTROLS_PASS supports=%d shard=%ld smoke=%d\n",
    n,shard,smoke);fflush(stdout);
  if(smoke){
    for(int k=0;k<n;k++){
      unsigned digest[8];planted_for_quartet(&initial,q[k],digest);
    }
    printf("ALL_1713_PLANTED_QUARTET_CONTROLS_PASS\n");fflush(stdout);
    return 0;
  }
  unsigned long long orig_total=0,plant_total=0;
  int quartets=0;double started=omp_get_wtime();
  for(int qi=0;qi<n;qi++){
    if(qi%128!=shard)continue;
    const int *p=q[qi];unsigned planted[8];planted_for_quartet(&initial,p,planted);
    unsigned long long original_hits=0,positive_hits=0;
    #pragma omp parallel for schedule(dynamic,1) reduction(+:original_hits,positive_hits)
    for(int v0=0;v0<256;v0++){
      uint8_t block[64];SHA256_CTX state;prepare(block);block[p[0]]=(uint8_t)v0;
      for(int v1=0;v1<256;v1++){
        block[p[1]]=(uint8_t)v1;
        for(uint32_t tail=0;tail<65536;tail++){
          block[p[2]]=(uint8_t)(tail>>8);
          block[p[3]]=(uint8_t)tail;
          state=initial;SHA256_Transform(&state,block);
          if(state.h[0]==target[0]){
            int same=1;for(int k=1;k<8;k++)same&=state.h[k]==target[k];
            if(same){
              original_hits++;
              #pragma omp critical
              {printf("ORIGINAL_K04_MATCH support=%d byte_positions=%d,%d,%d,%d component=",
                      qi,p[0],p[1],p[2],p[3]);
               for(int k=0;k<16;k++)printf("%02X",block[k]);
               printf("\n");fflush(stdout);}
            }
          }
          if(state.h[0]==planted[0]){
            int same=1;for(int k=1;k<8;k++)same&=state.h[k]==planted[k];
            if(same)positive_hits++;
          }
        }
      }
    }
    if(positive_hits!=1)quit("planted exhaustive quartet target not recovered once");
    orig_total+=original_hits;plant_total+=positive_hits;quartets++;
    printf("QUARTET_DONE q=%d indexes=%d,%d,%d,%d complete_checks=4294967296 original_hits=%llu plant_hits=%llu\n",
      qi,p[0],p[1],p[2],p[3],original_hits,positive_hits);fflush(stdout);
  }
  const unsigned long long checks=(unsigned long long)quartets*4294967296ULL;
  printf("SHARD_COMPLETE shard=%ld quartets=%d full_sha256_checks=%llu original_hits=%llu plants=%llu elapsed=%.3f\n",
     shard,quartets,checks,orig_total,plant_total,omp_get_wtime()-started);fflush(stdout);
  if(orig_total)return 9;
  if(plant_total!=(unsigned long long)quartets)return 3;
  return 0;
}
