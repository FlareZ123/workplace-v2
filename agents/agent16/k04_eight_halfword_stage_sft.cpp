// H-17 K04: exact eight-2-byte fragment permutation and stage test.
// Source-pinned; historical evidence and acceptance remain read-only.
// Compile with C++17 and OpenSSL libcrypto.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
static constexpr char src[]="A9A9DC5731A5E2AE879C47215C2559D5";
static constexpr char maskhex[]="8556C8CB6140A7F9A5123AC7571BEE1C";
static constexpr char targethex[]="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static constexpr char source_sha[]="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static int nib(char x){if(x>='0'&&x<='9')return x-'0';if(x>='A'&&x<='F')return x-'A'+10;if(x>='a'&&x<='f')return x-'a'+10;return -1;}
template <size_t N> static std::array<unsigned char,N> bytes(const char* hex){
  std::array<unsigned char,N> v{};
  for(size_t i=0;i<N;i++)v[i]=(unsigned char)((nib(hex[2*i])<<4)|nib(hex[2*i+1]));
  return v;
}
int main(int argc,char**argv){
  if(argc!=2){std::fprintf(stderr,"give original spool source path\n");return 2;}
  std::ifstream f(argv[1],std::ios::binary);
  std::string s((std::istreambuf_iterator<char>(f)),{});
  if(s.empty()){std::fprintf(stderr,"source missing\n");return 3;}
  unsigned char hash[SHA256_DIGEST_LENGTH];
  SHA256((const unsigned char*)s.data(),s.size(),hash);
  const auto pinned=bytes<32>(source_sha);
  if(!std::equal(hash,hash+32,pinned.begin())){std::fprintf(stderr,"source sha mismatch\n");return 4;}
  const std::string marker="JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
  if(s.find(marker+src)==std::string::npos||s.find(marker,s.find(marker)+1)!=std::string::npos){
    std::fprintf(stderr,"source selector failed\n");return 5;
  }
  const auto p=bytes<16>(src);
  const auto mask=bytes<16>(maskhex);
  const auto target=bytes<32>(targethex);
  std::array<int,8> order{0,1,2,3,4,5,6,7};
  std::array<unsigned char,16> raw{},copy_reduced{},mask_permuted{},candidate{};
  uint64_t count=0,control[3]={},hit[3]={};
  const std::array<int,8> special{7,1,4,2,6,0,5,3};
  std::array<std::array<unsigned char,16>,3> planted{};
  for(int j=0;j<8;j++){
    int k=special[j]*2;
    for(int z=0;z<2;z++){
      planted[0][2*j+z]=p[k+1-z]^mask[2*j+z];
      planted[1][2*j+z]=p[k+1-z]^mask[k+1-z];
      planted[2][2*j+z]=p[2*j+z]^mask[k+1-z];
    }
  }
  unsigned char ctrlhash[3][32];
  for(int stage=0;stage<3;stage++)SHA256(planted[stage].data(),16,ctrlhash[stage]);
  do{
    for(unsigned rev=0;rev<256;rev++){
      for(int j=0;j<8;j++){
        int k=order[j]*2;
        for(int z=0;z<2;z++){
          int shift=(rev&(1U<<j))?(1-z):z;
          raw[2*j+z]=p[k+shift];
          copy_reduced[2*j+z]=p[k+shift]^mask[k+shift];
          mask_permuted[2*j+z]=mask[k+shift];
        }
      }
      count++;
      for(int stage=0;stage<3;stage++){
        for(int j=0;j<16;j++)
          candidate[j]=stage==0?(raw[j]^mask[j]):stage==1?copy_reduced[j]:(p[j]^mask_permuted[j]);
        SHA256(candidate.data(),16,hash);
        if(!std::memcmp(hash,target.data(),32)){
          hit[stage]++;
          std::printf("ORIGINAL_K04_MATCH stage=%d component=",stage);
          for(auto byte:candidate)std::printf("%02X",byte);
          std::puts("");
        }
        if(!std::memcmp(hash,ctrlhash[stage],32))control[stage]++;
      }
    }
  }while(std::next_permutation(order.begin(),order.end()));
  std::printf("pairs=8 permutations=40320 flips=256 assignments=%llu original_by_stage=%llu,%llu,%llu planted_by_stage=%llu,%llu,%llu\n",
    (unsigned long long)count,(unsigned long long)hit[0],(unsigned long long)hit[1],(unsigned long long)hit[2],
    (unsigned long long)control[0],(unsigned long long)control[1],(unsigned long long)control[2]);
  if(count!=10321920||control[0]!=2||control[1]!=1||control[2]!=1)return 6;
  return (hit[0]+hit[1]+hit[2])?7:0;
}
