// Source-pinned single-file SFT: speculative 32-bit CRC32 additive coupon scrambler.
// Reproduces complete K04 original digest checks for ALL 2^32 initial states.
// Selected copied ACK is disputed; an ACK is not proof of physical coupon integrity.
// Usage: build with g++ -O3 -std=c++17 ... -lcrypto ; run shard total msb0|lsb0.
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <openssl/sha.h>
using B16=std::array<unsigned char,16>;
using B32=std::array<unsigned char,32>;
template<std::size_t N> static std::array<unsigned char,N> hex(const char* s){
  std::array<unsigned char,N> r{};
  for(std::size_t i=0;i<N;i++){unsigned x;if(std::sscanf(s+2*i,"%2x",&x)!=1) throw std::runtime_error("hex");r[i]=(unsigned char)x;}
  return r;
}
static B16 emit(std::uint32_t state,bool lsb){
  B16 out{};
  for(int i=0;i<128;i++){
    const unsigned bit=state&1u;
    state=(state>>1)^((state&1u)?0xEDB88320u:0u);
    out[i/8]|=(unsigned char)(bit<<(lsb?(i%8):(7-i%8)));
  }
  return out;
}
static std::pair<std::uint64_t,std::uint64_t> words(const B16& b){
  std::uint64_t x=0,y=0;std::memcpy(&x,b.data(),8);std::memcpy(&y,b.data()+8,8);return {x,y};
}
static B32 digest(std::uint64_t x,std::uint64_t y){
  B16 b{};std::memcpy(b.data(),&x,8);std::memcpy(b.data()+8,&y,8);
  B32 h{};SHA256(b.data(),16,h.data());return h;
}
static void source_pin(){
  std::ifstream file("resources/evidence/print/spool-reconstruction.log",std::ios::binary);
  if(!file) throw std::runtime_error("run at repository root");
  const std::string s((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());
  B32 h{};SHA256((const unsigned char*)s.data(),s.size(),h.data());
  if(h!=hex<32>("7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083"))
    throw std::runtime_error("spool SHA256 mismatch");
  const std::string selector="JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
  std::size_t count=0,pos=0;
  while((pos=s.find(selector,pos))!=std::string::npos){++count;pos+=selector.size();}
  if(count!=1)throw std::runtime_error("selected source row mismatch");
}
int main(int argc,char**argv){
  if(argc!=4){std::cerr<<"usage: shard total msb0|lsb0\n";return 2;}
  try{
    source_pin();
    const auto shard=(std::uint32_t)std::stoul(argv[1]),count=(std::uint32_t)std::stoul(argv[2]);
    const std::string mode=argv[3];
    if(count==0||(count&(count-1))||count>4096||shard>=count||(mode!="msb0"&&mode!="lsb0"))
      throw std::runtime_error("invalid shard");
    const bool lsb=mode=="lsb0";
    const auto ack=hex<16>("A9A9DC5731A5E2AE879C47215C2559D5");
    const auto mask=hex<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
    const auto target=hex<32>("930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");
    B16 original{};for(int i=0;i<16;i++)original[i]=ack[i]^mask[i];
    const auto [base0,base1]=words(original);
    std::array<std::pair<std::uint64_t,std::uint64_t>,32> basis{};
    for(int j=0;j<32;j++)basis[j]=words(emit(std::uint32_t(1)<<j,lsb));
    const std::uint32_t planted=0xA5301F69u;
    const auto [test0,test1]=words(emit(planted,lsb));
    const auto planted_digest=digest(base0^test0,base1^test1);
    const std::uint64_t size=(std::uint64_t(1)<<32)/count,start=size*shard,end=start+size;
    std::uint64_t gray=start^(start>>1),p0=0,p1=0;
    for(int j=0;j<32;j++)if(gray&(std::uint64_t(1)<<j)){p0^=basis[j].first;p1^=basis[j].second;}
    unsigned hits=0,positives=0;
    for(std::uint64_t i=start;i<end;i++){
      if(i>start){int bit=__builtin_ctzll(i);p0^=basis[bit].first;p1^=basis[bit].second;}
      const auto h=digest(base0^p0,base1^p1);
      if(h==target){++hits;std::printf("ORIGINAL_MATCH mode=%s seed=%08x\n",mode.c_str(),(unsigned)gray);}
      if(h==planted_digest){
        if(gray!=planted)throw std::runtime_error("unexpected synthetic collision");
        ++positives;std::printf("PLANTED_MATCH mode=%s seed=%08x\n",mode.c_str(),(unsigned)gray);
      }
      gray=i+1;gray^=gray>>1;
    }
    std::uint32_t index=planted;for(int s=1;s<32;s<<=1)index^=index>>s;
    unsigned expect=index>=start&&index<end?1:0;
    if(positives!=expect)throw std::runtime_error("planted positive missing");
    std::printf("DONE mode=%s shard=%u/%u assignments=%llu original_hits=%u planted_hits=%u\n",
      mode.c_str(),shard,count,(unsigned long long)size,hits,positives);
    return hits?42:0;
  }catch(const std::exception& e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
