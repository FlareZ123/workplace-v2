/* Joint original-caption/damaged-nonce experiment. Historical source remains read-only.
 * Tests all 16 single-byte and 120 two-byte nonce correction locations, 255 replacement
 * values per altered byte, for eight source-linked full phrases. Does not assume an
 * author-final inscription is present in the source. */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const unsigned char nonce0[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,
                                         0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32]={
 0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,
 0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
struct phrase {const char *source; const char *text;};
static const struct phrase phrases[]={
 {"N13 Emily scene", "at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on"},
 {"N02 Emily first draft", "a good watch leaves the room ready for the next pair of hands"},
 {"N06 Emily second draft", "the little lamp stays on until the corridor has gone quiet"},
 {"N01 Jason photo", "the sea looks different when you have finally finished your tea"},
 {"N09 Zoey photo", "nobody should have to make their first cup alone after a bad night"},
 {"N17 standby negative label", "leave the light on for the next watch"},
 {"N18 commissioning negative label", "back before the first boat"},
 {"N20 Emily meta-description", "i wanted the line to hold the sea the end of the night and the voices at the table"}
};
static unsigned char nonce[16];
static uint64_t tested;

static int check(const char *message, const unsigned char cmp[32]) {
    unsigned char ipad[64],opad[64],inner[SHA256_DIGEST_LENGTH],outer[SHA256_DIGEST_LENGTH], digest[SHA256_DIGEST_LENGTH];
    SHA256_CTX c;
    memset(ipad,0x36,sizeof ipad);memset(opad,0x5c,sizeof opad);
    for(size_t i=0;i<sizeof nonce;i++){ipad[i]^=nonce[i];opad[i]^=nonce[i];}
    SHA256_Init(&c); SHA256_Update(&c,ipad,sizeof ipad); SHA256_Update(&c,message,strlen(message)); SHA256_Final(inner,&c);
    SHA256_Init(&c); SHA256_Update(&c,opad,sizeof opad); SHA256_Update(&c,inner,sizeof inner); SHA256_Final(outer,&c);
    SHA256(outer,16,digest);
    tested++;
    return memcmp(digest,cmp,sizeof digest)==0;
}

static int scan(const char *message, const unsigned char cmp[32],int print_hit){
    memcpy(nonce,nonce0,sizeof nonce);
    for(unsigned i=0;i<16;i++) {
       for(unsigned x=0;x<256;x++){
          if(x==nonce0[i])continue;
          nonce[i]=(unsigned char)x;
          if(check(message,cmp)){
             if(print_hit)printf("HIT onebyte position=%u value=%02X\n",i,x);
             return 1;
          }
       }
       nonce[i]=nonce0[i];
    }
    for(unsigned i=0;i<16;i++)for(unsigned j=i+1;j<16;j++){
       for(unsigned x=0;x<256;x++){
          if(x==nonce0[i])continue;
          nonce[i]=(unsigned char)x;
          for(unsigned y=0;y<256;y++){
             if(y==nonce0[j])continue;
             nonce[j]=(unsigned char)y;
             if(check(message,cmp)){
                if(print_hit)printf("HIT twobyte positions=%u,%u values=%02X,%02X\n",i,j,x,y);
                return 1;
             }
          }
          nonce[j]=nonce0[j];
       }
       nonce[i]=nonce0[i];
    }
    return 0;
}

int main(void){
    unsigned char synthetic[32];
    memcpy(nonce,nonce0,16); nonce[0]=0x29;nonce[8]=0x51;
    unsigned char ipad[64],opad[64],inner[32],outer[32];SHA256_CTX c;
    memset(ipad,0x36,64);memset(opad,0x5c,64);
    for(int i=0;i<16;i++){ipad[i]^=nonce[i];opad[i]^=nonce[i];}
    SHA256_Init(&c);SHA256_Update(&c,ipad,64);SHA256_Update(&c,phrases[0].text,strlen(phrases[0].text));SHA256_Final(inner,&c);
    SHA256_Init(&c);SHA256_Update(&c,opad,64);SHA256_Update(&c,inner,32);SHA256_Final(outer,&c);
    SHA256(outer,16,synthetic);
    tested=0;
    if(!scan(phrases[0].text,synthetic,1)){fprintf(stderr,"Synthetic two-byte control failed\n");return 2;}
    printf("SYNTHETIC PASS checks=%llu\n",(unsigned long long)tested);
    for(size_t p=0;p<sizeof phrases/sizeof phrases[0];p++){
       uint64_t before=tested;
       int hit=scan(phrases[p].text,target,1);
       printf("ORIGINAL source=%s checks=%llu result=%s\n",phrases[p].source,(unsigned long long)(tested-before),hit?"PASS":"NO_MATCH");
       fflush(stdout);
       if(hit)return 0;
    }
    printf("ORIGINAL TOTAL checks=%llu NO_MATCH\n",(unsigned long long)tested);
    return 1;
}
