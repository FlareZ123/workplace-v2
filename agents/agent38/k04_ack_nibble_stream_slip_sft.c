/* H-17 historical ACK2 copied hex-text stream slip, odd 3/5/7 nibbles.
   Original official K04 SHA256 commitment; read-only source pinned by workflow.
   C11, OpenSSL, OpenMP. argv dir shift begin end threads.
*/
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/sha.h>
#include <omp.h>
static const char *COPIED="A9A9DC5731A5E2AE879C47215C2559D5";
static const char *MASK="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *TARGET="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";
static unsigned nib(char x){return x<='9'?x-'0':x-'A'+10;}
static void setnib(unsigned char *out,int idx,unsigned val){
 unsigned char *p=&out[idx/2];
 if(idx%2)*p=(unsigned char)((*p&0xf0)|val);
 else *p=(unsigned char)((*p&0x0f)|(val<<4));
}
static void unpack(const char *s,unsigned char *out,size_t n){
 for(size_t i=0;i<n;i++)out[i]=(unsigned char)(16*nib(s[i*2])+nib(s[i*2+1]));
}
static void unknown(unsigned char*out,const unsigned char *mask,int direction,int shift,uint64_t value){
 const int start=direction?32-shift:0;
 for(int j=0;j<shift;j++)setnib(out,start+j,(unsigned)(value>>(4*j))&15);
 for(int k=0;k<16;k++)out[k]^=mask[k];
}
int main(int argc,char**argv){
 if(argc!=6){fprintf(stderr,"usage: dir shift begin end threads\n");return 4;}
 const int direction=atoi(argv[1]),shift=atoi(argv[2]),threads=atoi(argv[5]);
 const uint64_t begin=strtoull(argv[3],NULL,10),end=strtoull(argv[4],NULL,10),n=UINT64_C(1)<<(4*shift);
 if(direction<0||direction>1||(shift!=3&&shift!=5&&shift!=7)||threads<1||threads>32||begin>=end||end>n)return 4;
 unsigned char raw[16],mask[16],wanted[32],base[16],control[32];
 unpack(COPIED,raw,16);unpack(MASK,mask,16);unpack(TARGET,wanted,32);
 memset(base,0,sizeof(base));
 for(int j=0;j<32-shift;j++){
  const int src=direction?j+shift:j;
  const int dst=direction?j:j+shift;
  setnib(base,dst,nib(COPIED[src]));
 }
 const uint64_t marker=UINT64_C(0xD3E19F20)&(n-1);
 unsigned char planted[16];memcpy(planted,base,16);unknown(planted,mask,direction,shift,marker);
 SHA256(planted,16,control);
 uint64_t hits=0,positives=0;const double t=omp_get_wtime();
 #pragma omp parallel num_threads(threads) reduction(+:hits,positives)
 {
  unsigned char candidate[16],digest[32];
  #pragma omp for schedule(static)
  for(uint64_t v=begin;v<end;v++){
   memcpy(candidate,base,16);
   unknown(candidate,mask,direction,shift,v);
   SHA256(candidate,16,digest);
   if(memcmp(digest,wanted,32)==0){
     #pragma omp critical
     {printf("ORIGINAL_MATCH dir=%d shift=%d value=%08" PRIX64 " component=",direction,shift,v);
      for(int k=0;k<16;k++)printf("%02X",candidate[k]);puts("");fflush(stdout);}
     hits++;
   }
   if(memcmp(digest,control,32)==0)positives++;
  }
 }
 const uint64_t expect=begin<=marker&&marker<end?1:0;
 printf("DONE dir=%d shift_nibbles=%d begin=%" PRIu64 " end=%" PRIu64 " tested=%" PRIu64 " original=%" PRIu64 " planted=%" PRIu64 " expected=%" PRIu64 " seconds=%.3f\n",
 direction,shift,begin,end,end-begin,hits,positives,expect,omp_get_wtime()-t);
 return positives!=expect?3:hits?2:0;
}
