/* H17: three-retry GF(256) source-coupon mixer.
 * Pure C/OpenSSL, read-only original files, exact 16byte K04 source mask.
 * A, B, C are source-selected 0417 RECOVER attempts1,2,3.
 * For every a,b,c in GF256: coupon[i] = a*A[i]+b*B[i]+c*C[i].
 * This speculative field-linear copier has no historical authenticity claim.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SZ 16
static const char *SRC_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *ACC_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const char *MASK_HEX="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *TARGET_HEX="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static uint8_t v[3][SZ], mask[SZ], target[32],mul[256][256];

static void fail(const char *message) { fprintf(stderr,"ERROR %s\n",message);exit(2); }
static int val(char c){
 if(c>='0'&&c<='9')return c-'0';
 if(c>='a'&&c<='f')return c-'a'+10;
 if(c>='A'&&c<='F')return c-'A'+10;
 return -1;
}
static void decode(const char *s,uint8_t *dst,size_t n){
 if(strlen(s)<2*n)fail("short hex");
 for(size_t i=0;i<n;++i){
  int a=val(s[2*i]),b=val(s[2*i+1]);
  if(a<0||b<0)fail("invalid hex");
  dst[i]=(uint8_t)(16*a+b);
 }
}
static void sha_file(const char *file,const char *expected){
 FILE *f=fopen(file,"rb");if(!f){perror(file);exit(2);}
 unsigned char data[65536],hash[32],expected_b[32];
 size_t n=fread(data,1,sizeof(data),f);
 if(ferror(f)||n==sizeof(data))fail("file read/size");
 fclose(f);SHA256(data,n,hash);decode(expected,expected_b,32);
 if(memcmp(hash,expected_b,32))fail("original source digest altered");
}
static void read_source(const char *root){
 char path[1024],line[1024];
 snprintf(path,sizeof(path),"%s/evidence/print/spool-reconstruction.log",root);
 sha_file(path,SRC_SHA);
 FILE *f=fopen(path,"rb");if(!f){perror(path);exit(2);}
 int seen[3]={0};
 while(fgets(line,sizeof(line),f)){
  if(!strstr(line,"JOB=PS-261003-0417 ")||!strstr(line,"CLASS=RECOVER "))continue;
  char *a=strstr(line,"ATTEMPT="), *p=strstr(line,"PAYLOAD=");
  if(!a||!p||a[8]<'1'||a[8]>'3')fail("unexpected selected job row");
  int i=a[8]-'1';
  if(seen[i]++)fail("duplicate original retry");
  if(!strstr(line,i==1?"STATE=ACK ":"STATE=REQUESTED "))fail("source job state");
  p+=8;
  char hex[33];memcpy(hex,p,32);hex[32]=0;decode(hex,v[i],SZ);
  if(val(p[32])>=0)fail("overlong source payload");
 }
 fclose(f);
 for(int i=0;i<3;++i)if(seen[i]!=1)fail("missing original retry");
 snprintf(path,sizeof(path),"%s/evidence/recovery-routing.json",root);
 sha_file(path,ROUTE_SHA);
 snprintf(path,sizeof(path),"%s/acceptance.json",root);
 sha_file(path,ACC_SHA);
 decode(MASK_HEX,mask,SZ);decode(TARGET_HEX,target,32);
}
static uint8_t times(uint8_t a,uint8_t b,unsigned poly){
 uint8_t answer=0;
 for(int j=0;j<8;++j){
  if(b&1)answer^=a;
  b>>=1;
  unsigned x=(unsigned)a<<1;
  if(x&256)x^=poly;
  a=(uint8_t)x;
 }
 return answer;
}
static void make_table(unsigned poly){
 for(int a=0;a<256;++a)for(int b=0;b<256;++b)
  mul[a][b]=times((uint8_t)a,(uint8_t)b,poly);
}
static void coupon(int a,int b,int c,uint8_t *out){
 for(int i=0;i<SZ;++i)
  out[i]=mul[a][v[0][i]]^mul[b][v[1][i]]^mul[c][v[2][i]];
}
static void reduced(const uint8_t *cp,uint8_t *hash){
 uint8_t arr[SZ];
 for(int i=0;i<SZ;++i)arr[i]=cp[i]^mask[i];
 SHA256(arr,SZ,hash);
}
static void print_hex(const uint8_t *buf,int n){
 for(int i=0;i<n;++i)printf("%02X",buf[i]);
}
int main(int argc,char **argv){
 if(argc!=2)fail("usage: gf256-retry RESOURCE_ROOT");
 read_source(argv[1]);
 uint64_t tot=0, hits=0;
 const unsigned polys[2]={0x11B,0x11D};
 for(int m=0;m<2;++m){
  make_table(polys[m]);
  uint8_t known_coupon[SZ],known_target[32],cp[SZ],got[32];
  coupon(13,29,47,known_coupon);
  reduced(known_coupon,known_target);
  uint64_t model_hits=0,model_plants=0;
  for(int a=0;a<256;++a){
   for(int b=0;b<256;++b){
    for(int c=0;c<256;++c){
     coupon(a,b,c,cp);
     reduced(cp,got);
     if(!memcmp(got,known_target,32))model_plants++;
     if(!memcmp(got,target,32)){
      model_hits++;
      printf("ORIGINAL_K04_MATCH poly=0x%X alpha=%d beta=%d gamma=%d coupon=",
       polys[m],a,b,c);
      print_hex(cp,16);putchar('\n');
     }
    }
   }
  }
  if(model_plants!=1)fail("planted full-coupon witness missing/non-unique");
  tot+=(1ULL<<24);hits+=model_hits;
  printf("GF256_MODEL polynomial=0x%X complete=%u authentic_matches=%llu planted=%llu\n",
   polys[m],(1U<<24),(unsigned long long)model_hits,(unsigned long long)model_plants);
 }
 printf("TOTAL_FULL_COMPONENTS=%llu authentic_hits=%llu synthetic_full_controls=2/2_PASS\n",
  (unsigned long long)tot,(unsigned long long)hits);
 return hits?4:0;
}
