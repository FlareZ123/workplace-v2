// H-17 K04: selected-ACK periodic bit and byte copier-fault channel.
// Source-pinned C++17/OpenSSL single-file test, run from repository root.
// Read-only: original resources, acceptance and candidate are unchanged.
// Full: 67,108,860 periodic-bit XOR + 50,529,024 byte-offset assignments.
// Fast byte3 branch: BYTE3_ONLY=1 (tests 50,331,648 assignments only).
#include <openssl/sha.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <fstream>
#include <iterator>
#include <cstdlib>

const char *PAY="A9A9DC5731A5E2AE879C47215C2559D5", *ROUTE="8556C8CB6140A7F9A5123AC7571BEE1C";
const char *HASH="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
const char *SPOOLHASH="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
unsigned char pay[16],route[16],base[16],target[32],target2[32],target3[32];
unsigned long long bitchecked=0,bytechecked=0,bithit=0,bytehit=0,bitplanted=0,byteplanted=0;

int hv(char c){return c<='9'?c-'0':(c|32)-'a'+10;}
void parse(const char *p,unsigned char *out,int n){for(int i=0;i<n;i++)out[i]=(hv(p[2*i])<<4)|hv(p[2*i+1]);}
void hexout(const unsigned char *p,int n){for(int i=0;i<n;i++)std::printf("%02X",p[i]);}
void testbit(unsigned char *candidate,int p,unsigned val,int orientation){
 unsigned char digest[32]; SHA256(candidate,16,digest);++bitchecked;
 if(!std::memcmp(digest,target,32)){++bithit;std::printf("BIT HIT p=%d val=%u orient=%d value=",p,val,orientation);hexout(candidate,16);std::puts("");}
 if(!std::memcmp(digest,target2,32))++bitplanted;
}
void testbyte(unsigned char *candidate,int p,unsigned val,int stage){
 unsigned char digest[32];SHA256(candidate,16,digest);++bytechecked;
 if(!std::memcmp(digest,target,32)){++bytehit;std::printf("BYTE HIT p=%d val=%u stage=%d value=",p,val,stage);hexout(candidate,16);std::puts("");}
 if(!std::memcmp(digest,target3,32))++byteplanted;
}
int main(){
 std::ifstream in("resources/evidence/print/spool-reconstruction.log",std::ios::binary);
 std::string spool((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
 unsigned char sh[32];char hd[65];SHA256(reinterpret_cast<const unsigned char*>(spool.data()),spool.size(),sh);
 for(int i=0;i<32;i++)std::sprintf(hd+2*i,"%02x",sh[i]);
 if(std::strcmp(hd,SPOOLHASH)||
    spool.find(std::string("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=")+PAY)==std::string::npos){
   std::puts("SOURCE FAIL");return 2;
 }
 std::ifstream rin("resources/evidence/recovery-routing.json",std::ios::binary);
 std::ifstream ain("resources/acceptance.json",std::ios::binary);
 std::string routing((std::istreambuf_iterator<char>(rin)),std::istreambuf_iterator<char>());
 std::string acceptance((std::istreambuf_iterator<char>(ain)),std::istreambuf_iterator<char>());
 if(routing.find(ROUTE)==std::string::npos||acceptance.find(HASH)==std::string::npos){
   std::puts("ROUTE/COMMITMENT FAIL");return 2;
 }
 parse(PAY,pay,16);parse(ROUTE,route,16);parse(HASH,target,32);
 for(int i=0;i<16;i++)base[i]=pay[i]^route[i];
 // Planted 17-bit periodic XOR and three-byte repeating modular adder.
 unsigned char synthbit[16];
 for(int i=0;i<16;i++){
   unsigned char b=0;
   for(int j=0;j<8;j++)b|=(((0x12FA7U>>((i*8+j)%17))&1U)<<j);
   synthbit[i]=base[i]^b;
 }
 SHA256(synthbit,16,target2);
 unsigned char synthbyte[16];const unsigned char z[3]={0xA5,0x3C,0x81};
 for(int i=0;i<16;i++)synthbyte[i]=static_cast<unsigned char>(pay[i]+z[i%3])^route[i];
 SHA256(synthbyte,16,target3);
 unsigned char candidate[16];
 // Repeated low-p-bit pattern over the 128-bit coupon. Both byte-bit orientations.
 // Requires GCC/Clang support for unsigned __int128, including MinGW/Clang on Windows.
 for(int p=1;p<=24 && !std::getenv("BYTE3_ONLY");p++){
   unsigned __int128 repeat=0;
   for(int i=0;i<128;i+=p)repeat|=static_cast<unsigned __int128>(1)<<i;
   uint32_t limit=1U<<p;
   for(uint32_t x=0;x<limit;x++){
     unsigned __int128 bits=repeat*x;
     for(int orient=0;orient<2;orient++){
       for(int j=0;j<16;j++){
         uint8_t b=static_cast<uint8_t>(bits>>(8*j));
         if(orient){
           b=((b&0xF0)>>4)|((b&0x0F)<<4);
           b=((b&0xCC)>>2)|((b&0x33)<<2);
           b=((b&0xAA)>>1)|((b&0x55)<<1);
         }
         candidate[j]=base[j]^b;
       }
       testbit(candidate,p,x,orient);
     }
   }
   std::printf("bitperiod p=%d cumulative=%llu hits=%llu\n",p,bitchecked,bithit);
   std::fflush(stdout);
 }
 // Repeat a 1,2,3-byte modular additive error over payload/mask/component.
 // In contrast with XOR, the three fault stages need not commute.
 for(int p=std::getenv("BYTE3_ONLY")?3:1;p<=3;p++){
   uint32_t limit=1U<<(8*p);
   for(uint32_t x=0;x<limit;x++){
     for(int stage=0;stage<3;stage++){
       for(int j=0;j<16;j++){
         uint8_t adder=static_cast<uint8_t>(x>>(8*(j%p)));
         candidate[j]=stage==0 ? static_cast<uint8_t>(pay[j]+adder)^route[j]
             :stage==1 ? pay[j]^static_cast<uint8_t>(route[j]+adder)
             :static_cast<uint8_t>(base[j]+adder);
       }
       testbyte(candidate,p,x,stage);
     }
   }
   std::printf("byteperiod p=%d cumulative=%llu hits=%llu\n",p,bytechecked,bytehit);
   std::fflush(stdout);
 }
 std::printf("bitchecks=%llu bithits=%llu bitsynthetic=%llu bytechecks=%llu bytehits=%llu bytesynthetic=%llu\n",
             bitchecked,bithit,bitplanted,bytechecked,bytehit,byteplanted);
 return std::getenv("BYTE3_ONLY")
   ? (bytechecked==50331648ULL&&!bytehit&&byteplanted>=1?0:1)
   : (bitchecked==67108860ULL&&bytechecked==50529024ULL&&!bithit&&!bytehit&&bitplanted>=1&&byteplanted>=1?0:1);
}
