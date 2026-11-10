// Agent 49 | H-17 K04 copier endian + sparse-bit composition.
// C++17 / OpenSSL. Run from repository root or pass spool path as argv[1].
// Every candidate is the complete 16-byte coupon, XORed with original mask,
// hashed against the untouched original full K04 SHA-256 commitment.
#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
using Bytes=std::array<uint8_t,16>;
static constexpr char source_hash[]="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static constexpr char target_hash[]="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static constexpr char mask_hex[]="8556C8CB6140A7F9A5123AC7571BEE1C";
static constexpr char selected_hex[]="A9A9DC5731A5E2AE879C47215C2559D5";
static uint8_t hexv(char x){return x>='0'&&x<='9'?x-'0':x>='A'&&x<='F'?x-'A'+10:x-'a'+10;}
static Bytes parse16(const char *s){Bytes r{};for(int i=0;i<16;i++)r[i]=uint8_t((hexv(s[i*2])<<4)|hexv(s[i*2+1]));return r;}
static std::array<uint8_t,32> parse32(const char *s){std::array<uint8_t,32> r{};for(int i=0;i<32;i++)r[i]=uint8_t((hexv(s[i*2])<<4)|hexv(s[i*2+1]));return r;}
static void require_source(const std::string &path){
 std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("spool path not readable");
 const std::string raw((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 uint8_t digest[32];SHA256((const uint8_t*)raw.data(),raw.size(),digest);
 if(!std::equal(digest,digest+32,parse32(source_hash).begin()))throw std::runtime_error("original spool source hash mismatch");
 std::istringstream input(raw);std::string line;int count=0;
 while(std::getline(input,line))if(line.find("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ")!=std::string::npos){
  const auto p=line.find("PAYLOAD=");if(p==std::string::npos||line.substr(p+8,32)!=selected_hex||line.find("DEST=bench")==std::string::npos)throw std::runtime_error("selected original row changed");count++;
 }
 if(count!=1)throw std::runtime_error("selected ACK row must occur exactly once");
}
static Bytes base(const Bytes &source,int variant){
 Bytes r{};
 for(int dst=0;dst<16;dst++){
  int from=dst;
  switch(variant){
   case 0:from=(dst/4)*4+(3-dst%4);break; // byte reversal in each native dword
   case 1:from=(3-dst/4)*4+dst%4;break; // reverse dword order
   case 2:from=15-dst;break; // whole-buffer byte order inversion
   case 3:from=(dst%4)*4+(dst/4);break; // 4x4 byte raster transpose
   default:throw std::runtime_error("unknown endian geometry");
  }
  r[dst]=source[from];
 }
 return r;
}
static constexpr const char *labels[]={"per-dword-endian","dword-order","full-byte-reverse","raster-transpose"};
static Bytes mask=parse16(mask_hex);
static std::array<uint8_t,32> expected=parse32(target_hash);
static bool check(const Bytes& coupon,const std::array<uint8_t,32>& wanted){
 Bytes c{};for(int i=0;i<16;i++)c[i]=coupon[i]^mask[i];
 uint8_t h[32];SHA256(c.data(),16,h);return std::equal(h,h+32,wanted.begin());
}
static std::array<uint8_t,32> hash_coupon(const Bytes &coupon){
 Bytes c{};for(int i=0;i<16;i++)c[i]=coupon[i]^mask[i];
 std::array<uint8_t,32> h{};SHA256(c.data(),16,h.data());return h;
}
struct Engine {
 Bytes coupon;
 uint64_t count=0;
 uint64_t original_hits=0;
 std::array<uint8_t,32> wanted=expected;
 int variant=0;
 void explore(int start,int depth){
  if(depth==0){count++;if(check(coupon,wanted)){
   original_hits++;
   if(wanted==expected){
    std::cerr<<"K04 ORIGINAL HIT variant="<<labels[variant]<<" coupon=";
    for(auto v:coupon)std::cerr<<std::hex<<std::setw(2)<<std::setfill('0')<<(unsigned)v;
    std::cerr<<std::dec<<"\n";
   }
  }return;}
  for(int bit=start;bit<=128-depth;bit++){
   coupon[bit/8]^=uint8_t(1u<<(bit%8));
   explore(bit+1,depth-1);
   coupon[bit/8]^=uint8_t(1u<<(bit%8));
  }
 }
};
static void synthetic_check(){
 const Bytes src=parse16(selected_hex);
 for(int v=0;v<4;v++){
  Bytes c=base(src,v);
  c[0]^=0x40; c[6]^=0x08; c[14]^=0x02; // an entire 128-bit coupon with three physical faults
  auto synthetic=hash_coupon(c);
  if(!check(c,synthetic))throw std::runtime_error("synthetic full-coupon positive failed");
  Engine e; e.coupon=base(src,v); e.wanted=synthetic; e.variant=v; e.explore(0,3);
  if(e.original_hits!=1||e.count!=341376)throw std::runtime_error("entire three-bit shell failed planted coupon recovery");
  c[14]^=0x02;
  if(check(c,synthetic))throw std::runtime_error("synthetic wrong-coupon negative failed");
 }
}
int main(int argc,char **argv){
 try{
  std::string path=argc>=2?argv[1]:"resources/evidence/print/spool-reconstruction.log";
  require_source(path);synthetic_check();
  if(argc>=3 && std::string(argv[2])=="--self-test"){std::cout<<"four complete planted three-bit exhaustive shells PASS\n";return 0;}
  auto original=parse16(selected_hex);
  if(check(original,expected))throw std::runtime_error("copied ACK unexpectedly accepted");
  std::cout<<"source SHA pinned, original copied ACK rejected, four planted true-coupon controls PASS\n"<<std::flush;
  uint64_t total=0, hits=0;
  for(int variant=0;variant<4;variant++){
   Engine e;e.coupon=base(original,variant);e.variant=variant;
   for(int weight=0;weight<=5;weight++){
    const uint64_t before=e.count;
    e.explore(0,weight);
    std::cout<<"transform="<<labels[variant]<<" bit_error_weight="<<weight<<" count="<<(e.count-before)<<" matches="<<e.original_hits<<"\n"<<std::flush;
   }
   total+=e.count;hits+=e.original_hits;
  }
  std::cout<<"FINAL original complete coupon commitments="<<total<<" original_hits="<<hits<<"\n";
  return hits>0?0:2;
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 3;}
}
