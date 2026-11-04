/* H-17: source-derived K02 telemetry donor, 16 distinct 33-bit K04 cosets.
 * C11 OpenSSL/OpenMP. args: data-file begin end threads [mode_count=16].
 * Data generated from 132 intact source packets by Agent1's Python SFT.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <omp.h>
#define DIM 33
#define BYTES 16
#define MODES 16
#define TOTAL (UINT64_C(1)<<DIM)
static const char *TARGET="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";
static uint8_t base[MODES][BYTES],delta[DIM][BYTES],want[32],control[MODES][32];
static uint8_t hexdigit(char ch) {
 if(ch>='0'&&ch<='9')return (uint8_t)(ch-'0');
 if(ch>='A'&&ch<='F')return (uint8_t)(10+ch-'A');
 fprintf(stderr,"illegal hex %02X\n",(unsigned char)ch);exit(4);
}
static void decode(const char *src,uint8_t *dst,size_t bytes){
 if(strlen(src)!=bytes*2){fprintf(stderr,"hex length %zu expected %zu\n",strlen(src),2*bytes);exit(4);}
 for(size_t i=0;i<bytes;i++)dst[i]=(uint8_t)((hexdigit(src[i*2])<<4)|hexdigit(src[i*2+1]));
}
static inline void xdelta(uint8_t out[BYTES],const uint8_t mask[BYTES]){
 for(int k=0;k<BYTES;k++)out[k]^=mask[k];
}
static void load(const char *filepath){
 FILE *f=fopen(filepath,"r");if(!f){perror(filepath);exit(4);}
 char t[65];
 for(int i=0;i<MODES;i++){
  if(fscanf(f,"%64s",t)!=1){fprintf(stderr,"missing base %d\n",i);exit(4);}
  decode(t,base[i],BYTES);
 }
 for(int j=0;j<DIM;j++){
  if(fscanf(f,"%64s",t)!=1){fprintf(stderr,"missing delta %d\n",j);exit(4);}
  decode(t,delta[j],BYTES);
  for(int k=8;k<16;k++)if(delta[j][k]){fprintf(stderr,"unexpected suffix delta %d\n",j);exit(4);}
 }
 if(fscanf(f,"%64s",t)==1){fprintf(stderr,"extra affine token\n");exit(4);}
 fclose(f);
 for(int i=0;i<MODES;i++)for(int k=i+1;k<MODES;k++){
  if(!memcmp(base[i]+8,base[k]+8,8)){fprintf(stderr,"overlapping suffix %d %d\n",i,k);exit(4);}
 }
}
int main(int argc,char**argv){
 if(argc!=5&&argc!=6){fprintf(stderr,"usage: data-file begin end threads [mode_count]\n");return 4;}
 uint64_t begin=strtoull(argv[2],NULL,10),end=strtoull(argv[3],NULL,10);
 int threads=atoi(argv[4]),modes=argc==6?atoi(argv[5]):MODES;
 if(begin>=end||end>TOTAL||threads<1||threads>32||modes<1||modes>MODES){fprintf(stderr,"invalid interval/threads/modes\n");return 4;}
 load(argv[1]);decode(TARGET,want,32);
 const uint64_t marker=UINT64_C(0x123456789),gray=marker^(marker>>1);
 for(int k=0;k<modes;k++){
  uint8_t planted[BYTES];memcpy(planted,base[k],BYTES);
  for(int j=0;j<DIM;j++)if(gray>>j&1)xdelta(planted,delta[j]);
  SHA256(planted,BYTES,control[k]);
  if(!memcmp(control[k],want,32)){fprintf(stderr,"synthetic equals original!\n");return 4;}
 }
 uint64_t original[MODES]={0},positive[MODES]={0};
 double start=omp_get_wtime();
 #pragma omp parallel num_threads(threads) reduction(+:original[:MODES],positive[:MODES])
 {
  int tid=omp_get_thread_num(),n=omp_get_num_threads();
  uint64_t left=begin+(end-begin)*(uint64_t)tid/(uint64_t)n;
  uint64_t right=begin+(end-begin)*(uint64_t)(tid+1)/(uint64_t)n;
  if(left<right){
   uint8_t current[MODES][BYTES],digest[32];
   uint64_t startgray=left^(left>>1);
   for(int k=0;k<modes;k++){
    memcpy(current[k],base[k],BYTES);
    for(int j=0;j<DIM;j++)if(startgray>>j&1)xdelta(current[k],delta[j]);
   }
   for(uint64_t i=left;i<right;i++){
    for(int k=0;k<modes;k++){
     SHA256(current[k],BYTES,digest);
     if(!memcmp(digest,want,32)){
      original[k]++;
      #pragma omp critical
      {
       printf("ORIGINAL_K04_MATCH mode=%d gray_index=%" PRIu64 " component=",k,i);
       for(int b=0;b<BYTES;b++)printf("%02X",current[k][b]);
       puts("");fflush(stdout);
      }
     }
     if(!memcmp(digest,control[k],32))positive[k]++;
    }
    if(i+1<right){
     int j=__builtin_ctzll(i+1);
     for(int k=0;k<modes;k++)xdelta(current[k],delta[j]);
    }
   }
  }
 }
 const uint64_t expect=begin<=marker&&marker<end?1:0;
 uint64_t failures=0;
 printf("DONE begin=%" PRIu64 " end=%" PRIu64 " states=%" PRIu64 " modes=%d complete_hashes=%" PRIu64 " expect_each=%" PRIu64 " sec=%.3f\n",begin,end,end-begin,modes,(end-begin)*(uint64_t)modes,expect,omp_get_wtime()-start);
 for(int k=0;k<modes;k++){
  printf("MODE %d original=%" PRIu64 " synthetic=%" PRIu64 "\n",k,original[k],positive[k]);
  if(positive[k]!=expect)failures|=1;
  if(original[k])failures|=2;
 }
 return failures?failures:0;
}
