/* H-17 K04: complete 32-bit repeated-word XOR copy-stage search.
   All sources and commitments are read-only.
   Build C++17 with OpenSSL libcrypto and OpenMP.
   Run: executable ORIGINAL_SOURCE_ROOT 256
   A smaller shard prefix 1..255 is for smoke runs only.
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const unsigned target[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const unsigned char original[16]={0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static const char *spool_sha="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *selected_row="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static const char *mask_hex="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *target_hex="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static void die(const char *s){fprintf(stderr,"ERROR %s\n",s);exit(2);}
static unsigned char *load(const char *root,const char *relative,size_t *n){
 char path[2048];if(snprintf(path,sizeof(path),"%s/%s",root,relative)>=(int)sizeof(path))die("path length");
 FILE *f=fopen(path,"rb");if(!f)die("missing source");if(fseek(f,0,SEEK_END))die("seek");long sz=ftell(f);if(sz<0||sz>1000000)die("length");rewind(f);
 unsigned char *data=(unsigned char*)malloc((size_t)sz+1);if(!data)die("allocation");if(fread(data,1,(size_t)sz,f)!=(size_t)sz)die("short read");fclose(f);data[sz]=0;*n=(size_t)sz;return data;
}
static void verify(const char *root){
 size_t n;unsigned char *x=load(root,"evidence/print/spool-reconstruction.log",&n),digest[32];SHA256(x,n,digest);char h[65];for(int i=0;i<32;i++)sprintf(h+2*i,"%02x",digest[i]);if(strcmp(h,spool_sha))die("spool SHA256");
 char *p=strstr((char*)x,selected_row);if(!p||strstr(p+strlen(selected_row),selected_row))die("selected ACK2");free(x);
 x=load(root,"evidence/recovery-routing.json",&n);if(!strstr((char*)x,mask_hex))die("mask original");free(x);
 x=load(root,"acceptance.json",&n);if(!strstr((char*)x,target_hex))die("target original");free(x);
}
static void block_for(uint32_t k,unsigned char block[64]){
 memset(block,0,64);
 unsigned char pattern[4]={(unsigned char)(k>>24),(unsigned char)(k>>16),(unsigned char)(k>>8),(unsigned char)k};
 for(int i=0;i<16;i++)block[i]=original[i]^pattern[i%4];
 block[16]=0x80;block[63]=0x80;
}
static unsigned digest_word(const unsigned char *p,int i){return ((unsigned)p[4*i]<<24)|((unsigned)p[4*i+1]<<16)|((unsigned)p[4*i+2]<<8)|p[4*i+3];}
int main(int argc,char **argv){
 if(argc!=3)die("usage: periodic_xor SOURCE_ROOT SHARDS [256 for full, 1 for quick first shard]");
 char *end=nullptr;long shards=strtol(argv[2],&end,10);if(!*argv[2]||*end||shards<1||shards>256)die("shards value");
 verify(argv[1]);SHA256_CTX initial;SHA256_Init(&initial);
 const uint32_t plantKey=0xC1A071F3u;unsigned planted[8];unsigned char block[64],digest[32];SHA256_CTX ctx;
 block_for(plantKey,block);SHA256(block,16,digest);for(int i=0;i<8;i++)planted[i]=digest_word(digest,i);
 for(unsigned k=0;k<1024;k++){
  uint32_t a=k*0x9e3779b9u;block_for(a,block);SHA256(block,16,digest);ctx=initial;SHA256_Transform(&ctx,block);
  for(int i=0;i<8;i++)if(ctx.h[i]!=digest_word(digest,i))die("SHA transform differential control");
 }
 unsigned long long originalHits=0,plantHits=0;double began=omp_get_wtime();
 printf("SOURCE_AND_1024_SHA_CONTROLS_PASS matrix=%ld/256 original_selected=16bytes repeated_fourbyte_xor\n",shards);fflush(stdout);
 #pragma omp parallel for schedule(dynamic,1) reduction(+:originalHits,plantHits)
 for(int hi=0;hi<shards;hi++){
  unsigned long long oh=0,ph=0;
  unsigned char b[64];SHA256_CTX s;
  for(uint32_t low=0;low<(1u<<24);low++){
   uint32_t key=((uint32_t)hi<<24)|low;
   block_for(key,b);s=initial;SHA256_Transform(&s,b);
   if(s.h[0]==target[0]){
    bool same=true;for(int i=1;i<8;i++)same &= (s.h[i]==target[i]);
    if(same){
      oh++;
      #pragma omp critical
      {printf("AUTHENTIC_K04_MATCH xor_key=%08X component=",key);for(int i=0;i<16;i++)printf("%02X",b[i]);printf("\n");fflush(stdout);}
    }
   }
   if(s.h[0]==planted[0]){
    bool same=true;for(int i=1;i<8;i++)same &= (s.h[i]==planted[i]);if(same)ph++;
   }
  }
  originalHits+=oh;plantHits+=ph;
  #pragma omp critical
  {printf("DONE shard=%d/256 checks=16777216 original_hits=%llu synthetic_hits=%llu\n",hi,oh,ph);fflush(stdout);}
 }
 unsigned long long checks=(unsigned long long)shards*(1ull<<24);
 printf("FINAL checked=%llu original_hits=%llu synthetic_hits=%llu seconds=%.3f\n",checks,originalHits,plantHits,omp_get_wtime()-began);
 if(shards==256 && plantHits!=1)die("planted exact full-key control failed");
 if(originalHits)return 10;
 return 0;
}
