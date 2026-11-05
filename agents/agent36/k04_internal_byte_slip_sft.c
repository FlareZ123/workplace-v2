/* Agent36: original K04 recovered-fragment double-ended internal byte slip.
 * Complete source-pinned test. Delete one or two adjacent copied bytes from an
 * arbitrary internal position, then insert one or two arbitrary source bytes at
 * any potentially different internal position. Reconstruct a full 16-byte
 * physical coupon, XOR the untouched route mask, and SHA256 the 16 bytes.
 * This is NOT a local whole-byte replacement-radius search or a mere edge slip.
 * Build: cc -O3 -Wno-deprecated-declarations -fopenmp file.c -lcrypto -o slip
 * Run: OMP_NUM_THREADS=8 slip /path/to/original-resources
 */
#include <assert.h>
#include <inttypes.h>
#include <omp.h>
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint8_t copy[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
                              0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
                              0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint8_t target[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,
 0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,
 0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static const char *pinned[][2]={
 {"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
 {"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static void file_pin(const char*root,const char *name,const char *expected){
 char path[2048],actual[65];snprintf(path,sizeof path,"%s/%s",root,name);
 FILE*f=fopen(path,"rb");if(!f){perror(path);exit(2);}
 SHA256_CTX state;SHA256_Init(&state);unsigned char buf[32768],sha[32];size_t count;
 while((count=fread(buf,1,sizeof buf,f)))SHA256_Update(&state,buf,count);
 if(ferror(f)){perror("read");exit(2);}fclose(f);SHA256_Final(sha,&state);
 for(int i=0;i<32;i++)snprintf(actual+2*i,3,"%02x",sha[i]);
 if(strcmp(actual,expected)){fprintf(stderr,"PIN_FAILED %s\n",name);exit(2);}
}
/* The order of the remaining 16-k bytes is preserved. The offset of the
 * deleted contiguous block and the location of the newly inserted block
 * may be independent. The second loop is the full 256^k insertion domain. */
static void reconstruct(int k,int deletion,int insertion,uint32_t value,uint8_t output[16]){
 uint8_t residue[16],coupon[16];int rr=0;
 for(int i=0;i<16;i++)if(i<deletion||i>=deletion+k)residue[rr++]=copy[i];
 assert(rr==16-k);int pos=0;
 for(int i=0;i<16;i++){
   if(i>=insertion&&i<insertion+k)coupon[i]=(uint8_t)(value>>(8*(i-insertion)));
   else coupon[i]=residue[pos++];
 }
 assert(pos==16-k);
 for(int i=0;i<16;i++)output[i]=coupon[i]^mask[i];
}
int main(int argc,char **argv){
 if(argc!=2){fprintf(stderr,"provide resources path\n");return 2;}
 for(int i=0;i<3;i++)file_pin(argv[1],pinned[i][0],pinned[i][1]);
 uint8_t plant[32],control[16];
 reconstruct(2,0,10,0xD35Eu,control);SHA256(control,16,plant);
 for(int k=1;k<=2;k++){
   uint64_t checks=0,hits=0,synthetic=0;
   const int n=17-k;const uint32_t limit=1u<<(8*k);
   /* Synthetic event has two-byte shift; scan planted only on k=2. */
   #pragma omp parallel reduction(+:checks,hits,synthetic)
   {
      uint8_t value[32],coupon[16];
      #pragma omp for schedule(dynamic)
      for(int del=0;del<n;del++)for(int ins=0;ins<n;ins++){
         for(uint32_t v=0;v<limit;v++){
             reconstruct(k,del,ins,v,coupon);
             SHA256(coupon,16,value);checks++;
             if(memcmp(value,plant,32)==0)synthetic++;
             if(memcmp(value,target,32)==0){
               #pragma omp critical
               {fprintf(stderr,"ORIGINAL K04 HIT k=%d del=%d insert=%d fill=%u component=",k,del,ins,v);
                for(int b=0;b<16;b++)fprintf(stderr,"%02X",coupon[b]);
                fputc('\n',stderr);}
               hits++;
             }
         }
      }
   }
   uint64_t expected=(uint64_t)n*n*limit;
   assert(checks==expected);
   assert(synthetic==(k==1?0:1));
   printf("K04_INTERNAL_SLIP k=%d original_assignments=%" PRIu64 " planted_positive=%" PRIu64 " original_hits=%" PRIu64 "\n",k,checks,synthetic,hits);
   if(hits) return 10;
 }
 return 0;
}
