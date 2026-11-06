// H-17 original printer-only variable-gap SFT, Agent12, 2026-11-06.
// Input: original unmodified resources/evidence/print/spool-reconstruction.log.
// Compile on CI with a C++17 compiler and pthread support.
// The exact GF(2) inverse of 0300 for xoshiro128** is frozen as four states.
// First-packet regeneration, three planted 17-gap positives, and second-packet
// 0..2^32-1 searches are checked. Never reads selected RECOVER ACK2.
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>
using U32=uint32_t; using U64=uint64_t;
using S32=std::array<U32,4>; using S64=std::array<U64,2>;
using Packet=std::array<unsigned char,16>;
static U32 rol32(U32 x,int n){return (x<<n)|(x>>(32-n));}
static U64 rol64(U64 x,int n){return (x<<n)|(x>>(64-n));}
static U64 ror64(U64 x,int n){return (x>>n)|(x<<(64-n));}
static U32 xs(S32 &s){U32 t=s[0]^(s[0]<<11);t^=t>>8;U32 v=s[3]^(s[3]>>19)^t;s={s[1],s[2],s[3],v};return v;}
static U32 xo(S32 &s){U32 v=rol32(s[1]*5u,7)*9u,t=s[1]<<9;
 s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rol32(s[3],11);return v;}
static U64 xr(S64 &s){U64 v=rol64(s[0]*5ull,7)*9ull,t=s[0]^s[1];
 s={rol64(s[0],24)^t^(t<<16),rol64(t,37)};return v;}
static U64 unstar(U64 y){return ror64(y*0x8e38e38e38e38e39ull,7)*0xcccccccccccccccdull;}
static Packet hex16(const std::string &hex){
 if(hex.size()!=32)throw std::runtime_error("wrong hex width");
 Packet p{};for(int i=0;i<16;i++)p[i]=static_cast<unsigned char>(std::stoul(hex.substr(2*i,2),nullptr,16));return p;
}
static std::array<Packet,2> load(const std::string &path){
 std::ifstream in(path);if(!in)throw std::runtime_error("source unavailable");
 std::array<Packet,2>a{};int found=0,selected=0;std::string line;
 while(std::getline(in,line)){
  if(line.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER")!=std::string::npos){selected++;continue;}
  for(int k=0;k<2;k++){
   std::string name="JOB=PS-261003-030"+std::to_string(k)+" ATTEMPT=1 STATE=ACK ";
   if(line.find(name)!=std::string::npos){
    auto pos=line.find("PAYLOAD=");if(pos==std::string::npos)throw std::runtime_error("payload absent");
    a[k]=hex16(line.substr(pos+8,32));found++;
   }
  }
 }
 if(found!=2||selected!=1||a[0]!=hex16("FBBBC54356483F5864BB3F06794518A5")||
    a[1]!=hex16("64176B6C3A91BD06B12FC0D90B3A7DB4"))
  throw std::runtime_error("original source anchors changed");
 return a;
}
static std::array<U32,4> words32(Packet p,bool little,bool reverse){
 std::array<U32,4>o{};for(int i=0;i<4;i++)for(int b=0;b<4;b++){
  if(little)o[i]|=U32(p[4*i+b])<<(8*b);else o[i]=(o[i]<<8)|p[4*i+b];
 }if(reverse)std::reverse(o.begin(),o.end());return o;
}
static std::array<U64,2> words64(Packet p,bool little,bool reverse){
 std::array<U64,2>o{};for(int i=0;i<2;i++)for(int b=0;b<8;b++){
  if(little)o[i]|=U64(p[8*i+b])<<(8*b);else o[i]=(o[i]<<8)|p[8*i+b];
 }if(reverse)std::swap(o[0],o[1]);return o;
}
// GF(2)-inverted initial states for the four exact 0300 xoshiro128**
// packet presentations: big-forward, big-reverse, little-forward, little-reverse.
// The generator must reproduce all four source words from each frozen state.
static constexpr S32 XOSH_PRE[4]={
 {0xC4F43F34u,0x5E4F746Fu,0x935AF8CAu,0x7884826Cu},
 {0x59144F00u,0x7EE8F201u,0x0564DE59u,0x8111FE91u},
 {0x6C7B6610u,0x27BEBED5u,0x44BEBB43u,0x5FB09E6Au},
 {0x34391A61u,0x93B7B16Fu,0xE938F974u,0x5420A7E7u}
};
static S64 invert_xoroshiro(std::array<U64,2>o){
 U64 a=unstar(o[0]),b=unstar(o[1]),y=b^rol64(a,24);
 U64 t=y^(y<<16)^(y<<32)^(y<<48);S64 s{a,t^a},test=s;
 for(auto word:o)if(xr(test)!=word)throw std::runtime_error("xoroshiro inversion failed");
 return s;
}
struct Summary {U64 first=0,full=0;};
static Summary find32(S32 s,std::array<U32,4> goal,U64 end,bool xoshiro){
 Summary n{};for(U64 gap=0;gap<=end;gap++){
  S32 c=s;U32 first=xoshiro?xo(c):xs(c);
  if(first==goal[0]){n.first++;bool all=true;
   for(int j=1;j<4;j++)if((xoshiro?xo(c):xs(c))!=goal[j]){all=false;break;}
   if(all)n.full++;
  }if(xoshiro)xo(s);else xs(s);
 }return n;
}
static Summary find64(S64 s,std::array<U64,2>goal,U64 end){
 Summary n{};for(U64 gap=0;gap<=end;gap++){
  S64 c=s;if(xr(c)==goal[0]){n.first++;if(xr(c)==goal[1])n.full++;}xr(s);
 }return n;
}
static void synthetic(){
 S32 a32{0x12345678u,0x87654321u,0xDEADBEEFu,0x0A5C9E3Bu};
 for(bool xoshiro:{false,true}){S32 s=a32;for(int i=0;i<4;i++)if(xoshiro)xo(s);else xs(s);
  S32 post=s;for(int i=0;i<17;i++)if(xoshiro)xo(s);else xs(s);
  std::array<U32,4>next{};for(auto &v:next)v=xoshiro?xo(s):xs(s);
  if(find32(post,next,100,xoshiro).full!=1)throw std::runtime_error("32bit planted positive failed");
 }
 S64 s{0x1234567890ABCDEFull,0xFEDCBA9876543210ull};std::array<U64,2> p{},q{};
 for(auto &v:p)v=xr(s);S64 post=s;for(int i=0;i<17;i++)xr(s);for(auto &v:q)v=xr(s);
 S64 reconstructed=invert_xoroshiro(p);for(int i=0;i<2;i++)xr(reconstructed);
 if(reconstructed!=post||find64(post,q,100).full!=1)throw std::runtime_error("64bit planted positive failed");
}
int main(int argc,char**argv){
 try{
  if(argc<2)throw std::runtime_error("need original spool path");
  const auto packets=load(argv[1]);
  const U64 maxgap=argc>2?std::strtoull(argv[2],nullptr,10):0xffffffffull;
  synthetic();
  std::array<Summary,12>results{};std::vector<std::thread> jobs;
  for(int m=0;m<3;m++)for(int v=0;v<4;v++)jobs.emplace_back([&,m,v]{
   bool little=v>=2, reverse=v%2;
   if(m==2){
    auto first=words64(packets[0],little,reverse),next=words64(packets[1],little,reverse);
    S64 s=invert_xoroshiro(first);xr(s);xr(s);results[m*4+v]=find64(s,next,maxgap);
   }else{
    auto first=words32(packets[0],little,reverse),next=words32(packets[1],little,reverse);
    S32 s=m==0?XOSH_PRE[v]:first;
    if(m==0)for(auto word:first)if(xo(s)!=word)throw std::runtime_error("first source xoshiro packet failed");
    results[m*4+v]=find32(s,next,maxgap,m==0);
   }
  });
  for(auto &j:jobs)j.join();
  U64 total=0,first_total=0;
  for(int m=0;m<3;m++)for(int v=0;v<4;v++){
   auto s=results[m*4+v];total+=s.full;first_total+=s.first;
   std::printf("%s view%d gaps=%llu first=%llu full=%llu\n",m==0?"xoshiro128**":m==1?"xorshift128":"xoroshiro128**",v,
    (unsigned long long)(maxgap+1),(unsigned long long)s.first,(unsigned long long)s.full);
  }
  if(total)throw std::runtime_error("original full second packet matched");
  std::printf("H17_SOURCE_NO_MATCH first_lane_total=%llu tested_per_view=%llu planted_17_PASS=true\n",
     (unsigned long long)first_total,(unsigned long long)(maxgap+1));
 }catch(const std::exception &e){std::fprintf(stderr,"ERROR %s\n",e.what());return 1;}
}
