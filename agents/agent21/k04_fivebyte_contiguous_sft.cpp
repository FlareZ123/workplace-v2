/* H-17 K04: exhaustive 5-byte contiguous replacement family.
 * The supplied original acceptance and evidence are read-only.
 * Each shard fixes one of 256 first-replacement-byte values.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>

static const unsigned wanted[8] = {0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const uint8_t baseline[16] = {0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static const char *spool_hash="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *selected="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static const char *mask="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *target="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static void die(const char *message){fprintf(stderr,"ERROR %s\n",message);exit(2);}
static unsigned char *read_data(const char *root,const char *name,size_t *n){
 char path[4096];if(snprintf(path,sizeof(path),"%s/%s",root,name)>=(int)sizeof(path))die("source path");
 FILE *f=fopen(path,"rb");if(!f)die("open original evidence");
 if(fseek(f,0,SEEK_END))die("seek");long z=ftell(f);if(z<0||z>2000000)die("size");
 rewind(f);unsigned char *p=(unsigned char*)malloc((size_t)z+1);if(!p)die("alloc");
 if(fread(p,1,(size_t)z,f)!=(size_t)z)die("read");fclose(f);p[z]=0;*n=(size_t)z;return p;
}
static void check_sources(const char *root){
 size_t n;unsigned char *p=read_data(root,"evidence/print/spool-reconstruction.log",&n);
 unsigned char digest[32];char hex[65];SHA256(p,n,digest);
 for(int k=0;k<32;k++)sprintf(hex+2*k,"%02x",digest[k]);
 if(strcmp(hex,spool_hash)||!strstr((const char*)p,selected))die("original spool/selected record");free(p);
 p=read_data(root,"evidence/recovery-routing.json",&n);
 if(!strstr((const char*)p,mask))die("original route mask");free(p);
 p=read_data(root,"acceptance.json",&n);
 if(!strstr((const char*)p,target))die("original commitment");free(p);
}
static void prepare(uint8_t *block){memset(block,0,64);memcpy(block,baseline,16);block[16]=0x80;block[63]=0x80;}
static unsigned digest_word(const uint8_t *digest,int k){return (unsigned(digest[4*k])<<24)|(unsigned(digest[4*k+1])<<16)|(unsigned(digest[4*k+2])<<8)|unsigned(digest[4*k+3]);}
static void plant(const SHA256_CTX &initial,int window,int shard,unsigned result[8]){
 uint8_t block[64],full[32];prepare(block);block[window]=uint8_t(shard);
 block[window+1]=1;block[window+2]=2;block[window+3]=3;block[window+4]=0;
 SHA256(block,16,full);SHA256_CTX ctx=initial;SHA256_Transform(&ctx,block);
 for(int k=0;k<8;k++){result[k]=digest_word(full,k);if(ctx.h[k]!=result[k])die("planted SHA256 block control");}
}
static bool hit(const SHA256_CTX &ctx,const unsigned target_words[8]){
 if(ctx.h[0]!=target_words[0])return false;
 for(int k=1;k<8;k++)if(ctx.h[k]!=target_words[k])return false;
 return true;
}
int main(int argc,char** argv){
 if(argc<4||argc>5)die("usage: fivebyte ROOT WINDOW_0_TO_11 SHARD_0_TO_255 [--smoke]");
 if(argc==5&&strcmp(argv[4],"--smoke"))die("unknown option");
 char *end=0;long w=strtol(argv[2],&end,10);if(!*argv[2]||*end||w<0||w>11)die("window");
 long shard=strtol(argv[3],&end,10);if(!*argv[3]||*end||shard<0||shard>255)die("shard");
 check_sources(argv[1]);SHA256_CTX initial;SHA256_Init(&initial);
 unsigned planted[8];plant(initial,int(w),int(shard),planted);
 printf("SOURCE_AND_PLANTED_SHA256_PASS window=%ld shard=%ld smoke=%d\n",w,shard,argc==5);fflush(stdout);
 unsigned long long original_hits=0,planted_hits=0;double start=omp_get_wtime();
 const int bound=(argc==5)?4:256;
 #pragma omp parallel for schedule(dynamic,1) reduction(+:original_hits,planted_hits)
 for(int x1=0;x1<bound;x1++){
  uint8_t block[64];prepare(block);block[w]=uint8_t(shard);block[w+1]=uint8_t(x1);
  SHA256_CTX ctx;
  for(int x2=0;x2<bound;x2++){block[w+2]=uint8_t(x2);
   for(int x3=0;x3<bound;x3++){block[w+3]=uint8_t(x3);
    for(int x4=0;x4<bound;x4++){block[w+4]=uint8_t(x4);
     ctx=initial;SHA256_Transform(&ctx,block);
     if(hit(ctx,wanted)){
      original_hits++;
      #pragma omp critical
      {printf("ORIGINAL_K04_MATCH window=%ld shard=%ld component=",w,shard);
       for(int i=0;i<16;i++)printf("%02X",block[i]);printf("\n");fflush(stdout);}
     }
     if(hit(ctx,planted))planted_hits++;
    }
   }
  }
 }
 const unsigned long long checks=(unsigned long long)bound*bound*bound*bound;
 printf("SHARD_COMPLETE window=%ld shard=%ld full_checks=%llu original_hits=%llu planted_hits=%llu elapsed=%.3f\n",w,shard,checks,original_hits,planted_hits,omp_get_wtime()-start);fflush(stdout);
 if(planted_hits!=1)die("planted candidate was not found exactly once");
 return original_hits?9:0;
}
