/* H-17 K04: unrestricted leading 2 bytes plus 3-byte printer donor segment.
 * This models a two-stage copier fault. Selected ACK2 is excluded as donor.
 * C11 + OpenSSL + OpenMP. Run from repository root:
 *   gcc -O3 -fopenmp -Wno-deprecated-declarations agents/agent7/k04_prefix2_donor3_copier_sft.c -lcrypto -o k04_test
 *   ./k04_test
 * Optional path argument overrides the source path for local archive extracts.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>

#define MAX_ROWS 140
static const char *ORIGINAL_SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const char *SELECTED_HEX = "A9A9DC5731A5E2AE879C47215C2559D5";
static const char *MASK_HEX = "8556C8CB6140A7F9A5123AC7571BEE1C";
static unsigned char donors[MAX_ROWS][16];
static unsigned char sourcebuf[64 * 1024];

static void unhex(const char *h, unsigned char *out, int n) {
    for (int i=0;i<n;i++) {unsigned v=0; if(sscanf(h+2*i,"%2x",&v)!=1) abort();out[i]=(unsigned char)v;}
}
static void hexify(const unsigned char *p, char *out, int n) {
    static const char t[]="0123456789abcdef";
    for(int i=0;i<n;i++){out[2*i]=t[p[i]>>4];out[2*i+1]=t[p[i]&15];}out[2*n]=0;
}
static void original_source(const char *path, unsigned char *selected, unsigned char *mask, unsigned char *goal, int *n) {
    FILE *f=fopen(path,"rb");if(!f){perror(path);exit(2);}size_t used=fread(sourcebuf,1,sizeof(sourcebuf),f);
    if(!feof(f)||ferror(f)){fprintf(stderr,"source too large or read error\n");exit(2);}fclose(f);
    unsigned char digest[32];char dtext[65];SHA256(sourcebuf,used,digest);hexify(digest,dtext,32);
    if(strcmp(dtext,ORIGINAL_SPOOL_SHA)){fprintf(stderr,"original spool SHA mismatch: %s\n",dtext);exit(2);}
    unhex(MASK_HEX,mask,16);unhex(K04_SHA,goal,32);unhex(SELECTED_HEX,selected,16);
    *n=0;int found=0;
    char *end=(char*)sourcebuf+used;char *p=(char*)sourcebuf;
    while(p<end){char *q=memchr(p,'\n',(size_t)(end-p));if(!q)q=end; char saved=*q;*q=0;
      char *pay=strstr(p,"PAYLOAD=");char *job=strstr(p,"JOB=PS-261003-");char *attempt=strstr(p,"ATTEMPT=");
      if(pay&&job&&attempt){unsigned char raw[16];if(strlen(pay+8)<32){fprintf(stderr,"short payload\n");exit(2);}unhex(pay+8,raw,16);
        int selected_row=strncmp(job+4,"PS-261003-0417",14)==0 && strncmp(attempt+8,"2 ",2)==0 && strstr(p,"CLASS=RECOVER")&&strstr(p,"STATE=ACK");
        if(selected_row){ if(memcmp(raw,selected,16)){fprintf(stderr,"ACK original bytes mismatch\n");exit(2);}found++;}
        else{if(*n>=MAX_ROWS) abort();memcpy(donors[(*n)++],raw,16);}
      }
      *q=saved;p=q<end?q+1:end;
    }
    if(found!=1||*n!=132){fprintf(stderr,"row count mismatch: selected=%d other=%d\n",found,*n);exit(2);}
    printf("ORIGINAL_SOURCE_SHA_PASS selected_ACK2_excluded donors=%d\n",*n);
}

static void make_block(unsigned char block[64],const unsigned char payload[16],const unsigned char mask[16]){
  memset(block,0,64);for(int i=0;i<16;i++)block[i]=payload[i]^mask[i];block[16]=0x80;block[63]=128;
}
static void target_sha_block(const unsigned char block[64],unsigned char digest[32]){
  SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,block);
  for(int i=0;i<8;i++){unsigned v=ctx.h[i];digest[4*i]=(unsigned char)(v>>24);digest[4*i+1]=(unsigned char)(v>>16);digest[4*i+2]=(unsigned char)(v>>8);digest[4*i+3]=(unsigned char)v;}
}
static void synthetic_test(const unsigned char *selected,const unsigned char *mask){
  unsigned char p[16],b[64],target[32],out[32];memcpy(p,selected,16);
  p[0]=0xBE;p[1]=0xEF;memcpy(p+2,donors[0]+2,3);make_block(b,p,mask);target_sha_block(b,target);
  unsigned char component[16], native_digest[32];
  for(int i=0;i<16;i++)component[i]=p[i]^mask[i];
  SHA256(component,16,native_digest);
  if(memcmp(target,native_digest,32)){fprintf(stderr,"SHA256 block/reference mismatch\n");exit(2);}
  unsigned long found=0;
  for(unsigned a=0;a<65536;a++){p[0]=a>>8;p[1]=a&255;make_block(b,p,mask);target_sha_block(b,out);if(!memcmp(out,target,32))found++;}
  if(found!=1){fprintf(stderr,"synthetic blinded complete five-byte coupon failed %lu\n",found);exit(2);}
  printf("SYNTHETIC_POSITIVE=1/1 recovered_full_coupon_with_unknown_prefix2_and_donor3\n");
}

int main(int argc,char**argv){
 if(argc>2){fprintf(stderr,"usage: test [original_spool_file]\n");return 2;}
 const char *path=argc==2 ? argv[1] : "resources/evidence/print/spool-reconstruction.log";
 unsigned char selected[16],mask[16],goal[32];int n=0;
 original_source(path,selected,mask,goal,&n);synthetic_test(selected,mask);
 unsigned long long all=0,first64=0,hits=0;
 #pragma omp parallel for reduction(+:all,first64,hits) schedule(dynamic,1)
 for(int d=0;d<n;d++)for(int s=0;s<=13;s++)for(int dest=2;dest<=13;dest++){
   unsigned char p[16],b[64],out[32];memcpy(p,selected,16);
   memcpy(p+dest,donors[d]+s,3);make_block(b,p,mask);
   for(unsigned a=0;a<65536;a++){
       b[0]=(unsigned char)((a>>8)^mask[0]);b[1]=(unsigned char)((a&255)^mask[1]);
       target_sha_block(b,out);all++;
       if(!memcmp(out,goal,8)){first64++;if(!memcmp(out,goal,32)){
          #pragma omp critical
          { printf("ORIGINAL_K04_HIT donor=%d source_start=%d dest_start=%d prefix=%04x\n",d,s,dest,a);fflush(stdout); }
          hits++;
       }}
   }
 }
 printf("SUMMARY donor_packets=%d donor_starts=14 dest_starts=12 arbitrary_prefix16=65536 checks=%llu first64=%llu original_hits=%llu\n",n,all,first64,hits);
 if(all!=(unsigned long long)n*14*12*65536ULL){fprintf(stderr,"count failure\n");return 2;}
 return hits ? 1 : 0;
}
