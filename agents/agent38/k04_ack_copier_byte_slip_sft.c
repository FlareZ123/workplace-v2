/* H-17 copier byte-origin displacement with edge erasure.
 * Full selected-ACK2 physical-coupon hypotheses; official K04 route mask.
 * Source, acceptance, and canonical candidate remain untouched.
 * Args: direction (0=missing prefix,1=missing suffix) shift(1..4) begin end threads.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/sha.h>
#include <omp.h>
static const char *COPY="A9A9DC5731A5E2AE879C47215C2559D5";
static const char *MASK="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *TARGET="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static void fromhex(const char*s,uint8_t*out,size_t n){
 for(size_t i=0;i<n;i++){unsigned v;if(sscanf(s+2*i,"%2x",&v)!=1)exit(4);out[i]=(uint8_t)v;}
}
static void unknown(uint8_t *out,const uint8_t*mask,int direction,int shift,uint64_t value){
 int pos=direction==0?0:16-shift;
 for(int j=0;j<shift;j++)out[pos+j]=mask[pos+j]^(uint8_t)(value>>(j*8));
}
int main(int argc,char**argv){
 if(argc!=6){fprintf(stderr,"usage: direction shift begin end threads\n");return 4;}
 int direction=atoi(argv[1]),shift=atoi(argv[2]),threads=atoi(argv[5]);
 uint64_t begin=strtoull(argv[3],NULL,10),end=strtoull(argv[4],NULL,10);
 if(direction<0||direction>1||shift<1||shift>4||threads<1||threads>32)return 4;
 uint64_t n=UINT64_C(1)<<(8*shift);if(begin>=end||end>n)return 4;
 uint8_t raw[16],mask[16],wanted[32],base[16],planted[16],control[32];
 fromhex(COPY,raw,16);fromhex(MASK,mask,16);fromhex(TARGET,wanted,32);
 if(direction==0){memmove(raw+shift,raw,16-shift);memset(raw,0,shift);}
 else{memmove(raw,raw+shift,16-shift);memset(raw+16-shift,0,shift);}
 for(int i=0;i<16;i++)base[i]=raw[i]^mask[i];
 uint64_t marker=UINT64_C(0xD3E19F20)&(n-1);
 memcpy(planted,base,16);unknown(planted,mask,direction,shift,marker);SHA256(planted,16,control);
 uint64_t matches=0,positives=0;double t=omp_get_wtime();
 #pragma omp parallel num_threads(threads) reduction(+:matches,positives)
 {
  uint8_t candidate[16],digest[32];memcpy(candidate,base,16);
  #pragma omp for schedule(static)
  for(uint64_t v=begin;v<end;v++){
   unknown(candidate,mask,direction,shift,v);SHA256(candidate,16,digest);
   if(memcmp(digest,wanted,32)==0){
    #pragma omp critical
    {printf("ORIGINAL_HIT direction=%d shift=%d edge=%08" PRIX64 " component=",direction,shift,v);
     for(int i=0;i<16;i++)printf("%02X",candidate[i]);puts("");fflush(stdout);}
    matches++;
   }
   if(memcmp(digest,control,32)==0)positives++;
  }
 }
 uint64_t expected=begin<=marker&&marker<end?1:0;
 printf("DONE dir=%d shift=%d begin=%" PRIu64 " end=%" PRIu64 " tested=%" PRIu64 " original=%" PRIu64 " synthetic=%" PRIu64 " expected=%" PRIu64 " seconds=%.3f\n",
        direction,shift,begin,end,end-begin,matches,positives,expected,omp_get_wtime()-t);
 return positives!=expected?3:matches?2:0;
}
