// H-17 selected-job three-way / four-lane Boolean reconstruction.
// Original evidence, route, commitment and copied ACK bytes are read-only.
// Build: g++ -std=c++17 -O3 -fopenmp -Wno-deprecated-declarations k04_threeway_lane_boolean_sft.cpp -lcrypto -o k04-threeway
// Run: OMP_NUM_THREADS=5 ./k04-threeway /path/to/unpacked/archive [cohort 0..3]
// Cohorts select each 3-of-4 same-job records, with a different 8-bit Boolean gate independently for each of four 32-bit lanes.
// A cohort which omits the disputed ACK2 is strictly selected-byte-withheld.
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <omp.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <set>
#include <stdexcept>
using B16=std::array<unsigned char,16>;
static const char* SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char* ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char* ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const int cohorts[4][3]={{0,1,2},{0,1,3},{0,2,3},{1,2,3}};
static const char* cohort_labels[4]={"LABEL_REQ1_ACK2","LABEL_REQ1_REQ3","LABEL_ACK2_REQ3","REQ1_ACK2_REQ3"};
static const int PLANT_CODES[4]={0x96,0xE1,0xA8,0x37};
static std::string read_file(const std::string &p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("missing source: "+p);std::ostringstream s;s<<f.rdbuf();return s.str();}
static void check_sha(const std::string&s,const char*expect,const char*path){unsigned char h[32];SHA256((const unsigned char*)s.data(),s.size(),h);char hex[65];for(int i=0;i<32;i++)sprintf(hex+2*i,"%02x",h[i]);hex[64]=0;if(std::strcmp(expect,hex))throw std::runtime_error(std::string("source SHA mismatch for ")+path);}
static std::string hex_field(const std::string&s,const std::string &begin,size_t length){size_t p=s.find(begin);if(p==std::string::npos)throw std::runtime_error("missing field: "+begin);p+=begin.size();if(p+length>s.size())throw std::runtime_error("truncated field");return s.substr(p,length);}
static int nib(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;if(c>='a'&&c<='f')return c-'a'+10;throw std::runtime_error("invalid hex");}
static B16 fromhex(const std::string &s){if(s.size()!=32)throw std::runtime_error("not 16 bytes");B16 b;for(int i=0;i<16;i++)b[i]=16*nib(s[2*i])+nib(s[2*i+1]);return b;}
static std::array<uint32_t,8> digestwords(const std::string &s){if(s.size()!=64)throw std::runtime_error("digest size");std::array<uint32_t,8> r{};for(int i=0;i<8;i++){for(int j=0;j<8;j++)r[i]=(r[i]<<4)|nib(s[8*i+j]);}return r;}
static uint32_t load32(const B16&b,int lane){int i=lane*4;return uint32_t(b[i])|(uint32_t(b[i+1])<<8)|(uint32_t(b[i+2])<<16)|(uint32_t(b[i+3])<<24);}
static void store32(unsigned char*dst,uint32_t v){for(int j=0;j<4;j++)dst[j]=uint8_t(v>>(8*j));}
static uint32_t boolgate(uint32_t a,uint32_t b,uint32_t c,int gate){uint32_t v=0;for(int i=0;i<8;i++)if(gate&(1<<i)){v|=((i&4)?a:~a)&((i&2)?b:~b)&((i&1)?c:~c);}return v;}
static bool match(const SHA256_CTX &ctx,const std::array<uint32_t,8>&d){if(ctx.h[0]!=d[0])return false;for(int j=1;j<8;j++)if(ctx.h[j]!=d[j])return false;return true;}
static void print16(const unsigned char*p){for(int i=0;i<16;i++)std::printf("%02X",p[i]);}
int main(int argc,char**argv){
  try {
    if(argc<2||argc>3){std::fprintf(stderr,"Usage: %s unpacked_original_root [cohort 0..3]\n",argv[0]);return 2;}
    const std::string root=argv[1];const int only=argc==3?atoi(argv[2]):-1;if(only>=4||only< -1)return 2;
    std::string spool=read_file(root+"/evidence/print/spool-reconstruction.log");check_sha(spool,SPOOL_SHA,"spool");
    std::string route=read_file(root+"/evidence/recovery-routing.json");check_sha(route,ROUTE_SHA,"route");
    std::string accept=read_file(root+"/acceptance.json");check_sha(accept,ACCEPT_SHA,"acceptance");
    B16 mask=fromhex(hex_field(route,"\"masked_component\": \"",32));
    auto target=digestwords(hex_field(accept,"\"K04\": \"",64));
    B16 source[4];int found=0;std::istringstream in(spool);std::string line;
    while(std::getline(in,line)){
      if(line.find("JOB=PS-261003-0417 ")==std::string::npos)continue;
      if(found>=4)throw std::runtime_error("extra selected job");
      const char* fingerprints[]={"2026-10-03T16:45:00+00:00 JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL",
        "2026-10-03T18:01:00Z JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER",
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER",
        "2026-10-03T18:03:00Z JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER"};
      if(line.find(fingerprints[found])!=0)throw std::runtime_error("historical record selector mismatch");
      source[found++]=fromhex(hex_field(line,"PAYLOAD=",32));
    }
    if(found!=4)throw std::runtime_error("missing 0417 records");
    SHA256_CTX initialized{};SHA256_Init(&initialized);
    uint64_t total=0,totalhit=0;
    for(int model=0;model<4;model++){
      if(only>=0 && model!=only)continue;
      std::vector<uint32_t> per_lane[4];
      std::array<uint32_t,4> planted_words;
      for(int lane=0;lane<4;lane++){
        uint32_t a=load32(source[cohorts[model][0]],lane),b=load32(source[cohorts[model][1]],lane),c=load32(source[cohorts[model][2]],lane);
        for(int gate=0;gate<256;gate++)per_lane[lane].push_back(boolgate(a,b,c,gate));
        std::sort(per_lane[lane].begin(),per_lane[lane].end());
        per_lane[lane].erase(std::unique(per_lane[lane].begin(),per_lane[lane].end()),per_lane[lane].end());
        planted_words[lane]=boolgate(a,b,c,PLANT_CODES[lane]);
      }
      unsigned char plant[16];for(int i=0;i<4;i++)store32(plant+4*i,planted_words[i]);for(int i=0;i<16;i++)plant[i]^=mask[i];
      unsigned char plant_sha[32];SHA256(plant,16,plant_sha);
      std::string planthex;char tmp[3];for(int i=0;i<32;i++){sprintf(tmp,"%02x",plant_sha[i]);planthex+=tmp;}
      auto plant_digest=digestwords(planthex);
      for(int lane=0;lane<4;lane++){const uint32_t m=load32(mask,lane);for(uint32_t& v:per_lane[lane])v^=m;}
      int max_first=per_lane[0].size();if(const char*e=getenv("H17_MAX_FIRST"))max_first=std::min(max_first,atoi(e));
      const uint64_t count=uint64_t(max_first)*per_lane[1].size()*per_lane[2].size()*per_lane[3].size();
      std::printf("START cohort=%d name=%s selected_payload_in_inputs=%d unique_lane_values=%zu,%zu,%zu,%zu full_candidates=%llu threads=%d\n",model,cohort_labels[model],model!=1,per_lane[0].size(),per_lane[1].size(),per_lane[2].size(),per_lane[3].size(),(unsigned long long)count,omp_get_max_threads());std::fflush(stdout);
      uint64_t checks=0,phits=0,rhits=0;const double begin=omp_get_wtime();
      #pragma omp parallel reduction(+:checks,phits,rhits)
      {
        SHA256_CTX ctx{};unsigned char block[64]{};block[16]=0x80;block[63]=0x80;
        #pragma omp for schedule(static)
        for(int i0=0;i0<max_first;i0++){
          store32(block,per_lane[0][i0]);
          for(uint32_t w1:per_lane[1]){
            store32(block+4,w1);
            for(uint32_t w2:per_lane[2]){
              store32(block+8,w2);
              for(uint32_t w3:per_lane[3]){
                store32(block+12,w3);
                ctx=initialized;SHA256_Transform(&ctx,block);checks++;
                if(match(ctx,target)){
                  rhits++;
                  #pragma omp critical
                  {std::printf("ORIGINAL_HIT cohort=%d component=",model);print16(block);std::puts("");std::fflush(stdout);}
                }
                if(match(ctx,plant_digest))phits++;
              }
            }
          }
        }
      }
      std::printf("COMPLETE cohort=%d checks=%llu original_hits=%llu planted_hits=%llu seconds=%.3f\n",model,(unsigned long long)checks,(unsigned long long)rhits,(unsigned long long)phits,omp_get_wtime()-begin);std::fflush(stdout);
      if(checks!=count||(max_first==(int)per_lane[0].size() && phits!=1))throw std::runtime_error("exhaustion or synthetic control failed");
      total+=checks;totalhit+=rhits;
    }
    std::printf("SUMMARY checked=%llu original_k04_hits=%llu\n",(unsigned long long)total,(unsigned long long)totalhit);return 0;
  }catch(const std::exception &e){std::fprintf(stderr,"ERROR %s\n",e.what());return 1;}
}
