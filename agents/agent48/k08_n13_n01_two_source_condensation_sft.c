/* Original K08 bounded source-word condensation, N13 plus N01. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>
typedef struct {char text[160];unsigned char len;} Segment;
static const char *a[]={"at","the","end","of","the","night","the","mugs","stood","beside","the","window","and","somebody","had","remembered","to","leave","the","little","lamp","on"};
static const char *b[]={"the","sea","looks","different","when","you","have","finally","finished","your","tea"};
static Segment sb[2048];
static SHA256_CTX ipad,opad;
static void unhex(const char*s,unsigned char*out,int n){for(int i=0;i<n;i++){unsigned v;if(sscanf(s+2*i,"%2x",&v)!=1)abort();out[i]=v;}}
static void init(const unsigned char*key){
 unsigned char p[64];
 for(int i=0;i<64;i++)p[i]=(i<16?key[i]:0)^0x36;
 SHA256_Init(&ipad);SHA256_Update(&ipad,p,64);
 for(int i=0;i<64;i++)p[i]=(i<16?key[i]:0)^0x5c;
 SHA256_Init(&opad);SHA256_Update(&opad,p,64);
}
static void digest(const char*text,unsigned char*out){
 SHA256_CTX p=ipad,q=opad;unsigned char inner[32],mac[32];
 SHA256_Update(&p,text,strlen(text));SHA256_Final(inner,&p);
 SHA256_Update(&q,inner,32);SHA256_Final(mac,&q);
 SHA256(mac,16,out);
}
int main(void){
 unsigned char key[16],wanted[32],planted[32],test[32];
 unhex("5F933DA6A1BD03C32DA5CBC25344F497",key,16);
 unhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747",wanted,32);
 init(key);
 int nb=0;
 for(unsigned mask=1;mask<(1u<<11);mask++){
  int n=__builtin_popcount(mask);if(n<2)continue;
  Segment*s=&sb[nb++];s->len=n;s->text[0]=0;
  for(int i=0;i<11;i++)if(mask&(1u<<i)){
   if(s->text[0])strcat(s->text," ");
   strcat(s->text,b[i]);
  }
 }
 if(nb!=2036)abort();
 char text[320],left[160];
 unsigned pmask=0x341;
 left[0]=0;
 for(int i=0;i<22;i++)if(pmask&(1u<<i)){
  if(left[0])strcat(left," ");
  strcat(left,a[i]);
 }
 snprintf(text,sizeof(text),"%s %s",left,sb[227].text);
 digest(text,planted);
 uint64_t count=0,hits=0,control=0;
 for(unsigned mask=1;mask<(1u<<22);mask++){
  int n=__builtin_popcount(mask);
  if(n<2||n>8)continue;
  left[0]=0;
  for(int i=0;i<22;i++)if(mask&(1u<<i)){
   if(left[0])strcat(left," ");
   strcat(left,a[i]);
  }
  for(int j=0;j<nb;j++){
   if(n+sb[j].len>10)continue;
   for(int order=0;order<2;order++){
    snprintf(text,sizeof(text),"%s %s",order?sb[j].text:left,order?left:sb[j].text);
    digest(text,test);count++;
    control+=!memcmp(test,planted,32);
    if(!memcmp(test,wanted,32)){hits++;printf("MATCH %s\n",text);}
   }
  }
 }
 printf("N13+N01 complete candidates=%llu original hits=%llu synthetic hits=%llu\n",
    (unsigned long long)count,(unsigned long long)hits,(unsigned long long)control);
 return count==273618994ULL&&hits==0&&control>=1?0:1;
}
