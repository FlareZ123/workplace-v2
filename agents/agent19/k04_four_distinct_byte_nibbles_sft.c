/*
 * H-17 K04: exhaustive four independent erroneous hex glyphs, each in a
 * different physical coupon byte, 1820 byte quartets * 16 nibble planes *
 * 65536 replacement glyph tuples, partitioned by quartet index modulo 16.
 * The original selected spool copy, route and slot commitment are SHA-pinned.
 * Compile: cc -O3 -std=c11 -Wno-deprecated-declarations agents/agent19/k04_four_distinct_byte_nibbles_sft.c -lcrypto -o k04nibs
 * Run: k04nibs self-test, or k04nibs SHARD(0..15)
 */
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>
static const unsigned char COPIED[16]={
 0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5
};
static const unsigned char MASK[16]={
 0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C
};
static const unsigned char TARGET[32]={
 0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
 0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
static const char * const PINS[][2]={
 {"resources/evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
 {"resources/evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"resources/acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static int pin(void) {
 unsigned char buffer[16384],digest[32];
 for(size_t i=0;i<sizeof(PINS)/sizeof(PINS[0]);i++){
  FILE *f=fopen(PINS[i][0],"rb");if(!f){perror(PINS[i][0]);return 0;}
  SHA256_CTX ctx;SHA256_Init(&ctx);
  size_t n;while((n=fread(buffer,1,sizeof(buffer),f))>0)SHA256_Update(&ctx,buffer,n);
  int bad=ferror(f);fclose(f);if(bad)return 0;
  SHA256_Final(digest,&ctx);
  char hex[65];for(int j=0;j<32;j++)sprintf(hex+2*j,"%02x",digest[j]);
  if(strcmp(hex,PINS[i][1])){fprintf(stderr,"source drift: %s\n",PINS[i][0]);return 0;}
 }
 return 1;
}
static void four(int a,int b,int c,int d,unsigned plane,uint16_t glyphs,unsigned char out[16]){
 const int pos[4]={a,b,c,d};
 for(int i=0;i<16;i++)out[i]=COPIED[i]^MASK[i];
 for(int i=0;i<4;i++){
  const unsigned char digit=(unsigned char)((glyphs>>(12-4*i))&15);
  const int p=pos[i];
  if(plane & (1u<<i))out[p]=(out[p]&0x0f)|(digit<<4);
  else out[p]=(out[p]&0xf0)|digit;
 }
}
static int equal(const unsigned char candidate[16],const unsigned char expected[32]){
 unsigned char digest[32];SHA256(candidate,16,digest);return memcmp(digest,expected,32)==0;
}
static int search(int shard,const unsigned char target[32],int positive){
 unsigned char candidate[16];uint64_t checks=0;int found=0;int rank=0;
 for(int a=0;a<13;a++)for(int b=a+1;b<14;b++)
 for(int c=b+1;c<15;c++)for(int d=c+1;d<16;d++,rank++){
  if(rank%16!=shard)continue;
  for(unsigned plane=0;plane<16;plane++){
   for(unsigned glyphs=0;glyphs<65536;glyphs++){
    four(a,b,c,d,plane,(uint16_t)glyphs,candidate);
    checks++;
    if(equal(candidate,target)){
     printf("MATCH shard=%d quartet=%d,%d,%d,%d plane=%u glyphs=%04X component=",
       shard,a,b,c,d,plane,glyphs);
     for(int i=0;i<16;i++)printf("%02X",candidate[i]);
     puts("");fflush(stdout);
     found++;
    }
   }
  }
 }
 printf("DONE shard=%d quartets=%d complete=%" PRIu64 " original_or_control_hits=%d\n",
   shard,(1820+15-shard)/16,checks,found);
 fflush(stdout);
 if(rank!=1820){fprintf(stderr,"unexpected quartet rank %d\n",rank);return -1;}
 const uint64_t expected=(uint64_t)((1820+15-shard)/16)*16*65536;
 if(checks!=expected){fprintf(stderr,"missing candidate count\n");return -1;}
 if(positive)return found==1;
 return found==0;
}
int main(int argc,char **argv){
 if(!pin())return 2;
 unsigned char test[16],hash[32];
 /* Synthetic target changes one selected hex nibble in four separate bytes. */
 four(0,5,10,15,5,0xC0DE,test);
 SHA256(test,16,hash);
 if(argc==2 && strcmp(argv[1],"self-test")==0){
  unsigned char candidate[16];int hits=0;
  for(unsigned plane=0;plane<16;plane++)for(unsigned glyphs=0;glyphs<65536;glyphs++){
   four(0,5,10,15,plane,(uint16_t)glyphs,candidate);
   if(equal(candidate,hash))hits++;
  }
  printf("Synthetic four-distinct-byte nibble recovery: %s (%d exact hits)\n",
    hits==1?"PASS":"FAIL",hits);
  return hits==1?0:3;
 }
 if(argc!=2){fputs("Usage: k04nibs SHARD(0..15) | self-test\n",stderr);return 2;}
 char *end;long shard=strtol(argv[1],&end,10);
 if(*end||shard<0||shard>15)return 2;
 int result=search((int)shard,TARGET,0);
 return result==1?0:10;
}
