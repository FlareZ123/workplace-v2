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

/* New conditional fault: leading copied A9 A9 bytes at positions 0,1,
   plus any two nonadjacent positions in 2..15, all bytes arbitrary.
   Adjacent second-pair positions were covered by older exhaustive work.
   The 78 disjoint new supports partition into sixteen CI shards.
*/
static unsigned word_from_digest(const uint8_t digest[32],int j) {
  return ((unsigned)digest[4*j]<<24)|((unsigned)digest[4*j+1]<<16)
      |((unsigned)digest[4*j+2]<<8)|digest[4*j+3];
}
static void pair_planted(const SHA256_CTX *initial,int i,int j,unsigned planted[8]) {
  uint8_t block[64],full[32];SHA256_CTX state;
  prepare(block);block[0]=0xde;block[1]=0xad;block[i]=0xbe;block[j]=0xef;
  SHA256(block,16,full);state=*initial;SHA256_Transform(&state,block);
  for(int k=0;k<8;k++){
    planted[k]=word_from_digest(full,k);
    if(state.h[k]!=planted[k])quit("pair planted control SHA mismatch");
  }
}
int main(int argc,char **argv) {
  if(argc<3||argc>4)quit("usage: broadpair ROOT SHARD_0_TO_15 [--smoke]");
  if(argc==4 && strcmp(argv[3],"--smoke")!=0)quit("unsupported mode");
  int smoke=argc==4;
  char *end=0;long shard=strtol(argv[2],&end,10);
  if(!*argv[2]||*end||shard<0||shard>15)quit("invalid shard");
  check_sources(argv[1]);
  SHA256_CTX initial;SHA256_Init(&initial);
  unsigned inherited_positive[8];check_hash_controls(&initial,inherited_positive);
  int pair_i[78],pair_j[78],n=0;
  for(int i=2;i<=15;i++)for(int j=i+2;j<=15;j++){
    if(n>=78)quit("pair limit");
    pair_i[n]=i;pair_j[n]=j;n++;
  }
  if(n!=78)quit("wrong number of disjoint nonadjacent second pairs");
  printf("SOURCE_AND_SHA256_CONTROLS_PASS pairs=%d shard=%ld smoke=%d\n",n,shard,smoke);fflush(stdout);
  if(smoke){
    for(int k=0;k<n;k++) {
      unsigned positive[8];pair_planted(&initial,pair_i[k],pair_j[k],positive);
    }
    printf("PLANTED_ALL_78_POSITION_CONTROLS_PASS\n");
    return 0;
  }
  unsigned long long all_hits=0,all_plants=0;
  int tested_pairs=0;double t0=omp_get_wtime();
  for(int pair=0;pair<n;pair++) {
    if(pair%16 != shard)continue;
    int i=pair_i[pair],j=pair_j[pair];
    unsigned planted[8];pair_planted(&initial,i,j,planted);
    unsigned long long orig_hits=0,plant_hits=0;
    #pragma omp parallel for schedule(dynamic,1) reduction(+:orig_hits,plant_hits)
    for(int a=0;a<256;a++){
      uint8_t block[64];SHA256_CTX state;prepare(block);block[0]=(uint8_t)a;
      for(int b=0;b<256;b++){
        block[1]=(uint8_t)b;
        for(uint32_t z=0;z<65536;z++){
          block[i]=(uint8_t)(z>>8);block[j]=(uint8_t)z;
          state=initial;SHA256_Transform(&state,block);
          if(state.h[0]==target[0]){
            int same=1;for(int k=1;k<8;k++)same&=(state.h[k]==target[k]);
            if(same){
              orig_hits++;
              #pragma omp critical
              {printf("ORIGINAL_K04_MATCH pair=%d bytes=0,1,%d,%d value=",pair,i,j);
               for(int k=0;k<16;k++)printf("%02X",block[k]);
               printf("\n");fflush(stdout);}
            }
          }
          if(state.h[0]==planted[0]){
            int same=1;for(int k=1;k<8;k++)same&=(state.h[k]==planted[k]);
            if(same)plant_hits++;
          }
        }
      }
    }
    if(plant_hits!=1)quit("complete pair planted SHA target not recovered exactly once");
    printf("PAIR_DONE pair=%d index2=%d index3=%d candidates=4294967296 original_hits=%llu positive=%llu\n",
      pair,i,j,orig_hits,plant_hits);fflush(stdout);
    tested_pairs++;all_hits+=orig_hits;all_plants+=plant_hits;
  }
  unsigned long long expected=(unsigned long long)tested_pairs*4294967296ULL;
  printf("SHARD_COMPLETE shard=%ld pairs=%d complete_checks=%llu original_hits=%llu planted=%llu secs=%.3f\n",
    shard,tested_pairs,expected,all_hits,all_plants,omp_get_wtime()-t0);fflush(stdout);
  if(all_hits)return 9;
  if(all_plants!=(unsigned long long)tested_pairs)return 3;
  return 0;
}
