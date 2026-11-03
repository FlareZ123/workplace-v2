// Exact source-to-target xoroshiro128** inversion and K04 continuation.
// Reproduce from repository root: c++ -O3 -std=c++17 ... -lcrypto;
// executable [offsets per state, default 1000000] [resource root, default resources/].
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <openssl/sha.h>

using Byte16 = std::array<unsigned char, 16>;
using Byte32 = std::array<unsigned char, 32>;
struct State {uint64_t a,b;};
static inline uint64_t rol(uint64_t x,unsigned r){return (x<<r)|(x>>(64-r));}
static inline uint64_t ror(uint64_t x,unsigned r){return (x>>r)|(x<<(64-r));}
static uint64_t next(State &s){
  uint64_t out=rol(s.a*uint64_t{5},7)*uint64_t{9};
  uint64_t x=s.a^s.b;
  s.a=rol(s.a,24)^x^(x<<16);
  s.b=rol(x,37);
  return out;
}
static uint64_t unmix(uint64_t y){
  return ror(y*UINT64_C(0x8e38e38e38e38e39),7)*UINT64_C(0xcccccccccccccccd);
}
static State inverse(uint64_t y0,uint64_t y1){
  uint64_t a=unmix(y0),next_a=unmix(y1);
  uint64_t v=next_a^rol(a,24);
  uint64_t x=v^(v<<16)^(v<<32)^(v<<48);
  return State{a,a^x};
}
static Byte16 fromhex16(const char *s){
  Byte16 b{};
  for(unsigned i=0;i<16;i++){unsigned x=0;if(std::sscanf(s+2*i,"%2x",&x)!=1)std::abort();b[i]=(unsigned char)x;}
  return b;
}
static Byte32 fromhex32(const char *s){
  Byte32 b{};
  for(unsigned i=0;i<32;i++){unsigned x=0;if(std::sscanf(s+2*i,"%2x",&x)!=1)std::abort();b[i]=(unsigned char)x;}
  return b;
}
static uint64_t load64(const unsigned char *p,bool little){
  uint64_t x=0;
  if(little)for(unsigned i=0;i<8;i++)x|=uint64_t(p[i])<<(8*i);
  else for(unsigned i=0;i<8;i++)x=(x<<8)|p[i];
  return x;
}
static void store64(uint64_t x,unsigned char *p,bool little){
  for(unsigned i=0;i<8;i++)p[i]=static_cast<unsigned char>((x>>((little?i:(7-i))*8))&255);
}
static Byte16 pack(uint64_t a,uint64_t b,bool little,bool reverse){
  Byte16 bytes{};
  store64(reverse?b:a,bytes.data(),little);
  store64(reverse?a:b,bytes.data()+8,little);
  return bytes;
}
static bool same_pair(uint64_t a,uint64_t b,const Byte16 &target){
  for(bool le:{false,true})for(bool rev:{false,true}){
    uint64_t c=load64(target.data()+(rev?8:0),le);
    uint64_t d=load64(target.data()+(rev?0:8),le);
    if(a==c&&b==d)return true;
  }
  return false;
}
static Byte32 sha16(const Byte16 &bytes){
  Byte32 out{};SHA256(bytes.data(),16,out.data());return out;
}
static void source_pin(const std::string &file,const char *expected){
  std::ifstream in(file,std::ios::binary);
  if(!in){std::fprintf(stderr,"no source file %s\n",file.c_str());std::exit(2);}
  std::string bytes((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
  unsigned char d[32];SHA256((const unsigned char*)bytes.data(),bytes.size(),d);
  char hex[65];for(unsigned i=0;i<32;i++)std::sprintf(hex+2*i,"%02x",d[i]);hex[64]=0;
  if(std::strcmp(hex,expected)){std::fprintf(stderr,"source SHA mismatch %s\n",file.c_str());std::exit(2);}
}
struct Counts {unsigned long long cross=0,hits=0;};
static Counts search(const char *title,State state,const Byte16 &mask,
                     const Byte16 &heldout,const Byte32 &goal,
                     unsigned long long count){
  Counts r{};
  uint64_t prev=next(state),cur=next(state);
  for(unsigned long long i=0;i<count;i++){
    if(same_pair(prev,cur,heldout)){
      r.cross++;
      std::printf("CROSSFIELD %s offset=%llu raw=%016llx_%016llx\n",
                  title,i,(unsigned long long)prev,(unsigned long long)cur);
    }
    for(bool le:{false,true})for(bool rev:{false,true}){
      Byte16 candidate=pack(prev,cur,le,rev);
      for(unsigned j=0;j<16;j++)candidate[j]^=mask[j];
      if(sha16(candidate)==goal){
        r.hits++;
        std::printf("K04_COMMITMENT_HIT %s offset=%llu little=%u reverse=%u component=",
                    title,i,unsigned(le),unsigned(rev));
        for(auto c:candidate)std::printf("%02X",c);
        std::printf("\n");
      }
    }
    prev=cur;cur=next(state);
  }
  std::printf("DONE %s offsets=%llu complete_SHA_checks=%llu crossfield=%llu commitment_hits=%llu\n",
              title,count,4*count,r.cross,r.hits);
  return r;
}
int main(int argc,char **argv){
  unsigned long long limit=argc>1?std::strtoull(argv[1],nullptr,10):1000000;
  if(limit==0||limit>50000000){std::fputs("limit outside 1..50m\n",stderr);return 2;}
  std::string dir=argc>2?argv[2]:"resources/";
  if(dir.back()!='/')dir.push_back('/');
  source_pin(dir+"evidence/recovery-routing.json",
             "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
  source_pin(dir+"acceptance.json",
             "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
  const Byte16 mask=fromhex16("8556C8CB6140A7F9A5123AC7571BEE1C");
  const Byte16 nonce=fromhex16("5F933DA6A1BD03C32DA5CBC25344F497");
  const Byte32 target=fromhex32("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");

  // Independent seeded synthetic control: recover full 128-bit initial state,
  // match a second source field at offset 700, and reconstruct an accepted
  // complete masked coupon at offset 4097.
  State planted{UINT64_C(0x5d1de1a5cafebeef),UINT64_C(0x17a5b3cb69a1cbca)};
  State s=planted;uint64_t y0=next(s),y1=next(s);
  State recovered=inverse(y0,y1);
  if(recovered.a!=planted.a||recovered.b!=planted.b)std::abort();
  s=planted;for(unsigned i=0;i<700;i++)next(s);
  uint64_t n0=next(s),n1=next(s);
  Byte16 planted_field=pack(n0,n1,true,true);
  s=planted;for(unsigned i=0;i<4097;i++)next(s);
  uint64_t t0=next(s),t1=next(s);
  Byte16 coupon=pack(t0,t1,false,false);
  for(unsigned i=0;i<16;i++)coupon[i]^=mask[i];
  Byte32 planted_hash=sha16(coupon);
  Counts positive=search("PLANTED",planted,mask,planted_field,planted_hash,4098);
  if(positive.cross!=1||positive.hits!=1){
    std::fputs("positive controls failed\n",stderr);return 3;
  }
  std::puts("PLANTED FULL-SOURCE AND FULL-K04 POSITIVE PASS");

  unsigned long long total=0,cross=0;
  for(unsigned field=0;field<2;field++){
    const Byte16 &seedbytes=field?nonce:mask;
    const Byte16 &other=field?mask:nonce;
    for(bool le:{false,true})for(bool rev:{false,true}){
      uint64_t f=load64(seedbytes.data()+(rev?8:0),le);
      uint64_t g=load64(seedbytes.data()+(rev?0:8),le);
      State init=inverse(f,g),v=init;
      if(next(v)!=f||next(v)!=g)std::abort();
      char name[70];std::sprintf(name,"%s_%s_%s",
                 field?"NONCE":"MASK",le?"LE":"BE",rev?"REV":"FWD");
      Counts c=search(name,init,mask,other,target,limit);
      total+=c.hits;cross+=c.cross;
    }
  }
  std::printf("ORIGINAL: 8 source views, %llu complete SHA checks, %llu crossfield hits, %llu authentic K04 hits\n",
              32*limit,cross,total);
  return 0;
}
