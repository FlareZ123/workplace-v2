// K04: native 32-bit seed -> four SplitMix64 words -> xoshiro256++ 1.0.
// Original sole first intact PS-261003-0417 REQUESTED1; no selected 18:02 ACK2.
// Bounded 2^32 zero-extended seeds x 2 initial-word orders x 64 output phases x 4 serializers.
// Compile: g++ -O3 -std=c++17 -o /tmp/h17_xoshiro256 agents/agent31/k04_xoshiro256pp_seed32_phase64.cpp
// Run: /tmp/h17_xoshiro256 --synthetic
//      /tmp/h17_xoshiro256 resources/evidence/print/spool-reconstruction.log [seed_start seed_end]
// Source SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <cstdint>
#include <array>
#include <cstring>
#include <fstream>
#include <string>
#include <iostream>
#include <stdexcept>
#include <chrono>
using U=uint64_t;using Packet=std::array<uint8_t,16>;
static inline U rot(U x,int n){return (x<<n)|(x>>(64-n));}
static inline U splitmix(U &s){U z=(s+=0x9E3779B97F4A7C15ULL);z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL;z=(z^(z>>27))*0x94D049BB133111EBULL;return z^(z>>31);}
struct State{U a,b,c,d;};
static inline State seed(uint32_t x,bool reverse){U z=x; U arr[4]={splitmix(z),splitmix(z),splitmix(z),splitmix(z)};return reverse? State{arr[3],arr[2],arr[1],arr[0]}:State{arr[0],arr[1],arr[2],arr[3]};}
static inline U output(const State& s){return rot(s.a+s.d,23)+s.a;}
static inline void step(State &s){U t=s.b<<17;s.c^=s.a;s.d^=s.b;s.b^=s.c;s.a^=s.d;s.c^=t;s.d=rot(s.d,45);}
static inline U word(const uint8_t* q,bool le){U v=0;for(int i=0;i<8;i++)v=(v<<8)|q[le?7-i:i];return v;}
static inline Packet pack(U y,U z,bool le,bool swap){Packet p{}; U q[]={y,z};for(int i=0;i<2;i++)for(int j=0;j<8;j++)p[8*i+j]=uint8_t(q[swap?1-i:i]>>(8*(le?j:7-j)));return p;}
static Packet load(const std::string &path){std::ifstream f(path);if(!f)throw std::runtime_error("could not open spool");std::string s;Packet p{};int n=0;while(std::getline(f,s)){if(s.find("JOB=PS-261003-0417")==std::string::npos||s.find("ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER")==std::string::npos)continue;auto x=s.find("PAYLOAD=");if(x==std::string::npos||s.size()<x+8+32)throw std::runtime_error("missing payload");for(int i=0;i<16;i++){auto h=[](char c){return c>='0'&&c<='9'?int(c-'0'):c>='A'&&c<='F'?int(c-'A'+10):-1;};int a=h(s[x+8+i*2]),b=h(s[x+8+i*2+1]);if(a<0||b<0)throw std::runtime_error("invalid hex");p[i]=uint8_t(a*16+b);}n++;}if(n!=1)throw std::runtime_error("nonunique source anchor");return p;}
struct Count{uint64_t states=0,first=0,whole=0;};
static Count scan(const Packet& p,U lo,U hi){std::array<U,4> obs0{},obs1{};for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){int k=le*2+sw;obs0[k]=word(p.data()+8*sw,le);obs1[k]=word(p.data()+8*(1-sw),le);}
 Count count{};for(U v=lo;v<hi;v++){for(int reverse=0;reverse<2;reverse++){State s=seed(uint32_t(v),reverse);count.states++;
 for(int phase=0;phase<64;phase++){U y=output(s);if(y==obs0[0]||y==obs0[1]||y==obs0[2]||y==obs0[3]){
 for(int k=0;k<4;k++)if(y==obs0[k]){count.first++;State t=s;step(t);if(output(t)==obs1[k]){count.whole++;std::cerr<<"FIT seed="<<v<<" reversed="<<reverse<<" phase="<<phase<<" view="<<k<<"\n";}}}
 step(s);}}
 }return count;}
static bool controls(){for(uint32_t sd:{42u,0xfffffff1u})for(int rev=0;rev<2;rev++)for(int phase:{0,17,63})for(int le=0;le<2;le++)for(int sw=0;sw<2;sw++){
 State s=seed(sd,rev);for(int j=0;j<phase;j++)step(s);U y=output(s);step(s);auto pkt=pack(y,output(s),le,sw);
 U lo=sd>100?0xffffffe0ULL:0ULL,hi=sd>100?0x100000000ULL:128ULL;
 auto c=scan(pkt,lo,hi);if(c.whole!=1){std::cerr<<"bad synthetic "<<sd<<" "<<rev<<" "<<phase<<" "<<le<<" "<<sw<<"\n";return false;}}
 return true;}
int main(int argc,char**argv){try{if(!controls())throw std::runtime_error("planted fullpacket controls failed");std::cout<<"SYNTHETIC=PASS planted_full_packets=48\n";
 if(argc==2&&std::string(argv[1])=="--synthetic")return 0;
 if(argc<2||argc>4)throw std::runtime_error("usage: prog spool [start end]");
 U lo=argc>2?std::stoull(argv[2]):0,hi=argc>3?std::stoull(argv[3]):0x100000000ULL;
 if(hi<=lo||hi>0x100000000ULL)throw std::runtime_error("invalid seed bounds");
 auto p=load(argv[1]);auto t=std::chrono::steady_clock::now();auto c=scan(p,lo,hi);
 auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count();
 std::cout<<"ORIGINAL=COMPLETED seeds="<<(hi-lo)<<" state_orders=2 phases=64 first_word_matches="<<c.first<<" whole_packet_matches="<<c.whole<<" elapsed_s="<<sec<<"\n";return 0;
 }catch(const std::exception &e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}}
