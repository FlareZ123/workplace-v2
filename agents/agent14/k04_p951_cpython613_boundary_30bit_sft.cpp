// Exact conditional CPython 613-word nonlinear wrap closure for H-17.
// Original printer spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// All 132 intact ACK rows constrain the source; selected row129 is excluded.
// Enumerates all 8 source-valid boundary choices x 2^30 source-valid S1 values.
// Separate Python SFT regenerates four genuinely seeded, source-exact histories.
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

using u32=std::uint32_t;
using u64=std::uint64_t;
constexpr u32 A=1664525U,B=1566083941U;
constexpr u32 IA=4276115653U,IB=1786162797U;
constexpr u32 BASE0=0x012bd6aaU,BASE1=0x82d2ab13U,BASE2=0x342096b7U,BASE3=0x54846536U;
constexpr u32 BASE614=0x9bc79ea8U,BASE615=0x58509579U,BASE616=0xae1032c0U;
constexpr u32 mx(u32 x,u32 multiplier){return (x^(x>>30U))*multiplier;}
constexpr u32 umx(u32 y,u32 inverse){const u32 z=y*inverse;return z^(z>>30U);}
constexpr u32 FIRST=BASE1^mx(BASE0,A);
struct Branch{u32 s7,highest623,s623,a623,a616,s615,key10,s2,a3,target612;};
constexpr Branch SOURCED[8]={
{0xb575b1d8U,0U,0x04710790U,0x1eb8b052U,0xd96f90cdU,0xa28f6d4eU,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0xb575b1d8U,1U,0x84710790U,0x9eb8b052U,0x1fbe523bU,0x23e1f2a9U,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0xe3461319U,0U,0x04710790U,0x1eb8b052U,0x795681d3U,0x1e2f323dU,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0xe3461319U,1U,0x84710790U,0x9eb8b052U,0xf514325aU,0xd5a65f98U,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0xd15772a6U,0U,0x04710790U,0x1eb8b052U,0x6b1e33b8U,0x13979a00U,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0xd15772a6U,1U,0x84710790U,0x9eb8b052U,0x597e8d42U,0x025758aaU,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0x8764d067U,0U,0x04710790U,0x1eb8b052U,0xd9d6a47aU,0xbc96213bU,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U},
{0x8764d067U,1U,0x84710790U,0x9eb8b052U,0xbee9f827U,0xdc70d665U,0x3c3df54fU,0xe32e1557U,0x4ef1e1eaU,0x42c42558U}
};
constexpr Branch PLANTED={
0x02e63002U,0U,0x3ff39e71U,0xcdd36627U,0xee4f19d6U,0xfcc6c4efU,0x5e6dfe83U,0x892cac65U,0xe99fa8cbU,0x3788c3a9U};

static inline u32 predicted_s612(u32 s1,const Branch&b){
 const u32 a1end=(s1+1U)^mx(b.s623,B);
 const u32 a2=(b.s2+2U)^mx(a1end,B);
 const u32 a1first=(a1end-b.key10-10U)^mx(b.a623,A);
 const u32 key0=a1first-FIRST;
 const u32 key1=a2-(BASE2^mx(a1first,A))-1U;
 const u32 key2=b.a3-(BASE3^mx(a2,A))-2U;
 const u32 a615=umx(BASE616^(b.a616-key2-2U),IA);
 const u32 s614=umx(a615^(b.s615+615U),IB);
 const u32 a614=umx(BASE615^(a615-key1-1U),IA);
 const u32 s613=umx(a614^(s614+614U),IB);
 const u32 a613=umx(BASE614^(a614-key0),IA);
 return umx(a613^(s613+613U),IB);
}

int main(){
 if((predicted_s612(0x28d0e66bU,PLANTED)&0x7fffffffU)!=PLANTED.target612)
  throw std::logic_error("actual CPython n613 planted seeded control failed");
 constexpr u64 N=1ULL<<30,CHUNK=1ULL<<18;
 constexpr unsigned THREADS=4;
 std::vector<std::pair<int,u32>> found;
 std::mutex output_lock;
 const auto begin=std::chrono::steady_clock::now();
 for(int branch=0;branch<8;branch++){
  const auto&config=SOURCED[branch];
  std::atomic<u64> next{0};
  std::vector<std::thread> workers;
  for(unsigned t=0;t<THREADS;t++)workers.emplace_back([&]{
   while(true){
    const u64 lo=next.fetch_add(CHUNK);
    if(lo>=N)break;
    const u64 hi=std::min(N,lo+CHUNK);
    for(u64 k=lo;k<hi;k++){
     const u32 s1=(static_cast<u32>(k)<<1U)|1U;
     const u32 s612=predicted_s612(s1,config);
     if((s612&0x7fffffffU)==config.target612){
      const std::lock_guard<std::mutex> guard(output_lock);
      found.emplace_back(branch,s1);
      std::cout<<"MATCH branch="<<branch<<" S1=0x"<<std::hex<<s1
               <<" S612=0x"<<s612<<std::dec<<'\n';
     }
    }
   }
  });
  for(auto&worker:workers)worker.join();
  std::cout<<"Complete branch "<<branch<<" checked "<<N<<" candidates\n";
 }
 std::sort(found.begin(),found.end());
 if(found!=std::vector<std::pair<int,u32>>{{1,0x6a1f8b63U},{5,0x4fe06869U}})
  throw std::logic_error("exact source boundary roots mismatch");
 const double secs=std::chrono::duration<double>(
   std::chrono::steady_clock::now()-begin).count();
 std::cout<<"PASS exhaustive 8*2^30 source boundary candidates, two roots; seconds="
          <<std::fixed<<std::setprecision(2)<<secs<<'\n';
}
