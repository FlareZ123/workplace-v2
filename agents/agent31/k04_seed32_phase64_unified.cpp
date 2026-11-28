// Original K04 low-entropy producer test, two intact physical source anchors.
// Complete 32bit signed/unsigned seeds, both state orders, phases0..63, 4 packet views.
// Compile: c++ -O3 -std=c++17 k04_seed32_phase64_unified.cpp -o seed32_phase64
// Run: ./seed32_phase64 --synthetic
//      ./seed32_phase64 resources/evidence/print/spool-reconstruction.log request|batch
// Original spool SHA256 must equal 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <array>
#include <cstdint>
#include <cstdio>
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <stdexcept>
using U=uint64_t; using Packet=std::array<uint8_t,16>;
static inline U rot(U x,unsigned n){return (x<<n)|(x>>(64-n));}
static inline U sm(U &s){U x=s+=0x9E3779B97F4A7C15ULL;x=(x^(x>>30))*0xBF58476D1CE4E5B9ULL;x=(x^(x>>27))*0x94D049BB133111EBULL;return x^(x>>31);}
static inline U out(U a,U b){return rot(a+b,17)+a;}
static inline void step(U &a,U &b){U x=a^b;a=rot(a,49)^x^(x<<21);b=rot(x,28);}
static inline void start(uint32_t seed,bool is_signed,bool swap,U &a,U &b){U v=is_signed?U(int64_t(int32_t(seed))):U(seed);a=sm(v);b=sm(v);if(swap){U t=a;a=b;b=t;}}
static inline U w64(const uint8_t *p,bool le){U v=0;for(unsigned i=0;i<8;i++)v=(v<<8)|p[le?7-i:i];return v;}
static Packet packet(U x,U y,bool le,bool ba){Packet z{};U w[2]={x,y};for(int i=0;i<2;i++)for(int j=0;j<8;j++)z[8*i+j]=uint8_t(w[ba?1-i:i]>>(8*(le?j:7-j)));return z;}
static Packet load(const char *fn,bool batch){std::ifstream f(fn);if(!f)throw std::runtime_error("cannot open spool");std::string line;Packet p{};int cnt=0;while(std::getline(f,line)){
 if(line.find(batch?"JOB=PS-261003-0300":"JOB=PS-261003-0417")==std::string::npos ||
    line.find(batch?"ATTEMPT=1 STATE=ACK CLASS=LABEL":"ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER")==std::string::npos)continue;
 auto i=line.find("PAYLOAD=");if(i==std::string::npos||i+8+32>line.size())throw std::runtime_error("bad payload");for(int j=0;j<16;j++){
  auto h=[](char c){return c>='0'&&c<='9'?int(c-'0'):c>='A'&&c<='F'?int(c-'A'+10):-1;};int a=h(line[i+8+2*j]),b=h(line[i+8+2*j+1]);if(a<0||b<0)throw std::runtime_error("bad hex");p[j]=uint8_t(a*16+b);}
  ++cnt;
 }if(cnt!=1)throw std::runtime_error("first request count not 1");return p;}
struct Count{uint64_t tested=0,first=0,full=0;};
static Count scan(const Packet &p,uint64_t lo,uint64_t hi,int phases){
 std::array<U,4> y0{},y1{};for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){int idx=le*2+sw;y0[idx]=w64(p.data()+8*sw,le);y1[idx]=w64(p.data()+8*(1-sw),le);}
 Count c{};
 for(uint64_t seed=lo;seed<hi;seed++){
  for(int mode=0;mode<2;mode++){
   if(mode && seed<0x80000000ULL)continue;
   for(int sw=0;sw<2;sw++){
    U a,b;start(uint32_t(seed),mode,sw,a,b);c.tested++;
    for(int k=0;k<phases;k++){
     U y=out(a,b);
     if(y==y0[0]||y==y0[1]||y==y0[2]||y==y0[3]){
      for(int view=0;view<4;view++)if(y==y0[view]){
       c.first++;U x=a,z=b;step(x,z);if(out(x,z)==y1[view])c.full++;
      }
     }
     step(a,b);
    }
   }
  }
 }
 return c;
}
static bool controls(int phases){
 for(uint32_t seed:{42U,0xFFFFFFF1U})for(int mode=0;mode<2;mode++)for(int swapped=0;swapped<2;swapped++){
  if(mode&&seed<0x80000000u)continue;
  for(int offset:{0,3,17,63})for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){
   U a,b;start(seed,mode,swapped,a,b);for(int i=0;i<offset;i++)step(a,b);U y0=out(a,b);step(a,b);U y1=out(a,b);
   auto p=packet(y0,out(a,b),le,sw);auto c=scan(p,seed<0x80000000u?0:0xFFFFFFE0ULL,seed<0x80000000u?128:0x100000000ULL,phases);
   if(c.full!=1 || c.first<1){std::cerr<<"Control failure at seed="<<seed<<" mode="<<mode<<" swap="<<swapped<<" offset="<<offset<<" layout="<<le<<","<<sw<<" first="<<c.first<<" full="<<c.full<<"\n";return false;}
  }
 }
 return true;
}
int main(int argc,char** argv){try{
  int p=64;
  if(!controls(p))throw std::runtime_error("synthetic planted recovery failed");
  std::cout<<"SYNTHETIC=PASS phase_offsets=64 real_enumerator_positive=96"<<std::endl;
  if(argc>1&&strcmp(argv[1],"--synthetic")==0)return 0;
  if(argc<3)throw std::runtime_error("usage: prog spool request|batch [seed_start seed_end], or --synthetic");
  bool batch=std::string(argv[2])=="batch";
  if(!batch&&std::string(argv[2])!="request")throw std::runtime_error("bad mode");
  U lo=argc>3?std::stoull(argv[3]):0ULL;
  U hi=argc>4?std::stoull(argv[4]):0x100000000ULL;
  if(hi>0x100000000ULL||hi<=lo)throw std::runtime_error("invalid seed range");
  auto packet=load(argv[1],batch);auto t=std::chrono::steady_clock::now();
  auto c=scan(packet,lo,hi,p);
  auto dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
  std::cout<<"ORIGINAL=COMPLETED mode="<<(batch?"batch":"request")<<" seed_start="<<lo<<" seed_end="<<hi<<" seed_state_assignments="<<c.tested<<" phases="<<p<<" first_word_matches="<<c.first<<" full_packet_matches="<<c.full<<" elapsed_s="<<dt<<std::endl;
  return 0;
 }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<std::endl;return 2;}}
