/* H17 K04 speculative 8-wire permutation and per-byte inversion.
   Run C11/OpenSSL: cc -O3 -std=c11 agents/agent9/k04_bitwire_affine_sft.c -lcrypto -o k04_wire && ./k04_wire
   The selected ACK is a copied, unauthenticated physical payload. Model tests
   uniformly permuting all 8 bits within each byte, then XORing one constant
   inversion mask. Stages: printer payload, route mask, both. When both stages
   share the same XOR byte, the inversion cancels, so only b=0 is needed.
   Source printer spool SHA256:
   7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
*/
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>
static const uint8_t payload[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const uint8_t mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint8_t target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static int nextperm(int *p){
 int k=6;while(k>=0&&p[k]>=p[k+1])--k;
 if(k<0)return 0;
 int j=7;while(p[j]<=p[k])--j;
 int t=p[k];p[k]=p[j];p[j]=t;
 for(int a=k+1,b=7;a<b;++a,--b){t=p[a];p[a]=p[b];p[b]=t;}
 return 1;
}
static uint8_t map8(int x,const int *perm){
 int y=0;for(int i=0;i<8;i++)y|=((x>>i)&1)<<perm[i];
 return (uint8_t)y;
}
int main(void){
 int perm[8]={0,1,2,3,4,5,6,7};
 const int planted[8]={4,0,6,1,3,7,2,5};
 const int planted_b=0x53;
 uint8_t synthetic[3][32],candidate[16],sha[32];
 unsigned long long counts[3]={0},hits[3]={0},positive[3]={0};
 for(int stage=0;stage<3;stage++){
   for(int i=0;i<16;i++){
     uint8_t p=payload[i],m=mask[i];
     if(stage==0||stage==2)p=map8(p,planted)^(stage==2?0:planted_b);
     if(stage==1||stage==2)m=map8(m,planted)^(stage==2?0:planted_b);
     candidate[i]=p^m;
   }
   SHA256(candidate,16,synthetic[stage]);
 }
 int perms=0;
 do{
   uint8_t tp[16],tm[16];
   for(int i=0;i<16;i++){tp[i]=map8(payload[i],perm);tm[i]=map8(mask[i],perm);}
   for(int stage=0;stage<3;stage++){
     int limit=(stage==2)?1:256;
     for(int b=0;b<limit;b++){
       for(int i=0;i<16;i++){
         uint8_t p=(stage==0||stage==2)?(tp[i]^b):payload[i];
         uint8_t m=(stage==1||stage==2)?(tm[i]^b):mask[i];
         candidate[i]=p^m;
       }
       SHA256(candidate,16,sha);
       counts[stage]++;
       if(memcmp(sha,target,32)==0){
         hits[stage]++;
         printf("ORIGINAL HIT stage %d shift %d component ",stage,b);
         for(int i=0;i<16;i++)printf("%02X",candidate[i]);puts("");
       }
       if(memcmp(sha,synthetic[stage],32)==0)positive[stage]++;
     }
   }
   perms++;
 }while(nextperm(perm));
 for(int stage=0;stage<3;stage++)printf("stage=%d tried=%llu original_matches=%llu synthetic_hits=%llu\n",stage,counts[stage],hits[stage],positive[stage]);
 if(perms!=40320||counts[0]!=10321920||counts[1]!=10321920||counts[2]!=40320)return 2;
 if(positive[0]!=1||positive[1]!=1||positive[2]!=1)return 3;
 printf("FINISHED permutations=%d matches=%llu\n",perms,hits[0]+hits[1]+hits[2]);
 return 0;
}
