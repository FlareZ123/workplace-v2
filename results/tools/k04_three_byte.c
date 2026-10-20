/* Recover a 16-byte key with up to three arbitrary byte substitutions.
 * This targets only H17 K04 and splits the 560 position-triples into shards.
 * Build: gcc -O3 k04_three_byte.c -lcrypto -o k04_three_byte
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static uint8_t x[16]={0x2C,0xFF,0x14,0x9C,0x50,0xE5,0x45,0x57,0x22,0x8E,0x7D,0xE6,0x0B,0x3E,0xB7,0xC9};
static const uint8_t target[32]={
0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: k04_three_byte shard total_shards\n");return 2;}
 const int shard=atoi(argv[1]),total=atoi(argv[2]);
 if(total<1||shard<0||shard>=total){fputs("invalid shard\n",stderr);return 2;}
 uint8_t digest[32];int triple_idx=0,processed=0;
 for(int i=0;i<14;i++)for(int j=i+1;j<15;j++)for(int k=j+1;k<16;k++){
  if((triple_idx++ % total)!=shard)continue;
  uint8_t old_i=x[i],old_j=x[j],old_k=x[k];
  for(uint32_t v=0;v<16777216u;v++){
   x[i]=(uint8_t)v;x[j]=(uint8_t)(v>>8);x[k]=(uint8_t)(v>>16);
   SHA256(x,16,digest);
   if(!memcmp(digest,target,32)){
    printf("FOUND positions=%d,%d,%d candidate=",i,j,k);
    for(int q=0;q<16;q++)printf("%02X",x[q]);
    puts("");return 0;
   }
  }
  x[i]=old_i;x[j]=old_j;x[k]=old_k;
  processed++;
 }
 printf("EXHAUSTED shard=%d total=%d triples=%d\n",shard,total,processed);
 return 0;
}
