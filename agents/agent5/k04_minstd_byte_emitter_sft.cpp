// Source-only SFT: byte-serialized Park-Miller minstd_rand/minstd_rand0.
// Compile with a C++17 compiler; run from repository root, passing a spool
// path as argv[1] only when resources/ is unavailable.
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>
using Packet = std::array<unsigned char,16>;
constexpr uint64_t MOD=2147483647ULL;
Packet packet(const std::string& file,const std::string& id) {
 std::ifstream f(file); if(!f) throw std::runtime_error("missing spool source");
 const std::regex re("JOB=PS-261003-"+id+" ATTEMPT=1 STATE=ACK ");
 std::string s;
 while(std::getline(f,s)) {
  if(!std::regex_search(s,re)) continue;
  const auto p=s.find("PAYLOAD="); if(p==std::string::npos) continue;
  Packet out{}; std::string hex=s.substr(p+8,32);
  if(hex.size()!=32) throw std::runtime_error("payload width");
  for(int i=0;i<16;i++) out[i]=(unsigned char)std::stoul(hex.substr(i*2,2),nullptr,16);
  return out;
 }
 throw std::runtime_error("missing job "+id);
}
struct Count {uint64_t four=0,whole=0,first=0;};
Count scan(const Packet& bytes,uint64_t mul,int shift) {
 Count c{};
 const uint64_t lows=1ULL<<shift, highs=1ULL<<(23-shift);
 for(uint64_t h=0;h<highs;h++) {
  uint64_t prefix=(((h<<8)|bytes[0])<<shift);
  for(uint64_t l=0;l<lows;l++) {
   uint64_t state=prefix|l;
   if(state==0||state>=MOD) continue;
   bool whole=true;
   for(int j=1;j<16;j++) {
    state=(state*mul)%MOD;
    if(((state>>shift)&255)!=bytes[j]) {whole=false;break;}
    if(j==3)c.four++;
   }
   if(whole){c.whole++;c.first=prefix|l;}
  }
 }
 return c;
}
Packet fixture(uint64_t mul,uint64_t seed,int shift) {
 Packet p{}; for(int i=0;i<16;i++){seed=(seed*mul)%MOD;p[i]=(seed>>shift)&255;}
 return p;
}
int main(int argc,char**argv) {
 const char* file=argc>1?argv[1]:"resources/evidence/print/spool-reconstruction.log";
 const std::string ids[]={"0300","0303","0350","0416"};
 Packet rows[4];
 for(int i=0;i<4;i++) rows[i]=packet(file,ids[i]);
 for(uint64_t a:{16807ULL,48271ULL}) for(int shift:{0,8,16,23}) {
  std::cout<<"ORIGINAL mul="<<a<<" shift="<<shift;
  for(int i=0;i<4;i++) {
   auto r=scan(rows[i],a,shift);
   std::cout<<" job"<<ids[i]<<":four="<<r.four<<",whole="<<r.whole;
   if(r.whole) throw std::runtime_error("source matched: investigate before dismissal");
  }
  auto positive=scan(fixture(a,271828,shift),a,shift);
  const uint64_t expected=(271828*a)%MOD;
  if(positive.whole!=1||positive.first!=expected) throw std::runtime_error("planted generator failed");
  std::cout<<" synthetic=PASS\n";
 }
 std::cout<<"All 32 original full-packet tests NO_MATCH; all 8 synthetic controls PASS\n";
}
