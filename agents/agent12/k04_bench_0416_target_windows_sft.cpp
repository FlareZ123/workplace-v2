// H17 K04: selected-job same-RECOVER/bench xoshiro/xorshift/xoroshiro producer.
// Source: genuine PS-261003-0416 16:40 ACK1, bench, RECOVER.
// Search actual K04 SHA256(coupon XOR original mask), 12 source/target layouts.
// Run 2 shards [0,8388607] and [8388608,16777215]. Original target unchanged.
// C++17, libcrypto SHA256, std::thread. Agent12, 2026-11-06.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <openssl/sha.h>
using U32=uint32_t;using U64=uint64_t;using S32=std::array<U32,4>;using S64=std::array<U64,2>;
using B16=std::array<unsigned char,16>;using B32=std::array<unsigned char,32>;
static U32 r32(U32 x,int k){return (x<<k)|(x>>(32-k));}
static U64 r64(U64 x,int k){return (x<<k)|(x>>(64-k));}
static U64 rr64(U64 x,int k){return (x>>k)|(x<<(64-k));}
static U32 xo(S32 &s){U32 v=r32(s[1]*5u,7)*9u,t=s[1]<<9;
 s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=r32(s[3],11);return v;}
static U32 xs(S32 &s){U32 t=s[0]^(s[0]<<11);t^=t>>8;
 U32 v=s[3]^(s[3]>>19)^t;s={s[1],s[2],s[3],v};return v;}
static U64 xr(S64 &s){U64 v=r64(s[0]*5ull,7)*9ull,t=s[0]^s[1];
 s={r64(s[0],24)^t^(t<<16),r64(t,37)};return v;}
static U64 unstar(U64 x){return rr64(x*0x8e38e38e38e38e39ull,7)*0xcccccccccccccccdull;}
static int digit(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return 10+c-'A';if(c>='a'&&c<='f')return 10+c-'a';throw std::runtime_error("bad hex");}
template<size_t N>static std::array<unsigned char,N> fromhex(const std::string &x){
 if(x.size()!=2*N)throw std::runtime_error("bad hex width");
 std::array<unsigned char,N>o{};for(size_t i=0;i<N;i++)o[i]=16*digit(x[2*i])+digit(x[2*i+1]);return o;
}
static const B16 MASK=fromhex<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
static const B32 GOAL=fromhex<32>("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
static B16 preserved(const std::string &path){
 std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("original spool unavailable");
 std::string all((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 unsigned char sha[32];SHA256(reinterpret_cast<const unsigned char*>(all.data()),all.size(),sha);
 const B32 pinned=fromhex<32>("7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 if(!std::equal(sha,sha+32,pinned.begin()))throw std::runtime_error("source spool SHA changed");
 const std::string selected="JOB=PS-261003-0416 ATTEMPT=1 STATE=ACK CLASS=RECOVER PAYLOAD=";
 auto start=all.find(selected);
 if(start==std::string::npos)throw std::runtime_error("source 0416 absent");
 auto coupon=fromhex<16>(all.substr(start+selected.size(),32));
 if(coupon!=fromhex<16>("F1F5A127EA44F563935C63F8A59A2801"))throw std::runtime_error("0416 coupon changed");
 return coupon;
}
static std::array<U32,4> w32(B16 p,bool le,bool reverse){
 std::array<U32,4>w{};for(int i=0;i<4;i++)for(int j=0;j<4;j++)
  if(le)w[i]|=U32(p[4*i+j])<<(j*8);else w[i]=(w[i]<<8)|p[4*i+j];
 if(reverse)std::reverse(w.begin(),w.end());return w;
}
static std::array<U64,2> w64(B16 p,bool le,bool reverse){
 std::array<U64,2>w{};for(int i=0;i<2;i++)for(int j=0;j<8;j++)
  if(le)w[i]|=U64(p[8*i+j])<<(j*8);else w[i]=(w[i]<<8)|p[8*i+j];
 if(reverse)std::swap(w[0],w[1]);return w;
}
// Original exact 128-rank GF(2) inversions of the four genuine 0416 views.
// Each value is checked by regenerating the *whole source packet* below.
static constexpr S32 XOPRE[4]={
 {0xAF364088u,0x1305109Bu,0xD72349C1u,0x1576E4DCu},
 {0xE3357FA0u,0x16D428FCu,0x4580C508u,0x20749E72u},
 {0x47A72EE3u,0x1095AC2Du,0x2638A366u,0x12BC994Au},
 {0x678D208Du,0x18667395u,0x01A8BEB1u,0xDA602B25u}
};
static S64 inverse64(std::array<U64,2> w){
 U64 a=unstar(w[0]),b=unstar(w[1]),y=b^r64(a,24);
 U64 t=y^(y<<16)^(y<<32)^(y<<48);S64 s{a,a^t},check=s;
 for(auto out:w)if(xr(check)!=out)throw std::runtime_error("64bit whole-packet source mismatch");
 return s;
}
static B16 coupon32(S32 s,bool xoshiro,bool le,bool reverse){
 U32 w[4];for(auto &a:w)a=xoshiro?xo(s):xs(s);
 B16 o{};for(int i=0;i<4;i++){U32 v=w[reverse?3-i:i];
  for(int j=0;j<4;j++)o[4*i+j]=static_cast<unsigned char>(v>>(le?j*8:(3-j)*8));
 }return o;
}
static B16 coupon64(S64 s,bool le,bool reverse){
 U64 w[2];for(auto &a:w)a=xr(s);
 B16 o{};for(int i=0;i<2;i++){U64 v=w[reverse?1-i:i];
  for(int j=0;j<8;j++)o[8*i+j]=static_cast<unsigned char>(v>>(le?j*8:(7-j)*8));
 }return o;
}
static B32 digest(B16 coupon){
 unsigned char in[16];for(int i=0;i<16;i++)in[i]=coupon[i]^MASK[i];
 B32 out{};SHA256(in,16,out.data());return out;
}
static void run(int m,int view,B16 first,U64 begin,U64 end){
 bool le=view>=2,rev=(view%2)!=0;
 S32 s32{};S64 s64{};
 if(m==2){auto w=w64(first,le,rev);s64=inverse64(w);xr(s64);xr(s64);}
 else{
  auto w=w32(first,le,rev);
  s32=m==0?XOPRE[view]:w;
  if(m==0)for(auto v:w)if(xo(s32)!=v)throw std::runtime_error("32bit whole-packet source mismatch");
 }
 // Full pipeline positive: independently planted future output at gap17.
 B16 planted{};
 if(m==2){auto a=s64;for(int i=0;i<17;i++)xr(a);planted=coupon64(a,le,rev);}
 else {auto a=s32;for(int i=0;i<17;i++)if(m==0)xo(a);else xs(a);planted=coupon32(a,m==0,le,rev);}
 const auto planted_target=digest(planted);
 U64 hit=0,pos=0;
 for(U64 i=0;i<begin;i++)if(m==2)xr(s64);else if(m==0)xo(s32);else xs(s32);
 for(U64 gap=begin;gap<=end;gap++){
  auto p=m==2?coupon64(s64,le,rev):coupon32(s32,m==0,le,rev);
  auto h=digest(p);
  if(h==GOAL){hit++;std::printf("ORIGINAL_HIT model%d view%d gap%llu\n",m,view,(unsigned long long)gap);}
  if(gap<=17 && h==planted_target)pos++;
  if(m==2)xr(s64);else if(m==0)xo(s32);else xs(s32);
 }
 if(pos!=((begin<=17&&end>=17)?1ull:0ull))throw std::runtime_error("synthetic gap17 not found exactly once");
 std::printf("K04_HASH model%d view%d begin=%llu end=%llu tested=%llu original_hits=%llu synthetic=%llu\n",
 m,view,(unsigned long long)begin,(unsigned long long)end,(unsigned long long)(end-begin+1),(unsigned long long)hit,(unsigned long long)pos);
 if(hit)throw std::runtime_error("authentic K04 found; examine target urgently");
}
int main(int argc,char**argv){
 try{
  if(argc<4)throw std::runtime_error("Usage: program original_spool.log begin_gap end_gap");
  U64 begin=std::strtoull(argv[2],nullptr,10),end=std::strtoull(argv[3],nullptr,10);
  if(end<begin||end>16777215ull)throw std::runtime_error("range outside frozen 2^24-gap experiment");
  B16 coupon=preserved(argv[1]);
  if(digest(fromhex<16>("A9A9DC5731A5E2AE879C47215C2559D5"))==GOAL)
   throw std::runtime_error("copied ACK unexpectedly authentic");
  std::vector<std::thread>tasks;
  for(int m=0;m<3;m++)for(int v=0;v<4;v++)tasks.emplace_back(run,m,v,coupon,begin,end);
  for(auto &t:tasks)t.join();
 }catch(const std::exception &e){std::fprintf(stderr,"ERROR %s\n",e.what());return 1;}
}
