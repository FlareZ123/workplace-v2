/* H-17 SFT: selected A9A9 pair replaced independently plus one repeated
 * per-word-byte-lane XOR or modular-add fault. Source files never modified.
 * Build with a C compiler and OpenSSL libcrypto. Run from repository root.
 */
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static const unsigned char P[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const unsigned char M[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char H[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static void pin(const char*root,const char*rel,const char*want){
 char path[1024],got[65];unsigned char b[8192],h[32];size_t n;
 if(snprintf(path,sizeof path,"%s/%s",root,rel)>=(int)sizeof path)exit(2);
 FILE *fp=fopen(path,"rb");if(!fp){perror(path);exit(2);}
 SHA256_CTX c;SHA256_Init(&c);
 while((n=fread(b,1,sizeof b,fp))>0)SHA256_Update(&c,b,n);
 if(ferror(fp))exit(2);fclose(fp);SHA256_Final(h,&c);
 for(int i=0;i<32;i++)sprintf(got+2*i,"%02x",h[i]);
 if(strcmp(got,want)){fprintf(stderr,"BAD SOURCE: %s\n",path);exit(2);}
}
static void construct(int mode,int lane,unsigned pad,unsigned first,unsigned char out[16]){
 for(int i=0;i<16;i++)out[i]=P[i]^M[i];
 for(int i=lane;i<16;i+=4)
   out[i]=((mode==0)?(P[i]^pad):((P[i]+pad)&255))^M[i];
 out[0]=(first>>8)^M[0];out[1]=(first&255)^M[1];
}
static void hex(const unsigned char*b){for(int i=0;i<16;i++)printf("%02X",b[i]);}
int main(int argc,char**argv){
 const char*root=argc>1?argv[1]:"resources";
 pin(root,"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 pin(root,"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
 pin(root,"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
 unsigned char a[16],d[32],fake_x[32],fake_a[32];
 construct(0,2,0x83,0x1762,a);SHA256(a,16,fake_x);
 construct(1,3,0x41,0x9C68,a);SHA256(a,16,fake_a);
 unsigned long long count=0,hits=0;unsigned pos_x=0,pos_a=0;
 for(int mode=0;mode<2;mode++)for(int lane=0;lane<4;lane++){
  unsigned long long local=0;
  for(unsigned pad=0;pad<256;pad++)for(unsigned first=0;first<65536;first++){
   construct(mode,lane,pad,first,a);SHA256(a,16,d);
   if(!memcmp(d,H,32)){
    printf("ORIGINAL MATCH mode=%d lane=%d pad=%u first=%04X component=",mode,lane,pad,first);
    hex(a);puts("");hits++;local++;
   }
   if(mode==0&&lane==2&&!memcmp(d,fake_x,32))pos_x++;
   if(mode==1&&lane==3&&!memcmp(d,fake_a,32))pos_a++;
   count++;
  }
  printf("mode=%s lane=%d full_checks=16777216 target_matches=%llu\n",mode?"ADD":"XOR",lane,local);fflush(stdout);
 }
 printf("TOTAL=%llu original_matches=%llu planted_xor=%u planted_add=%u\n",count,hits,pos_x,pos_a);
 return count==134217728ULL&&hits==0&&pos_x==1&&pos_a==1?0:1;
}
