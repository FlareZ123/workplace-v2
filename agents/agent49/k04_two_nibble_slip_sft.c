/* Agent49: complete two-deletion/two-insertion hexadecimal nibble slip family.
 * Each preserved copied hex nibble remains in order. The source-selected ACK2
 * and XOR mask are exact from original spool/routing, pinned by report.
 * Build: cc -O3 -o k04_double_nibble_slip k04_double_nibble_slip.c -lcrypto
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <openssl/sha.h>

static const char hex[]="0123456789ABCDEF";
static const char source[]="A9A9DC5731A5E2AE879C47215C2559D5";
static const unsigned char mask[16]={
  0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C
};
static const unsigned char target[32]={
  0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
  0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
static int val(char c){if(c>='0'&&c<='9')return c-'0';return c-'A'+10;}
static void digest(const char *c,unsigned char out[32]){
  unsigned char x[16];
  for(int n=0;n<16;n++)x[n]=(unsigned char)(((val(c[2*n])<<4)|val(c[2*n+1]))^mask[n]);
  SHA256(x,16,out);
}
int main(void){
  assert(strlen(source)==32);
  char control[33],removed[31],candidate[33];
  int q=0;
  for(int i=0;i<32;i++)if(i!=3&&i!=17)removed[q++]=source[i];
  q=0;
  for(int i=0;i<32;i++){
    if(i==4)control[i]='D';
    else if(i==26)control[i]='7';
    else control[i]=removed[q++];
  }
  assert(q==30); control[32]=0;
  unsigned char positive[32],got[32];digest(control,positive);
  assert(memcmp(positive,target,32)!=0);
  unsigned long long checks=0,positives=0,hits=0;
  for(int d1=0;d1<31;d1++)for(int d2=d1+1;d2<32;d2++){
    q=0;
    for(int i=0;i<32;i++)if(i!=d1&&i!=d2)removed[q++]=source[i];
    assert(q==30);
    for(int p1=0;p1<31;p1++)for(int p2=p1+1;p2<32;p2++){
      q=0;
      for(int i=0;i<32;i++)if(i==p1||i==p2)candidate[i]='0';else candidate[i]=removed[q++];
      assert(q==30); candidate[32]=0;
      for(int a=0;a<16;a++){
        candidate[p1]=hex[a];
        for(int b=0;b<16;b++){
          candidate[p2]=hex[b];
          digest(candidate,got); checks++;
          if(!memcmp(got,positive,32)){assert(!strcmp(candidate,control));positives++;}
          if(!memcmp(got,target,32)){
            hits++;
            fprintf(stdout,"ORIGINAL_K04_HIT %s remove=%d,%d insert=%d,%d nib=%X,%X\n",candidate,d1,d2,p1,p2,a,b);
          }
        }
      }
    }
  }
  assert(checks==62980096ULL);
  assert(positives>0);
  printf("double-slip assignments=%llu control_matches=%llu original_hits=%llu\n",checks,positives,hits);
  return hits?1:0;
}
