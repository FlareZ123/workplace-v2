// Agent36: all-source 4x4 printer-word reassembly from any word offset.
// One complete donor 4-byte word may be selected from any of 133 source
// printer packets and from any of the four lanes, independently per output lane.
// Exactly 532^4 = 80,102,584,576 source assignments, with disjoint sharding.
// No original source or verified REC8 material is written.
// Compile: g++ -O3 -std=c++17 -fopenmp -Wno-deprecated-declarations
//  -Wall -Wextra -Werror file.cpp -lcrypto -o run
// Run: run RESOURCE_DIRECTORY shard shards [donor_limit=532]
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using B16=std::array<unsigned char,16>;
static constexpr int TOTAL=532;
static const unsigned char MASK[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
 0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const char* TARGET="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const char* SPOOLSHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char* ROUTESHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char* ACCEPTSHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static std::string hex(const unsigned char*data,size_t len){
 static const char*d="0123456789abcdef";std::string result;
 result.reserve(len*2);for(size_t i=0;i<len;i++){result+=d[data[i]>>4];result+=d[data[i]&15];}
 return result;
}
static std::vector<unsigned char> decode(const std::string& raw){
 if(raw.size()%2)throw std::runtime_error("odd hex length");
 std::vector<unsigned char> out(raw.size()/2);
 auto digit=[](char c)->int{if(c>='0'&&c<='9')return c-'0';
     if(c>='A'&&c<='F')return c-'A'+10;
     if(c>='a'&&c<='f')return c-'a'+10;
     throw std::runtime_error("nonhex");};
 for(size_t i=0;i<out.size();i++)out[i]=(unsigned char)((digit(raw[i*2])<<4)|digit(raw[i*2+1]));
 return out;
}
static std::string source(const std::string&root,const char*relative,const char*expected){
 std::ifstream f(root+"/"+relative,std::ios::binary);if(!f)throw std::runtime_error("source missing: "+std::string(relative));
 std::string all((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 unsigned char sha[32];SHA256((const unsigned char*)all.data(),all.size(),sha);
 if(hex(sha,32)!=expected)throw std::runtime_error("source SHA mismatch: "+std::string(relative));
 return all;
}
static std::array<std::array<unsigned char,4>,TOTAL> donor;
static void parse(const std::string& data){
 std::istringstream input(data);std::string line;int packets=0;
 while(std::getline(input,line)){
  const auto start=line.find("PAYLOAD=");if(start==std::string::npos)continue;
  if(start+8+32>line.size()||packets>=133)throw std::runtime_error("packet count or payload length");
  auto bytes=decode(line.substr(start+8,32));
  if(packets==129){
   if(line.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER")==std::string::npos ||
      hex(bytes.data(),16)!="a9a9dc5731a5e2ae879c47215c2559d5")
      throw std::runtime_error("selected source row mismatch");
  }
  for(int lane=0;lane<4;lane++)for(int j=0;j<4;j++)
    donor[packets*4+lane][j]=bytes[lane*4+j];
  packets++;
 }
 if(packets!=133)throw std::runtime_error("expected 133 spool payloads");
}
static void component(int a,int b,int c,int d,unsigned char out[16]){
 const int ids[]={a,b,c,d};
 for(int i=0;i<4;i++)for(int j=0;j<4;j++)
   out[i*4+j]=donor[ids[i]][j]^MASK[i*4+j];
}
static uint32_t sha_word(const unsigned char*x){return ((uint32_t)x[0]<<24)|((uint32_t)x[1]<<16)|((uint32_t)x[2]<<8)|x[3];}
int main(int argc,char**argv){try{
 if(argc<4||argc>5)throw std::runtime_error("usage: RESOURCE_DIRECTORY shard shards [donor_limit]");
 int shard=std::stoi(argv[2]),shards=std::stoi(argv[3]);
 int limit=argc==5?std::stoi(argv[4]):TOTAL;
 if(shards<1||shards>256||shard<0||shard>=shards||limit<32||limit>TOTAL)
   throw std::runtime_error("invalid shard/limit");
 parse(source(argv[1],"evidence/print/spool-reconstruction.log",SPOOLSHA));
 source(argv[1],"evidence/recovery-routing.json",ROUTESHA);
 source(argv[1],"acceptance.json",ACCEPTSHA);
 auto wanted=decode(TARGET);unsigned char raw[16],plantsha[32];
 const int planted[4]={11,14,21,28};
 component(planted[0],planted[1],planted[2],planted[3],raw);
 SHA256(raw,16,plantsha);
 uint32_t accepted[8],positive[8];
 for(int i=0;i<8;i++){accepted[i]=sha_word(wanted.data()+4*i);positive[i]=sha_word(plantsha+4*i);}
 SHA256_CTX empty;SHA256_Init(&empty);
 unsigned char block[64]={0};block[16]=0x80;block[63]=0x80;
 uint64_t count=0,hits=0,controls=0;
 for(int a=shard;a<limit;a+=shards){
  const auto &x=donor[a];
  for(int i=0;i<4;i++)block[i]=x[i]^MASK[i];
  for(int b=0;b<limit;b++){
   const auto &y=donor[b];
   for(int i=0;i<4;i++)block[4+i]=y[i]^MASK[4+i];
   for(int c=0;c<limit;c++){
    const auto &z=donor[c];
    for(int i=0;i<4;i++)block[8+i]=z[i]^MASK[8+i];
    for(int d=0;d<limit;d++){
      const auto &w=donor[d];
      for(int i=0;i<4;i++)block[12+i]=w[i]^MASK[12+i];
      SHA256_CTX state=empty;SHA256_Transform(&state,block);
      count++;
      if(state.h[0]==accepted[0]){
       bool ok=true;for(int i=1;i<8;i++)ok&=(state.h[i]==accepted[i]);
       if(ok){hits++;std::fprintf(stderr,"ORIGINAL_K04_HIT indices=%d,%d,%d,%d component=",a,b,c,d);
        for(int j=0;j<16;j++)std::fprintf(stderr,"%02X",block[j]);
        std::fputc('\n',stderr);}
      }
      if(state.h[0]==positive[0]){
       bool ok=true;for(int i=1;i<8;i++)ok&=(state.h[i]==positive[i]);
       if(ok)controls++;
      }
    }
   }
  }
 }
 uint64_t assigned=(uint64_t)(limit/shards+(shard<limit%shards));
 if(count!=assigned*(uint64_t)limit*limit*limit)throw std::runtime_error("coverage mismatch");
 const uint64_t expected_control=shard==11%shards?1:0;
 if(controls!=expected_control)throw std::runtime_error("complete synthetic coupon positive mismatch");
 std::printf("MOSAIC_DONE shard=%d shards=%d limit=%d firstwords=%llu SHA256_checks=%llu synthetic_hits=%llu original_hits=%llu\n",
 shard,shards,limit,(unsigned long long)assigned,(unsigned long long)count,
 (unsigned long long)controls,(unsigned long long)hits);
 return hits?10:0;
 }catch(const std::exception&e){std::fprintf(stderr,"ERROR %s\n",e.what());return 2;}
}
