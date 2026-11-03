/* H17 K08: delete-only order-preserving subsequences of Emily's MAIL-11
   final-envelope DESCRIPTION, not an authenticated final quotation.
   Original MAIL-11 SHA256 f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29.
   Fixed source words: people, room, watch, water, night.
   24 optional source tokens -> 16,777,216 complete normalized candidates.
   Exact original nonce / original K08 commitment; no source modification.
   Build using a C compiler linked to libcrypto; no external account access. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <openssl/sha.h>
static const char *words[] = {"for","this","envelope","i","wanted","the","line","that","felt","like","people","making","room","for","each","other","after","a","long","watch","with","the","water","outside","and","the","night","almost","finished"};
static const unsigned char nonce[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static SHA256_CTX inner_base,outer_base;
static void init(void){
 unsigned char pad[64];memset(pad,0x36,64);for(int i=0;i<16;i++)pad[i]^=nonce[i];SHA256_Init(&inner_base);SHA256_Update(&inner_base,pad,64);
 memset(pad,0x5c,64);for(int i=0;i<16;i++)pad[i]^=nonce[i];SHA256_Init(&outer_base);SHA256_Update(&outer_base,pad,64);
}
static void keyhash(const char *p,int n,unsigned char out[32]){
 SHA256_CTX st;unsigned char inner[32],outer[32];st=inner_base;SHA256_Update(&st,p,n);SHA256_Final(inner,&st);
 st=outer_base;SHA256_Update(&st,inner,32);SHA256_Final(outer,&st);SHA256(outer,16,out);
}
int main(void){
 init();unsigned char digest[32];
 const char *control="a good watch leaves the room ready for the next pair of hands";
 SHA256_CTX a=inner_base;unsigned char m[32];SHA256_Update(&a,control,strlen(control));SHA256_Final(m,&a);
 a=outer_base;SHA256_Update(&a,m,32);SHA256_Final(m,&a);
 const char *known="BF889359B0303F2B2B2FD96AE841210B";char h[33];for(int i=0;i<16;i++)sprintf(h+2*i,"%02X",m[i]);
 if(strcmp(h,known)){fprintf(stderr,"HMAC control failed: %s\n",h);return 2;}
 const int n=29;int bit[29];int nsel=0;for(int i=0;i<n;i++)bit[i]=(i==10||i==12||i==19||i==22||i==26)?-1:nsel++;
 if(nsel!=24){fprintf(stderr,"index error\n");return 2;}
 char phrase[512];unsigned long long checked=0;
 for(uint64_t mask=0;mask<(1ull<<24);mask++){
  int length=0;
  for(int i=0;i<n;i++){
   int selected=bit[i]<0 || (mask>>bit[i])&1;
   if(selected){if(length)phrase[length++]=' ';size_t len=strlen(words[i]);memcpy(phrase+length,words[i],len);length+=(int)len;}
  }
  phrase[length]=0;
  keyhash(phrase,length,digest);checked++;
  if(!memcmp(digest,target,32)){printf("MATCH %s\n",phrase);return 0;}
 }
 printf("MATCHES=0 CHECKED=%llu FIRST-DRAFT-HMAC-CONTROL=PASS\n",checked);return 0;
}
