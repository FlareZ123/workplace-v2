/* H-17 K04: source-only full 32-bit affine Boolean bitplane coupon producer.
 * Each printer bit position has a fixed affine rule across 3 original
 * same-job packets, excluding the disputed selected ACK2 buffer.
 * Each of 8 positions has 16 rules => exact 16^8 128bit coupons.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint8_t donor[3][16]={
 {0xe1,0xe6,0x0d,0x5f,0x6b,0x6d,0xd2,0x22,0x5f,0xa6,0xd5,0xa2,0xa6,0x3a,0xd9,0x32},
 {0xcd,0x3e,0x4f,0x21,0x6a,0xdb,0x2f,0xb1,0x80,0xda,0x2a,0xa9,0x0b,0x33,0xf7,0xa4},
 {0x44,0xd5,0x3d,0xfc,0x29,0xd7,0x94,0x3a,0x95,0xd8,0x93,0x71,0xda,0x58,0xec,0x64}};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const unsigned original[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const char *raw[3]={"E1E60D5F6B6DD2225FA6D5A2A63AD932","CD3E4F216ADB2FB180DA2AA90B33F7A4","44D53DFC29D7943A95D89371DA58EC64"};
static void die(const char *s){fprintf(stderr,"FATAL: %s\n",s);exit(2);}
static void source(const char *root,const char *rel,const char *want,int spool){
 char path[1024],hex[65];if(snprintf(path,sizeof(path),"%s/%s",root,rel)>=(int)sizeof(path))die("path too long");
 FILE *f=fopen(path,"rb");if(!f)die("missing source");SHA256_CTX ctx;SHA256_Init(&ctx);
 uint8_t b[8192],hash[32];size_t n;
 while((n=fread(b,1,sizeof b,f))>0)SHA256_Update(&ctx,b,n);
 if(ferror(f))die("source read error");fclose(f);SHA256_Final(hash,&ctx);
 for(int i=0;i<32;i++)sprintf(hex+2*i,"%02x",hash[i]);
 if(strcmp(hex,want))die("source SHA256 changed");
 if(spool){
   char buf[32768];f=fopen(path,"rb");n=fread(buf,1,sizeof(buf)-1,f);fclose(f);buf[n]=0;
   for(int i=0;i<3;i++)if(!strstr(buf,raw[i]))die("same-job source packet missing");
 }
}
struct words{uint64_t lo,hi;};static struct words tab[8][16];
static void setup(void){for(int bit=0;bit<8;bit++)for(int f=0;f<16;f++){
 uint8_t buf[16]={0};
 for(int i=0;i<16;i++){
  unsigned a=(donor[0][i]>>bit)&1,b=(donor[1][i]>>bit)&1,c=(donor[2][i]>>bit)&1;
  unsigned x=(f&1?a:0)^(f&2?b:0)^(f&4?c:0)^((f>>3)&1);
  buf[i]=(uint8_t)(x<<bit);
 }
 memcpy(&tab[bit][f].lo,buf,8);memcpy(&tab[bit][f].hi,buf+8,8);
}}
static void component(uint32_t code,uint8_t out[16]){
 uint64_t lo=0,hi=0,ml,mh;memcpy(&ml,mask,8);memcpy(&mh,mask+8,8);
 for(int bit=0;bit<8;bit++){
  struct words x=tab[bit][(code>>(bit*4))&15];
  lo|=x.lo;hi|=x.hi;
 }
 lo^=ml;hi^=mh;memcpy(out,&lo,8);memcpy(out+8,&hi,8);
}
static unsigned word(const uint8_t *a,int i){
 return ((unsigned)a[4*i]<<24)|((unsigned)a[4*i+1]<<16)|((unsigned)a[4*i+2]<<8)|a[4*i+3];
}
int main(int argc,char **argv){
 if(argc<3||argc>4)die("usage: bitplane resources shard [--smoke]");
 int smoke=argc==4;if(smoke&&strcmp(argv[3],"--smoke"))die("bad mode");
 char *end=0;long sh=strtol(argv[2],&end,10);
 if(!*argv[2]||*end||sh<0||sh>=64)die("invalid shard");
 source(argv[1],"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",1);
 source(argv[1],"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",0);
 source(argv[1],"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",0);
 setup();SHA256_CTX initial;SHA256_Init(&initial);
 uint8_t blk[64],planted[16],digest[32];
 memset(blk,0,64);blk[16]=0x80;blk[63]=0x80;
 const uint32_t planted_code=0xc3a5e7f1U;
 component(planted_code,planted);SHA256(planted,16,digest);
 unsigned planted_digest[8];for(int i=0;i<8;i++)planted_digest[i]=word(digest,i);
 memcpy(blk,planted,16);SHA256_CTX state=initial;SHA256_Transform(&state,blk);
 for(int i=0;i<8;i++)if(state.h[i]!=planted_digest[i])die("planted genuine SHA256 mismatch");
 if(smoke){
  component(0,blk);state=initial;SHA256_Transform(&state,blk);SHA256(blk,16,digest);
  for(int i=0;i<8;i++)if(state.h[i]!=word(digest,i))die("zero-rule SHA256 mismatch");
  printf("ORIGINAL_SOURCE_AND_PLANTED_SHA256_POSITIVE_PASS shard=%ld\n",sh);return 0;
 }
 const uint64_t start=(uint64_t)sh<<26,stop=((uint64_t)sh+1)<<26;
 unsigned long long hits=0,plants=0;
 for(uint64_t idx=start;idx<stop;idx++){
  uint32_t code=(uint32_t)idx;component(code,blk);
  state=initial;SHA256_Transform(&state,blk);
  if(state.h[0]==original[0]){
   int same=1;for(int i=1;i<8;i++)same&=state.h[i]==original[i];
   if(same){
    hits++;printf("ORIGINAL_MATCH affine_rule=%08X component=",code);
    for(int j=0;j<16;j++)printf("%02X",blk[j]);puts("");fflush(stdout);
   }
  }
  if(state.h[0]==planted_digest[0]){
   int same=1;for(int i=1;i<8;i++)same&=state.h[i]==planted_digest[i];
   if(same)plants++;
  }
 }
 unsigned expected=(planted_code>>26)==(uint32_t)sh;
 printf("SHARD_COMPLETE shard=%ld start=%llu end=%llu complete_sha256=%llu original_matches=%llu planted_matches=%llu expected_planted=%u\n",
 sh,(unsigned long long)start,(unsigned long long)stop,(unsigned long long)(stop-start),hits,plants,expected);
 return hits?9:plants!=expected?3:0;
}
