// H-17 original K08 source-wide crew vocabulary four-word exact search.
// Build: g++ -O3 -std=c++17 -Wno-deprecated-declarations k08_crew_fourword_sft.cpp -lcrypto -o k08_crew_fourword_sft
// Run: ./k08_crew_fourword_sft <original-notes> <original-galley> <first-index> <last-index>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using D=std::array<unsigned char,32>;
D hash(const void *data,size_t len){D out{};SHA256(static_cast<const unsigned char*>(data),len,out.data());return out;}
std::string hex(const unsigned char* p,size_t n){const char*x="0123456789abcdef";std::string s;for(size_t i=0;i<n;i++){s.push_back(x[p[i]>>4]);s.push_back(x[p[i]&15]);}return s;}
std::string read(const std::string& path){std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("Cannot read "+path);return std::string((std::istreambuf_iterator<char>(f)),{});}
struct Reducer{
 SHA256_CTX in,out;
 Reducer(){const unsigned char key[16]={0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};unsigned char p[64],q[64];for(int i=0;i<64;i++){unsigned char k=i<16?key[i]:0;p[i]=k^0x36;q[i]=k^0x5c;}SHA256_Init(&in);SHA256_Update(&in,p,64);SHA256_Init(&out);SHA256_Update(&out,q,64);}
 void component(const std::string& phrase,unsigned char result[16])const{SHA256_CTX a=in,b=out;unsigned char u[32],v[32];SHA256_Update(&a,phrase.data(),phrase.size());SHA256_Final(u,&a);SHA256_Update(&b,u,32);SHA256_Final(v,&b);std::memcpy(result,v,16);}
};
int main(int argc,char**argv){try{
 if(argc!=5)throw std::runtime_error("Expected <original-notes> <original-galley> <lo> <hi>");
 const std::string note=read(argv[1]),galley=read(argv[2]);
 if(hex(hash(note.data(),note.size()).data(),32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw std::runtime_error("Notes SHA mismatch");
 if(hex(hash(galley.data(),galley.size()).data(),32)!="23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46")throw std::runtime_error("Galley SHA mismatch");
 std::set<std::string> vocab;std::string str=note+galley,token;
 for(unsigned char c:str){if((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')){token.push_back(static_cast<char>(std::tolower(c)));}else if(!token.empty()){vocab.insert(token);token.clear();}}
 if(!token.empty())vocab.insert(token);
 if(vocab.size()!=321)throw std::runtime_error("Source vocabulary cardinality mismatch");
 std::string joined;for(const auto&x:vocab){joined+=x;joined+='\n';}
 if(hex(hash(joined.data(),joined.size()).data(),32)!="399ddef7c8cce60aa1e78d3ec85683b0188c08b4346ad0bd824d4068d8dc29ba")throw std::runtime_error("Vocab SHA mismatch");
 std::vector<std::string>w(vocab.begin(),vocab.end());size_t lo=std::stoull(argv[3]),hi=std::stoull(argv[4]);if(!(lo<hi&&hi<=w.size()))throw std::runtime_error("Bad shard");
 Reducer r;unsigned char component[16];r.component("a good watch leaves the room ready for the next pair of hands",component);
 if(hex(component,16)!="bf889359b0303f2b2b2fd96ae841210b")throw std::runtime_error("Historical N02 HMAC control failed");
 const D target={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
 const std::string plant=w[lo]+" night voices table";
 r.component(plant,component);const D synthetic=hash(component,16);
 uint64_t candidates=0,hits=0,positives=0;
 for(size_t i=lo;i<hi;i++)for(const auto&b:w)for(const auto&c:w){
  const std::string prefix=w[i]+" "+b+" "+c+" ";SHA256_CTX p=r.in;SHA256_Update(&p,prefix.data(),prefix.size());
  for(const auto&d:w){SHA256_CTX inner=p,outer=r.out;unsigned char h1[32],h2[32],khash[32];SHA256_Update(&inner,d.data(),d.size());SHA256_Final(h1,&inner);SHA256_Update(&outer,h1,32);SHA256_Final(h2,&outer);SHA256(h2,16,khash);
   if(!std::memcmp(khash,target.data(),32)){hits++;std::cout<<"AUTHENTIC_K08: "<<prefix<<d<<" COMPONENT="<<hex(h2,16)<<std::endl;}
   if(!std::memcmp(khash,synthetic.data(),32)){positives++;if(prefix+d!=plant)throw std::runtime_error("Incorrect synthetic preimage");}
   ++candidates;
  }
 }
 const uint64_t n=321,expected=(hi-lo)*n*n*n;
 if(candidates!=expected||positives!=1)throw std::runtime_error("Incomplete coverage or no planted positive");
 std::cout<<"K08_CREW4 source_sha256="<<hex(hash(note.data(),note.size()).data(),32)<<" vocab_sha256="<<hex(hash(joined.data(),joined.size()).data(),32)<<" shard="<<lo<<":"<<hi<<" checked="<<candidates<<" original_hits="<<hits<<" planted_hits="<<positives<<std::endl;
 return hits?10:0;
 }catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<std::endl;return 2;}}
