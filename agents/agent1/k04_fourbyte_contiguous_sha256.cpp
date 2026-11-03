// H-17 K04: complete brute force of ONE contiguous four-byte coupon replacement.
// Run with position 0..12 and shard 0..15. Each shard checks exactly 2^28 values.
// Immutable original K04 SHA256 commitment; no source/verifier modification.
// Correctness controls: actual source baseline digest and independent planted coupon.
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
using u32=std::uint32_t;
static constexpr u32 K[]={
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static constexpr u32 H[]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static constexpr u32 EXPECT[]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static inline u32 word(const std::array<unsigned char,16>& a,int p){return (u32(a[p])<<24)|(u32(a[p+1])<<16)|(u32(a[p+2])<<8)|a[p+3];}
static inline void sha16(const std::array<unsigned char,16>& in,u32 out[8]){
 u32 w[64];
 w[0]=word(in,0);w[1]=word(in,4);w[2]=word(in,8);w[3]=word(in,12);
 w[4]=0x80000000;for(int t=5;t<15;t++)w[t]=0;w[15]=128;
 for(int t=16;t<64;t++){
  u32 x=w[t-15],y=w[t-2];
  u32 s0=std::rotr(x,7)^std::rotr(x,18)^(x>>3),s1=std::rotr(y,17)^std::rotr(y,19)^(y>>10);
  w[t]=w[t-16]+s0+w[t-7]+s1;
 }
 u32 a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
 for(int t=0;t<64;t++){
  u32 s1=std::rotr(e,6)^std::rotr(e,11)^std::rotr(e,25);
  u32 ch=(e&f)^(~e&g);
  u32 temp=h+s1+ch+K[t]+w[t];
  u32 s0=std::rotr(a,2)^std::rotr(a,13)^std::rotr(a,22);
  u32 maj=(a&b)^(a&c)^(b&c);
  h=g;g=f;f=e;e=d+temp;d=c;c=b;b=a;a=temp+s0+maj;
 }
 out[0]=a+H[0];out[1]=b+H[1];out[2]=c+H[2];out[3]=d+H[3];
 out[4]=e+H[4];out[5]=f+H[5];out[6]=g+H[6];out[7]=h+H[7];
}
static constexpr std::array<unsigned char,16> BASE={0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static void set_four(std::array<unsigned char,16>& b,int p,u32 v){for(int i=0;i<4;i++)b[p+i]=(unsigned char)(v>>(8*i));}
static bool eq(const u32 a[8],const u32 b[8]){for(int i=0;i<8;i++)if(a[i]!=b[i])return false;return true;}
int main(int argc,char** argv){
 u32 digest[8];sha16(BASE,digest);
 constexpr u32 BASE_HASH[]={0x11a7f606,0x4781a6ac,0x7678dc6d,0xd24759af,0x95981c8a,0x927f8da4,0x43651535,0x4d34549b};
 if(!eq(digest,BASE_HASH)){std::fputs("FAIL baseline source SHA256\n",stderr);return 2;}
 auto sample=BASE;set_four(sample,4,0x12345678);sha16(sample,digest);
 constexpr u32 PLANTED[]={0x478424de,0xa3fc1243,0x34ac6622,0x616db148,0xe052675b,0xe20267d9,0xe31795f8,0xa147bf11};
 if(!eq(digest,PLANTED)){std::fputs("FAIL planted SHA256\n",stderr);return 3;}
 if(argc!=3){std::puts("SELF_TEST_PASS. Usage: k04_fourbyte position(0..12) shard(0..15)");return 0;}
 const int pos=std::atoi(argv[1]),shard=std::atoi(argv[2]);
 if(pos<0||pos>12||shard<0||shard>15){std::fputs("invalid position/shard\n",stderr);return 4;}
 const std::uint64_t lo=std::uint64_t(shard)<<28,hi=(std::uint64_t(shard)+1)<<28;
 auto b=BASE;auto start=std::chrono::steady_clock::now();
 std::uint64_t matches=0;
 for(std::uint64_t v=lo;v<hi;v++){
  set_four(b,pos,static_cast<u32>(v));sha16(b,digest);
  if(digest[0]==EXPECT[0]&&eq(digest,EXPECT)){
   ++matches;
   std::printf("ORIGINAL_K04_HIT pos=%d shard=%d overwritten=%08x coupon=",pos,shard,(unsigned int)v);
   for(auto c:b)std::printf("%02X",(unsigned)c);std::puts("");
  }
 }
 const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::printf("DONE pos=%d shard=%d checked=%llu actual_hits=%llu seconds=%.3f rate=%.0f\n",pos,shard,(unsigned long long)(hi-lo),(unsigned long long)matches,seconds,(hi-lo)/seconds);
 return 0;
}
