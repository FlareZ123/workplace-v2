// Hypothetical K04 issuer: full 64bit UTC epoch-time seeds -> SplitMix64 -> xoroshiro128++.
// Anchors are intact original first-request or first-batch packet, NOT selected ACK2.
// Compile: g++ -O3 -std=c++17 agents/agent31/k04_xoro_time_seed64_unified.cpp -o /tmp/h17_time64
// Run: /tmp/h17_time64 --synthetic
//      /tmp/h17_time64 resources/evidence/print/spool-reconstruction.log batch|request <start> <end> 64
// Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <array>
#include <cstdint>
#include <cstdio>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using U=uint64_t;using Packet=std::array<uint8_t,16>;
static inline U rot(U x,int n){return (x<<n)|(x>>(64-n));}
static inline U mix(U &s){U x=s+=0x9E3779B97F4A7C15ULL;x=(x^(x>>30))*0xBF58476D1CE4E5B9ULL;x=(x^(x>>27))*0x94D049BB133111EBULL;return x^(x>>31);}
static inline U output(U a,U b){return rot(a+b,17)+a;}
static inline void step(U &a,U &b){U x=a^b;a=rot(a,49)^x^(x<<21);b=rot(x,28);}
static inline void init(U seed,bool swap,U &a,U &b){a=mix(seed);b=mix(seed);if(swap){U t=a;a=b;b=t;}}
static inline U word(const uint8_t *p,bool le){U x=0;for(int i=0;i<8;i++)x=(x<<8)|p[le?7-i:i];return x;}
static inline Packet encode(U y,U z,bool le,bool sw){Packet p{};U a[]={y,z};for(int i=0;i<2;i++)for(int j=0;j<8;j++)p[8*i+j]=uint8_t(a[sw?1-i:i]>>(8*(le?j:7-j)));return p;}
static Packet load_first(const std::string &file,bool batch){std::ifstream f(file);if(!f)throw std::runtime_error("no spool");std::string l;Packet p{};int count=0;
 while(std::getline(f,l)){if(l.find(batch?"JOB=PS-261003-0300":"JOB=PS-261003-0417")==std::string::npos||
    l.find(batch?"ATTEMPT=1 STATE=ACK CLASS=LABEL":"ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER")==std::string::npos)continue;
  auto pos=l.find("PAYLOAD=");if(pos==std::string::npos||pos+8+32>l.size())throw std::runtime_error("payload missing");
  for(int i=0;i<16;i++){auto h=[](char c)->int{return c>='0'&&c<='9'?c-'0':c>='A'&&c<='F'?c-'A'+10:-1;};int a=h(l[pos+8+2*i]),b=h(l[pos+8+2*i+1]);if(a<0||b<0)throw std::runtime_error("bad hex");p[i]=uint8_t((a<<4)|b);}count++;}
 if(count!=1)throw std::runtime_error("not one untouched first packet");return p;}
struct Count{U seeds=0,first=0,full=0;};
static Count scan(const Packet &p,U lo,U hi,int phases){std::array<U,4> y0{},y1{};
 for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){y0[le*2+sw]=word(p.data()+8*sw,le);y1[le*2+sw]=word(p.data()+8*(1-sw),le);}
 Count n{};for(U seed=lo;seed<hi;seed++){n.seeds++;
  for(int swapped=0;swapped<2;swapped++){U a,b;init(seed,swapped,a,b);
   for(int i=0;i<phases;i++){U y=output(a,b);if(y==y0[0]||y==y0[1]||y==y0[2]||y==y0[3]){
    for(int j=0;j<4;j++)if(y==y0[j]){n.first++;U x=a,z=b;step(x,z);if(output(x,z)==y1[j]){n.full++;std::cerr<<"WHOLE_PACKET_FIT seed="<<seed<<" state_swap="<<swapped<<" phase="<<i<<" view="<<j<<"\n";}}}
    step(a,b);}
  }}return n;}
static bool controls(){for(U seed:{1791045900000000000ULL,1791050460999999999ULL})for(int ss=0;ss<2;ss++)for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++)for(int phase:{0,17,63}){
 U a,b;init(seed,ss,a,b);for(int i=0;i<phase;i++)step(a,b);U y=output(a,b);step(a,b);Packet p=encode(y,output(a,b),le,sw);
 U start=seed-3,end=seed+4;Count c=scan(p,start,end,64);if(c.full!=1)return false;
 }return true;}
int main(int argc,char**argv){try{
 if(!controls())throw std::runtime_error("48 planted 64bit controls failed");std::cout<<"SYNTHETIC=PASS full64_seed_enumerator_positives=48"<<std::endl;
 if(argc==2&&std::string(argv[1])=="--synthetic")return 0;
 if(argc!=6)throw std::runtime_error("usage: prog spool batch|request start_inclusive end_exclusive 64");
 std::string mode=argv[2];if(mode!="batch"&&mode!="request")throw std::runtime_error("bad mode");
 auto p=load_first(argv[1],mode=="batch");
 U lo=std::stoull(argv[3]),hi=std::stoull(argv[4]);int phases=std::stoi(argv[5]);if(hi<=lo||hi-lo>1000000000ULL||phases!=64)throw std::runtime_error("bad interval or phase bound");
 auto start=std::chrono::steady_clock::now();Count c=scan(p,lo,hi,phases);auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<"ORIGINAL=COMPLETED mode="<<mode<<" seed_base="<<lo<<" seed_end="<<hi<<" seeds="<<c.seeds<<" state_orders=2 phases="<<phases<<" first_word="<<c.first<<" complete_packet="<<c.full<<" elapsed_s="<<seconds<<std::endl;
 return 0;
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}}
