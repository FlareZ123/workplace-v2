/* Source-pinned H-17 K04 exploratory test, 16 November 2026.
 * One observed leading A9 byte repeated by the copier, losing a final byte;
 * then exact V.17/V.29 received-stream descrambling with all 23 prior bits.
 * This is a composite speculative model, not a historical claim.
 * C++17, OpenSSL and OpenMP. Compile with -O3 -fopenmp -lcrypto.
 */
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>

static constexpr int HISTORY=23;
static constexpr unsigned HISTORIES=1u<<23;
static constexpr unsigned char copied[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static constexpr unsigned char mask[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static constexpr unsigned orig_hash[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const char *orig_hex="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const char *spool_digest="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *selected="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static void die(const char *s){std::fprintf(stderr,"FAIL: %s\n",s);std::exit(2);}
static std::string read(const std::string &p){std::ifstream f(p,std::ios::binary);if(!f)die("source unavailable");return std::string(std::istreambuf_iterator<char>(f),{});}
static std::string hex(const unsigned char *p,int n){static const char a[]="0123456789abcdef";std::string r;for(int i=0;i<n;++i){r+=a[p[i]>>4];r+=a[p[i]&15];}return r;}
static void source_pin(const std::string &root){
 const auto s=read(root+"/evidence/print/spool-reconstruction.log"); unsigned char h[32];SHA256((const unsigned char*)s.data(),s.size(),h);
 if(hex(h,32)!=spool_digest||s.find(selected)==std::string::npos||s.find(selected,s.find(selected)+1)!=std::string::npos)die("spool hash/selector");
 if(read(root+"/evidence/recovery-routing.json").find("8556C8CB6140A7F9A5123AC7571BEE1C")==std::string::npos)die("mask");
 if(read(root+"/acceptance.json").find(orig_hex)==std::string::npos)die("acceptance");
}
static std::array<unsigned char,16> decoded(unsigned state,bool msb,unsigned char last){
 unsigned char s[16];s[0]=copied[0];for(int i=1;i<15;++i)s[i]=copied[i+1];s[15]=last;
 int input[128]={},out[128]={};for(int i=0;i<128;++i){int bi=msb?7-i%8:i%8;input[i]=(s[i/8]>>bi)&1;}
 for(int i=0;i<128;++i){auto prev=[&](int back){int j=i-back;return j>=0?input[j]:(int)((state>>(j+23))&1u);};out[i]=input[i]^prev(18)^prev(23);}
 std::array<unsigned char,16> result{};for(int i=0;i<128;++i){int bi=msb?7-i%8:i%8;result[i/8]|=(unsigned char)(out[i]<<bi);}return result;
}
static unsigned word(const unsigned char *p,int i){return ((unsigned)p[4*i]<<24)|((unsigned)p[4*i+1]<<16)|((unsigned)p[4*i+2]<<8)|p[4*i+3];}
static void block_for(const std::array<unsigned char,16> &x,unsigned char b[64]){std::memset(b,0,64);for(int i=0;i<16;++i)b[i]=x[i]^mask[i];b[16]=0x80;b[63]=0x80;}
static bool same_hash(const SHA256_CTX &c,const unsigned *tar){if(c.h[0]!=tar[0])return false;for(int i=1;i<8;++i)if(c.h[i]!=tar[i])return false;return true;}
int main(int argc,char **argv){
 if(argc!=3)die("usage: original_source_root {pilot|all|shard:START:COUNT}");
 const bool all=std::strcmp(argv[2],"all")==0;
 const bool pilot=std::strcmp(argv[2],"pilot")==0;
 const bool shard=std::strncmp(argv[2],"shard:",6)==0;
 if(!all&&!pilot&&!shard)die("mode");
 int hiStart=0,hiMax=all?256:1;
 if(shard){int start=0,count=0;if(std::sscanf(argv[2],"shard:%d:%d",&start,&count)!=2||start<0||count<1||start+count>256)die("shard range");hiStart=start;hiMax=count;}
 source_pin(argv[1]);
 SHA256_CTX init;SHA256_Init(&init);unsigned char b[64],digest[32];
 for(int k=0;k<512;++k){auto c=decoded((unsigned)(k*3719u)&(HISTORIES-1u),(k&1)!=0,(unsigned char)k);block_for(c,b);SHA256(b,16,digest);SHA256_CTX z=init;SHA256_Transform(&z,b);for(int i=0;i<8;++i)if(z.h[i]!=word(digest,i))die("SHA256 transform comparison");}
 const auto planted=decoded(0x5A3C12u,true,0x42);
 block_for(planted,b);SHA256(b,16,digest);unsigned synth_hash[8];for(int i=0;i<8;++i)synth_hash[i]=word(digest,i);
 unsigned long long original=0,synthetic=0;const double started=omp_get_wtime();
 for(int mode=0;mode<2;++mode){
  const bool msb=(mode==0); const auto zero=decoded(0,msb,0);
  unsigned char deltas[23][3];for(int i=0;i<23;++i){auto alt=decoded(1u<<i,msb,0);for(int j=0;j<3;++j)deltas[i][j]=alt[j]^zero[j];for(int j=3;j<16;++j)if(alt[j]!=zero[j])die("history unexpectedly beyond first 23 bits");}
  for(unsigned state: {0u,1u,3u,0x5A3C12u,HISTORIES-1u}){auto ref=decoded(state,msb,0);auto got=zero;for(int i=0;i<23;++i)if(state&(1u<<i))for(int j=0;j<3;++j)got[j]^=deltas[i][j];if(got!=ref)die("basis control");}
  
  unsigned long long orig_mode=0,synth_mode=0;
  #pragma omp parallel for schedule(dynamic,1) reduction(+:orig_mode,synth_mode)
  for(int hi=hiStart;hi<hiStart+hiMax;++hi){
   SHA256_CTX z;unsigned char block[64];block_for(zero,block);for(int i=15;i<23;++i)if((hi>>(i-15))&1)for(int j=0;j<3;++j)block[j]^=deltas[i][j];
   unsigned old=0;
   for(unsigned lo=0;lo<(1u<<15);++lo){
    const unsigned gray=lo^(lo>>1);if(lo){const unsigned change=gray^old;const int bit=__builtin_ctz(change);for(int j=0;j<3;++j)block[j]^=deltas[bit][j];}old=gray;
    // The final unknown input byte maps bijectively onto the final descrambled byte.
    // Enumerating every output byte is identical to enumerating all 256 missing inputs.
    for(unsigned last=0;last<256;++last){block[15]=(unsigned char)last;z=init;SHA256_Transform(&z,block);
     if(same_hash(z,orig_hash)){orig_mode++;
       #pragma omp critical
       {std::printf("ORIGINAL_K04_MATCH mode=%s state=%06X output_byte=%02X component=",msb?"msb":"lsb",((unsigned)hi<<15)|gray,last);for(int k=0;k<16;++k)std::printf("%02X",block[k]);std::printf("\n");std::fflush(stdout);}}
     if(msb&&same_hash(z,synth_hash))synth_mode++;
    }
   }
  }
  original+=orig_mode;synthetic+=synth_mode;
  std::printf("MODE_DONE mode=%s checked=%llu original_hits=%llu synthetic_hits=%llu\n",msb?"msb":"lsb",(unsigned long long)hiMax*(1u<<15)*256,orig_mode,synth_mode);std::fflush(stdout);
 }
 const unsigned long long expected=(unsigned long long)hiMax*(1u<<15)*256*2;
 std::printf("FINAL checked=%llu original_hits=%llu synthetic_hits=%llu sha256_differential_pass=512 seconds=%.3f\n",expected,original,synthetic,omp_get_wtime()-started);
 if(all&&synthetic!=1)die("planted positive count");return original?10:0;
}

