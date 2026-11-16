// Agent40 H-17 K04: three independent source-buffer byte dislocations near three 4-byte seams.
// Speculative capture/reassembly fault motivated by retained-fragment spool copy.
// Candidate bytes are fully checked under original XOR mask and SHA256 commitment.
// Read-only original ZIP-extracted resources, source SHA256 pinned.
// Linux CI: g++ -O3 -std=c++17 -Wall -Wextra -Werror <file> -lcrypto -o k04_seams
// Usage: k04_seams <resources-directory> <shard-index> <shard-count> [--smoke]
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <algorithm>

using Block = std::array<unsigned char, 16>;
using Digest = std::array<unsigned char, 32>;

// Compile with ROUTE_MASK_DISLOCATION to reconstruct the transcribed 16-byte
// route-mask operand while retaining the copied selected coupon unmodified.
#if defined(ROUTE_MASK_DISLOCATION)
static constexpr Block payload{{
  0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
  0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C}};
static constexpr Block route{{
  0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,
  0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5}};
#else
static constexpr Block payload{{
  0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,
  0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5}};
static constexpr Block route{{
  0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
  0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C}};
#endif
static constexpr Digest target{{
  0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,
  0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
  0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,
  0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0}};

static std::string load(const std::string &path) {
  std::ifstream in(path, std::ios::binary);
  if (!in) { std::fprintf(stderr, "READ_FAILED %s\n", path.c_str()); std::exit(2); }
  return std::string(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
}
static std::string hex(const unsigned char *data, size_t length) {
  const char *digits="0123456789abcdef";
  std::string answer(length*2,'0');
  for(size_t i=0;i<length;++i) {
    answer[2*i]=digits[data[i]>>4];answer[2*i+1]=digits[data[i]&15];
  }
  return answer;
}
static void pin(const std::string &root, const char *filename, const char *expected) {
  const std::string path=root+"/"+filename;
  const std::string bytes=load(path);
  Digest h{};
  SHA256(reinterpret_cast<const unsigned char *>(bytes.data()), bytes.size(), h.data());
  if(hex(h.data(),h.size()) != expected) {
    std::fprintf(stderr,"SOURCE_PIN_FAILED %s\n",filename);std::exit(2);
  }
  if(std::strcmp(filename,"evidence/print/spool-reconstruction.log")==0) {
    const std::string marker="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
    const auto pos=bytes.find(marker);
    if(pos==std::string::npos||bytes.find(marker,pos+1)!=std::string::npos) {
      std::fprintf(stderr,"SELECTED_SOURCE_UNIQUE_FAILED\n");std::exit(2);
    }
  }
}
static void positions(int support, int deletion[3],int insertion[3]) {
  // Exactly one dropped and one reinserted byte near each of seams 4, 8 and 12.
  // Each zone has four candidate byte positions; zones cannot overlap.
  insertion[2]=10+(support%4);support/=4;
  insertion[1]=6+(support%4);support/=4;
  insertion[0]=2+(support%4);support/=4;
  deletion[2]=10+(support%4);support/=4;
  deletion[1]=6+(support%4);support/=4;
  deletion[0]=2+(support%4);
}
static Block base_component(int support) {
  int d[3],i[3];positions(support,d,i);
  unsigned char retained[13];int retained_length=0;
  for(int p=0;p<16;++p) if(p!=d[0]&&p!=d[1]&&p!=d[2])
    retained[retained_length++]=payload[p];
  if(retained_length!=13)std::abort();
  Block component{};int used=0;
  for(int p=0;p<16;++p) {
    const bool inserted=p==i[0]||p==i[1]||p==i[2];
    component[p]=route[p]^(inserted?0:retained[used++]);
  }
  if(used!=13)std::abort();
  return component;
}
static void assign(Block &component, const int i[3], uint32_t value) {
  component[i[0]]=route[i[0]]^static_cast<unsigned char>(value);
  component[i[1]]=route[i[1]]^static_cast<unsigned char>(value>>8);
  component[i[2]]=route[i[2]]^static_cast<unsigned char>(value>>16);
}
int main(int argc,char **argv) {
  if(argc<4||argc>5) {
    std::fprintf(stderr,"USAGE resources shard-index shard-count [--smoke]\n");return 2;
  }
  const int shard=std::atoi(argv[2]), shards=std::atoi(argv[3]);
  const bool smoke=argc==5&&std::strcmp(argv[4],"--smoke")==0;
  if(shards<1||shards>4096||shard<0||shard>=shards||(argc==5&&!smoke))return 2;
  const std::string root=argv[1];
  pin(root,"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
  pin(root,"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
  pin(root,"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
  // Test the actual repair on a nonidentity first support in this shard.
  const int first=shard;
  const uint32_t injected=0x5D3AB7;
  Block planted=base_component(first);
  int deletion[3],insertion[3];positions(first,deletion,insertion);
  assign(planted,insertion,injected);
  Digest synthetic{};SHA256(planted.data(),planted.size(),synthetic.data());
  uint64_t checked=0, positives=0, original_hits=0, supported=0;
  const uint32_t limit=smoke?(1u<<16):(1u<<24);
  for(int support=shard;support<4096;support+=shards) {
    positions(support,deletion,insertion);
    Block component=base_component(support);
    Digest computed{};
    ++supported;
    for(uint32_t value=0;value<limit;++value) {
      assign(component,insertion,value);
      SHA256(component.data(),component.size(),computed.data());
      ++checked;
      if(support==first && value==injected && computed==synthetic && component==planted)
        ++positives;
      if(computed==target) {
        ++original_hits;
        std::fprintf(stderr,"K04_HIT support=%d del=%d,%d,%d ins=%d,%d,%d value=%06X component=%s\n",
          support,deletion[0],deletion[1],deletion[2],insertion[0],insertion[1],insertion[2],
          value,hex(component.data(),component.size()).c_str());
        std::fflush(stderr);
      }
    }
    if((supported%8)==0) {
      std::printf("PROGRESS shard=%d supports=%llu checks=%llu\n", shard,
        static_cast<unsigned long long>(supported),static_cast<unsigned long long>(checked));
      std::fflush(stdout);
    }
  }
  const uint64_t expected_supports=(4095-shard)/shards+1;
  const uint64_t expected=expected_supports*limit;
  std::printf("THREE_SEAM_%s shard=%d/%d supports=%llu expected_supports=%llu checks=%llu expected=%llu planted=%llu authentic=%llu\n",
     smoke?"SMOKE":"COMPLETE",shard,shards,
     static_cast<unsigned long long>(supported),static_cast<unsigned long long>(expected_supports),
     static_cast<unsigned long long>(checked),static_cast<unsigned long long>(expected),
     static_cast<unsigned long long>(positives),static_cast<unsigned long long>(original_hits));
  // In smoke, injected value above 2^16, so no planted control is enumerated.
  if(checked!=expected || supported!=expected_supports || positives!=(smoke?0u:1u))return 2;
  return original_hits?10:0;
}
