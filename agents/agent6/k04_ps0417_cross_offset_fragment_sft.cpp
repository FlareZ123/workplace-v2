#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>

struct Comp { int l[4]; };

static bool same(const SHA256_CTX& c, const uint32_t t[8]) {
  for (int i=0;i<8;i++) if (c.h[i]!=t[i]) return false;
  return true;
}
static void digest_words(const unsigned char d[32], uint32_t w[8]) {
  for (int i=0;i<8;i++)
    w[i]=((uint32_t)d[4*i]<<24)|((uint32_t)d[4*i+1]<<16)|
         ((uint32_t)d[4*i+2]<<8)|d[4*i+3];
}

int main(int argc, char** argv) {
  if (argc!=5) {
    std::cerr << "usage: program input.bin threads shard shard_count\n";
    return 2;
  }
  int nth=atoi(argv[2]), shard=atoi(argv[3]), nshards=atoi(argv[4]);
  if (nshards<1 || shard<0 || shard>=nshards) return 2;

  unsigned char in[112];
  std::ifstream f(argv[1],std::ios::binary);
  f.read((char*)in,sizeof(in));
  if (f.gcount()!=sizeof(in)) return 2;

  unsigned char rows[4][16], mask[16];
  memcpy(rows,in,64); memcpy(mask,in+64,16);
  uint32_t target[8]; digest_words(in+80,target);

  // Synthetic positive control: four distinct source windows, variable lengths.
  const int pl[4]={3,5,4,4}, pr[4]={0,1,2,3}, po[4]={1,2,3,4};
  unsigned char planted[16], pd[32], pblock[64]{};
  int at=0;
  for (int q=0;q<4;q++)
    for (int j=0;j<pl[q];j++) planted[at++]=rows[pr[q]][po[q]+j];
  for (int j=0;j<16;j++) pblock[j]=planted[j]^mask[j];
  pblock[16]=0x80; pblock[63]=0x80;
  SHA256(pblock,16,pd);
  uint32_t synthetic[8]; digest_words(pd,synthetic);

  SHA256_CTX initial; SHA256_Init(&initial);
  SHA256_CTX check=initial; SHA256_Transform(&check,pblock);
  if (!same(check,synthetic)) {
    std::cerr << "SHA256 transform self-check failed\n";
    return 3;
  }

  std::vector<Comp> comps;
  for (int a=1;a<=13;a++)
    for (int b=1;b<=14-a;b++)
      for (int c=1;c<=15-a-b;c++) {
        int d=16-a-b-c;
        if (d>=1) { Comp x{{a,b,c,d}}; comps.push_back(x); }
      }
  if (comps.size()!=455) return 4;

  std::vector<uint64_t> expected(nshards,0);
  for (size_t ci=0;ci<comps.size();ci++) {
    uint64_t ways=1;
    for (int q=0;q<4;q++) ways*=4ULL*(17-comps[ci].l[q]);
    expected[ci%nshards]+=ways;
  }

  std::atomic<uint64_t> done{0}, next_report{250000000ULL};
  uint64_t total=0, orig_hits=0, syn_hits=0;
  auto start=std::chrono::steady_clock::now();
  omp_set_num_threads(nth);

  #pragma omp parallel reduction(+:total,orig_hits,syn_hits)
  {
    uint64_t local=0;
    unsigned char block[64]{};
    block[16]=0x80; block[63]=0x80;
    SHA256_CTX ctx;

    #pragma omp for schedule(dynamic,1)
    for (size_t ci=0;ci<comps.size();ci++) {
      if ((int)(ci%nshards)!=shard) continue;
      const Comp& co=comps[ci];
      int l0=co.l[0], l1=co.l[1], l2=co.l[2], l3=co.l[3];
      int e0=17-l0, e1=17-l1, e2=17-l2, e3=17-l3;

      for (int r0=0;r0<4;r0++) for (int o0=0;o0<e0;o0++)
      for (int r1=0;r1<4;r1++) for (int o1=0;o1<e1;o1++)
      for (int r2=0;r2<4;r2++) for (int o2=0;o2<e2;o2++)
      for (int r3=0;r3<4;r3++) for (int o3=0;o3<e3;o3++) {
        int pos=0;
        for (int j=0;j<l0;j++,pos++) block[pos]=rows[r0][o0+j]^mask[pos];
        for (int j=0;j<l1;j++,pos++) block[pos]=rows[r1][o1+j]^mask[pos];
        for (int j=0;j<l2;j++,pos++) block[pos]=rows[r2][o2+j]^mask[pos];
        for (int j=0;j<l3;j++,pos++) block[pos]=rows[r3][o3+j]^mask[pos];

        ctx=initial; SHA256_Transform(&ctx,block);
        if (same(ctx,target)) {
          orig_hits++;
          #pragma omp critical
          { std::printf("ORIGINAL_HIT details_withheld\n"); std::fflush(stdout); }
        }
        if (same(ctx,synthetic)) syn_hits++;
        local++; total++;

        if (local>=1000000ULL) {
          uint64_t now=done.fetch_add(local)+local;
          local=0;
          uint64_t threshold=next_report.load();
          if (now>=threshold && next_report.compare_exchange_strong(threshold,threshold+250000000ULL)) {
            double sec=std::chrono::duration<double>(
                std::chrono::steady_clock::now()-start).count();
            #pragma omp critical
            { std::printf("PROGRESS shard=%d checked=%llu elapsed=%.1f s\n",
                          shard,(unsigned long long)now,sec); std::fflush(stdout); }
          }
        }
      }
    }
    if (local) done.fetch_add(local);
  }

  double sec=std::chrono::duration<double>(
      std::chrono::steady_clock::now()-start).count();
  std::printf("COMPLETE shard=%d/%d compositions=%zu candidates=%llu expected=%llu "
              "original_hits=%llu synthetic_hits=%llu elapsed=%.3f s threads=%d\n",
              shard,nshards,comps.size(),(unsigned long long)total,
              (unsigned long long)expected[shard],(unsigned long long)orig_hits,
              (unsigned long long)syn_hits,sec,nth);
  return total==expected[shard] ? 0 : 5;
}
