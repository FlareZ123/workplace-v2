// H-17 K08 exploratory complete-phrase constructor.
// Hypothesis: the eight selected note initials ATEALBIT constrain an 8-word
// keeper phrase drawn from the complete 321-token crew/galley vocabulary.
// This is an inferred clue, not an authenticated authoring rule.
// Build: g++ -O3 -std=c++17 -Wno-deprecated-declarations k08_atealbit_fullcrew_sft.cpp -lcrypto -o k08_atealbit_fullcrew_sft
// Run: ./k08_atealbit_fullcrew_sft <notes> <galley> <a-index-lo> <a-index-hi> [limit]
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Digest=std::array<unsigned char,32>;
static Digest sha256(const void *p,size_t n){Digest d{};SHA256(static_cast<const unsigned char*>(p),n,d.data());return d;}
static std::string hex(const unsigned char*p,size_t n){static const char*x="0123456789abcdef";std::string s;s.reserve(2*n);for(size_t i=0;i<n;i++){s.push_back(x[p[i]>>4]);s.push_back(x[p[i]&15]);}return s;}
static std::string read_file(const std::string&p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("Cannot read "+p);return std::string((std::istreambuf_iterator<char>(f)),{});}
struct Hmac16{
 SHA256_CTX inner_base,outer_base;
 Hmac16(){
  const unsigned char key[16]={0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};
  unsigned char ipad[64],opad[64];
  for(size_t i=0;i<64;i++){unsigned char k=i<16?key[i]:0;ipad[i]=k^0x36;opad[i]=k^0x5c;}
  SHA256_Init(&inner_base);SHA256_Update(&inner_base,ipad,64);
  SHA256_Init(&outer_base);SHA256_Update(&outer_base,opad,64);
 }
 void digest_from_prefix(const SHA256_CTX&prefix,const char*suffix,size_t n,unsigned char out16[16])const{
  SHA256_CTX in=prefix;unsigned char ih[32],oh[32];
  SHA256_Update(&in,suffix,n);SHA256_Final(ih,&in);
  SHA256_CTX out=outer_base;SHA256_Update(&out,ih,32);SHA256_Final(oh,&out);
  std::memcpy(out16,oh,16);
 }
 void component(const std::string&phrase,unsigned char out16[16])const{
  digest_from_prefix(inner_base,phrase.data(),phrase.size(),out16);
 }
};
static void append_word(char *buf,size_t &n,const std::string&w){std::memcpy(buf+n,w.data(),w.size());n+=w.size();}
int main(int argc,char**argv){try{
 if(argc!=5&&argc!=6)throw std::runtime_error("Expected <notes> <galley> <lo> <hi> [limit]");
 const std::string notes=read_file(argv[1]),galley=read_file(argv[2]);
 if(hex(sha256(notes.data(),notes.size()).data(),32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw std::runtime_error("notes SHA mismatch");
 if(hex(sha256(galley.data(),galley.size()).data(),32)!="23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46")throw std::runtime_error("galley SHA mismatch");
 std::set<std::string> vocab;std::string token,all=notes+galley;
 for(unsigned char c:all){if((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9'))token.push_back(static_cast<char>(std::tolower(c)));else if(!token.empty()){vocab.insert(token);token.clear();}}
 if(!token.empty())vocab.insert(token);
 if(vocab.size()!=321)throw std::runtime_error("vocabulary cardinality mismatch");
 std::string joined;for(const auto&w:vocab){joined+=w;joined+='\n';}
 if(hex(sha256(joined.data(),joined.size()).data(),32)!="399ddef7c8cce60aa1e78d3ec85683b0188c08b4346ad0bd824d4068d8dc29ba")throw std::runtime_error("vocabulary SHA mismatch");
 std::map<char,std::vector<std::string>> by_initial;for(const auto&w:vocab)if(!w.empty()&&w[0]>='a'&&w[0]<='z')by_initial[w[0]].push_back(w);
 const auto &A=by_initial.at('a'),&T=by_initial.at('t'),&E=by_initial.at('e'),&L=by_initial.at('l'),&B=by_initial.at('b'),&I=by_initial.at('i');
 const size_t lo=std::stoull(argv[3]),hi=std::stoull(argv[4]);if(!(lo<hi&&hi<=A.size()))throw std::runtime_error("bad shard range");
 const uint64_t per_a=uint64_t(T.size())*E.size()*A.size()*L.size()*B.size()*I.size()*T.size();
 const uint64_t total=uint64_t(hi-lo)*per_a;
 const uint64_t limit=argc==6?std::stoull(argv[5]):UINT64_MAX;
 const uint64_t expected=std::min(total,limit);
 Hmac16 hmac;
 // Historical control: N02's known draft must reproduce its exact HMAC component.
 unsigned char control[16];hmac.component("a good watch leaves the room ready for the next pair of hands",control);
 if(hex(control,16)!="bf889359b0303f2b2b2fd96ae841210b")throw std::runtime_error("historical N02 HMAC control failed");
 const Digest target={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
 uint64_t checked=0,hits=0,planted=0;
 const std::string plant_phrase=A[lo]+" "+T.front()+" "+E.front()+" "+A.front()+" "+L.front()+" "+B.front()+" "+I.front()+" "+T.front();
 unsigned char plant_component[16];hmac.component(plant_phrase,plant_component);
 const Digest plant_target=sha256(plant_component,16);
 for(size_t ai=lo;ai<hi&&checked<expected;ai++){
  const std::string &w0=A[ai];
  for(const auto&w1:T)for(const auto&w2:E)for(const auto&w3:A){
   if(checked>=expected)break;
   char prefix[256];size_t pn=0;
   append_word(prefix,pn,w0);prefix[pn++]=' ';append_word(prefix,pn,w1);prefix[pn++]=' ';append_word(prefix,pn,w2);prefix[pn++]=' ';append_word(prefix,pn,w3);prefix[pn++]=' ';
   SHA256_CTX prefix_ctx=hmac.inner_base;SHA256_Update(&prefix_ctx,prefix,pn);
   for(const auto&w4:L)for(const auto&w5:B)for(const auto&w6:I)for(const auto&w7:T){
    if(checked>=expected)break;
    char suffix[256];size_t sn=0;
    append_word(suffix,sn,w4);suffix[sn++]=' ';append_word(suffix,sn,w5);suffix[sn++]=' ';append_word(suffix,sn,w6);suffix[sn++]=' ';append_word(suffix,sn,w7);
    unsigned char comp[16];hmac.digest_from_prefix(prefix_ctx,suffix,sn,comp);
    const Digest candidate=sha256(comp,16);
    if(candidate==target){++hits;std::cout<<"ORIGINAL_K08_HIT phrase="<<std::string(prefix,pn)+std::string(suffix,sn)<<" component="<<hex(comp,16)<<std::endl;}
    if(ai==lo&&w1==T.front()&&w2==E.front()&&w3==A.front()&&w4==L.front()&&w5==B.front()&&w6==I.front()&&w7==T.front()){
      if(candidate==plant_target)++planted;
    }
    ++checked;
   }
  }
 }
 if(checked!=expected||planted!=1)throw std::runtime_error("incomplete coverage or synthetic positive failed");
 std::cout<<"K08_ATEALBIT_FULLCREW notes_sha256="<<hex(sha256(notes.data(),notes.size()).data(),32)
          <<" galley_sha256="<<hex(sha256(galley.data(),galley.size()).data(),32)
          <<" vocabulary_sha256="<<hex(sha256(joined.data(),joined.size()).data(),32)
          <<" shard="<<lo<<":"<<hi<<" checked="<<checked<<" original_hits="<<hits
          <<" planted_hits="<<planted<<" pattern=ATEALBIT"<<std::endl;
 return hits?10:0;
 }catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<std::endl;return 2;}}
