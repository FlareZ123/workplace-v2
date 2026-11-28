// K04: exhaustive 32-bit SplitMix64 -> xoroshiro128++ first-request producer screen.
// C++17: c++ -O3 -std=c++17 -Wall -Wextra -o seedcheck seedcheck.cpp
// Usage: ./seedcheck --synthetic | ./seedcheck /path/to/spool-reconstruction.log
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using U=uint64_t;
using Packet=std::array<uint8_t,16>;
static inline U rot(U x,int n){return (x<<n)|(x>>(64-n));}
static inline U next(U &s){U x=(s+=0x9E3779B97F4A7C15ULL);x=(x^(x>>30))*0xBF58476D1CE4E5B9ULL;x=(x^(x>>27))*0x94D049BB133111EBULL;return x^(x>>31);}
static inline void seedstate(uint32_t seed,bool signedmode,bool swapped,U &a,U &b){U s=signedmode?U(int64_t(int32_t(seed))):U(seed);a=next(s);b=next(s);if(swapped){U t=a;a=b;b=t;}}
static inline U out(U a,U b){return rot(a+b,17)+a;}
static inline void step(U &a,U &b){U t=a^b;a=rot(a,49)^t^(t<<21);b=rot(t,28);}
static U word(const uint8_t *p,bool le){U x=0;for(int i=0;i<8;i++)x=(x<<8)|p[le?7-i:i];return x;}
static Packet pack(U a,U b,bool le,bool swap){Packet p{};U v[2]={a,b};for(int i=0;i<2;i++)for(int j=0;j<8;j++)p[8*i+j]=uint8_t(v[swap?1-i:i]>>(8*(le?j:7-j)));return p;}
static Packet read_first(const std::string &file){std::ifstream f(file);if(!f)throw std::runtime_error("cannot open source");std::string line;Packet p{};int n=0;while(std::getline(f,line)){
 if(line.find("JOB=PS-261003-0417")==std::string::npos||line.find("ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER")==std::string::npos)continue;
 auto pos=line.find("PAYLOAD=");if(pos==std::string::npos)throw std::runtime_error("no payload");auto s=line.substr(pos+8,32);if(s.size()!=32)throw std::runtime_error("bad length");
 for(int i=0;i<16;i++){auto h=[](char c)->int{if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;return -1;};int x=h(s[2*i]),y=h(s[2*i+1]);if(x<0||y<0)throw std::runtime_error("bad hex");p[i]=uint8_t(16*x+y);}n++;}
 if(n!=1)throw std::runtime_error("nonunique first request");
 return p;}
struct Count{U seeds=0,first=0,full=0;};
static Count scan(const Packet &p,U from,U to){
 std::array<std::array<U,2>,4> views{};for(int le=0;le<2;le++)for(int swap=0;swap<2;swap++)views[2*le+swap]={word(p.data()+8*swap,le),word(p.data()+8*(1-swap),le)};
 Count c{};for(U seed=from;seed<to;seed++)for(int mode=0;mode<2;mode++){
  if(mode && seed<0x80000000ULL)continue; // avoid duplicate sign-extension states
  for(int swapstate=0;swapstate<2;swapstate++){
   U a,b;seedstate(uint32_t(seed),mode,swapstate,a,b);U y=out(a,b);c.seeds++;
   for(const auto &v:views)if(v[0]==y){c.first++;U x=a,z=b;step(x,z);if(out(x,z)==v[1])c.full++;}
  }
 }
 return c;
}
static bool controls(){
 for(uint32_t seed:{uint32_t(0),uint32_t(42),uint32_t(0x7FFFFFFF),uint32_t(0x80000000),uint32_t(0xFFFFFFE3)})
 for(int mode=0;mode<2;mode++)for(int ss=0;ss<2;ss++){
  if(mode&&seed<0x80000000U)continue;
  U a,b;seedstate(seed,mode,ss,a,b);U y0=out(a,b);step(a,b);U y1=out(a,b);
  for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){
   auto p=pack(y0,y1,le,sw);U x,z;seedstate(seed,mode,ss,x,z);if(out(x,z)!=word(p.data()+8*sw,le))return false;step(x,z);if(out(x,z)!=word(p.data()+8*(1-sw),le))return false;
  }
 }
 // Assert the real enumerator finds one planted match at each of 16 serializer/state-view combinations.
 for(int seedcase=0;seedcase<2;seedcase++)for(int ss=0;ss<2;ss++)for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){
  uint32_t seed=seedcase?0xFFFFFFE3U:42U;U a,b;seedstate(seed,seedcase,ss,a,b);U y=out(a,b);step(a,b);
  auto p=pack(y,out(a,b),le,sw);auto c=scan(p,seedcase?0xFFFFFF00ULL:0ULL,seedcase?4294967296ULL:128ULL);
  if(c.first!=1||c.full!=1||c.seeds!=(seedcase?1024:256))return false;
 }
 return true;
}
int main(int argc,char **argv){try{
 if(!controls())throw std::runtime_error("positive-control failure");
 std::cout<<"synthetic=PASS planted_full_pair=16\n";
 if(argc==2&&std::string(argv[1])=="--synthetic")return 0;
 if(argc!=2)throw std::runtime_error("expected spool path or --synthetic");
 auto p=read_first(argv[1]);auto c=scan(p,0,4294967296ULL);
 std::cout<<"seed_range=2^32 distinct_initializations="<<c.seeds<<" source_serializers=4 first_word_matches="<<c.first<<" full_packet_matches="<<c.full<<"\n";
 return 0;
}catch(const std::exception &e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 2;}}
