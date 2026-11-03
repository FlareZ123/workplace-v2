// H-17 K04 combined transport-fault SFT. Read-only, C++17 + OpenSSL.
// Compile: C++17 with libcrypto. Tests first-two-byte copied ACK damage
// composed with all 24 four-word permutations and 16 word reversals.
// The selected ACK and original mask/commitment are pinned from supplied archive.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstring>
using Block=std::array<unsigned char,16>;
constexpr Block raw={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
constexpr Block mask={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr std::array<unsigned char,32> target={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
int main(){
  auto build=[&](const std::array<int,4>& p,int rev,int value){
    Block out{};
    for(int j=0;j<4;j++)for(int k=0;k<4;k++){
      int source=4*p[j]+((rev>>j&1)?3-k:k);
      out[4*j+k]=source==0?(unsigned char)(value>>8):source==1?(unsigned char)value:raw[source];
    }
    return out;
  };
  // Planted full candidate from another word order and two differing bytes.
  std::array<int,4> planted_order={2,0,3,1};
  Block planted=build(planted_order,5,0x1234);
  for(int j=0;j<16;j++)planted[j]^=mask[j];
  unsigned char planted_hash[32]; SHA256(planted.data(),16,planted_hash);
  if(!memcmp(planted_hash,target.data(),32))return 2;
  std::array<int,4> order={0,1,2,3};
  unsigned long long assignments=0,positive=0,direct_hits=0,masked_hits=0;
  const auto before=std::chrono::steady_clock::now();
  do{
    for(int rev=0;rev<16;rev++){
      Block direct=build(order,rev,0),reduced=direct;
      int pos[2]={-1,-1};
      for(int j=0;j<4;j++)for(int k=0;k<4;k++){
        int source=4*order[j]+((rev>>j&1)?3-k:k);
        if(source<2)pos[source]=4*j+k;
      }
      if(pos[0]<0||pos[1]<0)return 3;
      for(int j=0;j<16;j++)reduced[j]^=mask[j];
      unsigned char digest[32];
      for(int value=0;value<65536;value++){
        const unsigned char a=(unsigned char)(value>>8),b=(unsigned char)value;
        direct[pos[0]]=a;direct[pos[1]]=b;
        reduced[pos[0]]=a^mask[pos[0]];
        reduced[pos[1]]=b^mask[pos[1]];
        SHA256(reduced.data(),16,digest);
        if(!memcmp(digest,target.data(),32)){masked_hits++;std::printf("MASKED original hit at %d%d%d%d reverse=%d bytes=%04X\n",order[0],order[1],order[2],order[3],rev,value);}
        if(!memcmp(digest,planted_hash,32))positive++;
        SHA256(direct.data(),16,digest);
        if(!memcmp(digest,target.data(),32)){direct_hits++;std::printf("DIRECT original hit at %d%d%d%d reverse=%d bytes=%04X\n",order[0],order[1],order[2],order[3],rev,value);}
        assignments+=2;
      }
    }
  }while(std::next_permutation(order.begin(),order.end()));
  const auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-before).count();
  std::printf("K04 composed fault candidates=%llu direct=%llu masked=%llu planted=%llu elapsed=%.2fs\n",assignments,direct_hits,masked_hits,positive,seconds);
  return assignments==50331648ULL && positive==1 && !direct_hits && !masked_hits ? 0:1;
}
