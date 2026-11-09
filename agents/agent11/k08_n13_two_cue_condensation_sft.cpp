// Agent 11 H-17 K08 exact two-cue N13 condensation experiment.
// Source first; source never modified. Compile with C++17 + OpenSSL libcrypto.
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

static SHA256_CTX inner_base, outer_base;
static constexpr unsigned char original[32]={
  0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,
  0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const std::array<const char*,22> n13={
 "at","the","end","of","the","night","the","mugs","stood","beside","the",
 "window","and","somebody","had","remembered","to","leave","the","little","lamp","on"};
static const std::array<const char*,2> sea={"sea","the sea"};
static const std::array<const char*,2> company={"voices at the table","the voices at the table"};

static std::string read_file(const std::string& path,const char* sha){
 std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing source "+path);
 std::string s((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 unsigned char d[32];SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),d);
 char h[65];for(int i=0;i<32;i++)std::sprintf(h+2*i,"%02x",d[i]);h[64]=0;
 if(std::strcmp(h,sha))throw std::runtime_error("original source changed: "+path);
 return s;
}
static void reduce(const char* s,size_t n,unsigned char* out){
 SHA256_CTX c=inner_base;
 SHA256_Update(&c,s,n);
 unsigned char inner[32],hmac[32];SHA256_Final(inner,&c);
 c=outer_base;SHA256_Update(&c,inner,32);SHA256_Final(hmac,&c);
 SHA256(hmac,16,out);
}
static size_t produce(const std::vector<const char*>& source,int sea_gap,int company_gap,
                      int sea_variant,int company_variant,bool company_first,char* out){
 size_t n=0;int word_count=0;
 auto append=[&](const char* s){
  if(word_count++)out[n++]=' ';
  const size_t k=std::strlen(s);std::memcpy(out+n,s,k);n+=k;
 };
 for(int gap=0;gap<=int(source.size());gap++){
  if(sea_gap==gap&&company_gap==gap){
   if(company_first){append(company[company_variant]);append(sea[sea_variant]);}
   else{append(sea[sea_variant]);append(company[company_variant]);}
  }else{
   if(sea_gap==gap)append(sea[sea_variant]);
   if(company_gap==gap)append(company[company_variant]);
  }
  if(gap<int(source.size()))append(source[gap]);
 }
 out[n]=0;
 return n;
}
int main(int argc,char** argv){
 if(argc<4){std::fprintf(stderr,"USAGE root source_mask_start source_mask_end [pilot]\n");return 2;}
 try{
  const std::string root=argv[1];
  const auto notes=read_file(root+"/evidence/crew/noticeboard-and-desk-notes.txt",
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
  read_file(root+"/acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
  read_file(root+"/evidence/recovery-routing.json",
    "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
  if(notes.find("N13 / Emily")==std::string::npos ||
     notes.find("At the end of the night the mugs stood beside the window, and somebody had remembered to leave the little lamp on.")==std::string::npos ||
     notes.find("I wanted the line to hold the sea, the end of the night and the voices at the table.")==std::string::npos)
      throw std::runtime_error("source N13 or N20 cue mismatch");
  unsigned char key[64]={0};
  const char* raw="5F933DA6A1BD03C32DA5CBC25344F497";
  for(int i=0;i<16;i++){unsigned v=0;std::sscanf(raw+2*i,"%2x",&v);key[i]=static_cast<unsigned char>(v);}
  unsigned char ipad[64],opad[64];
  for(int i=0;i<64;i++){ipad[i]=key[i]^0x36;opad[i]=key[i]^0x5c;}
  SHA256_Init(&inner_base);SHA256_Update(&inner_base,ipad,64);
  SHA256_Init(&outer_base);SHA256_Update(&outer_base,opad,64);
  unsigned char digest[32],known16[16]={0xBF,0x88,0x93,0x59,0xB0,0x30,0x3F,0x2B,0x2B,0x2F,0xD9,0x6A,0xE8,0x41,0x21,0x0B},check[32];
  const char* prior="a good watch leaves the room ready for the next pair of hands";
  reduce(prior,std::strlen(prior),digest);SHA256(known16,16,check);
  if(std::memcmp(check,digest,32))throw std::runtime_error("authentic N02 HMAC control FAILED");
  const auto lo=std::strtoull(argv[2],nullptr,10), hi=std::strtoull(argv[3],nullptr,10);
  if(lo>=hi || hi>(1u<<22))throw std::runtime_error("invalid mask range");
  // Planted complete phrase from a nontrivial legal source mask, independently
  // reduced, then looked up using the exact same search as the original target.
  std::vector<const char*> plant_words={"at","the","end","of"};char planted[512];
  size_t pl=produce(plant_words,2,3,0,1,false,planted);reduce(planted,pl,digest);
  unsigned char plant_hash[32];std::memcpy(plant_hash,digest,32);
  std::uint64_t checked=0,eligible=0,original_hits=0,plant_hits=0;
  char output[512];
  for(std::uint64_t mask=lo;mask<hi;mask++){
   const int count=__builtin_popcountll(mask);
   if(count<4||count>12)continue;
   std::vector<const char*> words;words.reserve(count);
   for(int i=0;i<22;i++)if((mask>>i)&1)words.push_back(n13[i]);
   eligible++;
   for(int s=0;s<=count;s++)for(int c=0;c<=count;c++){
    for(int order=0;order<(s==c?2:1);order++){
     for(int sv=0;sv<2;sv++)for(int cv=0;cv<2;cv++){
      const auto length=produce(words,s,c,sv,cv,order!=0,output);
      reduce(output,length,digest);checked++;
      if(std::memcmp(digest,original,32)==0){
       original_hits++;
       std::printf("ORIGINAL_K08_PASS mask=%llu sea_gap=%d company_gap=%d order=%d sv=%d cv=%d caption=%s\n",
         (unsigned long long)mask,s,c,order,sv,cv,output);
       std::fflush(stdout);
      }
      if(std::memcmp(digest,plant_hash,32)==0)plant_hits++;
     }
    }
   }
  }
  if(lo<=15 && hi>15 && plant_hits==0)throw std::runtime_error("in-family planted positive NOT FOUND");
  std::printf("RESULT ranges=[%llu,%llu) eligible_masks=%llu complete_assignments=%llu original_hits=%llu synthetic_positive=%llu\n",
    (unsigned long long)lo,(unsigned long long)hi,
    (unsigned long long)eligible,(unsigned long long)checked,
    (unsigned long long)original_hits,(unsigned long long)plant_hits);
  return original_hits?1:0;
 }catch(const std::exception& e){std::fprintf(stderr,"ERROR %s\n",e.what());return 3;}
}
