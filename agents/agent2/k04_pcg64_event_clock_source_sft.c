/* H-17 K04: NumPy PCG64 SeedSequence(uint64) event-clock source gate.
 * C11 GCC/Clang + OpenSSL. Read-only. Usage: sft SPOOL 0420|0448 BEGIN_US COUNT
 * Use two 120m-width intervals centered at event Unix microsecond epochs.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <openssl/sha.h>
typedef unsigned __int128 U128;
static const U128 A=(((U128)UINT64_C(2549297995355413924))<<64)|UINT64_C(4865540595714422341);
static uint32_t hashmix(uint32_t x,uint32_t *c){x^=*c;*c*=UINT32_C(0x931e8875);x*=*c;return x^(x>>16);}
static uint32_t mix(uint32_t a,uint32_t b){uint32_t v=a*UINT32_C(0xca01f9dd)-b*UINT32_C(0x4973f715);return v^(v>>16);}
static void seed(uint64_t key,U128 *s,U128 *inc){
 uint32_t p[4],g[8],h=UINT32_C(0x43b0d7e5);
 p[0]=hashmix((uint32_t)key,&h);p[1]=hashmix((uint32_t)(key>>32),&h);
 p[2]=hashmix(0,&h);p[3]=hashmix(0,&h);
 for(int i=0;i<4;i++)for(int j=0;j<4;j++)if(i!=j)p[j]=mix(p[j],hashmix(p[i],&h));
 h=UINT32_C(0x8b51f9dd);
 for(int j=0;j<8;j++){uint32_t x=p[j%4]^h;h*=UINT32_C(0x58f38ded);x*=h;g[j]=x^(x>>16);}
 uint64_t w[4];for(int j=0;j<4;j++)w[j]=(uint64_t)g[2*j]|((uint64_t)g[2*j+1]<<32);
 U128 initial=((U128)w[0]<<64)|w[1],sequence=((U128)w[2]<<64)|w[3];
 *inc=(sequence<<1)|1;*s=*inc;*s+=initial;*s=*s*A+*inc;
}
static uint64_t next(U128 *s,U128 inc){*s=*s*A+inc;uint64_t hi=(uint64_t)(*s>>64),lo=(uint64_t)*s;uint32_t r=(uint32_t)(hi>>58);uint64_t x=hi^lo;return (x>>r)|(x<<((-r)&63));}
static int source_check(const char *path){
 FILE *f=fopen(path,"rb");if(!f){perror(path);return 0;}
 fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);if(n<=0){fclose(f);return 0;}
 unsigned char *a=malloc((size_t)n);if(!a){fclose(f);return 0;}
 size_t got=fread(a,1,(size_t)n,f);fclose(f);if(got!=(size_t)n){free(a);return 0;}
 unsigned char hash[32];SHA256(a,(size_t)n,hash);free(a);
 const unsigned char expected[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
 return !memcmp(hash,expected,32);
}
int main(int argc,char **argv){
 if(argc!=5){fprintf(stderr,"usage: test SOURCEPATH 0420|0448 BEGIN_US COUNT\n");return 2;}
 if(!source_check(argv[1])){fprintf(stderr,"source SHA mismatch\n");return 3;}
 U128 s,i;seed(UINT64_C(1311768467463790320),&s,&i);
 if(s!=(((U128)UINT64_C(0x9d84f0228dae1bb9)<<64)|UINT64_C(0x376b9ca7fa4c33c6))||
    i!=(((U128)UINT64_C(0xe4e230777823c5e3)<<64)|UINT64_C(0xb7a96858e6c63bc9))||
    next(&s,i)!=UINT64_C(0x34455331ba6e7cbe)||next(&s,i)!=UINT64_C(0x5f9d240f0ffe035d)){
    fprintf(stderr,"NumPy 64bit seed positive failed\n");return 4;
 }
 const unsigned char t0420[16]={0x43,0x24,0x75,0xf7,0x2a,0x62,0xdb,0x39,0xf3,0xd5,0x69,0x3e,0x2c,0x93,0x7f,0xa4};
 const unsigned char t0448[16]={0x23,0x4b,0xe1,0x86,0xe9,0x7e,0xe0,0x58,0x30,0x90,0x97,0x90,0xe3,0x36,0x10,0x9e};
 const unsigned char *target=(!strcmp(argv[2],"0420"))?t0420:(!strcmp(argv[2],"0448"))?t0448:NULL;
 if(!target){fprintf(stderr,"unknown event\n");return 2;}
 uint64_t be=0,le=0,be2=0,le2=0;
 for(int k=0;k<8;k++){be=(be<<8)|target[k];le=(le<<8)|target[7-k];be2=(be2<<8)|target[8+k];le2=(le2<<8)|target[15-k];}
 uint64_t start=strtoull(argv[3],NULL,10),count=strtoull(argv[4],NULL,10),xor64=0,half=0,full=0;
 uint64_t planted=start+1000;U128 pstate,pinc;seed(planted,&pstate,&pinc);
 for(int phase=0;phase<7;phase++)(void)next(&pstate,pinc);
 uint64_t px=next(&pstate,pinc),py=next(&pstate,pinc);int found=0;
 for(uint64_t k=planted-100;k<=planted+100;k++){
  U128 state,increment;seed(k,&state,&increment);
  for(int phase=0;phase<16;phase++){
   uint64_t x=next(&state,increment);
   if(x==px){U128 cp=state;uint64_t y=next(&cp,increment);if(y==py){if(k==planted&&phase==7)found++;else return 5;}}
  }
 }
 if(found!=1){fprintf(stderr,"synthetic full-coupon control failed\n");return 5;}
 for(uint64_t v=start;v<start+count;v++){
  seed(v,&s,&i);
  for(int phase=0;phase<16;phase++){
   uint64_t x=next(&s,i);if(phase==0)xor64^=x;
   if(x==be||x==le){half++;U128 cp=s;uint64_t y=next(&cp,i);
    if((x==be&&y==be2)||(x==le&&y==le2))full++;
    printf("CANDIDATE seed=%" PRIu64 " phase=%d x=%016" PRIx64 " y=%016" PRIx64 "\n",v,phase,x,y);
   }
  }
 }
 printf("RESULT event=%s begin=%" PRIu64 " count=%" PRIu64 " phases=16 half_hits=%" PRIu64 " full_hits=%" PRIu64 " planted=1 xor0=%016" PRIx64 "\n",argv[2],start,count,half,full,xor64);
 return 0;
}
