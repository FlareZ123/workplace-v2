/* H17 selected ESC-N ACK2: first five physical bytes possibly miscopied.
   Source-copy is not authenticated; this program does not modify evidence. */
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
using U8=unsigned char;
using B16=std::array<U8,16>;
using D32=std::array<U8,32>;
static constexpr B16 copied{{0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5}};
static constexpr B16 mask{{0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C}};
static constexpr D32 goal{{0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0}};
static constexpr uint32_t IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static constexpr uint64_t TOTAL=UINT64_C(1)<<40;
static std::string load(const char*p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("missing original");return {std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()};}
static std::string hex(const U8*d,size_t n){std::string s;const char*h="0123456789ABCDEF";for(size_t i=0;i<n;i++){s+=h[d[i]>>4];s+=h[d[i]&15];}return s;}
static void pin(const char*spool,const char*route,const char*accept){
 const char*paths[3]={spool,route,accept};
 const char*checks[3]={"7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083","F8FCBCA73D23BF1066EDB88C088F89CD24CF22E7C78A4A412166254A4764D8A5","681739241B757B471ACCA4C0FEF9D9D97E9493883887736D5DB3B92BFB0C137F"};
 for(int k=0;k<3;k++){auto s=load(paths[k]);U8 d[32];SHA256(reinterpret_cast<const U8*>(s.data()),s.size(),d);if(hex(d,32)!=checks[k])throw std::runtime_error("source sha mismatch");
 if(k==0){auto i=s.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER");if(i==std::string::npos||s.find("PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5",i)>s.find('\n',i))throw std::runtime_error("selected row mismatch");}}
}
static inline void put40(uint64_t v,U8*block){for(int i=4;i>=0;i--){block[i]=U8(v)^mask[i];v>>=8;}}
static inline void hash(SHA256_CTX&ctx,const U8*block){std::memcpy(ctx.h,IV,sizeof IV);SHA256_Transform(&ctx,block);}
static bool equal(const SHA256_CTX&ctx,const D32&d){for(int i=0;i<8;i++){uint32_t v=(uint32_t(d[4*i])<<24)|(uint32_t(d[4*i+1])<<16)|(uint32_t(d[4*i+2])<<8)|d[4*i+3];if(v!=ctx.h[i])return false;}return true;}
int main(int argc,char**argv){
 if(argc!=7){std::fprintf(stderr,"arguments: spool route acceptance shard parts limit(0=full)\n");return 2;}
 try{
  pin(argv[1],argv[2],argv[3]);
  uint64_t shard=std::stoull(argv[4]),parts=std::stoull(argv[5]),limit=std::stoull(argv[6]);
  if(parts<1||parts>4096||shard>=parts)throw std::runtime_error("invalid shard");
  uint64_t begin=TOTAL*shard/parts,end=TOTAL*(shard+1)/parts;
  if(limit&&begin+limit<end)end=begin+limit;
  if(end<=begin)throw std::runtime_error("empty shard");
  U8 block[64]={};for(int i=0;i<16;i++)block[i]=copied[i]^mask[i];block[16]=0x80;block[63]=0x80;
  SHA256_CTX ctx{};
  uint64_t planted=begin+314159%(end-begin);put40(planted,block);
  D32 plant{};SHA256(block,16,plant.data());hash(ctx,block);
  if(!equal(ctx,plant))throw std::runtime_error("fast SHA and original SHA disagree");
  uint64_t authentic=0,controls=0;
  for(uint64_t v=begin;v<end;v++){
   put40(v,block);hash(ctx,block);
   if(ctx.h[0]==UINT32_C(0x930A52A1)&&equal(ctx,goal)){
    authentic++;B16 physical{};for(int k=0;k<16;k++)physical[k]=block[k]^mask[k];
    std::printf("K04_AUTHENTIC_MATCH physical=%s component=%s\n",hex(physical.data(),16).c_str(),hex(block,16).c_str());std::fflush(stdout);
   }
   if(equal(ctx,plant)){if(v!=planted)throw std::runtime_error("unexpected planted collision");controls++;}
  }
  std::printf("K04_FIVEBYTE_PREFIX shard=%llu parts=%llu begin=%llu end=%llu tested=%llu authentic=%llu planted=%llu\n",
   (unsigned long long)shard,(unsigned long long)parts,(unsigned long long)begin,(unsigned long long)end,
   (unsigned long long)(end-begin),(unsigned long long)authentic,(unsigned long long)controls);
  return authentic?10:(controls==1?0:5);
 }catch(const std::exception&e){std::fprintf(stderr,"ERROR %s\n",e.what());return 3;}
}
