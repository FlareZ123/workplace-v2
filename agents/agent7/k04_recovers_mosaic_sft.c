/* Source-pinned 3^16 byte-mosaic K04 selected-event complete-candidate search.
   All 16 bytes of any hypothesized original coupon are independently chosen
   from original 0417 RECOVER attempts 1/2/3, with no guessed byte values.
   Source, acceptance, routing and official candidate are read-only. */
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static const char *spool_pin="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *mask_txt="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *target_txt="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static unsigned char source[3][16],coupon[16], mask[16],target[32],positive[32];
static unsigned long long tested=0, original_hits=0, synthetic_hits=0;
static int present[3];

static void die(const char *why){fprintf(stderr,"ERROR: %s\n",why);exit(2);}
static int nibble(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;if(c>='a'&&c<='f')return c-'a'+10;return -1;}
static void decode(const char *p,unsigned char *out,int n){for(int i=0;i<n;i++){int a=nibble(p[2*i]),b=nibble(p[2*i+1]);if(a<0||b<0)die("bad hex");out[i]=(unsigned char)((a<<4)|b);}}
static void printhex(const unsigned char *p,int n){for(int i=0;i<n;i++)printf("%02X",p[i]);}
static char *readfile(const char *p, size_t *sz){FILE *f=fopen(p,"rb");if(!f)die("missing source file");fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);if(n<0)die("size");char *s=malloc((size_t)n+1);if(!s)die("alloc");if(fread(s,1,(size_t)n,f)!=(size_t)n)die("read");fclose(f);s[n]=0;*sz=(size_t)n;return s;}
static void hash(unsigned char *out,const unsigned char *data,size_t len){SHA256(data,len,out);}
static void prepare(const char *dir){
 char p[1024];size_t n;
 snprintf(p,sizeof p,"%s/evidence/print/spool-reconstruction.log",dir);
 char *txt=readfile(p,&n);unsigned char check[32];hash(check,(unsigned char*)txt,n);
 char pin[65];for(int i=0;i<32;i++)sprintf(pin+2*i,"%02x",(unsigned char)check[i]);if(strcmp(pin,spool_pin))die("spool SHA mismatch");
 char *line=strtok(txt,"\n");
 while(line){
  if(strstr(line,"JOB=PS-261003-0417")&&strstr(line,"CLASS=RECOVER")){
   char *att=strstr(line,"ATTEMPT="),*pl=strstr(line,"PAYLOAD=");if(!att||!pl)die("missing 0417 field");
   int a=atoi(att+8);if(a<1||a>3||present[a-1])die("unexpected 0417 attempt");
   if(strlen(pl+8)<32)die("bad 0417 coupon");
   decode(pl+8,source[a-1],16);present[a-1]=1;
  }
  line=strtok(NULL,"\n");
 }
 free(txt);if(!present[0]||!present[1]||!present[2])die("0417 attempt missing");
 snprintf(p,sizeof p,"%s/evidence/recovery-routing.json",dir);
 char *r=readfile(p,&n);if(!strstr(r,mask_txt))die("route mask mismatch");free(r);
 snprintf(p,sizeof p,"%s/acceptance.json",dir);
 r=readfile(p,&n);if(!strstr(r,target_txt))die("acceptance target mismatch");free(r);
 decode(mask_txt,mask,16);decode(target_txt,target,32);
 for(int i=0;i<16;i++)coupon[i]=(unsigned char)(source[i%3][i]^mask[i]);
 hash(positive,coupon,16);memset(coupon,0,16);
}
static void search(int pos){
 if(pos==16){
  unsigned char digest[32];hash(digest,coupon,16);tested++;
  if(!memcmp(digest,target,32)){original_hits++;if(original_hits<4){printf("ORIGINAL_K04_MATCH component=");printhex(coupon,16);puts("");fflush(stdout);}}
  if(!memcmp(digest,positive,32))synthetic_hits++;
  return;
 }
 for(int src=0;src<3;src++){coupon[pos]=(unsigned char)(source[src][pos]^mask[pos]);search(pos+1);}
}
int main(int argc,char **argv){if(argc!=2)die("usage: k04_recovers_mosaic_sft ROOT_DIR");prepare(argv[1]);
 printf("ORIGINAL_SPOOL_SHA_PIN_PASS; 0417 RECOVER_ATTEMPTS=1,2,3\n");
 for(int a=0;a<3;a++){printf("SOURCE_ATTEMPT_%d=",a+1);printhex(source[a],16);puts("");}
 fflush(stdout);search(0);
 printf("COMPLETE_MOSAIC_ASSIGNMENTS=%llu ORIGINAL_K04_HITS=%llu SYNTHETIC_HITS=%llu\n",tested,original_hits,synthetic_hits);
 if(tested!=43046721ULL||synthetic_hits!=1||original_hits)return 3;
 puts("SOURCE_PIN_AND_FULL_DIGEST_POSITIVE_PASS; ORIGINAL_K04_NOT_RECOVERED");return 0;
}
