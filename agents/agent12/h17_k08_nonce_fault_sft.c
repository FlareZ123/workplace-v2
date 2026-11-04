#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>

/* Exact original H-17 keeper nonce and K08 full SHA256 commitment.
   Compiling: cc -O3 -Wall -Wextra -o h17_k08_nonce_fault
              agents/agent12/h17_k08_nonce_fault_sft.c -lcrypto
   --selftest supplies a synthetic two-byte mutation check.
   Each normal invocation exhausts one source-provided normalized caption
   against the unmodified original target, from byte position 0..15. */
static const unsigned char n0[16]={0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};
static const unsigned char target[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static int check(const unsigned char *key,const char *text,const unsigned char *digest){
 unsigned char out[32],hash[32];unsigned int sz=32;
 HMAC(EVP_sha256(),key,16,(const unsigned char*)text,strlen(text),out,&sz);
 SHA256(out,16,hash);
 return memcmp(hash,digest,32)==0;
}
int main(int argc,char**argv){
 if(argc==2 && strcmp(argv[1],"--selftest")==0){
    const char *phrase="a good watch leaves the room ready for the next pair of hands";
    unsigned char k[16],out[32],d[32]; unsigned int len=32;
    memcpy(k,n0,16); k[0]=0x42;k[7]=0x24;
    HMAC(EVP_sha256(),k,16,(const unsigned char*)phrase,strlen(phrase),out,&len);
    SHA256(out,16,d);
    if(!check(k,phrase,d)||check(n0,phrase,d))return 3;
    puts("SELFTEST synthetic two-byte nonce mutation PASS");return 0;
 }
 if(argc!=3){fprintf(stderr,"usage: prog normalized_phrase first_byte_position | --selftest\n");return 2;}
 const char*phrase=argv[1]; int start=atoi(argv[2]);
 if(start<0||start>15)return 2;
 unsigned char key[16];memcpy(key,n0,16);unsigned long long checks=0;
 if(start==0){if(check(key,phrase,target)){printf("MATCH baseline: %s\n",phrase);return 0;}}
 for(int i=start;i<16;i++){
  for(int v=0;v<256;v++){
   if(v==n0[i])continue;
   key[i]=v;
   if(check(key,phrase,target)){printf("MATCH single i=%d v=%02X %s\n",i,v,phrase);return 0;}
   checks++;
  }
  key[i]=n0[i];
  for(int j=i+1;j<16;j++){
   for(int v=0;v<256;v++){
    if(v==n0[i])continue;
    key[i]=v;
    for(int w=0;w<256;w++){
     if(w==n0[j])continue;
     key[j]=w;
     if(check(key,phrase,target)){printf("MATCH two i=%d j=%d v=%02X w=%02X %s\n",i,j,v,w,phrase);return 0;}
     checks++;
    }
    key[j]=n0[j];
   }
   key[i]=n0[i];
  }
 }
 printf("NO_MATCH start=%d checks=%llu phrase=%s\n",start,checks,phrase);
 return 0;
}
