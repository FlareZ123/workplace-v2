// Seed-complete original printer source test for XXH3-128 17+ byte metadata issuers.
// Header-only public xxHash, OpenSSL SHA256 and OpenMP; immutable original source.
// No original selected row129 or acceptance target is used in source fitting.
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <atomic>
#include <fstream>
#include <string>
#include <iterator>
#include <openssl/sha.h>
#define XXH_INLINE_ALL
#include <xxhash.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static constexpr uint64_t TAGLOW_LE=0x583F485643C5BBFBULL;
static constexpr uint64_t TAGHIGH_LE=0xA5184579063FBB64ULL;
static constexpr uint64_t TAGLOW_BE=0xFBBBC54356483F58ULL;
static constexpr uint64_t TAGHIGH_BE=0x64BB3F06794518A5ULL;
static constexpr uint64_t SEEDMAX=4294967296ULL;

int main(int argc,char** argv) {
  if(argc!=5) {fprintf(stderr,"Need: message-type start end threads\n");return 2;}
  std::ifstream inp("resources/evidence/print/spool-reconstruction.log",std::ios::binary);
  if(!inp) {fprintf(stderr,"Missing original spool source\n");return 2;}
  const std::string source((std::istreambuf_iterator<char>(inp)),std::istreambuf_iterator<char>());
  unsigned char hash[32];
  SHA256((const unsigned char*)source.data(),source.size(),hash);
  const char* actual_first = "2026-10-03T07:00:00+00:00 JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=FBBBC54356483F5864BB3F06794518A5 DEST=store";
  const char* expected_hash="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
  char hexdigest[65];
  for(int i=0;i<32;i++) std::snprintf(hexdigest+2*i,3,"%02x",hash[i]);
  if(std::strcmp(hexdigest,expected_hash)!=0 || source.find(actual_first)==std::string::npos){fprintf(stderr,"Source pin mismatch\n");return 6;}

  int typ=atoi(argv[1]);
  const uint64_t from=strtoull(argv[2],nullptr,10), to=strtoull(argv[3],nullptr,10);
  int nth=atoi(argv[4]);
  if(from>=to || to>SEEDMAX || nth<1 || nth>128 || typ<0||typ>3) return 3;
  const char * const m[4]={
    "2026-10-03T07:00:00+00:00 JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL DEST=store",
    "JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL DEST=store",
    "PS-261003-0300|1|ACK|LABEL|store",
    "PS-261003-0300/1/ACK/LABEL/store"
  };
  XXH128_hash_t chk=XXH3_128bits_withSeed(m[typ],strlen(m[typ]),0x12345678ULL);
  printf("SOURCE_SHA256_PASS\n");
  printf("SOURCE_GATE type=%d len=%zu from=%llu to=%llu threads=%d lib_reference_12345678=%016llX%016llX\n",typ,strlen(m[typ]),(unsigned long long)from,(unsigned long long)to,nth,(unsigned long long)chk.high64,(unsigned long long)chk.low64);
  XXH128_hash_t orig=XXH3_128bits_withSeed(m[typ],strlen(m[typ]),0xABCDEF01ULL);
  XXH128_hash_t altered=XXH3_128bits_withSeed(m[typ],strlen(m[typ]),0xABCDEF00ULL);
  if(orig.low64==altered.low64 || orig.high64==altered.high64) return 5;
  std::atomic<unsigned long long> first32(0), full(0), planted(0);
  #pragma omp parallel for num_threads(nth) schedule(static)
  for(uint64_t seed=from;seed<to;seed++) {
    XXH128_hash_t h=XXH3_128bits_withSeed(m[typ],strlen(m[typ]),seed);
    if((uint32_t)h.low64==(uint32_t)TAGLOW_LE || (uint32_t)h.low64==(uint32_t)TAGHIGH_LE ||
       (uint32_t)h.low64==(uint32_t)TAGLOW_BE || (uint32_t)h.low64==(uint32_t)TAGHIGH_BE) {
        first32++;
        if((h.low64==TAGLOW_LE && h.high64==TAGHIGH_LE) ||
           (h.low64==TAGHIGH_LE && h.high64==TAGLOW_LE) ||
           (h.low64==TAGLOW_BE && h.high64==TAGHIGH_BE) ||
           (h.low64==TAGHIGH_BE && h.high64==TAGLOW_BE)) {
           printf("FULL_SOURCE_HIT type=%d seed=%llu\n",typ,(unsigned long long)seed);full++;
        }
    }
    if(h.low64==orig.low64 && h.high64==orig.high64) planted++;
  }
  printf("SOURCE_FINISHED type=%d seeds=%llu first32=%llu fullsource=%llu planted=%llu plantedexpected=%llu\n",typ,(unsigned long long)(to-from),first32.load(),full.load(),planted.load(),(unsigned long long)(from<=0xABCDEF01ULL && 0xABCDEF01ULL<to));
  return planted.load()==(from<=0xABCDEF01ULL && 0xABCDEF01ULL<to) ? 0:4;
}
