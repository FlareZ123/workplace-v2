// One missing 32-bit printer register following cyclic source-word rotation.
// Source-owned read-only input. All original commitment comparisons are full SHA256.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>

using Bytes=std::array<unsigned char,16>;
using Digest=std::array<unsigned char,32>;

std::string hex(const unsigned char* p,size_t n){
 static constexpr char h[]="0123456789ABCDEF";std::string out;out.reserve(n*2);
 for(size_t i=0;i<n;i++){out.push_back(h[p[i]>>4]);out.push_back(h[p[i]&15]);}return out;
}
std::vector<unsigned char> unhex(const std::string& s){
 if(s.size()%2)throw std::runtime_error("hex length");std::vector<unsigned char> out;
 for(size_t i=0;i<s.size();i+=2){int a=std::stoi(s.substr(i,2),nullptr,16);out.push_back(static_cast<unsigned char>(a));}return out;
}
std::string read(const std::string& p){
 std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("cannot read: "+p);
 return std::string(std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>());
}
void source_pin(const std::string& path, const std::string& sha){
 std::string s=read(path);Digest digest{};
 SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),digest.data());
 if(hex(digest.data(),32)!=sha)throw std::runtime_error("SHA256 pin mismatch for "+path);
}
Bytes source_coupon(const std::string& path){
 std::istringstream in(read(path));std::string line,payload;int count=0;
 while(std::getline(in,line)){
  if(line.find("JOB=PS-261003-0417 ")==std::string::npos||line.find("ATTEMPT=2 STATE=ACK CLASS=RECOVER ")==std::string::npos)continue;
  auto pos=line.find("PAYLOAD=");if(pos==std::string::npos)throw std::runtime_error("selected row without payload");
  payload=line.substr(pos+8,32);count++;
 }
 if(count!=1)throw std::runtime_error("selected ACK2 not unique");auto bytes=unhex(payload);
 if(bytes.size()!=16)throw std::runtime_error("payload length");Bytes b{};std::copy(bytes.begin(),bytes.end(),b.begin());
 return b;
}
std::array<uint32_t,8> words(const Digest& d){
 std::array<uint32_t,8> out{};for(size_t i=0;i<8;i++){
  size_t o=4*i;out[i]=uint32_t(d[o])<<24|uint32_t(d[o+1])<<16|uint32_t(d[o+2])<<8|uint32_t(d[o+3]);
 }return out;
}
std::array<unsigned char,64> block(const Bytes& coupon,const Bytes& mask){
 std::array<unsigned char,64> b{};for(size_t i=0;i<16;i++)b[i]=coupon[i]^mask[i];b[16]=0x80;b[63]=128;return b;
}
void write_word(unsigned char* block,int offset,uint32_t x,const Bytes& mask){
 for(int k=0;k<4;k++)block[offset+k]=static_cast<unsigned char>(x>>(24-8*k))^mask[offset+k];
}
Digest sha_full(const Bytes& coupon,const Bytes& mask){
 Bytes comp{};for(int i=0;i<16;i++)comp[i]=coupon[i]^mask[i];Digest out{};SHA256(comp.data(),comp.size(),out.data());return out;
}
std::array<uint32_t,8> transform(const std::array<unsigned char,64>& block){
 SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,block.data());
 std::array<uint32_t,8> out{};for(int i=0;i<8;i++)out[i]=ctx.h[i];return out;
}
int main(int argc,char** argv){
 try{
  if(argc<2||argc>4)throw std::runtime_error("Usage: k04_ring_free32_sft RESOURCE_DIRECTORY [LIMIT_PER_TEMPLATE, 0=full] [THREADS]");
  const std::string root=argv[1];const uint64_t limit=argc>2?std::stoull(argv[2]):uint64_t(1)<<32;
  const int threads=argc>3?std::stoi(argv[3]):omp_get_max_threads();
  if(limit==0||limit>(uint64_t(1)<<32)||threads<1||threads>64)throw std::runtime_error("invalid bounds");
  source_pin(root+"/evidence/print/spool-reconstruction.log","7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083");
  source_pin(root+"/evidence/recovery-routing.json","F8FCBCA73D23BF1066EDB88C088F89CD24CF22E7C78A4A412166254A4764D8A5");
  source_pin(root+"/acceptance.json","681739241B757B471ACCA4C0FEF9D9D97E9493883887736D5DB3B92BFB0C137F");
  Bytes raw=source_coupon(root+"/evidence/print/spool-reconstruction.log");
  if(hex(raw.data(),16)!="A9A9DC5731A5E2AE879C47215C2559D5")throw std::runtime_error("selected copy mismatch");
  const auto m=unhex("8556C8CB6140A7F9A5123AC7571BEE1C");Bytes mask{};std::copy(m.begin(),m.end(),mask.begin());
  Digest expected{};auto e=unhex("930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");std::copy(e.begin(),e.end(),expected.begin());
  const auto ref=words(expected);
  omp_set_num_threads(threads);
  SHA256_CTX initial;SHA256_Init(&initial);
  uint64_t all=0;int originals=0,controls=0;
  auto start=std::chrono::steady_clock::now();
  std::cout<<"SOURCE_VALIDATED copied="<<hex(raw.data(),16)<<" templates=12 per_template="<<limit<<" threads="<<threads<<"\n"<<std::flush;
  // r=0 is excluded: the four source-aligned missing-register spaces are already
  // exhausted by the historical contiguous 4-byte copier scan.
  for(int rotation=1;rotation<=3;rotation++)for(int free_lane=0;free_lane<4;free_lane++){
   Bytes candidate{};for(int j=0;j<4;j++)for(int k=0;k<4;k++)candidate[4*j+k]=raw[4*((j+rotation)%4)+k];
   auto static_block=block(candidate,mask);const int off=4*free_lane;
   const uint32_t planted=0x00001234;
   Bytes plant=candidate;for(int k=0;k<4;k++)plant[off+k]=static_cast<unsigned char>(planted>>(24-8*k));
   Digest plantsha=sha_full(plant,mask);auto plant_words=words(plantsha);
   auto checkblock=block(plant,mask);if(transform(checkblock)!=plant_words)throw std::runtime_error("SHA one-block control failed");
   long long original_hits=0,synthetic_hits=0;
   auto tst=std::chrono::steady_clock::now();
   #pragma omp parallel reduction(+:original_hits,synthetic_hits)
   {
    auto b=static_block;SHA256_CTX ctx;
    #pragma omp for schedule(dynamic,1024)
    for(uint64_t i=0;i<limit;i++){
     write_word(b.data(),off,static_cast<uint32_t>(i),mask);
     ctx=initial;SHA256_Transform(&ctx,b.data());
     if(ctx.h[0]==ref[0]&&ctx.h[1]==ref[1]){
      bool matches=true;for(int k=2;k<8;k++)if(ctx.h[k]!=ref[k])matches=false;
      if(matches){original_hits++;
       Bytes rawcandidate=candidate;for(int k=0;k<4;k++)rawcandidate[off+k]=static_cast<unsigned char>(i>>(24-8*k));
       #pragma omp critical
       {std::cout<<"ORIGINAL_K04_MATCH rotation="<<rotation<<" free_lane="<<free_lane<<" free="<<i<<" coupon="<<hex(rawcandidate.data(),16)<<"\n"<<std::flush;}
      }
     }
     if(ctx.h[0]==plant_words[0]&&ctx.h[1]==plant_words[1]){
      bool matches=true;for(int k=2;k<8;k++)if(ctx.h[k]!=plant_words[k])matches=false;
      if(matches)synthetic_hits++;
     }
    }
   }
   if(synthetic_hits!=(limit>planted?1:0))throw std::runtime_error("synthetic expectation mismatch");
   all+=limit;originals+=original_hits;controls+=synthetic_hits;
   auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-tst).count();
   std::cout<<"TEMPLATE rotation="<<rotation<<" free_lane="<<free_lane<<" complete="<<limit<<" original_hits="<<original_hits<<" synthetic_hits="<<synthetic_hits<<" seconds="<<std::fixed<<std::setprecision(2)<<elapsed<<"\n"<<std::flush;
  }
  auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::cout<<"SUMMARY complete="<<all<<" original_hits="<<originals<<" synthetic_hits="<<controls<<" seconds="<<std::fixed<<std::setprecision(2)<<elapsed<<"\n"<<std::flush;
  return originals?10:0;
 }catch(const std::exception& e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
