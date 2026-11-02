// H-17 selected ESC-N coupon: two-nibble fragment loss/insertion hypothesis.
// Reproducible C++17/OpenSSL SHA256/OpenMP SFT; source and original commitments immutable.
// Source spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <openssl/sha.h>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>

static constexpr const char* P="A9A9DC5731A5E2AE879C47215C2559D5";
static constexpr const char* M="8556C8CB6140A7F9A5123AC7571BEE1C";
static constexpr const char* TARGET="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";
static unsigned hexch(char x){if(x>='0'&&x<='9')return x-'0';return x-'A'+10;}
static void decode(const char* str,unsigned char* out,size_t bytes){for(size_t i=0;i<bytes;++i)out[i]=(hexch(str[2*i])<<4)|hexch(str[2*i+1]);}
static void setnib(unsigned char* a,int p,unsigned v){unsigned char &q=a[p/2];if((p&1)==0)q=static_cast<unsigned char>((q&15)|(v<<4));else q=static_cast<unsigned char>((q&240)|v);}
static void getbase(unsigned char* out,const unsigned char* kept,int i,int j){
  for(int z=0,k=0;z<32;++z){unsigned digit=z==i||z==j?0:kept[k++];setnib(out,z,digit);}
}
int main(){
  unsigned char p[32],mask[16],target[32];
  for(int i=0;i<32;++i)p[i]=hexch(P[i]);
  decode(M,mask,16);decode(TARGET,target,32);
  // Known-answer synthetic positive uses two deletion positions, two inserted positions.
  unsigned char syntheticKept[30],syntheticCoupon[16]={0},synKey[16],syntheticTarget[32];
  for(int k=0,i=0;i<32;++i){if(i!=2&&i!=4)syntheticKept[k++]=p[i];}
  getbase(syntheticCoupon,syntheticKept,7,28);
  setnib(syntheticCoupon,7,11);setnib(syntheticCoupon,28,4);
  for(int i=0;i<16;++i)synKey[i]=syntheticCoupon[i]^mask[i];
  SHA256(synKey,16,syntheticTarget);
  const auto start=std::chrono::steady_clock::now();
  unsigned long long total=0,realMatches=0,syntheticMatches=0;
  #pragma omp parallel for schedule(dynamic,1) reduction(+:total,realMatches,syntheticMatches)
  for(int di=0;di<31;++di){
    for(int dj=di+1;dj<32;++dj){
      unsigned char kept[30];
      for(int k=0,i=0;i<32;++i){if(i!=di&&i!=dj)kept[k++]=p[i];}
      for(int ip=0;ip<31;++ip){for(int jp=ip+1;jp<32;++jp){
        unsigned char base[16]={0};getbase(base,kept,ip,jp);
        for(int a=0;a<16;++a){
          unsigned char one[16];std::memcpy(one,base,16);setnib(one,ip,a);
          for(int b=0;b<16;++b){
            unsigned char candidate[16],key[16],digest[32];
            std::memcpy(candidate,one,16);setnib(candidate,jp,b);
            for(int t=0;t<16;++t)key[t]=candidate[t]^mask[t];
            SHA256(key,16,digest);
            ++total;
            if(std::memcmp(digest,target,32)==0){
              ++realMatches;
              #pragma omp critical
              {std::printf("ORIGINAL MATCH del=%d,%d insert=%d,%d values=%X,%X coupon=",di,dj,ip,jp,a,b);
               for(auto v:candidate)std::printf("%02X",v);
               std::printf(" component=");for(auto v:key)std::printf("%02X",v);std::puts("");}
            }
            if(std::memcmp(digest,syntheticTarget,32)==0)++syntheticMatches;
          }
        }
      }}
    }
  }
  const double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::printf("total=%llu expected=62980096 original_matches=%llu synthetic_matches=%llu runtime_seconds=%.3f\n",
              total,realMatches,syntheticMatches,sec);
  return total==62980096ULL&&syntheticMatches>0?0:2;
}
