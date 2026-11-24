#define _POSIX_C_SOURCE 200809L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdatomic.h>
#include <omp.h>
static const unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static const int values[]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,127};
#define NV (sizeof(values)/sizeof(values[0]))
#define NP ((NV*(NV-1))/2)
static int pa[NP],pb[NP];
static atomic_int found=0;
static unsigned char hp[16],hc[16];
static uint64_t hit1=0,hit2=0;
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
static inline void savehit(const unsigned char*p,const unsigned char*c,uint64_t a,uint64_t b){
  if(atomic_exchange(&found,1)==0){
#pragma omp critical
    {memcpy(hp,p,16);memcpy(hc,c,16);hit1=a;hit2=b;}
  }
}
static inline void check(const unsigned char*p,uint64_t a,uint64_t b){
  unsigned char c[16],d[32];
  for(int i=0;i<16;i++)c[i]=p[i]^mask[i];
  SHA256(c,16,d);
  if(!memcmp(d,target,32))savehit(p,c,a,b);
}
static void finish(const char*mode,uint64_t n,double elapsed){
  printf("model=%s candidates=%llu elapsed_seconds=%.3f threads=%d hit=%s\n",mode,(unsigned long long)n,elapsed,omp_get_max_threads(),atomic_load(&found)?"YES":"NO");
  if(atomic_load(&found)){
    printf("hit_parameters=%llu,%llu\n",(unsigned long long)hit1,(unsigned long long)hit2);
    char fn[128];snprintf(fn,sizeof(fn),"/tmp/h17_k04_hit_%s.bin",mode);
    FILE*f=fopen(fn,"wb");if(f){fwrite(hp,1,16,f);fwrite(hc,1,16,f);fclose(f);printf("hit_material=%s\n",fn);}
  }
}
static int run_palette(int packed,int start,int end){
  int n=0;for(int i=0;i<NV;i++)for(int j=i+1;j<NV;j++){pa[n]=values[i];pb[n]=values[j];n++;}
  if(end>NP)end=NP;if(start<0||start>=end)return 2;
  uint64_t total=0;double t=now();
#pragma omp parallel for schedule(dynamic,1) reduction(+:total)
  for(int k=start;k<end;k++){
    for(uint32_t x=0;x<65536;x++){
      unsigned char p[16];
      for(int i=0;i<8;i++){
        int q=(x>>(2*i))&3;
        unsigned fore=(q&1)?pb[k]:pa[k],back=(q&2)?pb[k]:pa[k];
        if(packed){unsigned w=fore|(back<<7);p[2*i]=w&255;p[2*i+1]=(w>>8)&255;}
        else{p[2*i]=fore;p[2*i+1]=back;}
      }
      check(p,k,x);total++;
    }
  }
  finish(packed?"packed-colour-word":"two-colour-index-pairs",total,now()-t);return 0;
}
static int run_two_style(void){
  uint64_t total=0;double t=now();
#pragma omp parallel for schedule(dynamic,1) reduction(+:total)
  for(int a=0;a<256;a++){
    for(int b=a+1;b<256;b++){
      for(unsigned x=0;x<256;x++){
        unsigned char p[16];
        for(int i=0;i<8;i++){unsigned short v=((x>>i)&1)?b:a;p[2*i]=v&255;p[2*i+1]=v>>8;}
        check(p,((uint64_t)a<<32)|b,x);total++;
      }
    }
  }
  for(int a=0;a<256;a++){
    unsigned char p[16];for(int i=0;i<8;i++){p[2*i]=a;p[2*i+1]=0;}
    check(p,a,a);total++;
  }
  finish("two-style-ids-0-255",total,now()-t);return 0;
}
static int run_ixfe(uint64_t start,uint64_t end){
  if(start>=end||end>(1ULL<<32))return 2;
  uint64_t total=0;double t=now();
#pragma omp parallel for schedule(static) reduction(+:total)
  for(uint64_t x=start;x<end;x++){
    unsigned char p[16];
    for(int i=0;i<8;i++){unsigned char ix=(x>>(4*i))&15;p[2*i]=ix;p[2*i+1]=0;}
    check(p,x,0);total++;
  }
  finish("eight-LE-ixfe-0-15",total,now()-t);return 0;
}
int main(int argc,char**argv){
  if(argc<2){fprintf(stderr,"mode: palette|packed|two-style|ixfe [start end]\n");return 2;}
  if(!strcmp(argv[1],"palette"))return run_palette(0,argc>2?atoi(argv[2]):0,argc>3?atoi(argv[3]):NP);
  if(!strcmp(argv[1],"packed"))return run_palette(1,argc>2?atoi(argv[2]):0,argc>3?atoi(argv[3]):NP);
  if(!strcmp(argv[1],"two-style"))return run_two_style();
  if(!strcmp(argv[1],"ixfe"))return run_ixfe(argc>2?strtoull(argv[2],0,10):0,argc>3?strtoull(argv[3],0,10):(1ULL<<32));
  fprintf(stderr,"unknown mode\n");return 2;
}