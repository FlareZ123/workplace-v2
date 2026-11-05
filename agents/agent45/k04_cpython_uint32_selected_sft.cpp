// H-17: exceptional selected RECOVER coupon from independently reseeded CPython Random(uint32).
// Fully specified bounded 32-bit seed attack, original source and commitments remain unchanged.
// CPython reference: https://github.com/python/cpython/blob/main/Modules/_randommodule.c
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <stdexcept>
#include <openssl/sha.h>
static constexpr uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static constexpr uint8_t goal[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static void outputs(uint32_t seed,uint32_t* w,int n){
  uint32_t mt[624];
  mt[0]=19650218u;
  for(int i=1;i<624;i++) mt[i]=1812433253u*(mt[i-1]^(mt[i-1]>>30))+(uint32_t)i;
  int i=1;
  for(int k=624;k>0;k--){
    mt[i]=(mt[i]^((mt[i-1]^(mt[i-1]>>30))*1664525u))+seed;
    i++;if(i==624){mt[0]=mt[623];i=1;}
  }
  for(int k=623;k>0;k--){
    mt[i]=(mt[i]^((mt[i-1]^(mt[i-1]>>30))*1566083941u))-(uint32_t)i;
    i++;if(i==624){mt[0]=mt[623];i=1;}
  }
  mt[0]=0x80000000u;
  for(int j=0;j<624;j++){
    uint32_t x=(mt[j]&0x80000000u)|(mt[(j+1)%624]&0x7fffffffu);
    mt[j]=mt[(j+397)%624]^(x>>1)^((x&1)?0x9908b0dfu:0u);
  }
  for(int j=0;j<n;j++){
    uint32_t y=mt[j];
    y^=y>>11;y^=(y<<7)&0x9d2c5680u;y^=(y<<15)&0xefc60000u;y^=y>>18;w[j]=y;
  }
}
static void keybytes(const uint32_t* w,int offset,int view,uint8_t* key){
  for(int j=0;j<4;j++){
    const uint32_t x=w[offset+((view&2)?3-j:j)];
    for(int k=0;k<4;k++)key[j*4+k]=uint8_t(x>>(8*((view&1)?k:3-k)))^mask[j*4+k];
  }
}
static bool candidate(const uint32_t* w,int offset,int view,const uint8_t* want){
  uint8_t key[16],digest[32];
  keybytes(w,offset,view,key);SHA256(key,16,digest);
  return std::memcmp(digest,want,32)==0;
}
static void controls(){
  uint32_t w[8];
  constexpr uint32_t seed0[8]={0xd82c07cdu,0x629f6fbeu,0xc2094cacu,0xe3e70682u,0x6baa9455u,0x0a5d2f34u,0x42485e3au,0xf728b4fau};
  outputs(0u,w,8);for(int i=0;i<8;i++)if(w[i]!=seed0[i])throw std::runtime_error("CPython seed 0 mismatch");
  constexpr uint32_t seedmax[8]={0xa2a6c909u,0x9e9c04f4u,0x3404e941u,0x3720bfa9u,0x9b7c60b4u,0x85bbddd4u,0x4a94f707u,0x9a6188fbu};
  outputs(0xffffffffu,w,8);for(int i=0;i<8;i++)if(w[i]!=seedmax[i])throw std::runtime_error("CPython seed max mismatch");
  constexpr uint32_t seedmid[8]={0xdc61f52du,0xf6af7e6fu,0x37c33e2du,0xa23b4b10u,0xd40cb916u,0xc2e05f9eu,0xbc5ace38u,0xafba2837u};
  outputs(0x12345678u,w,8);for(int i=0;i<8;i++)if(w[i]!=seedmid[i])throw std::runtime_error("CPython seed 0x12345678 mismatch");
  uint8_t key[16],synth[32];keybytes(w,2,3,key);SHA256(key,16,synth);
  if(!candidate(w,2,3,synth)||candidate(w,2,2,synth))throw std::runtime_error("planted coupon detection failed");
}
int main(int argc,char** argv){
  if(argc!=4){std::fprintf(stderr,"usage: selected START COUNT MAX_OFFSET\n");return 2;}
  try{
    uint64_t start=std::stoull(argv[1]),count=std::stoull(argv[2]);
    int maxoffset=std::stoi(argv[3]);
    if(start>=0x100000000ULL||count==0||count>0x100000000ULL-start||maxoffset<0||maxoffset>8)throw std::runtime_error("bad range");
    controls();
    uint64_t checks=0,hits=0;
    for(uint64_t seed=start;seed<start+count;seed++){
      uint32_t w[12];outputs(uint32_t(seed),w,maxoffset+4);
      for(int off=0;off<=maxoffset;off++)for(int view=0;view<4;view++){
        if(candidate(w,off,view,goal)){std::printf("ORIGINAL_K04_HIT seed=%llu off=%d view=%d\n",(unsigned long long)seed,off,view);hits++;}
        checks++;
      }
    }
    std::printf("SOURCE_CPYTHON_CONTROLS_PASS start=%llu count=%llu offsets=0..%d checks=%llu hits=%llu\n",
       (unsigned long long)start,(unsigned long long)count,maxoffset,(unsigned long long)checks,(unsigned long long)hits);
    return hits?1:0;
  }catch(const std::exception&e){std::fprintf(stderr,"ERROR %s\n",e.what());return 2;}
}
