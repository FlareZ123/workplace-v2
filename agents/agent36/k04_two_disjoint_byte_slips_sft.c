/* Agent36: two independently lost copied bytes and two arbitrary bytes
 * inserted at independent output positions, source-order preserved.
 * 120^2 * 2^16 = 943,718,400 complete K04 original comparisons.
 * 14,745,600 adjacent/adjacent cases overlap the earlier k=2 contiguous
 * double-block test; 928,972,800 are new non-double-contiguous cases.
 * One generated complete planted target is checked through the same path.
 * Build: cc -O3 -fopenmp -Wno-deprecated-declarations -Wall -Wextra -Werror
 *        file.c -lcrypto -o binary
 * Run: OMP_NUM_THREADS=8 binary original_resources [limit_geometries]
 */
#include <assert.h>
#include <inttypes.h>
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint8_t COPY[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
  0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t MASK[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
  0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint32_t K04_SHA_WORDS[8]={
 0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
 0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const char *PIN[][2]={
 {"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
 {"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static int pairs[120][2];
static void init_pairs(void){int at=0;
 for(int i=0;i<16;i++)for(int j=i+1;j<16;j++){
    pairs[at][0]=i;pairs[at][1]=j;at++;
 }
 assert(at==120);
}
static void pin_file(const char*root,const char*relative,const char*sha){
 char p[2048];snprintf(p,sizeof p,"%s/%s",root,relative);
 FILE*f=fopen(p,"rb");if(!f){perror(p);exit(2);}
 SHA256_CTX state;SHA256_Init(&state);uint8_t buf[32768];size_t n;
 while((n=fread(buf,1,sizeof buf,f)))SHA256_Update(&state,buf,n);
 if(ferror(f)){perror("read source");exit(2);}fclose(f);
 uint8_t hash[32];SHA256_Final(hash,&state);char result[65];
 for(int i=0;i<32;i++)sprintf(result+2*i,"%02x",hash[i]);
 result[64]=0;
 if(strcmp(result,sha)){fprintf(stderr,"WRONG ORIGINAL SOURCE %s\n",relative);exit(2);}
}
static void reconstruct(int del0,int del1,int insert0,int insert1,
                        uint8_t byte0,uint8_t byte1,uint8_t out[16]){
 uint8_t remain[14];int r=0;
 for(int i=0;i<16;i++)if(i!=del0&&i!=del1)remain[r++]=COPY[i];
 assert(r==14);int at=0;
 for(int i=0;i<16;i++){
    uint8_t b=i==insert0?byte0:i==insert1?byte1:remain[at++];
    out[i]=b^MASK[i];
 }
 assert(at==14);
}
static uint32_t be32(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
int main(int argc,char**argv){
 if(argc!=2&&argc!=3){fprintf(stderr,"usage: SOURCE_ROOT [geometry_limit]\n");return 2;}
 const int geometries=argc==3?atoi(argv[2]):14400;
 if(geometries<1||geometries>14400){fprintf(stderr,"bad geometry limit\n");return 2;}
 for(int i=0;i<3;i++)pin_file(argv[1],PIN[i][0],PIN[i][1]);
 init_pairs();uint8_t planted[16],plant_sha[32];
 reconstruct(4,11,2,14,0xf2,0x0b,planted);SHA256(planted,16,plant_sha);
 uint32_t positive_words[8];for(int i=0;i<8;i++)positive_words[i]=be32(plant_sha+4*i);
 SHA256_CTX empty;SHA256_Init(&empty);
 uint64_t hits=0,controls=0,checks=0;
 const double begin=omp_get_wtime();
 #pragma omp parallel reduction(+:hits,controls,checks)
 {
  uint8_t block[64];SHA256_CTX state;
  #pragma omp for schedule(dynamic,8)
  for(int geom=0;geom<geometries;geom++){
    int dx=geom/120,ix=geom%120;
    int d0=pairs[dx][0],d1=pairs[dx][1];
    int i0=pairs[ix][0],i1=pairs[ix][1];
    memset(block,0,64);
    reconstruct(d0,d1,i0,i1,0,0,block);
    block[16]=0x80;block[63]=0x80;
    for(uint32_t value=0;value<65536;value++){
      block[i0]=(uint8_t)value^MASK[i0];
      block[i1]=(uint8_t)(value>>8)^MASK[i1];
      state=empty;SHA256_Transform(&state,block);
      checks++;
      if(state.h[0]==K04_SHA_WORDS[0]){
        int ok=1;for(int q=1;q<8;q++)ok&=state.h[q]==K04_SHA_WORDS[q];
        if(ok){hits++;
        #pragma omp critical
         {fprintf(stderr,"ORIGINAL_K04_HIT geom=%d d=%d,%d i=%d,%d fill=%04X component=",geom,d0,d1,i0,i1,value);
          for(int j=0;j<16;j++)fprintf(stderr,"%02X",block[j]);
          fputc('\n',stderr);}}
      }
      if(state.h[0]==positive_words[0]){
         int ok=1;for(int q=1;q<8;q++)ok&=state.h[q]==positive_words[q];
         if(ok)controls++;
      }
    }
  }
 }
 const uint64_t expected=(uint64_t)geometries*65536u;
 if(checks!=expected){fprintf(stderr,"COUNT MISMATCH expected=%"PRIu64" observed=%"PRIu64"\n",expected,checks);return 2;}
 const int plant_geometry=0; // Determined below from pair rank (4,11) and (2,14).
 int del_index=-1,insert_index=-1;
 for(int i=0;i<120;i++){
    if(pairs[i][0]==4&&pairs[i][1]==11)del_index=i;
    if(pairs[i][0]==2&&pairs[i][1]==14)insert_index=i;
 }
 assert(del_index>=0&&insert_index>=0);
 const int actual_plant_geometry=del_index*120+insert_index;
 const uint64_t expected_control=(actual_plant_geometry<geometries)?1:0;
 if(controls!=expected_control){fprintf(stderr,"PLANTED CONTROL MISMATCH observed=%"PRIu64" expected=%"PRIu64" planted_geom=%d\n",controls,expected_control,actual_plant_geometry);return 3;}
 printf("K04_TWO_DISJOINT_SLIPS geometry=%d full_checks=%"PRIu64" planted=%"PRIu64" original_hits=%"PRIu64" elapsed_s=%.3f\n",
     geometries,checks,controls,hits,omp_get_wtime()-begin);
 (void)plant_geometry;
 return hits?10:0;
}
