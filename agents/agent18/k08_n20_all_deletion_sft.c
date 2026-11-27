/* H-17 K08: exhaustive deletion-only search over Emily's complete N20 note.
   Candidate family: every one of 2^30 order-preserving token subsequences,
   including empty/full. Exact K08 normal form is already represented because
   the source tokens are lowercase alphanumeric words joined by single spaces.
   Usage: ./sft noticeboard-and-desk-notes.txt FIRST_SHARD LAST_SHARD
   Each shard is 2^24 masks; full domain is FIRST=0 LAST=64. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>
#include <omp.h>
static const char *WORDS[30]={"i","wanted","the","line","to","hold","the","sea","the","end","of","the","night","and","the","voices","at","the","table","do","not","use","the","standby","label","just","because","it","is","shorter"};
static const char *N20="I wanted the line to hold the sea, the end of the night and the voices at the table. Do not use the standby label just because it is shorter.";
static const unsigned char NONCE[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char NOTES_SHA[32]={0x13,0xf2,0x31,0x8c,0xcc,0x54,0xf3,0x5b,0x59,0x0a,0x2d,0x76,0xb3,0xa8,0x02,0x44,0xfe,0x24,0xd7,0x0f,0x06,0x99,0xc6,0x7c,0x05,0x85,0x8e,0x8b,0x89,0x83,0xc5,0xcb};
static SHA256_CTX INNER,OUTER;
static void hmac16(const char *p,int n,unsigned char out[16]){SHA256_CTX s;unsigned char a[32],b[32];s=INNER;SHA256_Update(&s,p,n);SHA256_Final(a,&s);s=OUTER;SHA256_Update(&s,a,32);SHA256_Final(b,&s);memcpy(out,b,16);}
static void slot(const char *p,int n,unsigned char out[32]){unsigned char h[16];hmac16(p,n,h);SHA256(h,16,out);}
static void init_hmac(void){unsigned char p[64];memset(p,0x36,64);for(int i=0;i<16;i++)p[i]^=NONCE[i];SHA256_Init(&INNER);SHA256_Update(&INNER,p,64);memset(p,0x5c,64);for(int i=0;i<16;i++)p[i]^=NONCE[i];SHA256_Init(&OUTER);SHA256_Update(&OUTER,p,64);}
static void source_gate(const char *path){FILE*f=fopen(path,"rb");if(!f){perror(path);exit(2);}fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);char*b=malloc((size_t)n+1);if(!b||fread(b,1,(size_t)n,f)!=(size_t)n){fprintf(stderr,"read fail\n");exit(2);}fclose(f);b[n]=0;unsigned char h[32];SHA256((unsigned char*)b,(size_t)n,h);if(memcmp(h,NOTES_SHA,32)){fprintf(stderr,"notes SHA mismatch\n");exit(2);}if(!strstr(b,N20)){fprintf(stderr,"N20 literal missing\n");exit(2);}free(b);}
static int build(uint64_t mask,char *phrase){int L=0;for(int i=0;i<30;i++)if((mask>>i)&1){if(L)phrase[L++]=' ';size_t z=strlen(WORDS[i]);memcpy(phrase+L,WORDS[i],z);L+=(int)z;}phrase[L]=0;return L;}
static void controls(void){
 const char *n02="a good watch leaves the room ready for the next pair of hands";unsigned char h[16];hmac16(n02,(int)strlen(n02),h);static const unsigned char want[16]={0xbf,0x88,0x93,0x59,0xb0,0x30,0x3f,0x2b,0x2b,0x2f,0xd9,0x6a,0xe8,0x41,0x21,0x0b};if(memcmp(h,want,16)){fprintf(stderr,"N02 HMAC control failed\n");exit(2);}char p[512];uint64_t m=(1ull<<6)|(1ull<<7)|(1ull<<11)|(1ull<<12);int L=build(m,p);if(strcmp(p,"the sea the night")){fprintf(stderr,"builder control failed: %s\n",p);exit(2);}unsigned char a[32],b[32];slot(p,L,a);slot("the sea the night",17,b);if(memcmp(a,b,32)){fprintf(stderr,"planted hashing control failed\n");exit(2);}fprintf(stdout,"CONTROLS notes_sha=N02_HMAC=builder=PASS\n");}
int main(int argc,char**argv){if(argc!=4){fprintf(stderr,"usage: %s notes.txt FIRST_SHARD LAST_SHARD\n",argv[0]);return 2;}int first=atoi(argv[2]),last=atoi(argv[3]);if(first<0||last>64||first>=last)return 2;source_gate(argv[1]);init_hmac();controls();const uint64_t B=1ull<<24;unsigned long long total=0;int any=0;
 for(int sh=first;sh<last;sh++){uint64_t s=(uint64_t)sh*B,e=s+B;volatile int found=0;char hit[512]={0};double t=omp_get_wtime();
 #pragma omp parallel
 {char phrase[512];unsigned char d[32];
  #pragma omp for schedule(static)
  for(uint64_t mask=s;mask<e;mask++){if(found)continue;int L=build(mask,phrase);slot(phrase,L,d);if(!memcmp(d,TARGET,32)){
   #pragma omp critical
   {if(!found){found=1;strcpy(hit,phrase);fprintf(stdout,"AUTHENTIC_K08 shard=%d mask=%llu text=%s\n",sh,(unsigned long long)mask,hit);fflush(stdout);}}
  }}
 }
 double dt=omp_get_wtime()-t;total+=(e-s);any|=found;fprintf(stdout,"SHARD=%d START=%llu END=%llu CHECKED=%llu HITS=%d SEC=%.3f\n",sh,(unsigned long long)s,(unsigned long long)e,(unsigned long long)(e-s),found,dt);fflush(stdout);
 }
 fprintf(stdout,"TOTAL_SHARDS=%d TOTAL_CHECKED=%llu AUTHENTIC_HITS=%d\n",last-first,total,any);return any?3:0;}
