// H17 original copied ACK2. One missing byte plus one missing hex digit;
// one arbitrary byte and nibble inserted elsewhere to restore 128 bits.
// Every byte deletion is aligned to two original hex digits. Byte insertion
// is similarly aligned in the reconstructed 32-nibble output.
// No original source, mask or commitment is modified.
// Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
// g++ -O3 -std=c++17 k04_mixed_8_4_copy_sft.cpp -lcrypto -o k04_mixed_8_4_copy_sft
// Usage: executable first_delete_byte count_delete_bytes [synthetic_sha256_hex]
#include <openssl/sha.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
using U8=uint8_t;
using U64=uint64_t;
constexpr U8 COPY[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
constexpr U8 MASK[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr U8 TARGET[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
int main(int argc,char**argv){
 if(argc!=3&&argc!=4)return 2;
 int start=std::atoi(argv[1]),size=std::atoi(argv[2]);
 if(start<0||size<=0||start+size>16)return 2;
 U8 target[32];std::memcpy(target,TARGET,32);
 if(argc==4){
   if(std::strlen(argv[3])!=64)return 2;
   for(int i=0;i<32;++i){
     unsigned v;
     if(std::sscanf(argv[3]+2*i,"%2x",&v)!=1)return 2;
     target[i]=U8(v);
   }
 }
 U8 orig[32],keep[29],base[16],comp[16],hash[32];
 for(int i=0;i<32;++i)orig[i]=(COPY[i/2]>>(4*(1-i%2)))&15;
 U64 tried=0,found=0;
 auto t0=std::chrono::steady_clock::now();
 for(int byte=start;byte<start+size;++byte){
   int da=byte*2;
   for(int db=0;db<32;++db){
     if(db==da||db==da+1)continue;
     int k=0;
     for(int i=0;i<32;++i)if(i!=da&&i!=da+1&&i!=db)keep[k++]=orig[i];
     if(k!=29)return 3;
     for(int insert_byte=0;insert_byte<16;++insert_byte){
       int pa=insert_byte*2;
       for(int pb=0;pb<32;++pb){
         if(pb==pa||pb==pa+1)continue;
         std::memcpy(base,MASK,16);k=0;
         for(int i=0;i<32;++i){
           if(i==pa||i==pa+1||i==pb)continue;
           if(k>=29)return 3;
           base[i/2]^=U8(keep[k++]<<(4*(1-i%2)));
         }
         if(k!=29)return 3;
         const int nibbyte=pb/2,shift=4*(1-pb%2);
         for(int v=0;v<4096;++v){
           std::memcpy(comp,base,16);
           comp[insert_byte]^=U8(v&255);
           comp[nibbyte]^=U8(((v>>8)&15)<<shift);
           SHA256(comp,16,hash);++tried;
           if(std::memcmp(hash,target,32)==0){
             ++found;
             std::printf("K04_EXACT_MATCH byte_drop=%d nibble_drop=%d byte_insert=%d nibble_insert=%d insval=%03X comp=",byte,db,insert_byte,pb,v);
             for(U8 value:comp)std::printf("%02X",value);
             std::printf("\n");std::fflush(stdout);
           }
         }
       }
     }
   }
 }
 auto t1=std::chrono::steady_clock::now();
 std::printf("COMPLETE startbyte=%d countbyte=%d checks=%llu hits=%llu elapsed=%.3f\n",
   start,size,(unsigned long long)tried,(unsigned long long)found,
   std::chrono::duration<double>(t1-t0).count());
}
