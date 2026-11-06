/* H17 selected physical coupon: one-based cassette-ticket five-byte defect,
   two source-caused prior same-job cache replacements and three free bytes.
   Original source and SHA256 commitment are read-only. C11/OpenSSL. */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <omp.h>

static const int pos[5]={0,2,9,13,15};
static const uint8_t prior[2][16]={
 {0xe1,0xe6,0x0d,0x5f,0x6b,0x6d,0xd2,0x22,0x5f,0xa6,0xd5,0xa2,0xa6,0x3a,0xd9,0x32},
 {0xcd,0x3e,0x4f,0x21,0x6a,0xdb,0x2f,0xb1,0x80,0xda,0x2a,0xa9,0x0b,0x33,0xf7,0xa4}};
static const uint8_t raw[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const unsigned target[8]={0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U};
static void fail(const char*s){fprintf(stderr,"FAIL %s\n",s);exit(2);}
static void check(const char *root,const char*path,const char*needle,const char*expected){
 char filename[4096]; snprintf(filename,sizeof(filename),"%s/%s",root,path);
 FILE*f=fopen(filename,"rb");if(!f)fail("file");fseek(f,0,SEEK_END);long n=ftell(f);if(n<0||n>1000000)fail("length");rewind(f);
 char *buf=malloc((size_t)n+1);if(!buf)fail("alloc");if(fread(buf,1,(size_t)n,f)!=(size_t)n)fail("read");fclose(f);buf[n]=0;
 if(!strstr(buf,needle))fail("literal absent");
 if(expected){
 uint8_t d[32];char txt[65];SHA256((const uint8_t*)buf,(size_t)n,d);for(int j=0;j<32;j++)sprintf(txt+j*2,"%02x",d[j]);
 if(strcmp(txt,expected))fail("source digest");}
 free(buf);
}
static void init(uint8_t b[64]){memset(b,0,64);for(int i=0;i<16;i++)b[i]=raw[i]^mask[i];b[16]=0x80;b[63]=0x80;}
static void write_pos(uint8_t b[64],int p,int x){b[p]=(uint8_t)x^mask[p];}
static int equal_sha(const SHA256_CTX*initial,const uint8_t b[64],const unsigned digest[8]){
 SHA256_CTX x=*initial;SHA256_Transform(&x,b);if(x.h[0]!=digest[0])return 0;for(int j=1;j<8;j++)if(x.h[j]!=digest[j])return 0;return 1;
}
static unsigned word32(const uint8_t*d,int j){return (unsigned)d[4*j]<<24|(unsigned)d[4*j+1]<<16|(unsigned)d[4*j+2]<<8|d[4*j+3];}
int main(int argc,char**argv){
 if(argc<2||argc>3)fail("usage ROOT [--smoke]");
 int smoke=argc==3&&!strcmp(argv[2],"--smoke");
 if(argc==3&&!smoke)fail("mode");
 check(argv[1],"evidence/print/spool-reconstruction.log","JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5", "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 check(argv[1],"evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt","L-29/N    01     ST-094", "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf");
 check(argv[1],"evidence/recovery-routing.json","8556C8CB6140A7F9A5123AC7571BEE1C",NULL);
 check(argv[1],"acceptance.json","930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",NULL);
 SHA256_CTX initial; SHA256_Init(&initial); uint8_t planted[64],digest[32];unsigned ptarget[8];init(planted);
 write_pos(planted,pos[0],prior[0][pos[0]]);write_pos(planted,pos[1],prior[1][pos[1]]);
 write_pos(planted,pos[2],0x35);write_pos(planted,pos[3],0x7a);write_pos(planted,pos[4],0xd2);
 SHA256(planted,16,digest);for(int j=0;j<8;j++)ptarget[j]=word32(digest,j);
 if(!equal_sha(&initial,planted,ptarget))fail("whole synthetic control");
 unsigned long long tested=0,found=0,plant=0;
 const uint32_t limit=smoke?(1U<<18):(1U<<24);
 #pragma omp parallel for schedule(dynamic,1) reduction(+:tested,found,plant)
 for(int job=0;job<40;job++){
  int pair=job/4,choose=job%4,a=0,b=1,kpair=0;
  for(int ia=0;ia<5;ia++)for(int ib=ia+1;ib<5;ib++)if(kpair++==pair){a=ia;b=ib;}
  int remaining[3],k=0;for(int j=0;j<5;j++)if(j!=a&&j!=b)remaining[k++]=pos[j];
  uint8_t block[64];init(block);write_pos(block,pos[a],prior[choose&1][pos[a]]);write_pos(block,pos[b],prior[(choose>>1)&1][pos[b]]);
  for(uint32_t v=0;v<limit;v++){
   write_pos(block,remaining[0],v>>16);write_pos(block,remaining[1],v>>8);write_pos(block,remaining[2],v);
   if(equal_sha(&initial,block,target)){
    found++;
    #pragma omp critical
    {printf("ORIGINAL_K04_FOUND coupon=");for(int j=0;j<16;j++)printf("%02X",block[j]^mask[j]);puts("");fflush(stdout);}
   }
   if(a==0&&b==1&&choose==2&&equal_sha(&initial,block,ptarget))plant++;
   tested++;
  }
 }
 unsigned long long expected=40ULL*limit;
 if(tested!=expected)fail("count");
 if(smoke && plant!=0)fail("smoke positive should be outside partial domain");
 if(!smoke&&plant!=1)fail("full planted witness");
 printf("SUMMARY case=one-based-five-ticket-two-previous-cache-three-free smoke=%d tested=%llu source_original_hits=%llu planted_whole_hits=%llu\n",smoke,tested,found,plant);
 return found?9:0;
}
