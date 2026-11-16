// Source-pinned exhaustive H-17 K04 native SFC32 same-job model, Agent29 (2026-11-16).
// g++ -O3 -std=c++17 -fopenmp agents/agent29/k04_sfc32_samejob_sft.cpp -lcrypto -o /tmp/k04sfc
// OMP_NUM_THREADS=4 /tmp/k04sfc resources/evidence/print/spool-reconstruction.log [orientation:0..3] [ack]
#include <openssl/sha.h>
#include <cstdint>
#include <cassert>
#include <cstring>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <array>
#include <string>
using U=uint32_t;using W=uint64_t;
constexpr char PIN[]="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
constexpr char TARGET[]="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
constexpr char MASK[]="8556C8CB6140A7F9A5123AC7571BEE1C";
U rol(U x){return (x<<21)|(x>>11);} U g(U x){return x^(x>>9);}
U ung(U x){x^=x>>9;x^=x>>18;return x;}
struct S{U a,b,c,k;};
U step(S& s){U t=s.a+s.b+s.k;s.a=g(s.b);s.b=9*s.c;s.c=rol(s.c)+t;s.k++;return t;}
S inv(U c,const U *q){U b1=9*c,c1=rol(c)+q[0],b2=9*c1;
 U gb=g(b1)+b2+q[1]+1-b1-q[2],b=ung(gb),k=q[1]-gb-b1-1;
 return S{q[0]-b-k,b,c,k};}
U fourth(U c,const U*q){U b1=9*c,c1=rol(c)+q[0],b2=9*c1,c2=rol(c1)+q[1];
 U gb=g(b1)+b2+q[1]+1-b1-q[2],k=q[1]-gb-b1-1;
 return g(b2)+9*c2+k+3;}
std::string hx(const unsigned char*b,int n){std::ostringstream ss;ss<<std::hex<<std::setfill('0');for(int i=0;i<n;i++)ss<<std::setw(2)<<unsigned(b[i]);return ss.str();}
std::array<unsigned char,16> dehex(const std::string&s){assert(s.size()==32);std::array<unsigned char,16>a{};for(int i=0;i<16;i++)a[i]=std::stoul(s.substr(2*i,2),nullptr,16);return a;}
std::array<U,4> decode(const std::array<unsigned char,16>&a,int o){std::array<U,4>b{};
 for(int i=0;i<4;i++)for(int j=0;j<4;j++)b[i]|=U(a[4*((o&1)?3-i:i)+j])<<(8*((o&2)?3-j:j));return b;}
std::array<unsigned char,16> encode(const U*b,int o){std::array<unsigned char,16>a{};
 for(int i=0;i<4;i++)for(int j=0;j<4;j++)a[4*((o&1)?3-i:i)+j]=uint8_t(b[i]>>(8*((o&2)?3-j:j)));return a;}
void controls(){U r=0x7efc3a32;
 for(int i=0;i<2000;i++){auto rnd=[&](){r=r*1664525+1013904223;return r;};
  S s{rnd(),rnd(),rnd(),rnd()},ref=s;U q[12];for(U&x:q)x=step(s);
  assert(fourth(ref.c,q)==q[3]);S z=inv(ref.c,q);for(int j=0;j<12;j++)assert(step(z)==q[j]);}
 S planted{0x89abcdef,0x13792456,1337,19};U q[128];for(U&x:q)x=step(planted);
 int count=0;for(U c=0;c<4096;c++)if(fourth(c,q)==q[3]){S z=inv(c,q);bool ok=true;
  for(int j=0;j<12;j++)ok&=(step(z)==q[j]);if(ok){count++;assert(c==1337);}}
 assert(count==1);auto want=encode(q+57,0);unsigned char h[32];SHA256(want.data(),16,h);count=0;
 for(int i=4;i<=124;i++){auto v=encode(q+i,0);unsigned char d[32];SHA256(v.data(),16,d);
  if(!memcmp(h,d,32)){count++;assert(i==57);}}assert(count==1);
 std::cout<<"SYNTHETIC_PASS 2000_state_inversions 4096_c0_1_whole_positive 121_window_1_positive\n";}
int main(int argc,char**argv){assert(argc==2||argc==3||argc==4);bool ack=(argc==4&&std::string(argv[3])=="ack");assert(argc!=4||ack);controls();std::ifstream f(argv[1],std::ios::binary);assert(f);
 std::string raw((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 unsigned char sha[32];SHA256((unsigned char*)raw.data(),raw.size(),sha);assert(hx(sha,32)==PIN);
 std::istringstream lines(raw);std::string ln,early,late;int first=0,third=0;
 while(std::getline(lines,ln)){
  if(ack){
   if(ln.find("JOB=PS-261003-0427 ")!=std::string::npos&&ln.find("STATE=ACK ")!=std::string::npos){first++;early=ln;}
   if(ln.find("JOB=PS-261003-0420 ")!=std::string::npos&&ln.find("ATTEMPT=2 ")!=std::string::npos&&ln.find("STATE=ACK ")!=std::string::npos){third++;late=ln;}
  }else if(ln.find("JOB=PS-261003-0417")!=std::string::npos&&ln.find("CLASS=RECOVER")!=std::string::npos){
   if(ln.find("ATTEMPT=1 ")!=std::string::npos){first++;early=ln;}
   if(ln.find("ATTEMPT=3 ")!=std::string::npos){third++;late=ln;}}
 }
 assert(first==1&&third==1);auto get=[](std::string line){auto p=line.find("PAYLOAD=");assert(p!=std::string::npos);return dehex(line.substr(p+8,32));};
 auto source1=get(early),source3=get(late),mask=dehex(MASK);
 for(int o=(argc>=3?std::stoi(argv[2]):0);o<(argc>=3?std::stoi(argv[2])+1:4);o++){
  auto a=decode(source1,o),b=decode(source3,o);W roots=0,whole=0,immediate_hash=0;
  std::vector<U> candidates;
  #pragma omp parallel for schedule(static) reduction(+:roots,whole,immediate_hash)
  for(W ci=0;ci<(W(1)<<32);ci++){
   U c=U(ci);if(fourth(c,a.data())!=a[3])continue;roots++;
   S s=inv(c,a.data());U q[12];for(U&v:q)v=step(s);
   for(int i=0;i<4;i++)assert(q[i]==a[i]);bool match=true;for(int i=0;i<4;i++)match&=q[i+8]==b[i];if(match)whole++;
   auto v=encode(q+4,o);for(int j=0;j<16;j++)v[j]^=mask[j];
   unsigned char d[32];SHA256(v.data(),16,d);if(hx(d,32)==TARGET)immediate_hash++;
   #pragma omp critical
   candidates.push_back(c);
  }
  W hidden=0,late_match=0,hidden_hash=0;
  for(U c:candidates){S s=inv(c,a.data());std::vector<U> stream((1<<20)+8);
   for(U&v:stream)v=step(s);
   for(W i=4;i<((W(1)<<20)+4);i++){bool match=true;for(int j=0;j<4;j++)match&=stream[i+j]==b[j];if(match)late_match++;
    auto v=encode(&stream[i],o);for(int j=0;j<16;j++)v[j]^=mask[j];
    unsigned char d[32];SHA256(v.data(),16,d);if(hx(d,32)==TARGET)hidden_hash++;hidden++;}}
  std::cout<<"ORIENTATION="<<o<<" checked="<<(W(1)<<32)<<" roots="<<roots<<" late_immediate="<<whole
   <<" K04_immediate="<<immediate_hash<<" hidden_complete_candidates="<<hidden<<" late_hidden="<<late_match
   <<" K04_hidden="<<hidden_hash<<"\n";
  assert(!whole&&!immediate_hash&&!late_match&&!hidden_hash);
 }
}
