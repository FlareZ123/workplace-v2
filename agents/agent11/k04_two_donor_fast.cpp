// Agent11 H17 two-donor inverse-twist K04 candidate test.
// C++20 + OpenSSL crypto. Build: g++ -O3 -std=c++20 -Wall k04_two_donor_fast.cpp -lcrypto -o k04_two_donor_fast
// Usage: k04_two_donor_fast donor.tsv 0 N ; N is the 531-count of generated source carrier rows.
// Source carrier input format: one 32-character hex word, tab, original provenance per line.
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include <openssl/sha.h>
using U=uint32_t;
constexpr U Mag=0x9908b0df;
constexpr std::array<unsigned char,16> Mask={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
constexpr std::array<unsigned char,32> Target={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
U temper(U x){x^=x>>11;x^=(x<<7)&0x9d2c5680;x^=(x<<15)&0xefc60000;x^=x>>18;return x;}
U untemper(U x){
 U y=x;for(int i=0;i<6;i++)y=x^(y>>18);x=y;
 y=x;for(int i=0;i<6;i++)y=x^((y<<15)&0xefc60000);x=y;
 y=x;for(int i=0;i<6;i++)y=x^((y<<7)&0x9d2c5680);x=y;
 y=x;for(int i=0;i<6;i++)y=x^(y>>11);return y;
}
U word(const unsigned char* b,bool big){
 if(big)return (U(b[0])<<24)|(U(b[1])<<16)|(U(b[2])<<8)|U(b[3]);
 return (U(b[3])<<24)|(U(b[2])<<16)|(U(b[1])<<8)|U(b[0]);
}
void store(U x,unsigned char*out){for(int j=0;j<4;j++)out[j]=static_cast<unsigned char>(x>>(8*j));}
U twist_reverse(U t){U bit=t>>31;return ((t^(bit?Mag:0))<<1)|bit;}
struct Donor{std::string label;std::array<unsigned char,16> raw;std::array<std::array<U,4>,4> states;};
std::string hex(const unsigned char*b,int len){std::ostringstream o;for(int i=0;i<len;i++)o<<std::hex<<std::uppercase<<std::setw(2)<<std::setfill('0')<<unsigned(b[i]);return o.str();}
Donor make(std::array<unsigned char,16> raw,std::string label){
 Donor d;d.label=label;d.raw=raw;
 for(int e=0;e<2;e++)for(int mode=0;mode<2;mode++)for(int k=0;k<4;k++){
  U v=word(raw.data()+4*k,e);d.states[2*e+mode][k]=(mode==0)?untemper(v):v;
 }
 return d;
}
void infer(const std::array<U,4>&x,const std::array<U,4>&y,std::array<U,4>&native){
 U t[4];for(int k=0;k<4;k++)t[k]=twist_reverse(x[k]^y[k]);
 for(int k=0;k<3;k++)native[k]=(t[k]&0x7fffffff)|(t[k+1]&0x80000000);
 native[3]=t[3]&0x7fffffff;
}
void synthetic(){
 std::mt19937 mt(20261103);std::array<U,1800> q;
 for(auto &v:q)v=mt();
 std::array<U,4> a,b,res;
 for(int i=0;i<4;i++){a[i]=untemper(q[1347+i]);b[i]=untemper(q[1574+i]);}
 infer(a,b,res);
 for(int i=0;i<4;i++){
  U actual=untemper(q[951+i]);
  if(i<3&&res[i]!=actual){std::cerr<<"synthetic failure lane"<<i<<"\n";std::exit(3);}
  if(i==3&&(res[i]&0x7fffffff)!=(actual&0x7fffffff)){std::cerr<<"synthetic failure last\n";std::exit(3);}
 }
 std::cout<<"SYNTHETIC_CPP_MT_REVERSE_TWO_DONOR PASS\n";
}
int main(int argc,char **argv){
 if(argc!=4){std::cerr<<"usage: <tsv> <first donor i begin> <first donor i end>\n";return 2;}
 synthetic();
 std::ifstream in(argv[1]);if(!in){std::cerr<<"no corpus\n";return 2;}
 std::vector<Donor> donors;std::string line;
 while(std::getline(in,line)){
  auto p=line.find('\t');if(p==std::string::npos)continue;
  std::array<unsigned char,16> raw{};
  for(int i=0;i<16;i++)raw[i]=static_cast<unsigned char>(std::stoul(line.substr(2*i,2),nullptr,16));
  donors.push_back(make(raw,line.substr(p+1)));
 }
 const size_t begin=std::stoull(argv[2]),end=std::stoull(argv[3]);
 if(end>donors.size()||begin>end)return 2;
 uint64_t count=0,hits=0;
 for(size_t i=begin;i<end;i++)for(size_t j=0;j<donors.size();j++)
 for(int ei=0;ei<4;ei++)for(int ej=0;ej<4;ej++){
  std::array<U,4> native{};
  infer(donors[i].states[ei],donors[j].states[ej],native);
  unsigned char candidate[16];
  for(int bit=0;bit<2;bit++){
   store(temper(native[0]),candidate);
   store(temper(native[1]),candidate+4);
   store(temper(native[2]),candidate+8);
   store(temper(native[3]|(U(bit)<<31)),candidate+12);
   for(int b=0;b<16;b++)candidate[b]^=Mask[b];
   unsigned char digest[32];SHA256(candidate,16,digest);
   if(std::memcmp(digest,Target.data(),32)==0){
    hits++;
    std::cout<<"MATCH K04="<<hex(candidate,16)<<" i="<<i<<" j="<<j<<" ei="<<ei<<" ej="<<ej
         <<" high="<<bit<<" A="<<donors[i].label<<" B="<<donors[j].label<<"\n";
   }
   count++;
   for(int b=0;b<16;b++)candidate[b]^=Mask[b];
  }
 }
 std::cout<<"COMPLETE first-range="<<begin<<":"<<end<<" donors="<<donors.size()
          <<" candidates="<<count<<" original_hits="<<hits<<"\n";
 return hits?0:1;
}
