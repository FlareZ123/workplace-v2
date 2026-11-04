// Read-only H-17 selected ACK two-stage word-rotation and bit-reflection SFT.
// C++17/OpenSSL; optional OpenMP for parallel permutation shards.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>
using B16=std::array<unsigned char,16>;
using B32=std::array<unsigned char,32>;
const std::string PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
const std::string HASH="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static B32 digest(const unsigned char* bytes,std::size_t n){B32 h{};SHA256(bytes,n,h.data());return h;}
static std::string hexd(const unsigned char* p,std::size_t n){static const char* hex="0123456789abcdef";std::string s;for(size_t i=0;i<n;++i){s+=hex[p[i]>>4];s+=hex[p[i]&15];}return s;}
static B16 unhex(const std::string& s){if(s.size()!=32)throw std::runtime_error("hex len");B16 out{};for(int i=0;i<16;i++)out[i]=(unsigned char)std::stoul(s.substr(2*i,2),nullptr,16);return out;}
static uint32_t bitrev(uint32_t x){x=((x & 0x55555555u)<<1)|((x>>1)&0x55555555u);x=((x&0x33333333u)<<2)|((x>>2)&0x33333333u);x=((x&0x0f0f0f0fu)<<4)|((x>>4)&0x0f0f0f0fu);x=((x&0x00ff00ffu)<<8)|((x>>8)&0x00ff00ffu);return(x<<16)|(x>>16);}
static uint32_t rot(uint32_t x,int r){return r?(x<<r)|(x>>(32-r)):x;}
static void word(B16&b,int lane,uint32_t w){for(int k=3;k>=0;--k){b[lane*4+k]=(unsigned char)w;w>>=8;}}
static uint32_t get(const B16&b,int lane){uint32_t a=0;for(int k=0;k<4;++k)a=(a<<8)|b[lane*4+k];return a;}
static B16 coupon(const std::array<std::array<uint32_t,64>,4>&r,
                   const std::array<int,4>&p,const std::array<int,4>&o){
 B16 out{};for(int i=0;i<4;++i)word(out,i,r[p[i]][o[i]]);return out;
}
int main(int argc,char** argv){
 if(argc!=4){std::cerr<<"args: original spool file path, permutation shard start, end (exclusive)\n";return 2;}
 int shardStart=std::stoi(argv[2]),shardEnd=std::stoi(argv[3]);
 if(shardStart<0||shardEnd>24||shardStart>=shardEnd)return 2;
 std::ifstream src(argv[1],std::ios::binary);
 if(!src){std::cerr<<"source unavailable\n";return 2;}
 std::string data((std::istreambuf_iterator<char>(src)),std::istreambuf_iterator<char>());
 if(hexd(digest((const unsigned char*)data.data(),data.size()).data(),32)!=PIN){
  std::cerr<<"original SHA mismatch\n";return 2;
 }
 const std::string id="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
 if(data.find(id)==std::string::npos||data.find(id,data.find(id)+1)!=std::string::npos)
  throw std::runtime_error("selected ACK missing/duplicated");
 B16 copied=unhex(data.substr(data.find(id)+id.size(),32));
 assert(hexd(copied.data(),16)=="a9a9dc5731a5e2ae879c47215c2559d5");
 B16 mask=unhex("8556C8CB6140A7F9A5123AC7571BEE1C");
 B32 real{};for(int i=0;i<32;++i)
  real[i]=(unsigned char)std::stoul(HASH.substr(2*i,2),nullptr,16);
 std::array<std::array<uint32_t,64>,4> rotate{};
 for(int i=0;i<4;++i)for(int r=0;r<64;++r)
  rotate[i][r]=rot(r<32?get(copied,i):bitrev(get(copied,i)),r%32);
 std::array<int,4> planted_perm={2,0,3,1},planted_rot={3,43,17,61};
 B16 planted=coupon(rotate,planted_perm,planted_rot);
 for(int i=0;i<16;++i)planted[i]^=mask[i];
 B32 synthetic=digest(planted.data(),16);
 std::vector<std::array<int,4>> permutations;
 std::array<int,4> p={0,1,2,3};
 do{permutations.push_back(p);}while(std::next_permutation(p.begin(),p.end()));
 unsigned long long actual=0,control=0;
 auto t0=std::chrono::steady_clock::now();
 #pragma omp parallel for reduction(+:actual,control) schedule(static)
 for(int k=shardStart;k<shardEnd;++k){
  auto perm=permutations[k];B16 raw{},cmp{};B32 out{};
  for(int i=0;i<64;++i)for(int j=0;j<64;++j)
   for(int l=0;l<64;++l)for(int m=0;m<64;++m){
    word(raw,0,rotate[perm[0]][i]);word(raw,1,rotate[perm[1]][j]);
    word(raw,2,rotate[perm[2]][l]);word(raw,3,rotate[perm[3]][m]);
    out=digest(raw.data(),16);
    if(out==real){++actual;
     #pragma omp critical
      std::cout<<"K04 DIRECT PASS: "<<hexd(raw.data(),16)<<"\n";
    }
    for(int t=0;t<16;++t)cmp[t]=raw[t]^mask[t];
    out=digest(cmp.data(),16);
    if(out==real){++actual;
     #pragma omp critical
      std::cout<<"K04 MASKED PASS: "<<hexd(cmp.data(),16)<<"\n";
    }
    if(out==synthetic)++control;
   }
 }
 auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
 std::cout<<"complete original stage SHA256 checks="
          <<2ULL*(shardEnd-shardStart)*64*64*64*64
          <<" original="<<actual<<" planted="<<control<<" secs="<<elapsed<<"\n";
 return (actual==0&&control==(shardStart<=13&&13<shardEnd?1ULL:0ULL))?0:1;
}
