/* Original H-17 printer source: exhaustive native MT19937 uint32-seed first-output
 * gate at retained packet lanes 0,1,2 in both 32-bit byte orientations,
 * withholding selected copied ACK2.
 * Complete candidate producer test: a surviving seed must reproduce at least
 * two consecutive original outputs (three for lane 0/1) before any K04
 * candidate could be derived.
 * The native producer model is a hypothesis, never an authenticated printer fact.
 */
#include <algorithm>
#include <iterator>
#include <immintrin.h>
#include <openssl/sha.h>
#include <omp.h>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <sstream>
#include <regex>
#include <random>
#include <vector>
#include <unordered_map>
#include <iomanip>

static constexpr uint32_t MAG=0x9908b0dfU;
static constexpr char SPOOL_SHA[]="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
struct Record {std::array<uint32_t,4> words{};int row;};
struct Witness {int row, lane, endian;};
static __m256i temper(__m256i x) {
 x=_mm256_xor_si256(x,_mm256_srli_epi32(x,11));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,7),_mm256_set1_epi32(0x9d2c5680U)));
 x=_mm256_xor_si256(x,_mm256_and_si256(_mm256_slli_epi32(x,15),_mm256_set1_epi32(0xefc60000U)));
 return _mm256_xor_si256(x,_mm256_srli_epi32(x,18));
}
static __m256i first(__m256i s0,__m256i s1,__m256i s397){
 auto u=_mm256_or_si256(_mm256_and_si256(s0,_mm256_set1_epi32(0x80000000U)),_mm256_and_si256(s1,_mm256_set1_epi32(0x7fffffffU)));
 auto correction=_mm256_and_si256(_mm256_sub_epi32(_mm256_setzero_si256(),_mm256_and_si256(u,_mm256_set1_epi32(1))),_mm256_set1_epi32(MAG));
 return temper(_mm256_xor_si256(s397,_mm256_xor_si256(_mm256_srli_epi32(u,1),correction)));
}
static std::array<uint32_t,8> first8(__m256i seeded){
 auto x=seeded;
 __m256i s1=_mm256_setzero_si256();
 for(int i=1;i<=397;i++){
  x=_mm256_add_epi32(_mm256_mullo_epi32(_mm256_xor_si256(x,_mm256_srli_epi32(x,30)),_mm256_set1_epi32(1812433253U)),_mm256_set1_epi32(i));
  if(i==1)s1=x;
 }
 alignas(32) std::array<uint32_t,8> out{};
 _mm256_store_si256((__m256i*)out.data(),first(seeded,s1,x));
 return out;
}
static std::vector<Record> source(const std::string &path){
 std::ifstream in(path,std::ios::binary);assert(in.good());
 std::string body((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
 unsigned char d[32];SHA256((const unsigned char*)body.data(),body.size(),d);
 char got[65];for(int k=0;k<32;k++)std::sprintf(got+2*k,"%02x",d[k]);got[64]=0; assert(std::string(got)==SPOOL_SHA);
 const std::regex pattern("PAYLOAD=([0-9A-F]{32})");
 std::vector<Record> packets;
 std::istringstream lines(body);std::string line;
 while(std::getline(lines,line)) {
  if(line.rfind("2026-",0)!=0)continue;
  Record rec{};rec.row=(int)packets.size();
  if(rec.row==129){
   assert(line.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER")!=std::string::npos);
   packets.push_back(rec); // The disputed copied ACK2 payload is never decoded.
   continue;
  }
  std::smatch m;assert(std::regex_search(line,m,pattern));
  for(int k=0;k<4;k++){
   auto s=m[1].str().substr(8*k,8);
   auto hexword=std::stoul(s,nullptr,16);
   rec.words[k]=(uint32_t)(((hexword&0xff)<<24)|((hexword&0xff00)<<8)|((hexword>>8)&0xff00)|(hexword>>24));
  }
  packets.push_back(rec);
 }
 assert(packets.size()==133);
 return packets;
}
int main(int argc,char**argv){
 assert(argc==4);
 const std::vector<Record> records=source(argv[1]);
 const uint64_t begin=std::strtoull(argv[2],nullptr,10),end=std::strtoull(argv[3],nullptr,10);
 assert(begin<=end&&end<=UINT64_C(4294967296));
 std::unordered_map<uint32_t,std::vector<Witness>> words;
 std::array<uint8_t,65536> hi{},lo{};
 for(const auto &r:records)if(r.row!=129){for(int lane=0;lane<=2;lane++){
  for(int endian=0;endian<2;endian++){
   const uint32_t word=endian?__builtin_bswap32(r.words[lane]):r.words[lane];
   words[word].push_back({r.row,lane,endian});hi[word>>16]=1;lo[word&65535]=1;
  }
 }}
 assert(words.size()==792);
 for(uint32_t seed:{0U,1U,5489U,0x12345678U,0xdeadbeefU,0xffffffffU}){
  const auto values=first8(_mm256_set1_epi32((int)seed));
  std::mt19937 truegenerator(seed);assert(values[0]==truegenerator());
  assert(values[1]==values[0]);
  for(int endian=0;endian<2;endian++)for(int lane=0;lane<=2;lane++){
   std::mt19937 planted(seed);
   std::array<uint32_t,4> packet{};
   for(int j=lane;j<4;j++){
    uint32_t native=planted();
    packet[j]=endian?__builtin_bswap32(native):native;
   }
   const uint32_t recover_first=endian?__builtin_bswap32(packet[lane]):packet[lane];
   const uint32_t recover_second=endian?__builtin_bswap32(packet[lane+1]):packet[lane+1];
   assert(recover_first==values[0]);
   std::mt19937 verify(seed);
   assert(recover_first==verify() && recover_second==verify());
   if(lane<=1){
    const uint32_t recover_third=endian?__builtin_bswap32(packet[lane+2]):packet[lane+2];
    assert(recover_third==verify());
   }
  }
 }
 std::printf("SOURCE_SHA_PASS source_intact_packets=132 eligible_firstoutput_origins=792 planted_packet_layouts=36/36 seeded_controls=6/6\n");std::fflush(stdout);
 uint64_t searched=0,possible=0,first_hits=0,second_hits=0,third_hits=0;
 const double started=omp_get_wtime();
 #pragma omp parallel reduction(+:searched,possible,first_hits,second_hits,third_hits)
 {
  #pragma omp for schedule(dynamic,8192)
  for(uint64_t base=begin;base<end;base+=8){
   const int n=(int)std::min<uint64_t>(8,end-base);
   const auto vec=_mm256_setr_epi32((int)(uint32_t)(base+0),(int)(uint32_t)(base+1),(int)(uint32_t)(base+2),(int)(uint32_t)(base+3),
      (int)(uint32_t)(base+4),(int)(uint32_t)(base+5),(int)(uint32_t)(base+6),(int)(uint32_t)(base+7));
   const auto w=first8(vec);
   for(int lane=0;lane<n;lane++){
    searched++;
    uint32_t firstword=w[lane];
    if(!hi[firstword>>16]||!lo[firstword&65535])continue;
    possible++;
    const auto it=words.find(firstword);if(it==words.end())continue;
    const uint32_t seed=(uint32_t)(base+(uint64_t)lane);
    for(const auto &witness:it->second){
     first_hits++;
     std::mt19937 rng(seed);assert(rng()==firstword);
     const auto &actual=records[witness.row];
     const uint32_t two=rng(),three=rng();
     const uint32_t actual2=witness.endian?__builtin_bswap32(actual.words[witness.lane+1]):actual.words[witness.lane+1];
     const bool second=two==actual2;
     if(second)second_hits++;
     const bool third=second&&witness.lane<=1&&three==(witness.endian?__builtin_bswap32(actual.words[witness.lane+2]):actual.words[witness.lane+2]);
     if(third)third_hits++;
     if(second){
      #pragma omp critical
      {std::printf("SOURCE_FIRST2 seed=%u row=%d lane=%d endian=%d first=%08X second=%08X third=%08X third_match=%d\n",
       seed,witness.row,witness.lane,witness.endian,firstword,two,three,third?1:0);std::fflush(stdout);}
     }
    }
   }
  }
 }
 std::printf("ORIGINAL_SCAN begin=%llu end=%llu searched=%llu bloom_survivors=%llu firstword_hits=%llu secondword_hits=%llu full3_hits=%llu seconds=%.2f\n",
  (unsigned long long)begin,(unsigned long long)end,(unsigned long long)searched,(unsigned long long)possible,
  (unsigned long long)first_hits,(unsigned long long)second_hits,(unsigned long long)third_hits,omp_get_wtime()-started);
 return third_hits?2:0;
}
