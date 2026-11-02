// H-17 K04 dislocated pair-byte copy-loss/reinsertion SFT.
// Source selected ACK-RECOVER attempt2 is a retained, unauthenticated buffer.
// Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// Extends the v1 225 * 2^16 contiguous-pair splice: deleting ANY TWO source
// byte positions and inserting ANY TWO unknown bytes in ANY two positions.
// Four-source mosaic and earlier bit/nibble mutations do not cover this exact
// dislocated full-byte two-omission model.
// Read-only original bytes and original REC8 acceptance; requires OpenSSL libcrypto.
#include <openssl/sha.h>
#include <cstdio>
#include <cstring>
#include <chrono>
#include <cstdint>

const unsigned char P[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
const unsigned char M[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
const unsigned char T[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};

void template_key(int d0,int d1,int i0,int i1,unsigned char out[16]){
  unsigned char kept[14];
  for(int a=0,k=0;a<16;++a)if(a!=d0&&a!=d1)kept[k++]=P[a];
  for(int a=0,k=0;a<16;++a)out[a]=(a==i0||a==i1)?M[a]:(kept[k++]^M[a]);
}

int main(){
  unsigned char positive[16],positive_hash[32];
  template_key(0,7,2,11,positive);
  positive[2]=0xA3^M[2];positive[11]=0x5D^M[11];
  SHA256(positive,16,positive_hash);
  unsigned long long count=0,found=0,control=0;
  const auto start=std::chrono::steady_clock::now();
  #pragma omp parallel for schedule(dynamic,1) reduction(+:count,found,control)
  for(int d0=0;d0<15;++d0){
    unsigned char candidate[16],digest[32];
    for(int d1=d0+1;d1<16;++d1){
      for(int i0=0;i0<15;++i0){
        for(int i1=i0+1;i1<16;++i1){
          template_key(d0,d1,i0,i1,candidate);
          for(unsigned v=0;v<65536;++v){
            candidate[i0]=static_cast<unsigned char>(v>>8)^M[i0];
            candidate[i1]=static_cast<unsigned char>(v)^M[i1];
            SHA256(candidate,16,digest);
            ++count;
            if(d0==0&&d1==7&&i0==2&&i1==11&&std::memcmp(digest,positive_hash,32)==0)++control;
            if(std::memcmp(digest,T,32)==0){
              ++found;
              #pragma omp critical
              {
                std::printf("MATCH deleted=%d,%d inserted=%d,%d add=%04X key=",d0,d1,i0,i1,v);
                for(unsigned char b:candidate)std::printf("%02X",b);
                std::printf("\n");std::fflush(stdout);
              }
            }
          }
        }
      }
    }
    std::printf("DONE_deleted_first=%d\n",d0);std::fflush(stdout);
  }
  const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::printf("COMPLETE pairs_delete=120 pairs_insert=120 inserted_values=65536 tested=%llu matches=%llu synthetic_hits=%llu seconds=%.3f\n",count,found,control,elapsed);
  return count==943718400ULL&&control==1&&found==0?0:1;
}
