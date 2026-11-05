/* Agent36 original K08 whole-nonce serialization / eight source captions.
 * 15,925,248 distinct 4x4 order assignments, each checked against eight
 * original-source phrases and original SHA256(HMAC16) commitment.
 * Build: cc -O3 -fopenmp -Wno-deprecated-declarations
 *        agents/agent36/k08_nonce_matrix_sft.c -lcrypto -o k08_nonce_matrix
 * Run: OMP_NUM_THREADS=8 ./k08_nonce_matrix
 */
#include <assert.h>
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <omp.h>
static const unsigned char base[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char n02control[16]={0xbf,0x88,0x93,0x59,0xb0,0x30,0x3f,0x2b,0x2b,0x2f,0xd9,0x6a,0xe8,0x41,0x21,0x0b};
static const char* phrase[]={
"at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on",
"a good watch leaves the room ready for the next pair of hands",
"the little lamp stays on until the corridor has gone quiet",
"leave the light on for the next watch",
"back before the first boat",
"i wanted the line to hold the sea the end of the night and the voices at the table",
"the sea looks different when you have finally finished your tea",
"nobody should have to make their first cup alone after a bad night"};
static unsigned order[24][4];
static void init(void){
 unsigned n=0;
 for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)
 for(unsigned c=0;c<4;c++)for(unsigned d=0;d<4;d++){
   if(a==b||a==c||a==d||b==c||b==d||c==d)continue;
   order[n][0]=a;order[n][1]=b;order[n][2]=c;order[n][3]=d;++n;
 }
 assert(n==24);
}
static void keyed(const unsigned char key[16],const char *msg,
                   unsigned char digest[32],unsigned char *component){
 unsigned char ipad[64],opad[64],inner[32],outer[32];SHA256_CTX state;
 memset(ipad,0x36,64);memset(opad,0x5c,64);
 for(int i=0;i<16;i++){ipad[i]^=key[i];opad[i]^=key[i];}
 SHA256_Init(&state);SHA256_Update(&state,ipad,64);
 SHA256_Update(&state,msg,strlen(msg));SHA256_Final(inner,&state);
 SHA256_Init(&state);SHA256_Update(&state,opad,64);
 SHA256_Update(&state,inner,32);SHA256_Final(outer,&state);
 if(component)memcpy(component,outer,16);
 SHA256(outer,16,digest);
}
static void nonce_at(uint64_t rank,unsigned char nonce[16]){
 unsigned spec[5];
 for(int i=0;i<5;i++){spec[i]=(unsigned)(rank%24);rank/=24;}
 int transpose=(int)rank;unsigned char matrix[16];
 for(int j=0;j<16;j++)matrix[j]=transpose?base[4*(j%4)+j/4]:base[j];
 for(int lane=0;lane<4;lane++)for(int j=0;j<4;j++)
    nonce[4*lane+j]=matrix[4*order[spec[4]][lane]+order[spec[lane]][j]];
}
int main(void){
 init();unsigned char observed[32],component[16];
 keyed(base,phrase[1],observed,component);
 assert(!memcmp(component,n02control,16));
 const uint64_t plant_rank=2*24*24*24+9;
 unsigned char plantkey[16],plantsha[32];
 nonce_at(plant_rank,plantkey);keyed(plantkey,phrase[0],plantsha,NULL);
 const uint64_t size=2ULL*24*24*24*24*24;
 unsigned long long original=0,planted=0;
 #pragma omp parallel reduction(+:original,planted)
 {
  unsigned char key[16],hash[32],kcomponent[16];
  #pragma omp for schedule(static)
  for(uint64_t rank=0;rank<size;rank++){
    nonce_at(rank,key);
    for(int p=0;p<8;p++){
      keyed(key,phrase[p],hash,kcomponent);
      if(!memcmp(hash,plantsha,32)&&p==0)planted++;
      if(!memcmp(hash,target,32)){
        #pragma omp critical
        {fprintf(stderr,"ORIGINAL_K08_HIT rank=%llu phrase=%s component=",
                 (unsigned long long)rank,phrase[p]);
         for(int k=0;k<16;k++)fprintf(stderr,"%02X",kcomponent[k]);
         fputc('\n',stderr);}
        original++;
      }
    }
  }
 }
 printf("nonce_order_models=%llu full_k08_checks=%llu planted=%llu original_hits=%llu\n",
        (unsigned long long)size,(unsigned long long)(size*8),planted,original);
 assert(planted==1);
 return original?0:1;
}
