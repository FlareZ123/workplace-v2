// H-17 K04: source-pinned selected copied payload, three-parameter position-ramp
// byte-copy model. Read-only complete original SHA256 candidate search.
#include <openssl/sha.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <chrono>

static constexpr uint8_t P[16] = {0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,
                                  0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static constexpr uint8_t M[16] = {0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
                                  0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static constexpr uint8_t T[32] = {
  0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
  0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
static std::vector<uint8_t> read(const std::string& path, const char* expected) {
 std::ifstream f(path, std::ios::binary);
 assert(f && "source missing");
 auto contents = std::vector<uint8_t>((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
 assert(!contents.empty());
 uint8_t digest[32]; SHA256(contents.data(),contents.size(),digest);
 char hex[65]; for(int i=0;i<32;i++) std::sprintf(hex+i*2,"%02x",digest[i]);
 hex[64]=0; assert(std::strcmp(hex,expected)==0 && "source SHA256 drift");
 return contents;
}
static void emit(uint32_t a,uint32_t b,uint32_t c,int stage,uint8_t out[16]) {
 for(unsigned i=0;i<16;i++) {
   const uint8_t x = stage==0?P[i] : stage==1?uint8_t(P[i]^M[i]):M[i];
   const uint8_t y = uint8_t(a*x + b*i + c);
   out[i] = stage==1?y : uint8_t(y^(stage==0?M[i]:P[i]));
 }
}
int main(int argc,char**argv) {
 assert(argc==2);
 std::string root=argv[1];
 auto spool=read(root+"/evidence/print/spool-reconstruction.log",
   "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 auto route=read(root+"/evidence/recovery-routing.json",
   "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
 auto acceptance=read(root+"/acceptance.json",
   "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
 const char* anchor = "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
 std::string printed(spool.begin(),spool.end()), routing(route.begin(),route.end()), accepts(acceptance.begin(),acceptance.end());
 assert(printed.find(anchor)!=std::string::npos);
 assert(routing.find("8556C8CB6140A7F9A5123AC7571BEE1C")!=std::string::npos);
 assert(accepts.find("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")!=std::string::npos);
 uint8_t planted[16], planted_hash[32]; emit(5,7,11,0,planted);SHA256(planted,16,planted_hash);
 uint64_t checked=0,planted_positive=0,original_hits=0;
 auto t0=std::chrono::steady_clock::now();
 uint8_t buff[16],h[32];
 for(uint32_t a=1;a<256;a+=2)
 for(uint32_t b=0;b<256;b++)
 for(uint32_t c=0;c<256;c++)
 for(int stage=0;stage<3;stage++) {
   emit(a,b,c,stage,buff);
   SHA256(buff,16,h);
   checked++;
   if(stage==0 && std::memcmp(h,planted_hash,32)==0) {
      planted_positive++;assert(a==5&&b==7&&c==11);
   }
   if(std::memcmp(h,T,32)==0) {
      original_hits++;
      std::printf("ORIGINAL_MATCH a=%u b=%u c=%u stage=%d comp=",a,b,c,stage);
      for(uint8_t x:buff) std::printf("%02X",x);
      std::puts("");
   }
 }
 assert(checked==UINT64_C(25165824) && planted_positive==1);
 auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
 std::printf("COMPLETE configurations=8388608 SHA256_checks=%llu planted=%llu original_hits=%llu seconds=%.3f\n",
   (unsigned long long)checked,(unsigned long long)planted_positive,
   (unsigned long long)original_hits,seconds);
 return original_hits?5:0;
}
