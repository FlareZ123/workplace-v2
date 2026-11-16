// Agent40 H17 source-pinned three-hex-glyph dislocations near 4-byte word seams.
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
using Digest=std::array<unsigned char,32>;
// Compile with -DROUTE_MASK_DISLOCATION to test independent route-mask
// transcription loss instead of the selected copied physical coupon loss.
#if defined(ROUTE_MASK_DISLOCATION)
static constexpr char source[]="8556C8CB6140A7F9A5123AC7571BEE1C";
static constexpr unsigned char mask[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
#else
static constexpr char source[]="A9A9DC5731A5E2AE879C47215C2559D5";
static constexpr unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
#endif
static constexpr unsigned char target[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static std::string read(const std::string&p){std::ifstream f(p,std::ios::binary);if(!f){std::fprintf(stderr,"READ_FAILED %s\n",p.c_str());std::exit(2);}return std::string(std::istreambuf_iterator<char>(f),{});}
static void pin(const std::string&root,const char*file,const char*expected){
 const auto s=read(root+"/"+file);Digest d{};SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),d.data());const char*hd="0123456789abcdef";char h[65];for(int k=0;k<32;k++){h[2*k]=hd[d[k]>>4];h[2*k+1]=hd[d[k]&15];}h[64]=0;
 if(std::strcmp(h,expected)){std::fprintf(stderr,"SOURCE_PIN_FAILED %s\n",file);std::exit(2);}
 if(std::strcmp(file,"evidence/print/spool-reconstruction.log")==0){const std::string marker="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";auto p=s.find(marker);if(p==s.npos||s.find(marker,p+1)!=s.npos)std::exit(2);}
}
static inline unsigned digit(char c){return c<='9'?c-'0':c-'A'+10;}
static inline char encode(unsigned x){return "0123456789ABCDEF"[x];}
static inline void coords(int code,int d[3],int i[3]){
 i[2]=22+code%4;code/=4;i[1]=14+code%4;code/=4;i[0]=6+code%4;code/=4;
 d[2]=22+code%4;code/=4;d[1]=14+code%4;code/=4;d[0]=6+code%4;
}
static void mk(int support,unsigned insert_value,unsigned char out[16]){
 int d[3],i[3];coords(support,d,i);
 char preserved[29];int n=0;for(int k=0;k<32;k++)if(k!=d[0]&&k!=d[1]&&k!=d[2])preserved[n++]=source[k];
 if(n!=29)std::abort();
 char result[32];int p=0;
 for(int k=0;k<32;k++)result[k]=(k==i[0])?encode(insert_value&15):(k==i[1])?encode((insert_value>>4)&15):(k==i[2])?encode((insert_value>>8)&15):preserved[p++];
 if(p!=29)std::abort();
 for(int k=0;k<16;k++)out[k]=static_cast<unsigned char>((digit(result[2*k])<<4|digit(result[2*k+1]))^mask[k]);
}
int main(int argc,char**argv){
 if(argc!=2){std::fprintf(stderr,"USAGE resources\n");return 2;}const std::string root=argv[1];
 pin(root,"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
 pin(root,"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
 pin(root,"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
 unsigned char candidate[16];const unsigned planted=0xBA7;mk(0,planted,candidate);Digest plantsha{};SHA256(candidate,16,plantsha.data());
 uint64_t tested=0,found=0,positive=0;Digest digest{};
 for(int support=0;support<4096;++support){
   for(unsigned v=0;v<4096;++v){
    mk(support,v,candidate);SHA256(candidate,16,digest.data());++tested;
    if(support==0&&v==planted&&digest==plantsha)++positive;
    if(std::memcmp(digest.data(),target,32)==0){++found;std::printf("REAL_K04 support=%d insertion=%03X value=",support,v);for(unsigned char x:candidate)std::printf("%02X",x);std::printf("\n");}
   }
 }
 std::printf("THREE_NIBBLE_SEAMS mode=%s supports=4096 checks=%llu expected=16777216 original=%llu planted=%llu\n",
#if defined(ROUTE_MASK_DISLOCATION)
 "route-mask",
#else
 "copied-coupon",
#endif
 (unsigned long long)tested,(unsigned long long)found,(unsigned long long)positive);
 return tested==16777216ULL&&positive==1?(found?10:0):2;
}
