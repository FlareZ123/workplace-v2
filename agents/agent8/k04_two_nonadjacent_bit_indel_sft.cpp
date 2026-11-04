/* K04 copied printer payload: arbitrary pair of interior bit deletions and insertions.
 * Source-pinned, original SHA256 commitment; positive synthetic control.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned __int128 U128;
static const unsigned target[8]={0x930a52a1U,0xbab97ca2U,0x96633213U,0x7c99e992U,
                                  0x98ea6182U,0xfb32ab63U,0xa3421dfbU,0x4fd8c9e0U};
static const uint8_t physical_copy[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
                                         0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
                                0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static void fail(const char*s){fprintf(stderr,"ERROR: %s\n",s);exit(2);}
static size_t read_source(const char*root,const char*relative,unsigned char**out){
 char file[4096];if(snprintf(file,sizeof file,"%s/%s",root,relative)>=(int)sizeof file)fail("path length");
 FILE*f=fopen(file,"rb");if(!f)fail("source absent");fseek(f,0,SEEK_END);
 long n=ftell(f);if(n<=0||n>1000000)fail("source length");rewind(f);
 unsigned char*p=(unsigned char*)malloc((size_t)n+1);if(!p)fail("alloc");
 if(fread(p,1,(size_t)n,f)!=(size_t)n)fail("read source");fclose(f);p[n]=0;*out=p;return (size_t)n;
}
static void verify_sources(const char*root){
 unsigned char*p;size_t n=read_source(root,"evidence/print/spool-reconstruction.log",&p);
 uint8_t digest[32];char sha[65];SHA256(p,n,digest);
 for(int i=0;i<32;i++)sprintf(sha+2*i,"%02x",digest[i]);
 if(strcmp(sha,"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"))fail("spool SHA changed");
 const char*row="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
 char*q=strstr((char*)p,row);if(!q||strstr(q+strlen(row),row))fail("selected source absent or repeated");free(p);
 read_source(root,"evidence/recovery-routing.json",&p);
 if(!strstr((char*)p,"8556C8CB6140A7F9A5123AC7571BEE1C"))fail("mask changed");free(p);
 read_source(root,"acceptance.json",&p);
 if(!strstr((char*)p,"930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"))fail("K04 SHA changed");free(p);
}
static U128 to128(const uint8_t v[16]){U128 x=0;for(int i=0;i<16;i++)x=(x<<8)|v[i];return x;}
static U128 low_mask(int bits){return bits?(((U128)1<<bits)-1):0;}
static U128 erase_bit(U128 x,int length,int pos){
 int k=length-pos-1;return ((x>>(k+1))<<k)|(x&low_mask(k));
}
static U128 insert_zero(U128 x,int length,int pos){
 int k=length-pos;return ((x>>k)<<(k+1))|(x&low_mask(k));
}
static void make_block(U128 val,uint8_t block[64]){
 memset(block,0,64);
 for(int i=0;i<16;i++)block[i]=(uint8_t)(val>>(120-8*i))^mask[i];
 block[16]=0x80;block[63]=0x80;
}
static void digest_of(const SHA256_CTX*initial,const uint8_t block[64],unsigned digest[8]){
 SHA256_CTX ctx=*initial;SHA256_Transform(&ctx,block);
 for(int k=0;k<8;k++)digest[k]=ctx.h[k];
}
static int eq_digest(const unsigned a[8],const unsigned b[8]){for(int j=0;j<8;j++)if(a[j]!=b[j])return 0;return 1;}
static void print_hex(const uint8_t b[64]){for(int j=0;j<16;j++)printf("%02X",b[j]);printf("\n");fflush(stdout);}
int main(int argc,char**argv){
 if(argc!=2)fail("usage: two_bit_indels ARCHIVE_ROOT");
 verify_sources(argv[1]);SHA256_CTX initial;SHA256_Init(&initial);
 U128 P=to128(physical_copy);
 U128 B=erase_bit(erase_bit(P,128,53),127,11);
 U128 synthetic=insert_zero(insert_zero(B,126,21),127,77)^((U128)1<<(127-21));
 uint8_t block[64],full[32];unsigned planted[8];make_block(synthetic,block);digest_of(&initial,block,planted);
 SHA256(block,16,full);
 for(int j=0;j<8;j++){
  unsigned v=((unsigned)full[4*j]<<24)|((unsigned)full[4*j+1]<<16)|((unsigned)full[4*j+2]<<8)|full[4*j+3];
  if(planted[j]!=v)fail("oneblock SHA mismatch");
 }
 uint64_t hits=0,positive=0,completed=0;
 const double started=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,1) reduction(+:hits,positive,completed)
 for(int d0=0;d0<127;d0++){
  uint8_t out[64];unsigned actual[8];
  for(int d1=d0+1;d1<128;d1++){
   U128 base=erase_bit(erase_bit(P,128,d1),127,d0);
   for(int i0=0;i0<127;i0++){
    U128 after_first=insert_zero(base,126,i0);
    U128 bit0=(U128)1<<(127-i0);
    for(int i1=i0+1;i1<128;i1++){
     U128 b0=insert_zero(after_first,127,i1);
     U128 bit1=(U128)1<<(127-i1);
     for(int b=0;b<4;b++){
      U128 val=b0|((b&2)?bit0:0)|((b&1)?bit1:0);
      make_block(val,out);digest_of(&initial,out,actual);
      if(actual[0]==target[0]&&eq_digest(actual,target)){
       hits++;
       #pragma omp critical
       {printf("ORIGINAL_K04_MATCH deletion=%d,%d insertion=%d,%d bits=%d,%d component=",d0,d1,i0,i1,b>>1,b&1);print_hex(out);}
      }
      if(actual[0]==planted[0]&&eq_digest(actual,planted))positive++;
     }
    }
   }
   completed++;
  }
 }
 const unsigned long long expected=(unsigned long long)8128*8128*4;
 if(completed!=8128)fail("missing deletion pair");
 if(positive==0)fail("synthetic full phrase absent");
 printf("SOURCE_PINNED complete_assignments=%llu original_matches=%llu planted_assignments=%llu deletion_pairs=%llu seconds=%.3f\n",
   expected,(unsigned long long)hits,(unsigned long long)positive,(unsigned long long)completed,omp_get_wtime()-started);
 return hits?9:0;
}
