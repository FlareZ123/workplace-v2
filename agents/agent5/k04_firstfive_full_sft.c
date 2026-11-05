/* H-17 K04: all 2^40 hypothetical five-byte prefix replacements.
   Supply 0..255 as shard: first coupon byte fixed, other four exhaustive.
   Original evidence/commitments read-only. C11, OpenSSL, OpenMP.
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *spool_sha="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *selector="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static const char *mask_text="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *target_text="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const uint8_t copied[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const unsigned target[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static void fail(const char *message){fprintf(stderr,"ERROR %s\n",message);exit(2);}
static void source_check(const char *root,const char *relative,const char *literal,const char *sha){
 char path[4096];if(snprintf(path,sizeof(path),"%s/%s",root,relative)>=(int)sizeof(path))fail("path");
 FILE *f=fopen(path,"rb");if(!f)fail("source missing");
 if(fseek(f,0,SEEK_END))fail("fseek");
 long n=ftell(f);if(n<1||n>1000000)fail("length");rewind(f);
 char *data=malloc((size_t)n+1);if(!data)fail("malloc");
 if(fread(data,1,(size_t)n,f)!=(size_t)n)fail("fread");
 fclose(f);data[n]=0;
 char *first=strstr(data,literal);
 if(!first||strstr(first+strlen(literal),literal))fail("nonunique source selector");
 if(sha){uint8_t digest[32];char hex[65];SHA256((uint8_t*)data,(size_t)n,digest);
  for(int i=0;i<32;i++)sprintf(hex+i*2,"%02x",digest[i]);hex[64]=0;
  if(strcmp(hex,sha))fail("source checksum");}
 free(data);
}
static void block_init(uint8_t block[64]){
 memset(block,0,64);
 for(int i=0;i<16;i++)block[i]=copied[i]^mask[i];
 block[16]=0x80;block[63]=0x80;
}
static unsigned word(const uint8_t *d,int i){
 int j=4*i;
 return ((unsigned)d[j]<<24)|((unsigned)d[j+1]<<16)|((unsigned)d[j+2]<<8)|(unsigned)d[j+3];
}
int main(int argc,char **argv){
 if(argc!=4)fail("usage: firstfive ROOT SHARD --smoke|--full");
 char *end=0;long shard=strtol(argv[2],&end,10);
 if(!*argv[2]||*end||shard<0||shard>255)fail("invalid shard");
 int smoke=!strcmp(argv[3],"--smoke");
 if(!smoke&&strcmp(argv[3],"--full"))fail("invalid mode");
 source_check(argv[1],"evidence/print/spool-reconstruction.log",selector,spool_sha);
 source_check(argv[1],"evidence/recovery-routing.json",mask_text,NULL);
 source_check(argv[1],"acceptance.json",target_text,NULL);
 SHA256_CTX initial;SHA256_Init(&initial);
 uint8_t plant[64],phash[32];block_init(plant);
 const uint8_t sample[5]={0x5f,0x6b,0x83,0x17,0xe9};
 for(int i=0;i<5;i++)plant[i]=sample[i]^mask[i];
 SHA256(plant,16,phash);
 unsigned positive[8];for(int i=0;i<8;i++)positive[i]=word(phash,i);
 SHA256_CTX state=initial;SHA256_Transform(&state,plant);
 for(int i=0;i<8;i++)if(state.h[i]!=positive[i])fail("SHA256 differential control");
 const uint64_t checks=smoke?(1ULL<<20):(1ULL<<32);
 unsigned long long seen=0,hits=0,plant_hits=0;
 double begun=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,1) reduction(+:seen,hits,plant_hits)
 for(int b1=0;b1<256;b1++){
  uint8_t block[64];SHA256_CTX s;block_init(block);
  block[0]=(uint8_t)shard^mask[0];block[1]=(uint8_t)b1^mask[1];
  for(uint64_t t=0;t<checks/256;t++){
   block[2]=(uint8_t)(t>>16)^mask[2];
   block[3]=(uint8_t)(t>>8)^mask[3];
   block[4]=(uint8_t)t^mask[4];
   s=initial;SHA256_Transform(&s,block);
   if(s.h[0]==target[0]){
    int equal=1;for(int i=1;i<8;i++)equal&=s.h[i]==target[i];
    if(equal){hits++;
     #pragma omp critical
     {printf("ORIGINAL_K04_MATCH shard=%ld coupon=",shard);
      for(int i=0;i<16;i++)printf("%02X",i==0?(unsigned)shard:i==1?(unsigned)b1:i==2?(unsigned)(t>>16)&255:i==3?(unsigned)(t>>8)&255:i==4?(unsigned)t&255:copied[i]);
      puts("");fflush(stdout);}
    }
   }
   if(s.h[0]==positive[0]){
    int equal=1;for(int i=1;i<8;i++)equal&=s.h[i]==positive[i];
    if(equal)plant_hits++;
   }
   seen++;
  }
 }
 if(seen!=checks)fail("coverage counter");
 if(!smoke && plant_hits!=(unsigned)(shard==0x5f))fail("five-byte planted control");
 printf("SHARD_COMPLETE shard=%ld full_sha256_checks=%llu original_hits=%llu planted_hits=%llu elapsed=%.3f smoke=%d\n",shard,seen,hits,plant_hits,omp_get_wtime()-begun,smoke);
 return hits?9:0;
}
