// Conditional p951 MT transfer-burst reachability SFT for H-17. No K04 commitment used.
// Built and invoked by k04_ax_batch_jump_sft.py. Input is a homogeneous GF(2) matrix.
// Output layout per state: four selected tempered uint32 words, followed by
// three arrays of sixteen future upper-16 tempered words, little endian.
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>
struct Row { uint32_t pivot; std::array<uint64_t,312> eq; };
static uint32_t temper(uint32_t x) {
 x^=x>>11; x^=(x<<7)&0x9d2c5680u; x^=(x<<15)&0xefc60000u; return x^(x>>18);
}
static uint32_t untemper(uint32_t x) {
 uint32_t y=x;
 for(int i=0;i<6;i++)y=x^(y>>18);x=y;
 for(int i=0;i<6;i++)y=x^((y<<15)&0xefc60000u);x=y;
 for(int i=0;i<6;i++)y=x^((y<<7)&0x9d2c5680u);x=y;
 for(int i=0;i<6;i++)y=x^(y>>11);return y;
}
static uint32_t advance(std::array<uint32_t,624>& x,uint64_t t) {
 const uint32_t a=x[t%624],b=x[(t+1)%624],y=(a&0x80000000u)|(b&0x7fffffffu);
 const uint32_t next=x[(t+397)%624]^(y>>1)^((y&1)?0x9908b0dfu:0u);
 x[t%624]=next;return next;
}
int main(int argc,char** argv) {
 if(argc!=4)return 2;
 std::mt19937 seeded(1234567); std::array<uint32_t,624> positive{};
 for(auto& v:positive)v=untemper(seeded());
 for(uint64_t t=0;t<2500;t++)if(temper(advance(positive,t))!=seeded()) {
  std::cerr<<"SEEDED_CONTROL_FAIL\n";return 3;
 }
 std::cerr<<"SEEDED_MT_ROLLING_2500 PASS\n";
 std::ifstream matrix(argv[1],std::ios::binary);
 uint32_t rank=0,nbits=0;matrix.read((char*)&rank,4);matrix.read((char*)&nbits,4);
 if(rank!=15632||nbits!=19968)throw std::runtime_error("unexpected source matrix");
 std::vector<Row> rows(rank);
 for(auto& row:rows) {
  matrix.read((char*)&row.pivot,4);matrix.read((char*)row.eq.data(),2496);
 }
 if(!matrix)throw std::runtime_error("truncated matrix");
 const int cases=std::stoi(argv[3]);
 std::ofstream output(argv[2],std::ios::binary|std::ios::trunc);
 std::mt19937_64 random(20261103);
 constexpr int ORIGIN=-1100;
 constexpr std::array<int,3> starts={-157+(1<<18),-157+(1<<21),-157+(1<<22)};
 for(int k=0;k<cases;k++) {
  std::array<uint64_t,312> state{};
  for(auto& w:state)w=random();
  for(const auto& row:rows)state[row.pivot/64]&=~(1ULL<<(row.pivot%64));
  for(const auto& row:rows) {
   const uint32_t p=row.pivot;int parity=0;
   for(uint32_t j=0;j<=p/64;j++)parity^=__builtin_parityll(state[j]&row.eq[j]);
   state[p/64]|=uint64_t(parity)<<(p%64);
  }
  if(k==0||k==cases-1) {
   for(const auto& row:rows) {
    int parity=0;
    for(unsigned j=0;j<=row.pivot/64;j++)parity^=__builtin_parityll(state[j]&row.eq[j]);
    if(parity)throw std::runtime_error("homogeneous state failed source equation");
   }
  }
  std::array<uint32_t,624> x{};
  for(int i=0;i<624;i++)x[i]=uint32_t(state[i/2]>>(32*(i%2)));
  std::array<uint32_t,4> selected{};
  std::array<std::array<uint16_t,16>,3> projected{};
  for(uint64_t t=0;t<static_cast<uint64_t>(starts.back()+16-ORIGIN-624);t++) {
   const uint32_t next=advance(x,t);
   const int stage=ORIGIN+int(t)+624;
   if(stage>=951&&stage<955)selected[stage-951]=temper(next);
   for(int c=0;c<3;c++)if(stage>=starts[c]&&stage<starts[c]+16)
    projected[c][stage-starts[c]]=uint16_t(temper(next)>>16);
  }
  output.write((const char*)selected.data(),16);
  for(const auto& section:projected)output.write((const char*)section.data(),32);
  if(k%64==0)std::cerr<<"PROJECTION "<<k<<"/"<<cases<<"\n";
 }
 output.flush();if(!output)throw std::runtime_error("failed output");
 std::cerr<<"TOTAL_STATES "<<cases<<"\n";
}
