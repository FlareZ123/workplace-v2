/* Original spool first whole-packet test of the 32bit MSVCRT rand LCG.
 * Enumerates every 32bit internal state after first observed output under
 * two 8bit projections. A state can correspond to any unknown prior phase.
 * C11/OpenMP. Input historical spool is read-only, source SHA pinned.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static const uint8_t original[16]={0xfb,0xbb,0xc5,0x43,0x56,0x48,0x3f,0x58,0x64,0xbb,0x3f,0x06,0x79,0x45,0x18,0xa5};
static const uint8_t pin[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static inline uint32_t advance(uint32_t x){return (uint32_t)(x*214013u+2531011u);}
static inline uint8_t output(uint32_t x,unsigned mode){return (uint8_t)(mode?(x>>23):(x>>16));}
static int source(const char *path){
 FILE *f=fopen(path,"rb");if(!f){perror(path);return 0;}SHA256_CTX c;SHA256_Init(&c);
 char b[8192];char start[30000]={0};size_t n,total=0;
 while((n=fread(b,1,sizeof(b),f))){SHA256_Update(&c,b,n);if(total+n>=sizeof(start)){fclose(f);return 0;}memcpy(start+total,b,n);total+=n;}
 int bad=ferror(f);fclose(f);uint8_t dig[32];SHA256_Final(dig,&c);
 return !bad&&!memcmp(dig,pin,32)&&strstr(start,"JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=FBBBC54356483F5864BB3F06794518A5");
}
int main(int argc,char **argv){
 if(argc!=2||!source(argv[1])){fprintf(stderr,"Original source failed\n");return 2;}
 uint64_t matches[2]={0,0};uint64_t planted[2]={0,0};
 for(unsigned mode=0;mode<2;mode++){
  const uint32_t synthetic_first=0x9c582f13u;
  uint8_t planted_stream[16];uint32_t y=synthetic_first;
  for(unsigned i=0;i<16;i++){planted_stream[i]=output(y,mode);y=advance(y);}
  unsigned long long m=0,p=0;
  #pragma omp parallel for reduction(+:m,p) schedule(static)
  for(uint32_t pos=0;pos<16777216u;pos++){
   uint32_t s=mode?(((pos>>23)<<31)|((uint32_t)original[0]<<23)|(pos&0x7fffffu)):(((pos>>16)<<24)|((uint32_t)original[0]<<16)|(pos&0xffffu));
   uint32_t cur=s;unsigned i=1;
   for(;i<16;i++){cur=advance(cur);if(output(cur,mode)!=original[i])break;}
   if(i==16){m++;printf("ORIGINAL_SOURCE_MATCH mode=%u firststate=%08X\n",mode,s);}
   /* Independent planted stream has a different first byte: recover it by its
    * own complete source-first constrained 2^24 state parameterization. */
   uint32_t q=mode?(((pos>>23)<<31)|((uint32_t)planted_stream[0]<<23)|(pos&0x7fffffu)):(((pos>>16)<<24)|((uint32_t)planted_stream[0]<<16)|(pos&0xffffu));
   cur=q;for(i=1;i<16;i++){cur=advance(cur);if(output(cur,mode)!=planted_stream[i])break;}
   if(i==16)p++;
  }
  matches[mode]=m;planted[mode]=p;
 }
 printf("COMPLETE_32BIT_STATES_PER_MODE=4294967296 low8_matches=%llu high8_matches=%llu planted_low=%llu planted_high=%llu\n",(unsigned long long)matches[0],(unsigned long long)matches[1],(unsigned long long)planted[0],(unsigned long long)planted[1]);
 return matches[0]||matches[1]||planted[0]!=256||planted[1]!=2?3:0;
}
