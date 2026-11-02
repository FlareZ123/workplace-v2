/* K04 hypothesis: coupon word = XOR subset of four 0417 retry payload words.
 * Independent subset per 32-bit lane, optional byte reversal and lane order. */
#include <stdio.h>
#include <string.h>
#include <openssl/sha.h>
static const unsigned char src[4][16]={
{0xE1,0xE6,0x0D,0x5F,0x6B,0x6D,0xD2,0x22,0x5F,0xA6,0xD5,0xA2,0xA6,0x3A,0xD9,0x32},
{0xCD,0x3E,0x4F,0x21,0x6A,0xDB,0x2F,0xB1,0x80,0xDA,0x2A,0xA9,0x0B,0x33,0xF7,0xA4},
{0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5},
{0x44,0xD5,0x3D,0xFC,0x29,0xD7,0x94,0x3A,0x95,0xD8,0x93,0x71,0xDA,0x58,0xEC,0x64}};
static const unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static unsigned char opt[4][30][4],orders[24][4];static int n;
static void permute(int k,int seen,unsigned char p[4]){
 if(k==4){memcpy(orders[n++],p,4);return;}
 for(int i=0;i<4;i++)if(!(seen&(1<<i))){p[k]=i;permute(k+1,seen|(1<<i),p);}
}
static void build(const int c[4],const unsigned char order[4],unsigned char out[16]){
 for(int w=0;w<4;w++)for(int b=0;b<4;b++)out[4*w+b]=opt[order[w]][c[order[w]]][b]^mask[4*w+b];
}
int main(void){
 for(int w=0;w<4;w++)for(int subset=1;subset<16;subset++){
  unsigned char v[4]={0};
  for(int i=0;i<4;i++)if(subset&(1<<i))for(int b=0;b<4;b++)v[b]^=src[i][4*w+b];
  for(int rev=0;rev<2;rev++)for(int b=0;b<4;b++)opt[w][2*(subset-1)+rev][b]=v[rev?3-b:b];
 }
 unsigned char p[4],out[16],hash[32],positive[32];permute(0,0,p);
 if(n!=24)return 2;
 const int planted[4]={7,18,4,29};build(planted,orders[13],out);SHA256(out,16,positive);
 unsigned long long tested=0,control=0,hits=0;
 for(int a=0;a<30;a++)for(int b=0;b<30;b++)for(int c=0;c<30;c++)for(int d=0;d<30;d++){
  int choice[4]={a,b,c,d};for(int k=0;k<24;k++){
   build(choice,orders[k],out);SHA256(out,16,hash);tested++;
   if(!memcmp(hash,positive,32))control++;
   if(!memcmp(hash,target,32)){hits++;printf("FOUND ");for(int j=0;j<16;j++)printf("%02X",out[j]);putchar('\n');}
  }
 }
 printf("tested=%llu synthetic_hits=%llu original_hits=%llu\n",tested,control,hits);
 if(tested!=19440000ULL||!control)return 2;
 return hits?0:1;
}
