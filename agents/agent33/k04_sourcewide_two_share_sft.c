/* Whole-evidence K04 two-share XOR exhaustive tester.
 * Receives 67470 sorted unique original 16-byte windows on stdin.
 * Checks direct and route-XOR stages against the unmodified original K04 SHA256.
 * Requires OpenSSL and OpenMP. A true planted two-source positive is mandatory.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif
#define N 67470
static const unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char target[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static const unsigned char carriers_digest[32]={0xe7,0x5d,0x45,0xa2,0xb9,0xe9,0x5e,0xd9,0x9c,0xe9,0x11,0xdc,0x9c,0x4d,0x19,0xff,0x04,0xcd,0x3b,0xbd,0x2d,0x5f,0xd7,0xef,0x54,0xe0,0x8d,0x2c,0x8f,0x94,0x8a,0xb5};
int main(int argc,char**argv){
 if(argc!=1){fprintf(stderr,"No arguments required: source blocks arrive on stdin\n");return 2;}
 (void)argv;
#ifdef _WIN32
 if(_setmode(_fileno(stdin),_O_BINARY)==-1){perror("binary mode");return 2;}
#endif
 unsigned char*data=malloc((size_t)N*16);
 if(!data){perror("allocation");return 2;}
 if(fread(data,16,N,stdin)!=N||fgetc(stdin)!=EOF){fprintf(stderr,"invalid source-carrier input length\n");free(data);return 2;}
 unsigned char digest[32];SHA256(data,(size_t)N*16,digest);
 if(memcmp(digest,carriers_digest,32)){fprintf(stderr,"source-carrier digest mismatch\n");free(data);return 2;}
 unsigned char planted[16],plant_hash[32];
 for(int k=0;k<16;k++)planted[k]=data[100*16+k]^data[57480*16+k]^mask[k];
 SHA256(planted,16,plant_hash);
 unsigned long long checks=0,hits=0,pos=0;
 double start=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,16) reduction(+:checks,hits,pos)
 for(int i=0;i<N;i++){
  unsigned char value[16],h[32];
  const unsigned char*a=data+(size_t)i*16;
  for(int j=i;j<N;j++){
   const unsigned char*b=data+(size_t)j*16;
   for(int k=0;k<16;k++)value[k]=a[k]^b[k];
   SHA256(value,16,h);checks++;
   if(memcmp(h,target,32)==0){
     #pragma omp critical
     {printf("ORIGINAL_DIRECT_MATCH i=%d j=%d\n",i,j);fflush(stdout);}
     hits++;
   }
   for(int k=0;k<16;k++)value[k]^=mask[k];
   SHA256(value,16,h);checks++;
   if(memcmp(h,target,32)==0){
     #pragma omp critical
     {printf("ORIGINAL_MASKED_MATCH i=%d j=%d\n",i,j);fflush(stdout);}
     hits++;
   }
   if(memcmp(h,plant_hash,32)==0)pos++;
  }
 }
 double elapsed=omp_get_wtime()-start;
 unsigned long long expected=(unsigned long long)N*(N+1);
 printf("CARRIERS=%d PAIRS=%llu COMPONENT_CHECKS=%llu EXPECTED=%llu ORIGINAL_HITS=%llu PLANT_HITS=%llu SECONDS=%.3f\n",N,expected/2,checks,expected,hits,pos,elapsed);
 free(data);
 return (checks!=expected||pos<1||hits!=0)?3:0;
}
