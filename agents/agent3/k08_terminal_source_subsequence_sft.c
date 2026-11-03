/* H17 K08 read-only terminal/version-source ordered subsequence search.
 * Build: cc -O3 agents/agent3/k08_terminal_source_subsequence_sft.c -lcrypto -o test_k08_terminal
 * Run: ./test_k08_terminal
 * Requires OpenSSL libcrypto. All texts originate in SHA-pinned original source.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>

static const unsigned char nonce[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const char *phrases[]={
 "the wording in my margin was never an official slogan the envelope only remembers the words i finally put on it",
 "people making room for each other after a long watch with the water outside and the night almost finished",
 "there were several captions and drafts on her desk the words she finally chose matter not our preferred paraphrase",
 "nobody should have to make their first cup alone after a bad night",
 "even the chipped blue one belongs to someone who expects to see it again",
 "someone asked why i count mugs when i could count beds a bed does not tell you whether anybody has sat down"
};
static void source_pin(const char *path,const char *want){
 FILE *f=fopen(path,"rb");assert(f);
 assert(fseek(f,0,SEEK_END)==0);long n=ftell(f); assert(n>0&&n<1000000);
 rewind(f);unsigned char *b=malloc((size_t)n);assert(b);
 assert(fread(b,1,(size_t)n,f)==(size_t)n);fclose(f);
 unsigned char d[32];SHA256(b,(size_t)n,d);free(b);
 char actual[65];
 for(int j=0;j<32;j++)sprintf(actual+2*j,"%02x",d[j]);
 actual[64]=0;
 assert(strcmp(actual,want)==0);
}
static void check(const char *phrase,unsigned char result[32]){
 unsigned char mac[32];unsigned int n=0;
 assert(HMAC(EVP_sha256(),nonce,16,(const unsigned char*)phrase,
             strlen(phrase),mac,&n)&&n==32);
 SHA256(mac,16,result);
}
int main(void){
 source_pin("resources/evidence/crew/noticeboard-and-desk-notes.txt",
 "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
 source_pin("resources/evidence/mail/11.eml",
 "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29");
 source_pin("resources/evidence/mail/20.eml",
 "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71");
 unsigned char known[32],planted[32],d[32];
 check("a good watch leaves the room ready for the next pair of hands",known);
 const unsigned char n02[32]={0x47,0xe7,0x87,0x78,0x5f,0xf2,0x50,0x82,0xb4,0xb9,0x60,0xad,0x41,0x5f,0x1e,0x03,0x0a,0xe0,0xed,0xc8,0x9c,0x38,0xb2,0xf6,0x1c,0x48,0xf9,0x33,0x12,0x82,0xea,0x55};
 assert(memcmp(known,n02,32)==0);
 check("the envelope remembers words on it",planted);
 uint64_t total=0,hits=0,positives=0;
 for(int n=0;n<6;n++){
  char text[700];strcpy(text,phrases[n]);
  char *words[40];int count=0;char *p=strtok(text," ");
  while(p){words[count++]=p;p=strtok(NULL," ");}
  assert(count>0&&count<31);
  for(uint64_t bits=1;bits<(UINT64_C(1)<<count);bits++){
   char phrase[700];int used=0;
   for(int j=0;j<count;j++)if((bits>>j)&1){
    if(used)phrase[used++]=' ';
    size_t len=strlen(words[j]);memcpy(phrase+used,words[j],len);used+=(int)len;
   }
   phrase[used]=0;check(phrase,d);
   if(memcmp(d,target,32)==0){
    hits++;printf("ORIGINAL HIT source=%d text=%s\n",n,phrase);
   }
   positives+=memcmp(d,planted,32)==0;
   total++;
  }
  printf("source %d original words=%d candidate assignments=%llu\n",
         n,count,(unsigned long long)((UINT64_C(1)<<count)-1));
 }
 assert(total==UINT64_C(7364602)&&positives==2&&hits==0);
 printf("completed=%llu original_matches=%llu synthetic_positive=%llu\n",
        (unsigned long long)total,(unsigned long long)hits,
        (unsigned long long)positives);
 return 0;
}