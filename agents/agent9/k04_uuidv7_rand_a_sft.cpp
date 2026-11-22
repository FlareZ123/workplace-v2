/**
 * K04 UUIDv7 conditional complete-coupon screen.
 * Compile: g++ -std=c++17 -O3 -pthread -Wno-deprecated-declarations -o k04_uuidv7_rand_a_sft k04_uuidv7_rand_a_sft.cpp -lcrypto
 * Run in 60,000-ms shards (inclusive start, exclusive end) and 4 threads:
 *   1791050460000 1791050520000 4
 *   1791050520000 1791050580000 4
 *   1791050580000 1791050640000 4
 * The selected original copy and original SHA commitment are immutable.
 * This is a conditional issuer model, not evidence of historical UUIDv7 use.
 */
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>
#include <openssl/sha.h>
using B16 = std::array<unsigned char,16>;
static constexpr B16 copied={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static constexpr B16 mask={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static constexpr std::array<uint32_t,8> target={
0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
struct Found {uint64_t ms=0;unsigned ra=0;int view=0;B16 coupon{},component{};};
static B16 coupon_for(uint64_t ms,unsigned ra,int view){
 B16 c{};
 for(int i=0;i<6;i++)c[5-i]=static_cast<unsigned char>(ms>>(8*i));
 c[6]=static_cast<unsigned char>(0x70|(ra>>8));c[7]=static_cast<unsigned char>(ra);
 std::memcpy(c.data()+8,copied.data()+8,8);
 if(view){
  std::swap(c[0],c[3]);std::swap(c[1],c[2]);
  std::swap(c[4],c[5]);std::swap(c[6],c[7]);
 }
 return c;
}
static B16 reduced(const B16& q){
 B16 c{};for(int i=0;i<16;i++)c[i]=q[i]^mask[i];return c;
}
static std::array<uint32_t,8> digest_words(const B16& component){
 unsigned char digest[32];SHA256(component.data(),16,digest);
 std::array<uint32_t,8> words{};
 for(int i=0;i<8;i++) words[i]=(uint32_t(digest[4*i])<<24)|(uint32_t(digest[4*i+1])<<16)|
      (uint32_t(digest[4*i+2])<<8)|uint32_t(digest[4*i+3]);
 return words;
}
static unsigned matches_both(const B16& component,const std::array<uint32_t,8>& synthetic){
 unsigned char data[64]={0};std::memcpy(data,component.data(),16);data[16]=0x80;data[63]=128;
 SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,data);
 bool original=true,planted=true;
 for(int i=0;i<8;i++){original&=ctx.h[i]==target[i];planted&=ctx.h[i]==synthetic[i];}
 return (original?1u:0u)|(planted?2u:0u);
}
int main(int argc,char** argv){
 if(argc!=4){std::fprintf(stderr,"usage: %s START_MS END_MS THREADS\n",argv[0]);return 2;}
 const uint64_t start=std::strtoull(argv[1],nullptr,10),end=std::strtoull(argv[2],nullptr,10);
 const int threads=std::atoi(argv[3]);
 if(!(start<end&&end-start<=360000&&threads>=1&&threads<=16))return 2;
 const auto tic=std::chrono::steady_clock::now();
 const B16 planted=reduced(coupon_for(start+13,0xACE,1));
 const auto planted_target=digest_words(planted);
 for(int view=0;view<2;view++)for(unsigned a:{0U,1U,0xACEU,0xFFFU}){
   const auto q=reduced(coupon_for(start+13,a,view));
   const auto digest=digest_words(q);
   unsigned char data[64]={0};std::memcpy(data,q.data(),16);data[16]=0x80;data[63]=128;
   SHA256_CTX ctx;SHA256_Init(&ctx);SHA256_Transform(&ctx,data);
   for(int j=0;j<8;j++)if(ctx.h[j]!=digest[j])return 3;
 }
 std::atomic<uint64_t> checked{0},positives{0},hits{0};
 std::vector<Found> found;std::mutex guard;
 std::vector<std::thread> workers;
 for(int t=0;t<threads;t++)workers.emplace_back([&,t]{
   uint64_t local_checked=0,local_pos=0,local_hits=0;
   std::vector<Found> local;
   for(uint64_t ms=start+t;ms<end;ms+=threads)
    for(int view=0;view<2;view++)for(unsigned ra=0;ra<4096;ra++){
      const auto q=coupon_for(ms,ra,view);const auto c=reduced(q);
      const unsigned flags=matches_both(c,planted_target);
      if(flags&1){local.push_back({ms,ra,view,q,c});local_hits++;}
      if(flags&2)local_pos++;
      local_checked++;
    }
   checked.fetch_add(local_checked);positives.fetch_add(local_pos);hits.fetch_add(local_hits);
   if(!local.empty()){std::lock_guard<std::mutex> lk(guard);found.insert(found.end(),local.begin(),local.end());}
 });
 for(auto& w:workers)w.join();
 const uint64_t expected=(end-start)*2ULL*4096ULL;
 const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-tic).count();
 const bool okay=checked==expected&&positives==1;
 std::printf("COMPLETE start=%llu end=%llu timestamp_count=%llu views=2 rand_a=4096 complete_checks=%llu expected=%llu original_hits=%llu synthetic_positives=%llu secs=%.3f valid=%d\n",
  (unsigned long long)start,(unsigned long long)end,(unsigned long long)(end-start),
  (unsigned long long)checked.load(),(unsigned long long)expected,(unsigned long long)hits.load(),
  (unsigned long long)positives.load(),seconds,int(okay));
 for(const auto& h:found){
   std::printf("ORIGINAL_MATCH ms=%llu rand_a=%u view=%d\ncoupon=", (unsigned long long)h.ms,h.ra,h.view);
   for(unsigned char x:h.coupon)std::printf("%02X",(unsigned)x);
   std::printf("\ncomponent=");
   for(unsigned char x:h.component)std::printf("%02X",(unsigned)x);
   std::printf("\n");
 }
 return okay?0:4;
}