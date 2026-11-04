// K04 heldout 0420 ACK2: CPython Random(float epoch seconds), 1-us clock grid.
// Original target selected PS-261003-0417 at 18:02 is deliberately absent.
// Compile as C++17 with OpenMP and OpenSSL crypto. Execute shards of 20,000,000 seeds.
#include <array>
#include <cmath>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <openssl/sha.h>

using u32=uint32_t; using u64=uint64_t;
constexpr u32 UPPER=0x80000000U, LOWER=0x7FFFFFFFU, MAG=0x9908B0DFU;
struct MT {
  std::array<u32,624> mt;
  int index;
  inline void init_genrand(u32 seed){
    mt[0]=seed;
    for(int i=1;i<624;i++)mt[i]=1812433253U*(mt[i-1]^(mt[i-1]>>30))+(u32)i;
    index=624;
  }
  inline void init_by_array(const u32* key,int len){
    init_genrand(19650218U);
    int i=1,j=0;
    for(int k=(624>len?624:len);k;k--){
      mt[i]=(mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1664525U)) + key[j] + (u32)j;
      i++;j++;
      if(i>=624){mt[0]=mt[623];i=1;}
      if(j>=len)j=0;
    }
    for(int k=623;k;k;k--){
      mt[i]=(mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1566083941U)) - (u32)i;
      i++;
      if(i>=624){mt[0]=mt[623];i=1;}
    }
    mt[0]=UPPER;
    index=624;
  }
  inline void seed_int(u64 s){
    u32 k[2]={(u32)s,(u32)(s>>32)};
    init_by_array(k,k[1]?2:1);
  }
  inline void twist(){
    for(int i=0;i<227;i++){
      u32 y=(mt[i]&UPPER)|(mt[i+1]&LOWER);
      mt[i]=mt[i+397] ^ (y>>1) ^ ((y&1)?MAG:0);
    }
    for(int i=227;i<623;i++){
      u32 y=(mt[i]&UPPER)|(mt[i+1]&LOWER);
      mt[i]=mt[i-227] ^ (y>>1) ^ ((y&1)?MAG:0);
    }
    u32 y=(mt[623]&UPPER)|(mt[0]&LOWER);
    mt[623]=mt[396] ^ (y>>1) ^ ((y&1)?MAG:0);
    index=0;
  }
  inline u32 next(){
    if(index>=624)twist();
    u32 y=mt[index++];
    y ^= y>>11;
    y ^= (y<<7)&0x9D2C5680U;
    y ^= (y<<15)&0xEFC60000U;
    y ^= y>>18;
    return y;
  }
};

static inline u64 python_hash_float(double value) {
  // CPython pyhash.c _Py_HashDouble for positive, finite Python 64bit floats.
  constexpr u64 P=(1ULL<<61)-1;
  int exponent=0;
  double mantissa=frexp(value,&exponent);
  u64 x=0;
  while(mantissa){
    x=((x<<28)&P)|(x>>(61-28));
    mantissa*=268435456.;
    exponent-=28;
    u64 integer=(u64)mantissa;
    mantissa-=(double)integer;
    x+=integer;
    if(x>=P)x-=P;
  }
  exponent=exponent>=0?exponent%61:60-((-1-exponent)%61);
  return ((x<<exponent)&P)|(x>>(61-exponent));
}
static inline u64 float_seed(u64 epoch_microsecond,int variant) {
  // Two plausible ways to round timestamp to an IEEE754 Python float:
  // float(microsecond_integer) / 1e6 versus seconds + fractional seconds.
  double t = variant == 0
    ? (double)epoch_microsecond / 1000000.
    : (double)(epoch_microsecond/1000000ULL)+(double)(epoch_microsecond%1000000ULL)*0.000001;
  return python_hash_float(t);
}

int main(int argc,char**argv){
  if(argc<3){fprintf(stderr,"usage: program start_epoch_us seed_count [phase_limit] [optional_target_hex] [original_spool_path]\n");return 2;}
  u64 first=strtoull(argv[1],nullptr,10),count=strtoull(argv[2],nullptr,10);
  int limit=argc>3?atoi(argv[3]):16;
  if(!count||limit<1||limit>60){fprintf(stderr,"Invalid seed count or phase_limit\n");return 2;}
  u32 target_le[4]={0xF7752443U,0x39DB622AU,0x3E69D5F3U,0xA47F932CU};
  u32 target_be[4]={0x432475F7U,0x2A62DB39U,0xF3D5693EU,0x2C937FA4U};
  if(argc>4){
    const char* hex=argv[4];
    if(strlen(hex)!=32){fprintf(stderr,"target hex requires exactly 32 digits\n");return 2;}
    unsigned byte[16];
    for(int i=0;i<16;i++)if(sscanf(hex+2*i,"%2x",&byte[i])!=1)return 2;
    for(int j=0;j<4;j++){
      int i=j*4;
      target_le[j]=(u32)byte[i]|((u32)byte[i+1]<<8)|((u32)byte[i+2]<<16)|((u32)byte[i+3]<<24);
      target_be[j]=__builtin_bswap32(target_le[j]);
    }
  }
  const char* filepath=argc>5?argv[5]:"resources/evidence/print/spool-reconstruction.log";
  std::ifstream source(filepath,std::ios::binary);
  if(!source){fprintf(stderr,"Original source unavailable: %s\n",filepath);return 3;}
  std::string evidence((std::istreambuf_iterator<char>(source)),std::istreambuf_iterator<char>());
  unsigned char sha[SHA256_DIGEST_LENGTH];SHA256((const unsigned char*)evidence.data(),evidence.size(),sha);
  char digest[65];for(int j=0;j<32;j++)sprintf(digest+2*j,"%02x",sha[j]);digest[64]=0;
  if(strcmp(digest,"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")){
    fprintf(stderr,"Original spool SHA256 mismatch: %s\n",digest);return 3;
  }
  const std::string comparator="2026-10-03T18:25:00Z JOB=PS-261003-0420 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=432475F72A62DB39F3D5693E2C937FA4 DEST=bench";
  if(evidence.find(comparator)==std::string::npos || evidence.find(comparator,evidence.find(comparator)+1)!=std::string::npos){
    fprintf(stderr,"Holdout original 0420 ACK2 identity not unique\n");return 3;
  }
  const u32* ts[2]={target_le,target_be};
  uint64_t attempts=0,firstword_hits=0,full_hits=0;
  const auto start=std::chrono::steady_clock::now();
  #pragma omp parallel reduction(+:attempts,firstword_hits,full_hits)
  {
    MT mt;
    #pragma omp for schedule(static)
    for(u64 n=0;n<count;n++){
      for(int variant=0;variant<2;variant++){
      mt.seed_int(float_seed(first+n,variant));
      std::array<u32,64> words;
      for(int i=0;i<limit+4;i++)words[i]=mt.next();
      for(int off=0;off<limit;off++){
        u32 w=words[off];
        for(int ori=0;ori<2;ori++){
          const u32* t=ts[ori];
          for(int rev=0;rev<2;rev++){
            if(w!=t[rev?3:0])continue;
            firstword_hits++;
            bool good=true;
            for(int k=1;k<4;k++)if(words[off+k]!=t[rev?3-k:k]){good=false;break;}
            if(good){
              full_hits++;
              #pragma omp critical
              {printf("MATCH epoch_microseconds=%llu variant=%d offset=%d endian=%d reversed=%d\n",(unsigned long long)(first+n),variant,off,ori,rev);}
            }
          }
        }
      }
      attempts++;
      }
    }
  }
  const auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  printf("tested=%llu firstword_hits=%llu full_matches=%llu seconds=%.3f rate=%.2f million seeds/sec\n",(unsigned long long)attempts,(unsigned long long)firstword_hits,(unsigned long long)full_hits,seconds,attempts/seconds/1e6);
  MT check;check.seed_int(float_seed(first,0));
  u32 sample[4];for(int i=0;i<4;i++)sample[i]=check.next();
  printf("SEED_FIRST microseconds=%llu python_float_hash=%llu outputs=%08x %08x %08x %08x\n",(unsigned long long)first,(unsigned long long)float_seed(first,0),sample[0],sample[1],sample[2],sample[3]);
}
