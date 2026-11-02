#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <openssl/sha.h>
#include <omp.h>
using U=unsigned __int128;
static U hex128(const char* h){U v=0;for(int i=0;i<32;i++){const char c=h[i];v=(v<<4)|(c<='9'?c-'0':c-'A'+10);}return v;}
static inline U remove1(U v,int p){const U lower=((U(1)<<p)-1);return (v&lower)|((p==127?U(0):v>>(p+1))<<p);}
static inline U insert1(U v,int p,int b){const U lower=((U(1)<<p)-1);return (v&lower)|((U(b))<<p)|(p==127?U(0):((v>>p)<<(p+1)));}
static inline bool digest_check(U comp, const unsigned char target[32]) {
  unsigned char buf[16],sha[32];
  for(int i=15;i>=0;i--){buf[i]=static_cast<unsigned char>(comp);comp>>=8;}
  SHA256(buf,16,sha);
  return memcmp(sha,target,32)==0;
}
int main(int argc,char**argv){
  const U ack=hex128("A9A9DC5731A5E2AE879C47215C2559D5");
  const U mask=hex128("8556C8CB6140A7F9A5123AC7571BEE1C");
  const char* eh="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";
  unsigned char goal[32]; for(int i=0;i<32;i++){char b[3]={eh[i*2],eh[i*2+1],0};goal[i]=strtoul(b,nullptr,16);}
  const U synth=insert1(insert1(remove1(remove1(ack,107),12),4,1),83,0);
  unsigned char synthetic_goal[32],tmp[16];U x=synth^mask;
  for(int i=15;i>=0;i--){tmp[i]=(unsigned char)x;x>>=8;}
  SHA256(tmp,16,synthetic_goal);
  if(!digest_check(synth^mask,synthetic_goal))return 2;
  if(synth!=(insert1(insert1(remove1(remove1(ack,107),12),4,0),83,0)|(U(1)<<4)))return 3;
  std::atomic<int> found(0);std::atomic<unsigned long long> total(0);
  const int a0=argc>1?atoi(argv[1]):0,a1=argc>2?atoi(argv[2]):127;
#pragma omp parallel
  {
    unsigned long long checked=0;
    #pragma omp for schedule(dynamic)
    for(int i=a0;i<a1;i++){
      for(int j=i+1;j<128;j++){
        const U shrunk=remove1(remove1(ack,j),i);
        for(int a=0;a<127;a++)for(int b=a+1;b<128;b++){
          const U base=insert1(insert1(shrunk,a,0),b,0);
          const U A=U(1)<<a,B=U(1)<<b;
          for(int bits=0;bits<4;bits++){
            const U candidate=base|((bits&1)?A:U(0))|((bits&2)?B:U(0));
            checked++;
            if(digest_check(candidate^mask,goal)){
              if(found.exchange(1)==0){printf("FOUND original_positions=%d,%d insert_positions=%d,%d inserted_bits=%d candidate=",i,j,a,b,bits);
                for(int pos=15;pos>=0;pos--){printf("%02X",(unsigned)((candidate>>(8*pos))&255));}printf("\n");}
              break;
            }
          }
        }
      }
    }
    total.fetch_add(checked,std::memory_order_relaxed);
  }
  printf("%s synthetic_control=PASS tested=%llu original_source_pairs=%d..%d\n",found?"FOUND":"NO_MATCH",(unsigned long long)total.load(),a0,a1);
  return 0;
}
