/* H-17 original-source test: CPython Random integer seed in [0,2^24),
 * first intact printer four-word record located at an unknown offset up
 * to 2999 native 32-bit draws. Selected K04 row and commitments withheld.
 * Compiled: cc -O3 -fopenmp -o k04_seed24_offset3000_sft ...
 */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>

#define N 624
#define M 397
#define U32 UINT32_C(0xffffffff)
typedef struct { uint32_t mt[N]; int index; } rng;
static void init_genrand(rng *r,uint32_t seed){
 r->mt[0]=seed;
 for(int i=1;i<N;i++)r->mt[i]=1812433253U*(r->mt[i-1]^(r->mt[i-1]>>30))+i;
 r->index=N;
}
static void init_cpython(rng *r,uint32_t seed){
 init_genrand(r,19650218U);
 int i=1,j=0;
 for(int k=N;k;k--){
  r->mt[i]=(r->mt[i]^((r->mt[i-1]^(r->mt[i-1]>>30))*1664525U))+seed+j;
  i++;j++;if(i>=N){r->mt[0]=r->mt[N-1];i=1;}j=0;
 }
 for(int k=N-1;k;k--){
  r->mt[i]=(r->mt[i]^((r->mt[i-1]^(r->mt[i-1]>>30))*1566083941U))-i;
  i++;if(i>=N){r->mt[0]=r->mt[N-1];i=1;}
 }
 r->mt[0]=0x80000000U;r->index=N;
}
static void twist(rng *r){
 for(int i=0;i<N;i++){
  uint32_t y=(r->mt[i]&0x80000000U)|(r->mt[(i+1)%N]&0x7fffffffU);
  r->mt[i]=r->mt[(i+M)%N]^(y>>1)^((y&1U)?0x9908b0dfU:0);
 }
 r->index=0;
}
static uint32_t draw(rng *r){
 if(r->index>=N)twist(r);
 uint32_t y=r->mt[r->index++];
 y^=y>>11;y^=(y<<7)&0x9d2c5680U;y^=(y<<15)&0xefc60000U;y^=y>>18;
 return y;
}
static const uint32_t target[4]={0x43c5bbfbU,0x583f4856U,0x063fbb64U,0xa5184579U};
static const unsigned char spool_sha[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static void original_source(const char *path){
 FILE *f=fopen(path,"rb");if(!f){perror(path);exit(2);}
 assert(fseek(f,0,SEEK_END)==0);long size=ftell(f);assert(size>0);
 rewind(f);char *raw=malloc((size_t)size+1);assert(raw);
 assert(fread(raw,1,(size_t)size,f)==(size_t)size);fclose(f);raw[size]=0;
 unsigned char digest[32];SHA256((unsigned char*)raw,(size_t)size,digest);
 assert(memcmp(digest,spool_sha,32)==0 && "original spool hash mismatch");
 char *p=strstr(raw,"PAYLOAD=");assert(p);p+=8;
 for(int lane=0;lane<4;lane++){
  uint32_t w=0;
  for(int j=3;j>=0;j--){unsigned byte;assert(sscanf(p+2*(lane*4+j),"%2x",&byte)==1);w=(w<<8)|byte;}
  assert(target[lane]==w && "first intact source differs");
 }
 free(raw);
}

int main(int argc,char **argv){
 assert(argc==4);
 original_source(argv[3]);
 uint32_t begin=(uint32_t)strtoul(argv[1],NULL,0);
 uint32_t end=(uint32_t)strtoul(argv[2],NULL,0);
 assert(begin<=end&&end<=(1U<<24));
 rng r;
 init_cpython(&r,123456U);
 uint32_t known[]={0xce3d9460U,0xd804530bU,0xcb477398U,0x4a27a1e3U};
 for(int j=0;j<3000;j++){
  uint32_t x=draw(&r);
  if(j<4)assert(x==known[j]);
  if(j==623)assert(x==0xec698549U);
  if(j==624)assert(x==0xc221f242U);
  if(j==1250)assert(x==0xee139379U);
  if(j==2500)assert(x==0x906d4124U);
  if(j==2999)assert(x==0x378728efU);
 }
 puts("CPython seeded positive controls through 3,000 outputs: PASS");fflush(stdout);
 uint64_t prefix=0,matches=0, outputs=0;
 double t0=(double)clock()/CLOCKS_PER_SEC;
 #pragma omp parallel reduction(+:prefix,matches,outputs) private(r)
 {
  #pragma omp for schedule(dynamic,4096)
  for(uint32_t seed=begin;seed<end;seed++){
   init_cpython(&r,seed);
   uint32_t a=0,b=0,c=0,d=0;
   for(int k=0;k<3000;k++){
    a=b;b=c;c=d;d=draw(&r);
    if(k>=131 && a==target[0]){
     prefix++;
     if(b==target[1]&&c==target[2]&&d==target[3]){
      matches++;
      #pragma omp critical
      {printf("SOURCE_MATCH seed=%u startindex=%d\n",seed,k-3);fflush(stdout);}
     }
    }
   }
   outputs+=3000;
  }
 }
 printf("CPython uint24 seeds [%u,%u) 3000 native outputs per seed\n",begin,end);
 printf("SOURCE_PREFIX_OCCURRENCES=%"PRIu64" FULL_COUPON_MATCHES=%"PRIu64" OUTPUTS=%"PRIu64" cpu_sec=%.1f\n",prefix,matches,outputs,(double)clock()/CLOCKS_PER_SEC-t0);
 return 0;
}
