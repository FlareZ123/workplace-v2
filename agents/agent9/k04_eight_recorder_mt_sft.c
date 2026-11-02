/*
 H-17 K04 eight distinct TRP2 donor construction, OpenSSL C / OpenMP.
 Input records are frozen directly from original recorder file (SHA256
 5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba).
 Original selected 18:02 printer ACK is excluded from candidate construction.
 Model: output = temper(middle XOR mt_twist(predecessor_highbit,successor))
         XOR original K04 mask, independently for four aligned 32bit words.
 Twelve CRC-valid archive-latch sources, then all sixteen including bad CRC.
 Read-only original REC8 SHA256 acceptance target; no original files changed.
 Compile: cc -O3 -fopenmp k04_eight_recorder_mt_sft.c -lcrypto -o k04_eight
 Run: OMP_NUM_THREADS=5 ./k04_eight
*/
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <omp.h>
enum { N=16 };
static const struct {int record, valid; const char *bytes;} donor[N]={
 {0,1,"6DCDA00E"},{2,1,"6FC2B743"},{8,1,"909A3940"},
 {10,1,"F01E4572"},{12,1,"8052760C"},{14,0,"C2DE39CC"},
 {17,1,"BFB00270"},{28,1,"9359AC1F"},{34,1,"FF8B7820"},
 {40,1,"5E9C08AB"},{41,0,"BA194782"},{45,1,"30D78977"},
 {53,1,"0A56E858"},{72,0,"F2595C84"},{75,1,"42BFD053"},
 {77,0,"2A4EE66D"}
};
static const char *maskhex="8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *targethex="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static uint32_t table[4][N][N][2];
static uint32_t states[N], mask[4], target[8];
static uint32_t ur(uint32_t y,int k){uint32_t x=y;for(int i=0;i<6;i++)x=y^(x>>k);return x;}
static uint32_t ul(uint32_t y,int k,uint32_t m){uint32_t x=y;for(int i=0;i<6;i++)x=y^((x<<k)&m);return x;}
static uint32_t untemper(uint32_t y){return ur(ul(ul(ur(y,18),15,0xEFC60000u),7,0x9D2C5680u),11);}
static uint32_t temper(uint32_t y){y^=y>>11;y^=(y<<7)&0x9D2C5680u;y^=(y<<15)&0xEFC60000u;y^=y>>18;return y;}
static uint32_t twist(int high,uint32_t next){uint32_t v=((uint32_t)high<<31)|(next&0x7FFFFFFFu);return (v>>1)^((v&1)?0x9908B0DFu:0);}
static unsigned hx(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;if(c>='a'&&c<='f')return c-'a'+10;exit(7);}
static void hex(const char*s,unsigned char*dst,int n){if((int)strlen(s)!=2*n)exit(7);for(int i=0;i<n;i++)dst[i]=(hx(s[2*i])<<4)|hx(s[2*i+1]);}
static uint32_t le32(const unsigned char*b){return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);}
static uint32_t be32(const unsigned char*b){return (uint32_t)b[3]|((uint32_t)b[2]<<8)|((uint32_t)b[1]<<16)|((uint32_t)b[0]<<24);}
static void set32(unsigned char*b,uint32_t x){b[0]=x&255;b[1]=(x>>8)&255;b[2]=(x>>16)&255;b[3]=(x>>24)&255;}
static void setup(void){
 unsigned char bytes[32];
 for(int i=0;i<N;i++){hex(donor[i].bytes,bytes,4);states[i]=untemper(le32(bytes));}
 hex(maskhex,bytes,16);for(int i=0;i<4;i++)mask[i]=le32(bytes+4*i);
 hex(targethex,bytes,32);for(int i=0;i<8;i++)target[i]=be32(bytes+4*i);
}
static void selftest(void){
 unsigned char msg[16],block[64]={0},digest[32];SHA256_CTX ctx;
 int m[4]={0,2,4,6},s[4]={1,3,5,7},b[4]={0,1,0,1};
 for(int j=0;j<4;j++)set32(msg+4*j,temper(states[m[j]]^twist(b[j],states[s[j]]))^mask[j]);
 SHA256(msg,16,digest);memcpy(block,msg,16);block[16]=0x80;block[63]=0x80;
 SHA256_Init(&ctx);SHA256_Transform(&ctx,block);
 for(int i=0;i<8;i++)if(ctx.h[i]!=be32(digest+4*i))exit(9);
 puts("synthetic_SHA256_Transform=PASS");
}
static void run(const char *mode){
 int selected[N],n=0; for(int i=0;i<N;i++)if(!strcmp(mode,"all")||donor[i].valid)selected[n++]=i;
 if((!strcmp(mode,"valid")&&n!=12)||(!strcmp(mode,"all")&&n!=16))exit(2);
 for(int j=0;j<4;j++)for(int x=0;x<n;x++)for(int y=0;y<n;y++)for(int b=0;b<2;b++)
  table[j][x][y][b]=temper(states[selected[x]]^twist(b,states[selected[y]]))^mask[j];
 unsigned long long checked=0,found=0;
 double begin=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,1) reduction(+:checked,found)
 for(int a=0;a<n;a++){
  unsigned char block[64]={0};SHA256_CTX ctx;block[16]=0x80;block[63]=0x80;
  uint64_t local=0;
  for(int b=0;b<n;b++)if(b!=a){
   uint32_t used0=(1u<<a)|(1u<<b);
   for(int hi0=0;hi0<2;hi0++){
    set32(block,table[0][a][b][hi0]);
    for(int c=0;c<n;c++)if(!(used0&(1u<<c)))
    for(int d=0;d<n;d++)if(!(used0&(1u<<d))&&d!=c){
     uint32_t used1=used0|(1u<<c)|(1u<<d);
     for(int hi1=0;hi1<2;hi1++){
      set32(block+4,table[1][c][d][hi1]);
      for(int e=0;e<n;e++)if(!(used1&(1u<<e)))
      for(int f=0;f<n;f++)if(!(used1&(1u<<f))&&f!=e){
       uint32_t used2=used1|(1u<<e)|(1u<<f);
       for(int hi2=0;hi2<2;hi2++){
        set32(block+8,table[2][e][f][hi2]);
        for(int g=0;g<n;g++)if(!(used2&(1u<<g)))
        for(int h=0;h<n;h++)if(!(used2&(1u<<h))&&h!=g){
         for(int hi3=0;hi3<2;hi3++){
          set32(block+12,table[3][g][h][hi3]);
          SHA256_Init(&ctx);SHA256_Transform(&ctx,block);local++;
          if(ctx.h[0]==target[0]&&ctx.h[1]==target[1]&&ctx.h[2]==target[2]&&ctx.h[3]==target[3]
          &&ctx.h[4]==target[4]&&ctx.h[5]==target[5]&&ctx.h[6]==target[6]&&ctx.h[7]==target[7]){
           found++;
           #pragma omp critical
           {
            printf("FOUND K04=");for(int z=0;z<16;z++)printf("%02X",block[z]);
            printf(" DONORS %d %d %d %d %d %d %d %d HIGH %d%d%d%d\n",
             donor[selected[a]].record,donor[selected[b]].record,donor[selected[c]].record,donor[selected[d]].record,
             donor[selected[e]].record,donor[selected[f]].record,donor[selected[g]].record,donor[selected[h]].record,
             hi0,hi1,hi2,hi3);fflush(stdout);
           }
          }
         }
        }
       }
      }
     }
    }
   }
  }
  checked+=local;
 }
 uint64_t total=16;for(int i=0;i<8;i++)total*=n-i;
 printf("mode=%s donors=%d checked=%llu expected=%" PRIu64 " matches=%llu seconds=%.3f\n",
  mode,n,checked,total,found,omp_get_wtime()-begin);
 if(checked!=total)exit(8);
}
int main(void){setup();selftest();run("valid");run("all");return 0;}
