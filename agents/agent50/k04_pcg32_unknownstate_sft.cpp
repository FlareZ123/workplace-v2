// PCG-XSH-RR 64/32 unknown-state reconstruction. Historical printer data never modify.
// Build: g++ -O3 -std=c++17 -fopenmp k04_pcg32_unknownstate_sft.cpp -o pcg32_sft
// Run: OMP_NUM_THREADS=5 ./pcg32_sft FBBBC543 56483F58 64BB3F06 794518A5 1
// Source spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// Parameters: PCG reference XSH-RR, constant stream increment 1442695040888963407.
// Copyright Agent50 research code, 2026-11-02. Uses only ISO C++17 and OpenMP.
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
static constexpr uint64_t A=6364136223846793005ULL;
static constexpr uint64_t C=1442695040888963407ULL;
static constexpr uint64_t LOW_MASK=(1ULL<<27)-1;
static inline uint32_t rotl(uint32_t x,unsigned r) { return r==0 ? x : (x<<r)|(x>>(32-r)); }
static inline uint32_t rotr(uint32_t x,unsigned r) { return r==0 ? x : (x>>r)|(x<<(32-r)); }
static inline uint32_t pcg(uint64_t s) {
    uint32_t x=static_cast<uint32_t>(((s>>18)^s)>>27);
    unsigned r=static_cast<unsigned>(s>>59);
    return rotr(x,r);
}
static uint64_t high_state_from_output(uint32_t y,unsigned r) {
    const uint32_t x=rotl(y,r);
    uint64_t s=(uint64_t)r<<59;
    for(int i=31;i>=0;--i) {
        const int j=i+27;
        unsigned bit=(x>>i)&1U;
        if(j+18<64) bit^=static_cast<unsigned>((s>>(j+18))&1);
        s|=(uint64_t)bit<<j;
    }
    return s;
}
static unsigned check(uint32_t y0,uint32_t y1,uint32_t y2,uint32_t y3,int gap) {
    uint64_t advanceA=1,advanceC=0;
    for(int k=0;k<gap;++k) {advanceC=advanceC*A+C;advanceA=advanceA*A;}
    std::array<uint64_t,32> H0,H1;
    for(unsigned r=0;r<32;++r) {
       H0[r]=high_state_from_output(y0,r);
       H1[r]=high_state_from_output(y1,r);
       if(pcg(H0[r])!=y0 || pcg(H1[r])!=y1) { std::fprintf(stderr,"Inverse error at r=%u\n",r);std::exit(2); }
    }
    std::atomic<uint64_t> hits2{0},hits3{0},hits4{0},first{0};
    auto t0=std::chrono::steady_clock::now();
    #pragma omp parallel for schedule(dynamic,1)
    for(int r=0;r<32;++r) {
      const uint64_t hi=H0[r];
      for(uint64_t low=0;low<(1ULL<<27);++low) {
        const uint64_t s=hi|low;
        const uint64_t sn=s*advanceA+advanceC;
        if((sn>>27)!= (H1[sn>>59]>>27)) continue;
        hits2.fetch_add(1,std::memory_order_relaxed);
        const uint64_t s2=sn*advanceA+advanceC;
        if(pcg(s2)!=y2) continue;
        hits3.fetch_add(1,std::memory_order_relaxed);
        const uint64_t s3=s2*advanceA+advanceC;
        if(pcg(s3)!=y3) continue;
        hits4.fetch_add(1,std::memory_order_relaxed);
        first.store(s,std::memory_order_relaxed);
      }
    }
    double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    std::printf("gap=%d observations=%08X %08X %08X %08X 2word=%llu 3word=%llu 4word=%llu firststate=%016llX elapsed=%.3fs\n",
        gap,y0,y1,y2,y3,(unsigned long long)hits2.load(),(unsigned long long)hits3.load(),
        (unsigned long long)hits4.load(),(unsigned long long)first.load(),elapsed);
    return (unsigned)hits4.load();
}
int main(int argc,char** argv) {
  uint64_t s=0x1234567890ABCDEFULL;
  for(int i=0;i<10000;++i) {
    const uint32_t w=pcg(s);
    const uint64_t h=high_state_from_output(w,static_cast<unsigned>(s>>59));
    if(h!=(s&~LOW_MASK)) return std::fprintf(stderr,"synthetic high-state inverse failed\n"),2;
    s=s*A+C;
  }
  std::puts("Synthetic 10,000 high-state inversions: PASS");
  if(argc!=5 && argc!=6) return std::fprintf(stderr,"Use four 32-bit hexadecimal observations [gap]\n"),2;
  std::array<uint32_t,4> w;
  for(int i=0;i<4;++i)w[i]=static_cast<uint32_t>(std::strtoul(argv[i+1],nullptr,16));
  int gap=argc==6?std::atoi(argv[5]):1;
  if(gap<1||gap>1024) return std::fprintf(stderr,"gap must be 1..1024\n"),2;
  check(w[0],w[1],w[2],w[3],gap);
}
