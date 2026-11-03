/* Original-source PCG XSH-RR 64/32 full-state inverse.
 * Requires C11, OpenSSL libcrypto and OpenMP. On a repository checkout:
 * cc -O3 -fopenmp -o pcg32_sft agents/agent27/k04_pcg32_fullstate_inverse_sft.c -lcrypto
 * OMP_NUM_THREADS=5 ./pcg32_sft resources/evidence/print/spool-reconstruction.log DA3E39CB94B95BDB
 * Repeat with increments 14057B7EF767814F and 1.
 * All file reads are source-only; K04 selected ACK, route mask, acceptance,
 * candidate and verifier are never read.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
static const uint64_t MULT=6364136223846793005ULL;
static const uint8_t source_sha[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static uint32_t rol32(uint32_t x,unsigned r){
 return (x<<(r&31))|(x>>((-r)&31));
}
static uint32_t pcg_out(uint64_t s){
 uint32_t x=(uint32_t)(((s>>18)^s)>>27);
 unsigned rot=(unsigned)(s>>59);
 return (x>>rot)|(x<<((-rot)&31));
}
/* With fixed rotation, all bits 27..58 follow by downward XOR inversion.
   Bits 59..63 are the rotation; only bits 0..26 remain to be enumerated.
   Exactly 32*2^27 == 2^32 states per first observed uint32 output. */
static uint64_t invert_upper(uint32_t output,unsigned rot){
 uint32_t x=rol32(output,rot);
 uint64_t upper=(uint64_t)rot<<59;
 for(int j=31;j>=0;j--){
  uint64_t bit=(x>>j)&1;
  if(j+45<=63)bit^=(upper>>(j+45))&1;
  upper|=bit<<(j+27);
 }
 assert(pcg_out(upper)==output);
 return upper;
}
static unsigned long long search(const uint32_t outputs[4],uint64_t inc,uint32_t maxlow,int need_positive){
 unsigned long long complete=0,visited=0;
 #pragma omp parallel for schedule(dynamic,1) reduction(+:complete,visited)
 for(int rot=0;rot<32;rot++){
  uint64_t upper=invert_upper(outputs[0],(unsigned)rot);
  for(uint32_t low=0;low<maxlow;low++){
   uint64_t state=upper|low;
   uint64_t next=state*MULT+inc;
   visited++;
   if(pcg_out(next)!=outputs[1])continue;
   uint64_t second=next*MULT+inc;
   uint64_t third=second*MULT+inc;
   if(pcg_out(second)!=outputs[2]||pcg_out(third)!=outputs[3])continue;
   complete++;
   #pragma omp critical
   {
    printf("FULL_FOURWORD_MATCH inc=%016llX state=%016llX\n",
      (unsigned long long)inc,(unsigned long long)state);
    fflush(stdout);
   }
  }
 }
 assert(visited==32ULL*maxlow);
 if(need_positive)assert(complete>0);
 printf("FULLSTATE_ENUMERATED=%llu MATCHES=%llu\n",visited,complete);
 return complete;
}
static void first_original_row(const char *path,uint32_t out[4],int big,int reverse){
 FILE *f=fopen(path,"rb");
 if(!f){perror(path);exit(2);}
 assert(fseek(f,0,SEEK_END)==0);
 long size=ftell(f);
 assert(size>0);
 rewind(f);
 char *raw=malloc((size_t)size+1);
 assert(raw);
 assert(fread(raw,1,(size_t)size,f)==(size_t)size);
 fclose(f);
 raw[size]=0;
 unsigned char digest[32];
 SHA256((unsigned char*)raw,(size_t)size,digest);
 assert(memcmp(digest,source_sha,32)==0);
 char *p=strstr(raw,"PAYLOAD=");
 assert(p);
 p+=8;
 unsigned char payload[16];
 for(int i=0;i<16;i++){
  unsigned v;
  assert(sscanf(p+2*i,"%2x",&v)==1);
  payload[i]=(unsigned char)v;
 }
 for(int i=0;i<4;i++){
  int src=reverse?3-i:i;
  uint32_t w=0;
  if(big)for(int j=0;j<4;j++)w=(w<<8)|payload[src*4+j];
  else for(int j=3;j>=0;j--)w=(w<<8)|payload[src*4+j];
  out[i]=w;
 }
 free(raw);
}
int main(int argc,char **argv){
 assert(argc==3);
 for(unsigned rot=0;rot<32;rot++)for(uint64_t j=0;j<4;j++){
  uint64_t state=((uint64_t)rot<<59)|0x052CA78D00000000ULL|
    (j?((1ULL<<27)-j):0);
  assert(invert_upper(pcg_out(state),rot)==
    (state&~((1ULL<<27)-1)));
 }
 puts("PASS 128 inversion controls spanning all 32 rotations");
 uint64_t inc=(uint64_t)strtoull(argv[2],NULL,16);
 assert((inc&1)==1);
 uint64_t planted=(0x853c49e6748fea9bULL&~((1ULL<<27)-1))|42ULL;
 uint32_t example[4];
 uint64_t state=planted;
 for(int i=0;i<4;i++){
  example[i]=pcg_out(state);
  state=state*MULT+inc;
 }
 assert((invert_upper(example[0],(unsigned)(planted>>59))|42ULL)==planted);
 assert(search(example,inc,100,1)==1);
 puts("PASS synthetic fourword original-state recovery");
 for(int big=0;big<2;big++)for(int reverse=0;reverse<2;reverse++){
  uint32_t observed[4];
  first_original_row(argv[1],observed,big,reverse);
  printf("SOURCE_ORIENTATION %s %s 4words=%08X,%08X,%08X,%08X\n",
   big?"BE":"LE",reverse?"REVERSE":"FORWARD",
   observed[0],observed[1],observed[2],observed[3]);
  fflush(stdout);
  assert(search(observed,inc,1U<<27,0)==0);
 }
 puts("PASS no original source row0 in tested PCG fixed-increment family");
 return 0;
}
