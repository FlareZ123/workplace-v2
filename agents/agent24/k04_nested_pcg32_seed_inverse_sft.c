/* H-17 conditional nested binary seed B producer.
 * Model: B is 32-bit outputs of PCG-XSH-RR 64/32 with fixed standard odd
 * increment 1442695040888963407. Neither historical PCG nor the hypothetical
 * p951 CPython Random(bytes) outer layer is authenticated.
 * Withhold K04 copied ACK2, route mask, all targets and the verifier.
 * On a repo checkout, build against OpenSSL with OpenMP and execute using
 * resources/evidence/print/spool-reconstruction.log as the argument.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#define PCG_MULT 6364136223846793005ULL
#define PCG_INC 1442695040888963407ULL
#define LOW_BOUND (1U<<27)
static const unsigned char SPOOL_SHA[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,
 0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,
 0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static uint64_t ja[581],jc[581];

static uint32_t rotl32(uint32_t x,unsigned k){
 return (x<<k)|(x>>((-k)&31));
}
static uint32_t rotr32(uint32_t x,unsigned k){
 return (x>>k)|(x<<((-k)&31));
}
static uint32_t pcg_output(uint64_t s){
 return rotr32((uint32_t)(((s>>18)^s)>>27),(unsigned)(s>>59));
}
static uint64_t inverse_upper(uint32_t value,unsigned rotation){
 uint32_t shifted=rotl32(value,rotation);
 uint64_t upper=(uint64_t)rotation<<59;
 for(int bit=31;bit>=0;bit--){
  uint64_t b=(shifted>>bit)&1;
  if(bit+45<=63)b^=(upper>>(bit+45))&1;
  upper|=b<<(bit+27);
 }
 assert(pcg_output(upper)==value);
 return upper;
}
static void source_pin(const char *path){
 FILE*f=fopen(path,"rb");assert(f);
 assert(fseek(f,0,SEEK_END)==0);
 long len=ftell(f);assert(len>0);rewind(f);
 unsigned char *buf=malloc((size_t)len);assert(buf);
 assert(fread(buf,1,(size_t)len,f)==(size_t)len);
 fclose(f);
 unsigned char digest[32];SHA256(buf,(size_t)len,digest);free(buf);
 assert(memcmp(digest,SPOOL_SHA,32)==0);
}
static void jump_init(void){
 ja[0]=1;jc[0]=0;
 for(int i=1;i<=580;i++){
  ja[i]=ja[i-1]*PCG_MULT;
  jc[i]=jc[i-1]*PCG_MULT+PCG_INC;
 }
}
static int search(uint32_t first,uint32_t second,uint32_t w12a,uint32_t w12b,
                  uint32_t w579,uint32_t w580,uint32_t low_bound){
 uint64_t match12=0,match1=0,match_tail=0;
 #pragma omp parallel for schedule(dynamic,1) reduction(+:match12,match1,match_tail)
 for(int rotation=0;rotation<32;rotation++){
  uint64_t high=inverse_upper(first,(unsigned)rotation);
  for(uint32_t low=0;low<low_bound;low++){
   uint64_t state=high|low;
   uint32_t predicted12=pcg_output(state*ja[12]+jc[12]);
   if(predicted12!=w12a && predicted12!=w12b)continue;
   match12++;
   if(pcg_output(state*PCG_MULT+PCG_INC)!=second)continue;
   match1++;
   if(pcg_output(state*ja[579]+jc[579])==w579 &&
      pcg_output(state*ja[580]+jc[580])==w580)match_tail++;
   #pragma omp critical
   fprintf(stdout,"MATCH_TWO_WORDS state=%016" PRIX64 "\n",state);
  }
 }
 printf("FIRST=%08X STATES=%" PRIu64 " MATCH_WORD12=%" PRIu64
        " MATCH_WORD1=%" PRIu64 " MATCH_TAIL=%" PRIu64 "\n",
        first,(uint64_t)32*low_bound,match12,match1,match_tail);
 fflush(stdout);
 return match1!=0;
}
int main(int argc,char **argv){
 assert(argc==2);
 source_pin(argv[1]);
 jump_init();
 puts("PASS: Original printer SHA256. Only published conditional B-word constraints below.");
 /* Genuine seeded PCG32 full-state planted positive on exactly the same search. */
 uint64_t planted=0xAABBCCDD9800002AULL;
 uint32_t word12=pcg_output(planted*ja[12]+jc[12]);
 assert(search(pcg_output(planted),pcg_output(planted*PCG_MULT+PCG_INC),
               word12,0,pcg_output(planted*ja[579]+jc[579]),
               pcg_output(planted*ja[580]+jc[580]),100)==1);
 puts("PASS: planted full-state recovery, first/12/1/579/580.");
 int original_positives=0;
 for(int reverse_bytes=0;reverse_bytes<2;reverse_bytes++){
  for(int first_variant=0;first_variant<2;first_variant++){
   uint32_t w0=first_variant?0xE4589C88U:0x64589C88U;
   uint32_t w1=0x49342EC0U;
   uint32_t w12a=0x6425CF5BU,w12b=0xE425CF5BU;
   uint32_t w579=0x06EDCDADU,w580=0xFD6A4CF7U;
   if(reverse_bytes){
    w0=__builtin_bswap32(w0);w1=__builtin_bswap32(w1);
    w12a=__builtin_bswap32(w12a);w12b=__builtin_bswap32(w12b);
    w579=__builtin_bswap32(w579);w580=__builtin_bswap32(w580);
   }
   printf("SOURCE orientation=%s first_variant=%d\n",
           reverse_bytes?"byte-reversed":"native",first_variant);
   fflush(stdout);
   original_positives+=search(w0,w1,w12a,w12b,w579,w580,LOW_BOUND);
  }
 }
 assert(original_positives==0);
 puts("COMPLETE: 4 x 2^32 states. ZERO source-compatible nested PCG32 states.");
 return 0;
}
