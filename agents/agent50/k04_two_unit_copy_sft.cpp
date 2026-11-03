// H-17 K04: exact two lost plus two inserted copied-payload units.
// Unit size g is 1 bit, 4 bits, or 8 bits; all positions and inserted values.
// Original selected 18:02 ACK2 copy, route XOR mask, and K04 SHA256 are immutable.
// Source spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// g++ -O3 -std=c++17 k04_two_unit_copy_sft.cpp -lcrypto -o k04_two_unit_copy_sft
// Usage: k04_two_unit_copy_sft bits_per_unit start_delete_pair count_pairs [synthetic_digest64]
// The optional SHA256 is for INDEPENDENT SYNTHETIC positive-control digests only.
#include <openssl/sha.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
using U8=uint8_t;
using U64=uint64_t;
constexpr U8 COPY[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
constexpr U8 MASK[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr U8 TARGET[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
int main(int argc,char**argv){
 if(argc!=4&&argc!=5)return 2;
 int g=std::atoi(argv[1]),start=std::atoi(argv[2]),len=std::atoi(argv[3]);
 if(g!=1&&g!=4&&g!=8)return 2;
 int N=128/g,limit=N*(N-1)/2,maxval=1<<g,maxcombined=1<<(2*g);
 if(start<0||len<=0||start+len>limit)return 2;
 U8 target[32],orig[128],keep[128],base[16],comp[16],digest[32];
 std::memcpy(target,TARGET,32);
 if(argc==5){
   if(std::strlen(argv[4])!=64)return 2;
   for(int i=0;i<32;++i){
     unsigned v;
     if(std::sscanf(argv[4]+i*2,"%2x",&v)!=1)return 2;
     target[i]=(U8)v;
   }
 }
 for(int i=0;i<N;++i){
   int bit=i*g;
   orig[i]=(COPY[bit/8]>>(8-g-bit%8))&(maxval-1);
 }
 U64 checked=0,accepted=0;
 int pair=0;
 double begin=std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
 for(int da=0;da<N-1;++da)for(int db=da+1;db<N;++db,++pair){
   if(pair<start||pair>=start+len)continue;
   int k=0;
   for(int i=0;i<N;++i)if(i!=da&&i!=db)keep[k++]=orig[i];
   for(int pa=0;pa<N-1;++pa)for(int pb=pa+1;pb<N;++pb){
     std::memcpy(base,MASK,16);
     k=0;
     for(int i=0;i<N;++i){
       if(i==pa||i==pb)continue;
       int bit=i*g;
       base[bit/8]^=(U8)(keep[k++]<<(8-g-bit%8));
     }
     std::memcpy(comp,base,16);
     const int ba=pa*g/8,bb=pb*g/8,sha=8-g-(pa*g%8),shb=8-g-(pb*g%8);
     for(int v=0;v<maxcombined;++v){
       if(ba==bb)comp[ba]=base[ba]^((U8)((v&(maxval-1))<<sha)|((U8)(v>>g)<<shb));
       else{
         comp[ba]=base[ba]^((U8)(v&(maxval-1))<<sha);
         comp[bb]=base[bb]^((U8)(v>>g)<<shb);
       }
       SHA256(comp,16,digest);
       ++checked;
       if(std::memcmp(digest,target,32)==0){
         ++accepted;
         std::printf("K04_EXACT_MATCH g=%d drop=%d,%d insert=%d,%d val=%X comp=",g,da,db,pa,pb,v);
         for(U8 b:comp)std::printf("%02X",b);
         std::printf("\n");
         std::fflush(stdout);
       }
     }
   }
 }
 double finish=std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
 std::printf("COMPLETE g=%d start=%d pairs=%d checked=%llu accepted=%llu elapsed=%.3f\n",
   g,start,len,(unsigned long long)checked,(unsigned long long)accepted,finish-begin);
}
