/* Original H-17 K04 masked coupon: exhaustive five-byte contiguous burst model.
 * Selected copy is disputed. This tests an independent physical/copy-stage burst
 * hypothesis; an original match must still be validated with unchanged verify.py.
 * Standard C++17/OpenMP, OpenSSL SHA256. Read-only archive and commitments.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const unsigned target[8] = {
 0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,
 0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U
};
static const uint8_t copied_component[16] = {
 0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,
 0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9
};
static const char *original_spool_sha = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *original_selected = "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static const char *original_mask = "8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *original_target = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static void fail(const char *msg){fprintf(stderr,"ERROR: %s\n",msg);exit(2);}
static size_t read_evidence(const char *root,const char *relative,unsigned char **out){
 char path[4096];
 if(snprintf(path,sizeof(path),"%s/%s",root,relative)>=(int)sizeof(path))fail("path too long");
 FILE *file=fopen(path,"rb");if(!file)fail("missing evidence");
 if(fseek(file,0,SEEK_END))fail("seek failure");
 long n=ftell(file);if(n<0||n>1000000L)fail("source size invalid");
 rewind(file);unsigned char *p=(unsigned char*)malloc((size_t)n+1);
 if(!p)fail("allocation failed");
 if(fread(p,1,(size_t)n,file)!=(size_t)n)fail("short source read");
 fclose(file);p[n]=0;*out=p;return (size_t)n;
}
static void source_controls(const char *root){
 unsigned char *p; size_t n=read_evidence(root,"evidence/print/spool-reconstruction.log",&p);
 uint8_t digest[32];char hex[65];SHA256(p,n,digest);
 for(int j=0;j<32;j++)sprintf(hex+j*2,"%02x",digest[j]);
 if(strcmp(hex,original_spool_sha))fail("original spool SHA mismatch");
 char *row=strstr((char*)p,original_selected);
 if(!row||strstr(row+strlen(original_selected),original_selected))fail("selected ACK2 row missing or repeated");
 free(p);
 read_evidence(root,"evidence/recovery-routing.json",&p);
 if(!strstr((char*)p,original_mask))fail("route mask mismatch");free(p);
 read_evidence(root,"acceptance.json",&p);
 if(!strstr((char*)p,original_target))fail("full original K04 commitment mismatch");free(p);
}
static void pad16(uint8_t block[64]){
 memset(block,0,64);memcpy(block,copied_component,16);
 block[16]=0x80;block[63]=0x80;
}
static unsigned get32(const unsigned char *b){return ((unsigned)b[0]<<24)|((unsigned)b[1]<<16)|((unsigned)b[2]<<8)|b[3];}
static void sha_words(const SHA256_CTX *initial,const uint8_t block[64],unsigned out[8]){
 SHA256_CTX s=*initial; SHA256_Transform(&s,block);
 for(int k=0;k<8;k++)out[k]=s.h[k];
}
static int equals8(const SHA256_CTX *initial,const uint8_t block[64],const unsigned wanted[8]){
 SHA256_CTX s=*initial;SHA256_Transform(&s,block);
 if(s.h[0]!=wanted[0])return 0;
 for(int k=1;k<8;k++)if(s.h[k]!=wanted[k])return 0;
 return 1;
}
static void seeded_witness(const SHA256_CTX *initial,int start,int shard,unsigned witness[8]){
 uint8_t block[64],full[32];pad16(block);
 block[start]=(uint8_t)shard;
 block[start+1]=0xde;block[start+2]=0xad;block[start+3]=0xbe;block[start+4]=0xef;
 SHA256(block,16,full);
 sha_words(initial,block,witness);
 for(int k=0;k<8;k++)if(get32(full+4*k)!=witness[k])fail("planted digest SHA disagreement");
}
static void smoke(const SHA256_CTX *initial){
 uint8_t block[64],full[32];unsigned computed[8];
 for(int i=0;i<3072;i++){
  int start=i%12;pad16(block);
  uint32_t v=(uint32_t)i*2654435761U+0xAA55A22BU;
  block[start]=(uint8_t)(i>>4);
  block[start+1]=(uint8_t)(v>>24);block[start+2]=(uint8_t)(v>>16);
  block[start+3]=(uint8_t)(v>>8);block[start+4]=(uint8_t)v;
  sha_words(initial,block,computed);SHA256(block,16,full);
  for(int k=0;k<8;k++)if(computed[k]!=get32(full+k*4))fail("SHA256_Transform != SHA256");
 }
 for(int start=0;start<12;start++)for(int shard=0;shard<256;shard++){
  unsigned witness[8];seeded_witness(initial,start,shard,witness);
  pad16(block);block[start]=(uint8_t)shard;
  block[start+1]=0xde;block[start+2]=0xad;block[start+3]=0xbe;block[start+4]=0xef;
  if(!equals8(initial,block,witness))fail("planted full commitment positive missing");
 }
 printf("ALL_3072_SHA_AND_3072_PLANTED_WITNESS_CONTROLS_PASS\n");fflush(stdout);
}
static void print_candidate(const uint8_t block[64]){
 for(int k=0;k<16;k++)printf("%02X",block[k]);
 printf("\n");fflush(stdout);
}
int main(int argc,char **argv){
 if(argc<3||argc>4)fail("usage: k04_fivebyte ARCHIVE_ROOT SHARD_0_TO_255 [--smoke]");
 char *end=0;long parsed=strtol(argv[2],&end,10);
 if(!argv[2][0]||*end||parsed<0||parsed>255)fail("invalid shard");
 if(argc==4&&strcmp(argv[3],"--smoke"))fail("unknown mode");
 source_controls(argv[1]);
 SHA256_CTX initial;SHA256_Init(&initial);
 smoke(&initial);
 printf("SOURCE_PIN_PASS shard=%ld mode=%s\n",parsed,argc==4?"smoke":"full");fflush(stdout);
 if(argc==4)return 0;
 const int shard=(int)parsed;
 uint64_t original_total=0,plant_total=0;
 for(int start=0;start<12;start++){
  unsigned witness[8];seeded_witness(&initial,start,shard,witness);
  uint64_t hits=0,plants=0;
  #pragma omp parallel for schedule(static) reduction(+:hits,plants)
  for(int second=0;second<256;second++){
   uint8_t block[64];SHA256_CTX state;pad16(block);
   block[start]=(uint8_t)shard;block[start+1]=(uint8_t)second;
   for(uint32_t last24=0;last24<0x1000000U;last24++){
    block[start+2]=(uint8_t)(last24>>16);
    block[start+3]=(uint8_t)(last24>>8);
    block[start+4]=(uint8_t)last24;
    state=initial; SHA256_Transform(&state,block);
    if(state.h[0]==target[0]){
     int equal=1;for(int j=1;j<8;j++)equal &= state.h[j]==target[j];
     if(equal){
      hits++;
      #pragma omp critical
      {printf("ORIGINAL_K04_MATCH shard=%d start=%d component=",shard,start);print_candidate(block);}
     }
    }
    if(state.h[0]==witness[0]){
     int equal=1;for(int j=1;j<8;j++)equal &= state.h[j]==witness[j];
     if(equal)plants++;
    }
   }
  }
  if(plants!=1)fail("exhaustive fivebyte planted unique witness missing");
  original_total+=hits;plant_total+=plants;
  printf("WINDOW_DONE start=%d shard=%d checks=4294967296 original_hits=%llu planted_hits=%llu\n",
   start,shard,(unsigned long long)hits,(unsigned long long)plants);fflush(stdout);
 }
 printf("SHARD_COMPLETE shard=%d windows=12 checks=51539607552 original_hits=%llu planted_hits=%llu\n",
  shard,(unsigned long long)original_total,(unsigned long long)plant_total);fflush(stdout);
 return original_total?9:0;
}
