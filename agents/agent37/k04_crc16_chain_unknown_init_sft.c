/* H-17 K04: exact original AX-7782 running CRC16 checkpoint bridge with
 * any 16bit initial CRC state, yielding all 2,684,354,560 distinct coupons.
 * Rebuilds/deduplicates 14byte coupon suffixes from original transfer log.
 * C11 OpenSSL, optional OpenMP: cc -O3 -fopenmp -Wno-deprecated-declarations
 * source.c -lcrypto -o k04crc; k04crc original-transfer-audit.jsonl
 * Original historical files, commitment and verifier are read-only.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static const uint8_t K07[16]={0x89,0x47,0xce,0xdc,0xb9,0xcc,0x73,0xba,0xb7,0xe8,0x7b,0xe6,0x33,0x02,0xc5,0xc9};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint32_t target[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const uint8_t PIN[32]={0x32,0x97,0x0a,0xd4,0x43,0x1a,0x9d,0x61,0x0c,0xc1,0x2d,0xcc,0xa2,0x81,0x3f,0x39,0xdd,0x8f,0xd2,0xe3,0x96,0xf9,0xe7,0x48,0xdc,0x94,0xb5,0x93,0x2c,0xb6,0x9a,0xdf};
static const uint8_t SUFFIX_PIN[32]={0x24,0x3c,0xdd,0x4d,0x39,0xd0,0x4f,0xf3,0xd1,0x41,0x19,0x20,0x46,0x92,0xf5,0x43,0xb5,0x3f,0xbf,0x05,0x87,0x12,0x9a,0x3b,0xb2,0xb5,0x32,0x2b,0x36,0x47,0x8c,0x2d};
static const uint16_t POLY[8]={0x1021,0x1021,0x8408,0xa001,0xa001,0xa6bc,0x8408,0xa001};
static const uint16_t INIT[8]={0,65535,65535,0,65535,0,0,65535};
static const uint16_t XOROUT[8]={0,0,65535,0,0,65535,0,0};
static const uint8_t REFLECT[8]={0,0,1,1,1,1,1,1};
typedef struct {uint8_t b[14];} Suffix;
_Static_assert(sizeof(Suffix)==14,"Suffix layout must be contiguous");
static uint16_t crc2(uint16_t seed,uint16_t data,unsigned mode){
 uint16_t c=seed;
 for(unsigned j=0;j<2;j++){
  uint8_t x=(uint8_t)(j?data:data>>8);
  if(REFLECT[mode]){c^=x;for(int k=0;k<8;k++)c=(uint16_t)((c>>1)^((c&1)?POLY[mode]:0));}
  else{c^=(uint16_t)x<<8;for(int k=0;k<8;k++)c=(uint16_t)((c<<1)^((c&32768)?POLY[mode]:0));}
 }
 return c;
}
static int compare_suffix(const void *a,const void *b){return memcmp(a,b,14);}
static int source(const char *path){
 FILE *f=fopen(path,"rb");if(!f){perror(path);return 0;}
 uint8_t buf[32768],digest[32];size_t len=fread(buf,1,sizeof(buf),f);
 int fail=ferror(f)||!feof(f);fclose(f);if(fail)return 0;
 SHA256(buf,len,digest);if(memcmp(digest,PIN,32))return 0;
 uint16_t values[8]={0};int attempts[8]={0};char *str=malloc(len+1);
 if(!str)abort();memcpy(str,buf,len);str[len]=0;
 for(char *line=strtok(str,"\n");line;line=strtok(NULL,"\n")){
  if(!strstr(line,"\"kind\": \"CHUNK\"")||!strstr(line,"\"transfer\": \"AX-7782\""))continue;
  char *sp=strstr(line,"\"seq\""),*ap=strstr(line,"\"attempt\""),*cp=strstr(line,"\"checkpoint\"");
  if(!sp||!ap||!cp){free(str);return 0;}
  int seq=atoi(strchr(sp,':')+1),attempt=atoi(strchr(ap,':')+1);
  if(seq<0||seq>7||attempt<=0){free(str);return 0;}
  if(attempt<=attempts[seq])continue;
  cp=strchr(cp,':')+1;while(*cp&&*cp!='\"')cp++;if(!*cp){free(str);return 0;}
  unsigned v=0;if(sscanf(cp+1,"%4x",&v)!=1||v>65535){free(str);return 0;}
  values[seq]=(uint16_t)v;attempts[seq]=attempt;
 }
 free(str);
 for(int j=0;j<8;j++)if(!attempts[j]||values[j]!=((uint16_t)K07[2*j]<<8|K07[2*j+1]))return 0;
 SHA256(K07,16,digest);
 static const uint8_t K07_component[16]={0x93,0x49,0x5f,0x5e,0x42,0x5a,0xb8,0xe5,0x92,0x12,0x3d,0xab,0xae,0xb6,0x85,0x45};
 return !memcmp(digest,K07_component,16);
}
static inline int sha_match(const SHA256_CTX *s,const uint32_t d[8]){
 return s->h[0]==d[0]&&s->h[1]==d[1]&&!memcmp(s->h,d,sizeof(uint32_t)*8);
}
int main(int argc,char **argv){
 if(argc!=2||!source(argv[1])){fprintf(stderr,"Original AX transfer source integrity or selection failed\n");return 2;}
 Suffix *suffix=malloc(sizeof(Suffix)*65536);if(!suffix)abort();
 unsigned count=0,synthetic_checks=0;
 for(unsigned m=0;m<8;m++){
  uint16_t *inv=malloc(65536*sizeof(uint16_t));if(!inv)abort();
  for(unsigned n=0;n<65536;n++)inv[crc2(0,(uint16_t)n,m)]=(uint16_t)n;
  for(unsigned n=0;n<65536;n++)if(crc2(0,inv[n],m)!=n)abort();
  /* Independently seeded authentic synthetic CRC chain, 7 known subsequent words. */
  const uint8_t original[16]={1,254,2,253,3,252,4,251,5,250,6,249,7,248,8,247};
  uint16_t states[8],state=INIT[m];
  for(unsigned i=0;i<8;i++){
   state=crc2(state,((uint16_t)original[2*i]<<8)|original[2*i+1],m);
   states[i]=state^XOROUT[m];
  }
  for(unsigned i=1;i<8;i++){
   uint16_t x=inv[(states[i]^XOROUT[m])^crc2(states[i-1]^XOROUT[m],0,m)];
   if(x!=((uint16_t)original[2*i]<<8|original[2*i+1]))abort();
  }
  synthetic_checks++;
  for(unsigned reverse=0;reverse<2;reverse++)for(unsigned shift=0;shift<8;shift++){
   uint8_t p[8][2];
   for(unsigned i=0;i<8;i++){
    unsigned idx=reverse?(7-((i+shift)&7)):((i+shift)&7);
    p[i][0]=K07[2*idx];p[i][1]=K07[2*idx+1];
   }
   for(unsigned endianmask=0;endianmask<256;endianmask++){
    uint16_t cp[8];
    for(unsigned i=0;i<8;i++)cp[i]=((endianmask>>i)&1)?((uint16_t)p[i][1]<<8|p[i][0]):((uint16_t)p[i][0]<<8|p[i][1]);
    for(unsigned endian=0;endian<2;endian++){
     Suffix *s=&suffix[count++];
     for(unsigned i=1;i<8;i++){
      uint16_t x=inv[(cp[i]^XOROUT[m])^crc2(cp[i-1]^XOROUT[m],0,m)];
      if(endian){s->b[2*i-2]=(uint8_t)x;s->b[2*i-1]=(uint8_t)(x>>8);}
      else{s->b[2*i-2]=(uint8_t)(x>>8);s->b[2*i-1]=(uint8_t)x;}
     }
    }
   }
  }
  free(inv);
 }
 if(count!=65536||synthetic_checks!=8)abort();
 qsort(suffix,count,sizeof(Suffix),compare_suffix);
 unsigned unique=0;
 for(unsigned i=0;i<count;i++)if(!unique||memcmp(suffix[i].b,suffix[unique-1].b,14))suffix[unique++]=suffix[i];
 if(unique!=40960)abort();
 uint8_t digest[32];SHA256((const uint8_t*)suffix,unique*14,digest);
 if(memcmp(digest,SUFFIX_PIN,32)){fprintf(stderr,"Independent suffix digest failed\n");return 4;}
 printf("SOURCE_DERIVED_CRC16_GEOMETRIES=%u UNIQUE_14BYTE_SUFFIXES=%u PLANTED_CRC_CHAINS=%u\n",count,unique,synthetic_checks);fflush(stdout);
 uint8_t planted[16]={0xf0,0xa5};memcpy(planted+2,suffix[17].b,14);
 for(int j=0;j<16;j++)planted[j]^=mask[j];
 SHA256(planted,16,digest);
 uint32_t plant[8];for(int j=0;j<8;j++)plant[j]=((uint32_t)digest[4*j]<<24)|((uint32_t)digest[4*j+1]<<16)|((uint32_t)digest[4*j+2]<<8)|digest[4*j+3];
 uint64_t checks=0,hits=0,plants=0;
 #pragma omp parallel for reduction(+:checks,hits,plants) schedule(static)
 for(int index=0;index<(int)unique;index++){
  uint8_t block[64]={0};block[16]=128;block[63]=128;
  for(int j=2;j<16;j++)block[j]=suffix[index].b[j-2]^mask[j];
  SHA256_CTX base,test;SHA256_Init(&base);
  for(uint32_t word=0;word<65536;word++){
   block[0]=(uint8_t)(word>>8)^mask[0];block[1]=(uint8_t)word^mask[1];
   test=base;SHA256_Transform(&test,block);
   checks++;
   if(sha_match(&test,target)){
    hits++;
    #pragma omp critical
    {printf("ORIGINAL_K04_MATCH suffix=%d first=%04X comp=",index,word);
     for(int j=0;j<16;j++)printf("%02X",block[j]);puts("");fflush(stdout);}
   }
   if(sha_match(&test,plant))plants++;
  }
 }
 printf("FULL_CHAIN UNIQUE_COUPONS=%llu ORIGINAL_MATCHES=%llu PLANTED_FULL_COUPON=%llu\n",(unsigned long long)checks,(unsigned long long)hits,(unsigned long long)plants);
 free(suffix);
 return checks!=2684354560ULL||hits||plants!=1?5:0;
}
