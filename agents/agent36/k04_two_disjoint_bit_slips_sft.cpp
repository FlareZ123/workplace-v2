// H17 Agent36: two missing raw serial bits, replaced by two arbitrary bits at
// independently chosen output positions. Preserve order of 126 surviving bits.
// 8128^2*4=264,257,536 complete original K04 SHA256 candidate assignments.
// Compares unchanged selected ACK2 after official mask, original target hash.
#include <openssl/sha.h>
#include <omp.h>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using u128=unsigned __int128;
static const char* pins[][2]={
 {"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
 {"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static const uint8_t copy[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
  0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
  0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint32_t goal[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,
  0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const int N=8128;
static std::array<std::pair<int,int>,N> pairs;
static std::string shahex(const std::string&s){
 uint8_t sha[32];SHA256((const uint8_t*)s.data(),s.size(),sha);
 static const char*h="0123456789abcdef";std::string result;
 for(int i=0;i<32;i++){result+=h[sha[i]>>4];result+=h[sha[i]&15];}
 return result;
}
static void source_pin(const char*root,const char*relative,const char*expect){
 std::ifstream f(std::string(root)+"/"+relative,std::ios::binary);
 if(!f)throw std::runtime_error("source missing");
 std::string s((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 if(shahex(s)!=expect)throw std::runtime_error("source sha mismatch");
}
static u128 as_int(const uint8_t*data){u128 x=0;for(int i=0;i<16;i++)x=(x<<8)|data[i];return x;}
static u128 low_mask(int n){return n==0?u128(0):(u128(1)<<n)-1;}
static u128 del_bit(u128 value,int pos){
 const u128 low=value&low_mask(pos);
 const u128 high=pos==127?0:value>>(pos+1);
 return low|(high<<pos);
}
static u128 insert_zero(u128 value,int pos){
 const u128 low=value&low_mask(pos);
 const u128 high=value>>pos;
 if(pos==127)return low;
 return low|(high<<(pos+1));
}
static void get_component(int di,int ii,uint8_t b0,uint8_t b1,uint8_t out[16]){
 u128 raw=as_int(copy),mask128=as_int(mask);
 const auto d=pairs[di],ins=pairs[ii];
 u128 removed=del_bit(del_bit(raw,d.second),d.first);
 u128 inserted=insert_zero(insert_zero(removed,ins.first),ins.second);
 inserted|=(u128(b0)<<ins.first)|(u128(b1)<<ins.second);
 const u128 component=inserted^mask128;
 for(int k=0;k<16;k++)out[15-k]=(uint8_t)(component>>(8*k));
}
int main(int argc,char**argv){try{
 if(argc!=2&&argc!=3)throw std::runtime_error("usage: RESOURCE_ROOT [delete_pair_count]");
 int dlimit=argc==3?std::atoi(argv[2]):N;
 if(dlimit<1||dlimit>N)throw std::runtime_error("bad pair limit");
 for(auto&p:pins)source_pin(argv[1],p[0],p[1]);
 int idx=0;for(int i=0;i<128;i++)for(int j=i+1;j<128;j++)pairs[idx++]={i,j};
 assert(idx==N);
 constexpr int plant_d0=31,plant_d1=94,plant_i0=14,plant_i1=107;
 int pd=-1,pi=-1;
 for(int k=0;k<N;k++){
  if(pairs[k]==std::make_pair(plant_d0,plant_d1))pd=k;
  if(pairs[k]==std::make_pair(plant_i0,plant_i1))pi=k;
 }
 assert(pd>=0&&pi>=0);
 uint8_t planted[16],plantedhash[32];get_component(pd,pi,1,0,planted);
 SHA256(planted,16,plantedhash);uint32_t positive[8];
 for(int j=0;j<8;j++)positive[j]=((uint32_t)plantedhash[4*j]<<24)|
     ((uint32_t)plantedhash[4*j+1]<<16)|((uint32_t)plantedhash[4*j+2]<<8)|plantedhash[4*j+3];
 const u128 raw=as_int(copy),mask128=as_int(mask);
 SHA256_CTX initial;SHA256_Init(&initial);
 uint64_t positives=0,original=0,checks=0;
 const double start=omp_get_wtime();
 #pragma omp parallel reduction(+:positives,original,checks)
 {
  uint8_t block[64];SHA256_CTX state;
  #pragma omp for schedule(dynamic,1)
  for(int d=0;d<dlimit;d++){
    u128 removed=del_bit(del_bit(raw,pairs[d].second),pairs[d].first);
    for(int i=0;i<N;i++){
      const auto ins=pairs[i];
      const u128 inserted=insert_zero(insert_zero(removed,ins.first),ins.second);
      const u128 component=inserted^mask128;
      std::memset(block,0,64);
      for(int j=0;j<16;j++)block[15-j]=(uint8_t)(component>>(j*8));
      block[16]=0x80;block[63]=0x80;
      const int byte0=15-ins.first/8,byte1=15-ins.second/8;
      const uint8_t bit0=(uint8_t)(1u<<(ins.first%8)),bit1=(uint8_t)(1u<<(ins.second%8));
      for(int v=0;v<4;v++){
        if(v&1)block[byte0]^=bit0;
        if(v&2)block[byte1]^=bit1;
        state=initial;SHA256_Transform(&state,block);checks++;
        if(state.h[0]==goal[0]){
          bool match=true;for(int j=1;j<8;j++)match&=state.h[j]==goal[j];
          if(match){original++;
           #pragma omp critical
           {std::fprintf(stderr,"REAL_K04_HIT d=%d,%d i=%d,%d bits=%d component=",pairs[d].first,pairs[d].second,ins.first,ins.second,v);
            for(int j=0;j<16;j++)std::fprintf(stderr,"%02X",block[j]);
            std::fputc('\n',stderr);}
          }
        }
        if(state.h[0]==positive[0]){
          bool match=true;for(int j=1;j<8;j++)match&=state.h[j]==positive[j];
          if(match)positives++;
        }
        if(v&2)block[byte1]^=bit1;
        if(v&1)block[byte0]^=bit0;
      }
    }
  }
 }
 assert(checks==(uint64_t)dlimit*N*4);
 assert(positives>=(uint64_t)(pd<dlimit));
 std::printf("BIT_SLIP2 completed_delete_pairs=%d total_delete_pairs=%d complete_original_SHA_checks=%llu planted=%llu original_hits=%llu elapsed=%.3fs\n",
 dlimit,N,(unsigned long long)checks,(unsigned long long)positives,(unsigned long long)original,omp_get_wtime()-start);
 return original?10:0;
 }catch(const std::exception&e){std::fprintf(stderr,"ERROR: %s\n",e.what());return 2;}
}
