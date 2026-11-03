// K08 eight-Emily-note one-word-per-note exhaustive source-conditioned test.
// C++17, OpenSSL libcrypto. Original archive evidence is read-only.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <regex>
#include <set>
#include <string>
#include <thread>
#include <vector>

static std::vector<std::string> tokenize(const std::string& s) {
  std::vector<std::string> result;
  std::string w;
  for (unsigned char c : s) {
    if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) w.push_back(char(c));
    else if (c >= 'A' && c <= 'Z') w.push_back(char(c + 32));
    else if (!w.empty()) { result.push_back(w); w.clear(); }
  }
  if (!w.empty()) result.push_back(w);
  return result;
}
static std::string hex(const unsigned char* b, size_t n) {
  static const char* h="0123456789abcdef";
  std::string s(n*2, '0');
  for(size_t i=0;i<n;i++){s[2*i]=h[b[i]>>4];s[2*i+1]=h[b[i]&15];}
  return s;
}
static bool eqhex(const unsigned char* b, size_t n, const std::string& h) {return hex(b,n)==h;}
struct Engine {
  std::array<unsigned char, 16> key{};
  SHA256_CTX innerPrefix{}, outerPrefix{};
  Engine() {
    const std::string raw="5F933DA6A1BD03C32DA5CBC25344F497";
    for(int i=0;i<16;i++) key[i]=unsigned(std::stoi(raw.substr(2*i,2),nullptr,16));
    std::array<unsigned char,64> ip{},op{};
    ip.fill(0x36);op.fill(0x5c);
    for(int i=0;i<16;i++){ip[i]^=key[i];op[i]^=key[i];}
    SHA256_Init(&innerPrefix);SHA256_Update(&innerPrefix,ip.data(),ip.size());
    SHA256_Init(&outerPrefix);SHA256_Update(&outerPrefix,op.data(),op.size());
  }
  void run(const char* phrase, size_t length, unsigned char outer[32]) const {
    unsigned char inner[32];
    SHA256_CTX c=innerPrefix;
    SHA256_Update(&c,phrase,length);SHA256_Final(inner,&c);
    c=outerPrefix;SHA256_Update(&c,inner,32);SHA256_Final(outer,&c);
  }
  bool accept(const char* phrase, size_t length, const unsigned char target[32]) const {
    unsigned char outer[32],com[32];run(phrase,length,outer);
    SHA256(outer,16,com);
    return std::equal(com,com+32,target);
  }
};
static void parseHex32(const char* h, unsigned char out[32]) {
  for(int i=0;i<32;i++){unsigned x=0;std::sscanf(h+2*i,"%2x",&x);out[i]=x;}
}
struct Shared {
  Engine eng;
  std::vector<std::vector<std::string>> words;
  unsigned char original[32], planted[32];
  std::atomic<uint64_t> checked{0};
  std::atomic<uint64_t> hits{0};
  std::atomic<uint64_t> plantHits{0};
};
static void recurse(const Shared& sh, std::string& phrase,int d,uint64_t& checked,uint64_t& hits,uint64_t& plantHits){
  if(d==8){
    checked++;
    unsigned char outer[32], com[32];
    sh.eng.run(phrase.data(),phrase.size(),outer);
    SHA256(outer,16,com);
    if(std::equal(com,com+32,sh.original)) {
      hits++;std::cout<<"ORIGINAL MATCH: "<<phrase<<"\n";
    }
    if(std::equal(com,com+32,sh.planted)) {
      plantHits++;std::cout<<"PLANTED MATCH: "<<phrase<<"\n";
    }
    return;
  }
  const size_t n=phrase.size();
  for(const std::string& w: sh.words[d]){
    if(d) phrase.push_back(' ');
    phrase+=w;
    recurse(sh,phrase,d+1,checked,hits,plantHits);
    phrase.resize(n);
  }
}
int main(int argc,char** argv){
  if(argc<2||argc>3){std::cerr<<"usage: k08_emily_eight_sft <original-notes-file> [max-first-note-choices=0-all]\n";return 2;}
  std::ifstream f(argv[1],std::ios::binary);if(!f) {std::cerr<<"Unable to open notes\n";return 2;}
  const std::string source((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
  unsigned char sourceHash[32];SHA256(reinterpret_cast<const unsigned char*>(source.data()),source.size(),sourceHash);
  if(hex(sourceHash,32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb") {
    std::cerr<<"Original crew-note SHA256 pin failed\n";return 3;
  }
  f.clear();f.seekg(0);
  Shared sh;std::string line;bool take=false;
  std::vector<int> ids;
  std::regex header("^N([0-9][0-9]) / Emily .*$");
  std::smatch m;
  while(std::getline(f,line)) {
    if(std::regex_match(line,m,header)) { ids.push_back(std::stoi(m[1]));take=true;continue; }
    if(take){
      take=false;
      const size_t colon=line.find(':');
      if(colon!=std::string::npos) line=line.substr(colon+1);
      const auto all=tokenize(line);
      std::set<std::string> seen;
      std::vector<std::string> unique;
      for(const auto& w: all)if(seen.insert(w).second)unique.push_back(w);
      sh.words.push_back(std::move(unique));
    }
  }
  if(ids!=std::vector<int>{2,6,10,13,17,18,20,23}){std::cerr<<"Unexpected Emily note IDs\n";return 2;}
  const std::vector<size_t> lengths{12,10,21,18,7,5,24,19};
  for(int i=0;i<8;i++)if(sh.words[i].size()!=lengths[i]){std::cerr<<"Unexpected note token counts\n";return 2;}
  parseHex32("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747",sh.original);
  unsigned char digest[32];
  const std::string known="a good watch leaves the room ready for the next pair of hands";
  sh.eng.run(known.data(),known.size(),digest);
  if(!eqhex(digest,16,"bf889359b0303f2b2b2fd96ae841210b")){
    std::cerr<<"Known original N02 HMAC prehash control failed\n";return 3;
  }
  std::string plant;
  const int idx[]{2,3,4,5,6,0,1,2};
  for(int i=0;i<8;i++){if(i)plant+=' ';plant+=sh.words[i][idx[i]];}
  sh.eng.run(plant.data(),plant.size(),digest);
  SHA256(digest,16,sh.planted);
  uint64_t total=1;for(const auto& w:sh.words)total*=w.size();
  const int maxfirst=(argc==3?std::stoi(argv[2]):0);
  const int nfirst=maxfirst>0?std::min(maxfirst,int(sh.words[0].size())):int(sh.words[0].size());
  std::cerr<<"Emily IDs: 2 6 10 13 17 18 20 23; unique-word counts: 12 10 21 18 7 5 24 19\n";
  std::cerr<<"Total exact distinct eight-word strings: "<<total<<"; first choices tested: "<<nfirst<<"\n";
  std::cerr<<"Planted phrase: "<<plant<<"\n";
  const auto start=std::chrono::steady_clock::now();
  std::array<uint64_t,12> counts{},hits{},plantHits{};
  std::vector<std::thread> threads;
  for(int i=0;i<nfirst;i++){
    threads.emplace_back([&,i](){
      std::string s=sh.words[0][i];
      recurse(sh,s,1,counts[i],hits[i],plantHits[i]);
      std::cerr<<"Finished prefix "<<i+1<<"/"<<nfirst<<" count="<<counts[i]<<"\n";
    });
  }
  for(auto& t:threads)t.join();
  uint64_t c=0,h=0,p=0;for(int i=0;i<nfirst;i++){c+=counts[i];h+=hits[i];p+=plantHits[i];}
  std::chrono::duration<double> dt=std::chrono::steady_clock::now()-start;
  std::cout<<"SUMMARY count="<<c<<" original_hits="<<h<<" planted_hits="<<p<<" seconds="<<dt.count()<<"\n";
  if(c!=total/12*nfirst) return 3;
  if(nfirst==12 && p!=1)return 3;
  return 0;
}
