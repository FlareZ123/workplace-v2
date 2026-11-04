/* H17: source-pinned common modular word-counter copier channel, 64 disjoint shards.
 * Each candidate Q_i = COPY_i - (k + slope*i) modulo 2^32, slope=-1,0,+1.
 * Both little/big word serializers. Original K04 = Q xor original route mask.
 * Usage: executable shard [count-per-shard], shard 0..63, default 2^26.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <openssl/sha.h>

static const uint8_t COPIED[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t MASK[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const char *SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const char *TARGET_SHA="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const uint32_t PLANTED_K=0xa5301f69U;

static void die(const char *msg){fprintf(stderr,"FAIL %s\n",msg);exit(2);}
static uint32_t be32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint8_t nibble(char x){if(x>='0'&&x<='9')return (uint8_t)(x-'0');if(x>='a'&&x<='f')return (uint8_t)(x-'a'+10);if(x>='A'&&x<='F')return (uint8_t)(x-'A'+10);die("hex");return 0;}
static void digest_words(const char*hex,uint32_t out[8]){for(int i=0;i<8;i++){uint8_t b[4];for(int j=0;j<4;j++)b[j]=(uint8_t)((nibble(hex[8*i+2*j])<<4)|nibble(hex[8*i+2*j+1]));out[i]=be32(b);}}
static void sha_pinned_file(const char *path,const char *expected){
 FILE *f=fopen(path,"rb");if(!f)die(path);
 SHA256_CTX c;SHA256_Init(&c);uint8_t buf[4096];size_t n;
 while((n=fread(buf,1,sizeof(buf),f)))SHA256_Update(&c,buf,n);
 if(ferror(f))die("read file");fclose(f);
 uint8_t digest[32];uint32_t expected_words[8];SHA256_Final(digest,&c);digest_words(expected,expected_words);
 for(int i=0;i<8;i++)if(be32(digest+4*i)!=expected_words[i])die("source sha256 mismatch");
}
static void place_word(uint8_t out[16],unsigned i,uint32_t x,int little){
 for(unsigned b=0;b<4;b++)out[4*i+b]=(uint8_t)(x>>(8*(little?b:3-b)));
}
static uint32_t load_word(const uint8_t p[16],unsigned i,int little){
 const uint8_t *q=p+4*i;return little?((uint32_t)q[0]|((uint32_t)q[1]<<8)|((uint32_t)q[2]<<16)|((uint32_t)q[3]<<24)):be32(q);
}
static void component(uint8_t out[16], const uint32_t src[4],int little,int slope,uint32_t k){
 for(unsigned i=0;i<4;i++)place_word(out,i,src[i]-k-(uint32_t)(slope*(int)i),little);
 for(unsigned i=0;i<16;i++)out[i]^=MASK[i];
}
static void test_sha_block(const uint8_t out[16], const uint32_t expect[8],int should_match){
 uint8_t block[64]={0};memcpy(block,out,16);block[16]=0x80;block[63]=128;
 SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,block);
 uint8_t digest[32];SHA256(out,16,digest);
 for(int i=0;i<8;i++)if(ctx.h[i]!=be32(digest+4*i))die("single block hash computation mismatch");
 int same=1;for(int i=0;i<8;i++)same &= ctx.h[i]==expect[i];if(same!=should_match)die("single block target mismatch");
}
int main(int argc,char**argv){
 if(argc<2||argc>3)die("usage shard [count]");
 char *end=NULL;long sh=strtol(argv[1],&end,10);if(!end||*end||sh<0||sh>=64)die("shard must be 0..63");
 uint64_t count=UINT64_C(1)<<26;
 if(argc==3){end=NULL;count=strtoull(argv[2],&end,10);if(!end||*end||!count||count>(UINT64_C(1)<<26))die("bad count");}
 sha_pinned_file("resources/evidence/print/spool-reconstruction.log",SPOOL_SHA);
 sha_pinned_file("resources/evidence/recovery-routing.json",ROUTE_SHA);
 sha_pinned_file("resources/acceptance.json",ACCEPT_SHA);
 uint32_t target[8];digest_words(TARGET_SHA,target);
 SHA256_CTX init;SHA256_Init(&init);
 uint64_t start=(uint64_t)sh<<26, stop=start+count;
 uint64_t total=0,original_hits=0,planted_hits=0;
 uint8_t planted_component[16];uint32_t planted_digest[8];uint32_t src[4];
 for(int i=0;i<4;i++)src[i]=load_word(COPIED,i,1);
 component(planted_component,src,1,1,PLANTED_K);
 uint8_t planted_sha[32];SHA256(planted_component,16,planted_sha);
 for(int i=0;i<8;i++)planted_digest[i]=be32(planted_sha+i*4);
 test_sha_block(planted_component,planted_digest,1);
 for(int little=0;little<=1;little++){
  for(int i=0;i<4;i++)src[i]=load_word(COPIED,i,little);
  for(int slope=-1;slope<=1;slope++){
   uint8_t block[64]={0};block[16]=0x80;block[63]=128;
   uint64_t local_original_hits=0,local_planted_hits=0;
   for(uint64_t key=start;key<stop;key++){
    component(block,src,little,slope,(uint32_t)key);
    SHA256_CTX c=init;SHA256_Transform(&c,block);
    uint32_t diff=0;for(int i=0;i<8;i++)diff|=c.h[i]^target[i];
    if(!diff){fprintf(stderr,"ORIGINAL_MATCH endian=%s slope=%d key=%08" PRIx64 "\n",little?"little":"big",slope,key);local_original_hits++;}
    if(little==1&&slope==1){
     uint32_t d=0;for(int i=0;i<8;i++)d|=c.h[i]^planted_digest[i];
     if(!d){local_planted_hits++;fprintf(stdout,"PLANTED_MATCH key=%08" PRIx64 "\n",key);}
    }
   }
   total+=count;original_hits+=local_original_hits;planted_hits+=local_planted_hits;
   if(local_original_hits){fprintf(stderr,"FAIL original commitment hit, preserve candidate\n");return 3;}
   if(little&&slope==1&&local_planted_hits!=((start<=PLANTED_K&&PLANTED_K<stop)?1U:0U))die("planted search count");
   fprintf(stdout,"MODE shard=%ld endian=%s slope=%d checked=%" PRIu64 " original_hits=%" PRIu64 " synthetic_hits=%" PRIu64 "\n",sh,little?"little":"big",slope,count,local_original_hits,local_planted_hits);
  }
 }
 printf("DONE shard=%ld count=%" PRIu64 " total=%" PRIu64 " original_hits=%" PRIu64 " planted_hits=%" PRIu64 "\n",sh,count,total,original_hits,planted_hits);
 return 0;
}
