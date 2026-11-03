// H17 K04: shifted four-byte fragments from four retained same-job spool buffers.
// Read-only C++17 / OpenSSL SFT; run four disjoint a-ranges: [0,26), [26,52), [52,78), [78,104).
#include <openssl/sha.h>
#include <array>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <chrono>
#include <cstdint>
#include <cstdlib>
using Block=std::array<unsigned char,16>;
using Fragment=std::array<unsigned char,4>;
constexpr Block source[4]={
{0xE1,0xE6,0x0D,0x5F,0x6B,0x6D,0xD2,0x22,0x5F,0xA6,0xD5,0xA2,0xA6,0x3A,0xD9,0x32},
{0xCD,0x3E,0x4F,0x21,0x6A,0xDB,0x2F,0xB1,0x80,0xDA,0x2A,0xA9,0x0B,0x33,0xF7,0xA4},
{0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5},
{0x44,0xD5,0x3D,0xFC,0x29,0xD7,0x94,0x3A,0x95,0xD8,0x93,0x71,0xDA,0x58,0xEC,0x64}
};
constexpr Block mask={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr std::array<unsigned char,32> target={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
int main(int argc,char**argv){
  const int lo=argc>1?std::atoi(argv[1]):0;
  const int hi=argc>2?std::atoi(argv[2]):104;
  if(lo<0||hi>104||lo>=hi)return 10;
  std::vector<Fragment> parts;
  for(int src=0;src<4;src++)for(int shift=0;shift<=12;shift++)for(int rev=0;rev<2;rev++){
    Fragment f{};
    for(int k=0;k<4;k++)f[k]=source[src][shift+(rev?3-k:k)];
    parts.push_back(f);
  }
  if(parts.size()!=104)return 1;
  auto unique=parts;std::sort(unique.begin(),unique.end());unique.erase(std::unique(unique.begin(),unique.end()),unique.end());
  if(unique.size()!=104)return 2;
  Block synthetic{};
  const std::array<int,4> chosen={3,26,53,102};
  for(int j=0;j<4;j++)for(int k=0;k<4;k++)synthetic[j*4+k]=parts[chosen[j]][k]^mask[j*4+k];
  unsigned char planted[32];SHA256(synthetic.data(),16,planted);
  if(!memcmp(planted,target.data(),32))return 3;
  std::uint64_t checked=0,planted_hits=0,original_hits=0,masked_hits=0;
  const auto start=std::chrono::steady_clock::now();
  Block direct{},reduced{};
  unsigned char digest[32];
  for(int a=lo;a<hi;a++){
    std::memcpy(direct.data(),parts[a].data(),4);
    for(int j=0;j<4;j++)reduced[j]=parts[a][j]^mask[j];
    for(int b=0;b<104;b++){
      std::memcpy(direct.data()+4,parts[b].data(),4);
      for(int j=0;j<4;j++)reduced[4+j]=parts[b][j]^mask[4+j];
      for(int c=0;c<104;c++){
        std::memcpy(direct.data()+8,parts[c].data(),4);
        for(int j=0;j<4;j++)reduced[8+j]=parts[c][j]^mask[8+j];
        for(int d=0;d<104;d++){
          std::memcpy(direct.data()+12,parts[d].data(),4);
          for(int j=0;j<4;j++)reduced[12+j]=parts[d][j]^mask[12+j];
          SHA256(reduced.data(),16,digest);
          if(!std::memcmp(digest,target.data(),32)){masked_hits++;printf("MASKED HIT %d %d %d %d\n",a,b,c,d);}
          if(!std::memcmp(digest,planted,32))planted_hits++;
          SHA256(direct.data(),16,digest);
          if(!std::memcmp(digest,target.data(),32)){original_hits++;printf("DIRECT HIT %d %d %d %d\n",a,b,c,d);}
          checked+=2;
        }
      }
    }
  }
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::printf("fragments=%zu assignments=%llu original_hits=%llu masked_hits=%llu planted=%llu secs=%.3f\n",parts.size(),(unsigned long long)checked,(unsigned long long)original_hits,(unsigned long long)masked_hits,(unsigned long long)planted_hits,seconds);
  return (checked==2ULL*(hi-lo)*104*104*104 && original_hits==0 && masked_hits==0 && planted_hits==(lo<=3&&hi>3?1ULL:0ULL))?0:4;
}
