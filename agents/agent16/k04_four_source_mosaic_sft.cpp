// H-17 K04: exhaustive same-job four-fragment source-copy candidate test.
// Closest prior: v1 results/k04-byte-mosaic.c, which includes only the three RECOVER
// attempts. This adds same-job acknowledged LABEL attempt1 at 16:45 UTC.
// Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// Historical hypothesis: a stage error selects a source byte at each SAME byte
// offset from one of four job0417 retained buffers. No media checksum exists.
// Build on Linux with g++ -O3 -fopenmp this-file.cpp -lcrypto -o mosaic
// Run four disjoint exhaustive shards: --range 0 4, --range 4 4,
// --range 8 4, --range 12 4. Control hit occurs in range 4..7.
#include <openssl/sha.h>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

constexpr char SOURCE[4][33]={
"E1E60D5F6B6DD2225FA6D5A2A63AD932", // 0417 attempt1 ACK LABEL
"CD3E4F216ADB2FB180DA2AA90B33F7A4", // 0417 attempt1 REQUESTED RECOVER
"A9A9DC5731A5E2AE879C47215C2559D5", // 0417 attempt2 ACK RECOVER copied
"44D53DFC29D7943A95D89371DA58EC64"  // 0417 attempt3 REQUESTED RECOVER
};
constexpr char MASK_HEX[]="8556C8CB6140A7F9A5123AC7571BEE1C";
constexpr char TARGET_HEX[]="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";

static unsigned nib(char c){return c<='9'?c-'0':c-'A'+10;}
static void decode(const char* s,unsigned char* t,int n){
  for(int i=0;i<n;++i)t[i]=(nib(s[2*i])<<4)|nib(s[2*i+1]);
}
int main(int argc,char** argv){
  int shards=16,first=0;
  unsigned long long steps=1ULL<<28;
  if(argc==3 && !std::strcmp(argv[1],"--shards"))shards=std::clamp(std::atoi(argv[2]),0,16);
  if(argc==3 && !std::strcmp(argv[1],"--steps"))steps=std::min(steps, std::strtoull(argv[2],nullptr,10));
  if(argc==4 && !std::strcmp(argv[1],"--range")){
    first=std::clamp(std::atoi(argv[2]),0,15);
    shards=std::clamp(std::atoi(argv[3]),1,16-first);
  }
  unsigned char source[4][16],mask[16],target[32];
  for(int s=0;s<4;s++)decode(SOURCE[s],source[s],16);
  decode(MASK_HEX,mask,16);decode(TARGET_HEX,target,32);
  unsigned char synthetic[16],syntheticHash[32];
  for(int i=0;i<16;i++)synthetic[i]=source[0][i]^mask[i];
  synthetic[0]=source[1][0]^mask[0];
  synthetic[14]=source[2][14]^mask[14];
  synthetic[15]=source[1][15]^mask[15];
  SHA256(synthetic,16,syntheticHash);

  unsigned long long total=0,found=0,controls=0;
  const auto start=std::chrono::steady_clock::now();
  #pragma omp parallel for schedule(dynamic,1) reduction(+:total,found,controls)
  for(int shard=first;shard<first+shards;++shard){
    unsigned char digest[32],candidate[16];
    unsigned char digit[14]={0};
    signed char dir[14];
    std::fill(dir,dir+14,1);
    for(int i=0;i<14;++i)candidate[i]=source[0][i]^mask[i];
    candidate[14]=source[shard&3][14]^mask[14];
    candidate[15]=source[(shard>>2)&3][15]^mask[15];
    for(unsigned long long count=0;count<steps;++count){
      SHA256(candidate,16,digest);
      ++total;
      if(shard==6 && std::memcmp(digest,syntheticHash,32)==0) ++controls;
      if(std::memcmp(digest,target,32)==0){
        #pragma omp critical
        {
          ++found;
          std::printf("MATCH shard=%d choice=",shard);
          for(int i=15;i>=0;--i)std::printf("%d",i>=14?((shard>>(2*(i-14)))&3):digit[i]);
          std::printf(" component=");for(auto b:candidate)std::printf("%02X",b);
          std::printf("\n");std::fflush(stdout);
        }
      }
      if(count+1==steps)break;
      for(int k=0;k<14;++k){
        int nd=int(digit[k])+int(dir[k]);
        if(nd>=0&&nd<4){
          digit[k]=static_cast<unsigned char>(nd);
          candidate[k]=source[nd][k]^mask[k];
          break;
        }
        dir[k]=-dir[k];
      }
    }
    std::printf("SHARD_DONE %d steps=%llu\n",shard,steps);
    std::fflush(stdout);
  }
  const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::printf("COMPLETE_first=%d shards=%d tested=%llu matches=%llu synthetic_hits=%llu seconds=%.3f rate=%.1f M/s\n",first,shards,total,found,controls,seconds,total/seconds/1e6);
  if(first<=6 && first+shards>6 && controls!=1) return 2;
  return found==0 ? 0 : 1;
}
