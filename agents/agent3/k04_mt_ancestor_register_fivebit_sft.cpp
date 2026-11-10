// H-17 selected printer K04: exhaustive <=5 initial MT register-bit corruption SFT.
// C++20 + OpenSSL libcrypto. Run with original spool-reconstruction.log path.
#include <array>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <map>
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
  if(argc!=2)throw std::runtime_error("provide original spool path only");
  std::ifstream in(argv[1],std::ios::binary);if(!in)throw std::runtime_error("original spool missing");
  std::string src((std::istreambuf_iterator<char>(in)),{});
  B32 digest{};SHA256(reinterpret_cast<const unsigned char*>(src.data()),src.size(),digest.data());
  if(digest!=hex32("7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"))throw std::runtime_error("source SHA mismatch");
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
  // Compute the actual native effect of all 624*32 original register-bit faults.
  std::map<std::array<uint32_t,4>,unsigned> effect_classes;
  unsigned nonzero=0;
  for(int w=0;w<624;++w)for(int b=0;b<32;++b){
   std::array<uint32_t,955> x{};x[w]=uint32_t(1)<<b;
   for(int t=0;t<=330;++t){
    uint32_t yy=(x[t]&0x80000000u)|(x[t+1]&0x7fffffffu);
    x[t+624]=x[t+397]^(yy>>1)^((x[t+1]&1u)?0x9908b0dfu:0u);
   }
   std::array<uint32_t,4> e{x[951],x[952],x[953],x[954]};
   if(e!=std::array<uint32_t,4>{}){++nonzero;++effect_classes[e];}
  }
  if(nonzero!=384||effect_classes.size()!=132)throw std::runtime_error("unexpected register influence map");
  std::array<D,4> special{};
  for(int i=0;i<4;++i){
   B16 u{};const uint32_t t=temper(0x9908b0dfu);
   for(int j=0;j<4;++j)u[i*4+j]=(t>>(j*8))&255;
   special[i]={load64(u.data()),load64(u.data()+8)};
  }
  // Exactly 128 single-native-bit and four 15-bit feedback-column influences.
  unsigned unit_effects=0,feedback_effects=0;
  for(const auto&item:effect_classes){
   const auto&e=item.first;
   if(std::popcount(e[0])+std::popcount(e[1])+std::popcount(e[2])+std::popcount(e[3])==1){++unit_effects;continue;}
   bool feedback=false;
   for(int i=0;i<4;++i)if(e[i]==0x9908b0dfu && e[(i+1)%4]==0 && e[(i+2)%4]==0 && e[(i+3)%4]==0)feedback=true;
   if(!feedback)throw std::runtime_error("unmodeled native-register signature");
   ++feedback_effects;
  }
  if(unit_effects!=128||feedback_effects!=4)throw std::runtime_error("incomplete native influence set");
  const U64 b0=load64(base.data()),b1=load64(base.data()+8);
  U64 p0=b0^special[0].lo,p1=b1^special[0].hi;
  for(int j:{0,17,34,67}){p0^=basis[j].lo;p1^=basis[j].hi;}
  B16 planted{};store64(planted.data(),p0);store64(planted.data()+8,p1);
  const B32 positive=hash16(planted);
  if(std::popcount(p0^b0)+std::popcount(p1^b1)<=8)throw std::runtime_error("positive overlaps output shell");
  U64 total=0,newchecks=0,oldskips=0,hits=0,poshits=0;
  for(int sc=1;sc<16;++sc){
   int specials_count=std::popcount(unsigned(sc));
   U64 a0=0,a1=0;
   for(int i=0;i<4;++i)if(sc&(1<<i)){a0^=special[i].lo;a1^=special[i].hi;}
   std::function<void(int,int,U64,U64)> visit=[&](int from,int left,U64 q0,U64 q1){
    if(left==0){
     ++total;
     if(std::popcount(q0)+std::popcount(q1)<=8){++oldskips;return;}
     B16 obj{};store64(obj.data(),b0^q0);store64(obj.data()+8,b1^q1);
     const B32 h=hash16(obj);++newchecks;
     if(h==target){++hits;std::cout<<"GENUINE_HIT special="<<sc<<"\n";}
     if(h==positive){if(obj!=planted)throw std::runtime_error("unexpected synthetic digest collision");++poshits;}
     return;
    }
    for(int j=from;j<=128-left;++j)visit(j+1,left-1,q0^basis[j].lo,q1^basis[j].hi);
   };
   for(int n=0;n<=5-specials_count;++n)visit(0,n,a0,a1);
  }
  if(total!=46201487u||newchecks!=46201455u||oldskips!=32u||hits||poshits!=1)
   throw std::runtime_error("unexpected exhaustive counts or control");
  std::cout<<"REGISTER_EFFECTS_NONZERO="<<nonzero<<" UNIQUE="<<effect_classes.size()
           <<" ALL_PHYSICAL_EFFECT_CLASSES="<<total<<" NEW_K04_SHA="<<newchecks
           <<" PRIOR_OUTPUT_SHELL="<<oldskips<<" ORIGINAL_K04_HITS="<<hits
           <<" PLANTED_HITS="<<poshits<<"\n";
  return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}
}
