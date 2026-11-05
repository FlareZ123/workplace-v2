// Agent13: exact byte-multiset permutation of source-selected ACK2 coupon.
// Hypothesis: selected physical paper coupon has the same 16 bytes in another order.
// No evidence independently authenticates that copier failure mechanism.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

using B16=std::array<unsigned char,16>;
using D32=std::array<unsigned char,32>;
static constexpr B16 copied{{0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5}};
static constexpr B16 mask{{0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C}};
static constexpr D32 commitment{{0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0}};
static constexpr uint64_t TOTAL=UINT64_C(10461394944000); // 16!/2!
static constexpr uint32_t IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};

static std::string file(const char*p){
  std::ifstream f(p,std::ios::binary);
  if(!f)throw std::runtime_error(std::string("Cannot open ")+p);
  return {std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()};
}
static std::string hex(const unsigned char*d,size_t n){
  const char*h="0123456789ABCDEF";std::string s;s.reserve(n*2);
  for(size_t i=0;i<n;i++){s.push_back(h[d[i]>>4]);s.push_back(h[d[i]&15]);}return s;
}
static void pin(const char*spool,const char*route,const char*acceptance){
  const char*paths[3]={spool,route,acceptance};
  const char*digests[3]={
    "7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083",
    "F8FCBCA73D23BF1066EDB88C088F89CD24CF22E7C78A4A412166254A4764D8A5",
    "681739241B757B471ACCA4C0FEF9D9D97E9493883887736D5DB3B92BFB0C137F"};
  for(int i=0;i<3;i++){
    auto s=file(paths[i]);unsigned char d[32];
    SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),d);
    if(hex(d,32)!=digests[i])throw std::runtime_error(std::string("Source SHA mismatch: ")+paths[i]);
    if(!i){
      auto at=s.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER");
      if(at==std::string::npos||s.find("PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5",at)>s.find(char(10),at))
        throw std::runtime_error("Wrong original selected row");
    }
  }
}
static uint64_t factorial(unsigned n){uint64_t r=1;for(unsigned i=2;i<=n;i++)r*=i;return r;}
static uint64_t count_distinct(const std::vector<unsigned char>&v){
  uint64_t result=factorial((unsigned)v.size());
  for(size_t i=0;i<v.size();){
    size_t j=i+1;while(j<v.size()&&v[j]==v[i])j++;
    result/=factorial((unsigned)(j-i));i=j;
  }
  return result;
}
static B16 unrank(uint64_t index){
  if(index>=TOTAL)throw std::invalid_argument("Rank too large");
  std::vector<unsigned char> left(copied.begin(),copied.end());
  std::sort(left.begin(),left.end());B16 out{};
  for(size_t i=0;i<16;i++){
    bool chosen=false;
    for(size_t j=0;j<left.size();j++){
      if(j&&left[j]==left[j-1])continue;
      auto rem=left;rem.erase(rem.begin()+j);
      auto possibilities=count_distinct(rem);
      if(index>=possibilities){index-=possibilities;continue;}
      out[i]=left[j];left.swap(rem);chosen=true;break;
    }
    if(!chosen)throw std::logic_error("Multiset unrank failed");
  }
  if(index)throw std::logic_error("Residual rank");
  return out;
}
static bool successor(B16&a){
  size_t i=15;
  while(i&&a[i-1]>=a[i])i--;
  if(!i)return false;
  size_t j=15;while(a[j]<=a[i-1])j--;
  std::swap(a[i-1],a[j]);
  size_t l=i,r=15;
  while(l<r){std::swap(a[l],a[r]);l++;r--;}
  return true;
}
static inline void reduce(const B16&p,unsigned char out[16]){
  for(size_t i=0;i<16;i++)out[i]=p[i]^mask[i];
}
static inline void sha16(const unsigned char raw[16],SHA256_CTX&ctx,unsigned char block[64]){
  std::memcpy(ctx.h,IV,sizeof(IV));
  std::memcpy(block,raw,16);
  SHA256_Transform(&ctx,block);
}
static bool matches(const SHA256_CTX&ctx,const D32&d){
  for(unsigned i=0;i<8;i++){
    uint32_t w=(uint32_t(d[4*i])<<24)|(uint32_t(d[4*i+1])<<16)|(uint32_t(d[4*i+2])<<8)|d[4*i+3];
    if(ctx.h[i]!=w)return false;
  }return true;
}
static void selftest(){
  if(factorial(16)/2!=TOTAL)throw std::logic_error("Wrong 16!/2 total");
  for(uint64_t rank:{UINT64_C(0),UINT64_C(1),UINT64_C(1234567),TOTAL/3,TOTAL/2,TOTAL-2,TOTAL-1}){
    auto p=unrank(rank);auto q=p;auto sorted=copied;
    std::sort(q.begin(),q.end());std::sort(sorted.begin(),sorted.end());
    if(q!=sorted)throw std::logic_error("Nonpermutation");
    unsigned char raw[16],direct[32];reduce(p,raw);SHA256(raw,16,direct);
    D32 d{};std::copy(direct,direct+32,d.begin());
    SHA256_CTX ctx{};unsigned char block[64]={};block[16]=0x80;block[63]=0x80;
    sha16(raw,ctx,block);if(!matches(ctx,d))throw std::logic_error("Fast and canonical SHA disagree");
    if(rank<TOTAL-1){auto next=p;if(!successor(next)||next!=unrank(rank+1))throw std::logic_error("Lexicographic successor wrong");}
  }
}
int main(int argc,char**argv){
  if(argc!=7){std::fprintf(stderr,"Usage: <binary> spool route acceptance shard_index shard_count max_candidates(0=full)\n");return 2;}
  try{
    pin(argv[1],argv[2],argv[3]);selftest();
    uint64_t index=std::stoull(argv[4]),parts=std::stoull(argv[5]),limit=std::stoull(argv[6]);
    if(parts<1||parts>4096||index>=parts)throw std::invalid_argument("Invalid shard");
    uint64_t start=TOTAL*index/parts,end=TOTAL*(index+1)/parts;
    if(limit&&start+limit<end)end=start+limit;
    if(end<=start)throw std::invalid_argument("Empty shard");
    uint64_t planted_rank=start+(UINT64_C(314159)%(end-start));
    auto planted_perm=unrank(planted_rank);
    unsigned char planted_component[16],planted_digest[32];
    reduce(planted_perm,planted_component);SHA256(planted_component,16,planted_digest);
    D32 planted{};std::copy(planted_digest,planted_digest+32,planted.begin());
    uint32_t plant_head=(uint32_t(planted[0])<<24)|(uint32_t(planted[1])<<16)|(uint32_t(planted[2])<<8)|planted[3];
    auto perm=unrank(start);uint64_t hits=0,plant_hits=0;
    SHA256_CTX ctx{};unsigned char block[64]={},raw[16];
    block[16]=0x80;block[63]=0x80;
    for(uint64_t rank=start;rank<end;rank++){
      reduce(perm,raw);sha16(raw,ctx,block);
      if(ctx.h[0]==UINT32_C(0x930A52A1)&&matches(ctx,commitment)){
        hits++;std::printf("K04_AUTHENTIC_MATCH rank=%llu coupon=%s component=%s\n",(unsigned long long)rank,hex(perm.data(),16).c_str(),hex(raw,16).c_str());std::fflush(stdout);
      }
      if(ctx.h[0]==plant_head&&matches(ctx,planted)){
        plant_hits++;if(rank!=planted_rank||perm!=planted_perm)throw std::logic_error("Wrong planted assignment");
      }
      if(rank+1<end&&!successor(perm))throw std::logic_error("Early permutation exhaustion");
    }
    std::printf("SHARD_COMPLETE index=%llu of=%llu start=%llu end=%llu tested=%llu original_hits=%llu planted_hits=%llu\n",
      (unsigned long long)index,(unsigned long long)parts,(unsigned long long)start,(unsigned long long)end,
      (unsigned long long)(end-start),(unsigned long long)hits,(unsigned long long)plant_hits);
    return hits?10:(plant_hits==1?0:5);
  }catch(const std::exception&e){std::fprintf(stderr,"ERROR %s\n",e.what());return 3;}
}
