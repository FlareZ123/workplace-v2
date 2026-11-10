// Original-source H-17 K04 native-MT pre-temper five-bit fault SFT (Agent 3).
// C++20 + OpenSSL libcrypto. Usage: binary spool.log [shard_id shard_count]
#include <array>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>
using U64=uint64_t;
using B16=std::array<unsigned char,16>;
using B32=std::array<unsigned char,32>;
struct D {U64 lo,hi;};
static B16 hex16(const std::string&s){
 if(s.size()!=32)throw std::runtime_error("bad hex16");
 B16 a{};
 for(int i=0;i<16;++i){unsigned x=0;if(std::sscanf(s.substr(i*2,2).c_str(),"%2x",&x)!=1)throw std::runtime_error("bad hex digit");a[i]=x;}
 return a;
}
static B32 hex32(const std::string&s){
 if(s.size()!=64)throw std::runtime_error("bad hex32");
 B32 a{};
 for(int i=0;i<32;++i){unsigned x=0;if(std::sscanf(s.substr(i*2,2).c_str(),"%2x",&x)!=1)throw std::runtime_error("bad hex digit");a[i]=x;}
 return a;
}
static U64 load64(const unsigned char*p){U64 v=0;for(int i=0;i<8;++i)v|=U64(p[i])<<(8*i);return v;}
static void store64(unsigned char*p,U64 x){for(int i=0;i<8;++i)p[i]=(x>>(8*i))&255;}
static uint32_t temper(uint32_t y){y^=y>>11;y^=(y<<7)&0x9d2c5680u;y^=(y<<15)&0xefc60000u;y^=y>>18;return y;}
static B32 hash16(const B16&v){B32 out{};SHA256(v.data(),16,out.data());return out;}
int main(int argc,char**argv){
 try{
  if(argc!=2&&argc!=4)throw std::runtime_error("expected spool path, optional shard and count");
  int shard=argc==4?std::stoi(argv[2]):0,part=argc==4?std::stoi(argv[3]):1;
  if(shard<0||part<1||shard>=part)throw std::runtime_error("invalid shard");
  std::ifstream in(argv[1],std::ios::binary);if(!in)throw std::runtime_error("original spool missing");
  std::string src((std::istreambuf_iterator<char>(in)),{});
  B32 digest{};SHA256(reinterpret_cast<const unsigned char*>(src.data()),src.size(),digest.data());
  if(digest!=hex32("7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"))throw std::runtime_error("source sha mismatch");
  std::vector<std::string> records;
  for(size_t pos=0;pos<src.size();){size_t e=src.find('\n',pos);if(e==std::string::npos)e=src.size();auto line=src.substr(pos,e-pos);if(line.find("PAYLOAD=")!=std::string::npos)records.push_back(line);pos=e+1;}
  if(records.size()!=133)throw std::runtime_error("expected 133 payloads");
  auto&row=records[129];
  const std::string marker="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
  if(row.find(marker)!=0)throw std::runtime_error("wrong selected route event");
  const B16 copied=hex16(row.substr(marker.size(),32));
  if(copied!=hex16("A9A9DC5731A5E2AE879C47215C2559D5"))throw std::runtime_error("wrong selected copy");
  const B16 mask=hex16("8556C8CB6140A7F9A5123AC7571BEE1C");
  const B32 target=hex32("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
  B16 base{};for(int i=0;i<16;++i)base[i]=copied[i]^mask[i];
  std::array<D,128> basis{};
  for(int i=0;i<128;++i){
   B16 x{};uint32_t t=temper(uint32_t(1)<<(i%32));
   for(int b=0;b<4;++b)x[(i/32)*4+b]=(t>>(b*8))&255;
   basis[i]={load64(x.data()),load64(x.data()+8)};
  }
  const U64 b0=load64(base.data()),b1=load64(base.data()+8);
  U64 p0=b0,p1=b1;for(int j:{0,17,34,67,126}){p0^=basis[j].lo;p1^=basis[j].hi;}
  B16 planted{};store64(planted.data(),p0);store64(planted.data()+8,p1);
  B32 positive=hash16(planted);
  if(std::popcount(p0^b0)+std::popcount(p1^b1)<=8)throw std::runtime_error("positive overlaps old output shell");
  U64 checks=0,overlap=0,matched=0,planted_count=0,pair=0;
  for(int a=0;a<124;++a)for(int b=a+1;b<125;++b,++pair){
   if(pair%part!=unsigned(shard))continue;
   U64 ab0=basis[a].lo^basis[b].lo,ab1=basis[a].hi^basis[b].hi;
   for(int c=b+1;c<126;++c)for(int d=c+1;d<127;++d){
    U64 pre0=ab0^basis[c].lo^basis[d].lo,pre1=ab1^basis[c].hi^basis[d].hi;
    for(int e=d+1;e<128;++e){
     U64 x=pre0^basis[e].lo,y=pre1^basis[e].hi;
     if(std::popcount(x)+std::popcount(y)<=8){++overlap;continue;}
     B16 component{};store64(component.data(),b0^x);store64(component.data()+8,b1^y);
     B32 h=hash16(component);++checks;
     if(h==target)++matched;
     if(h==positive){if(component!=planted)throw std::runtime_error("unexpected synthetic digest collision");++planted_count;}
    }
   }
  }
  if(matched!=0||planted_count>1)throw std::runtime_error("unexpected target/positive result");
  std::cout<<"SHARD="<<shard<<" PART="<<part<<" NEW_CHECKS="<<checks<<" OLD_SHELL_SKIPS="<<overlap<<" ORIGINAL_HITS="<<matched<<" PLANTED_HITS="<<planted_count<<"\n";
  return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}
}
