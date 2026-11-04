// K04 original-source 624-word MT pool-as-seed, distinct from contiguous-output mosaics.
// C++17/OpenSSL worker; invoked by k04_624_seedpool_sft.py.
#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
using namespace std;
constexpr uint32_t M=0x9908B0DF;
constexpr int GROUPN[4]={528,88,4,4};
constexpr unsigned char MASK[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr unsigned char TARGET[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
uint32_t untemper(uint32_t x){
 uint32_t y=x;
 for(int i=0;i<6;i++)y=x^(y>>18);x=y;
 for(int i=0;i<6;i++)y=x^((y<<15)&0xEFC60000);x=y;
 for(int i=0;i<6;i++)y=x^((y<<7)&0x9D2C5680);x=y;
 for(int i=0;i<6;i++)y=x^(y>>11);x=y;
 return x;
}
uint32_t temper(uint32_t x){
 x^=x>>11; x^=(x<<7)&0x9D2C5680; x^=(x<<15)&0xEFC60000; x^=x>>18;return x;
}
uint32_t getword(const unsigned char *p,bool big){
 if(big)return (uint32_t(p[0])<<24)|(uint32_t(p[1])<<16)|(uint32_t(p[2])<<8)|uint32_t(p[3]);
 return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);
}
void twist(uint32_t s[624]){
 for(int i=0;i<624;i++){
  uint32_t y=(s[i]&0x80000000)|(s[(i+1)%624]&0x7fffffff);
  s[i]=s[(i+397)%624]^(y>>1)^((y&1)?M:0);
 }
}
void coupon(const uint32_t state[624],int offset,int serialize,int outputmode,unsigned char out[16]){
 for(int k=0;k<4;k++){
  uint32_t w=state[offset+((serialize&2)?3-k:k)];
  if(outputmode)w=temper(w);
  for(int j=0;j<4;j++)out[4*k+j]=uint8_t(w>>(((serialize&1)?(3-j):j)*8));
 }
}
void digest(const unsigned char input[16],unsigned char h[32]){
 unsigned char c[16];for(int i=0;i<16;i++)c[i]=input[i]^MASK[i];SHA256(c,16,h);
}
int main(int argc,char**argv){
 if(argc<2||argc>4){cerr<<"usage: k04_624_seedpool seed_pool.bin [native_word_mode:0..15] [max_stage:0..620]\n";return 2;}
 int mode=argc>=3?stoi(argv[2]):-1, max_stage=argc>=4?stoi(argv[3]):620;
 if(mode>15||mode < -1||max_stage<307||max_stage>620) return 2;
 for(uint32_t v: {0u,1u,0x12345678u,0xFFFFFFFFu,0xF5A127E3u}) {
  if(untemper(temper(v))!=v){cerr<<"MT temper inverse failed";return 3;}
 }
 ifstream f(argv[1],ios::binary);
 if(!f){cerr<<"Cannot read fixture\n";return 2;}
 vector<unsigned char> data((istreambuf_iterator<char>(f)),{});
 if(data.size()!=624*4){cerr<<"Expected exact 2496 fixture bytes\n";return 2;}
 array<int,4> order={0,1,2,3}; uint64_t checks=0,hits=0,control=0;
 unsigned char h[32],raw[16],positive_digest[32];
 // Synthetic positive from source, under known order, variant and selected input mode.
 {uint32_t a[624];const int positive_mode=mode>=0?mode:15;
 for(int i=0;i<624;i++){
  uint32_t w=getword(&data[4*i],false);
  int group=i<528?0:(i<616?1:(i<620?2:3));
  a[i]=positive_mode&(1<<group)?untemper(w):w;
 }
 twist(a);coupon(a,307,0,1,raw);digest(raw,positive_digest);}
 do{
  // 8-option printer layout; 4 options for recorder, signed ink and procedure.
  for(int variant=0;variant<8*4*4*4;variant++){
   int t=variant,options[4];options[0]=t%8;t/=8;
   for(int g=1;g<4;g++){options[g]=t%4;t/=4;}
   int totalm=mode>=0?1:16;
   for(int mi=0;mi<totalm;mi++){
    int native_mode=mode>=0?mode:mi;
    uint32_t a[624];int out=0;
    for(int go:order){
     int groupstart=0;for(int g=0;g<go;g++)groupstart+=GROUPN[g];
     const int count=GROUPN[go],opt=options[go];
     for(int k=0;k<count;k++){
      int idx=k;
      if(go==0){int packet=k/4,lane=k%4;
        if(opt&2)packet=131-packet;
        if(opt&4)lane=3-lane;
        idx=4*packet+lane;
      }else if(opt&2)idx=count-1-k;
      uint32_t w=getword(&data[4*(groupstart+idx)],opt&1);
      if(native_mode&(1<<go))w=untemper(w);
      a[out++]=w;
     }
    }
    if(out!=624){cerr<<"input count corruption\n";return 3;}
    twist(a);
    for(int stage=0;stage<=max_stage;stage++){
     for(int outputmode=0;outputmode<2;outputmode++){
      for(int ser=0;ser<4;ser++){
       coupon(a,stage,ser,outputmode,raw);
       digest(raw,h);checks++;
       if(!memcmp(h,TARGET,32)){
        hits++;printf("ORIGINAL_HIT mode=%d variant=%d order=%d%d%d%d stage=%d ser=%d output=%d raw=",native_mode,variant,order[0],order[1],order[2],order[3],stage,ser,outputmode);
        for(unsigned char c:raw)printf("%02X",c);printf("\n");fflush(stdout);
       }
       if(!memcmp(h,positive_digest,32))control++;
      }
     }
    }
   }
  }
 }while(next_permutation(order.begin(),order.end()));
 printf("COMPLETE assignments=%llu original_hits=%llu synthetic_hits=%llu modes=%d windows=%d\n",(unsigned long long)checks,(unsigned long long)hits,(unsigned long long)control,mode,max_stage+1);
 return (hits>0)?10:((control==0)?3:0);
}
