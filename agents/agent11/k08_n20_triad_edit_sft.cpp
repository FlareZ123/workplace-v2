#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>
static std::string hex(const unsigned char* b, size_t n) {
 static const char* h="0123456789abcdef";std::string s(n*2,'0');
 for(size_t i=0;i<n;i++){s[2*i]=h[b[i]>>4];s[2*i+1]=h[b[i]&15];}return s;
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

static const std::vector<std::string> lex={"17",
"a",
"after",
"again",
"almost",
"also",
"an",
"and",
"appliance",
"archive",
"are",
"as",
"at",
"b",
"back",
"because",
"been",
"beside",
"board",
"but",
"c",
"captions",
"circulated",
"comment",
"copies",
"copy",
"corridor",
"crew",
"cup",
"d",
"decide",
"desk",
"do",
"draft",
"drafts",
"each",
"emily",
"end",
"envelope",
"export",
"felt",
"file",
"final",
"finally",
"finished",
"first",
"footer",
"for",
"four",
"goes",
"going",
"gone",
"good",
"had",
"hands",
"has",
"have",
"headings",
"hold",
"how",
"i",
"in",
"is",
"issue",
"issued",
"it",
"just",
"kept",
"label",
"labels",
"lamp",
"last",
"later",
"leave",
"leaves",
"like",
"line",
"little",
"long",
"making",
"margin",
"marked",
"material",
"meant",
"mixed",
"mugs",
"my",
"never",
"next",
"night",
"not",
"notes",
"nothing",
"of",
"official",
"old",
"on",
"only",
"or",
"order",
"other",
"out",
"outside",
"page",
"pages",
"pair",
"people",
"photograph",
"phrase",
"please",
"put",
"quarterly",
"quiet",
"rc",
"ready",
"receipt",
"recovery",
"regardless",
"remembered",
"remembers",
"report",
"revision",
"room",
"s",
"scanner",
"sea",
"second",
"section",
"service",
"shorter",
"slogan",
"so",
"somebody",
"sound",
"standby",
"stays",
"stood",
"strip",
"strips",
"survive",
"table",
"tells",
"text",
"that",
"the",
"their",
"this",
"those",
"timestamps",
"to",
"treat",
"until",
"us",
"use",
"voices",
"wanted",
"was",
"watch",
"water",
"were",
"where",
"window",
"with",
"withdrawn",
"wording",
"words",
"worked"};
static const std::vector<std::string> bases={"the sea the end of the night and the voices at the table",
"the sea at the end of the night and the voices at the table",
"the sea outside at the end of the night and the voices at the table",
"at the end of the night the sea and the voices at the table",
"the sea and the voices at the table at the end of the night"};

static std::vector<std::string> split(std::string s){
 std::vector<std::string> v;std::istringstream in(s);std::string w;while(in>>w)v.push_back(w);return v;
}
struct Answer { uint64_t checks=0,hits=0,plant=0;};
static const std::array<unsigned char,32> TARGET={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static std::array<unsigned char,32> PLANT;
static void test(const Engine &eng,const std::vector<std::string>&w,Answer&res){
 std::string phrase;for(const auto& x:w){if(!phrase.empty())phrase+=' ';phrase+=x;}
 unsigned char tmp[32],sha[32];eng.run(phrase.data(),phrase.size(),tmp);SHA256(tmp,16,sha);
 res.checks++;if(std::equal(sha,sha+32,TARGET.begin())){res.hits++;std::cout<<"ORIGINAL MATCH: "<<phrase<<"\n";}
 if(std::equal(sha,sha+32,PLANT.begin())){res.plant++;std::cout<<"PLANTED MATCH: "<<phrase<<"\n";}
}
static void work(const Engine& eng,size_t idx,Answer&res){
 auto b=split(bases[idx]);int n=(int)b.size();
 test(eng,b,res);
 for(int a=0;a<n;a++){
  for(const auto&w:lex){if(w==b[a])continue;auto x=b;x[a]=w;test(eng,x,res);}
  for(int c=a+1;c<n;c++){
   for(const auto&w:lex){if(w==b[a])continue;
    auto x=b;x[a]=w;
    for(const auto&z:lex){if(z==b[c])continue;x[c]=z;test(eng,x,res);}
   }
  }
 }
 for(int gap=0;gap<=n;gap++){
  for(int a=0;a<n;a++){
   for(const auto&w:lex){if(w==b[a])continue;
    auto x=b;x[a]=w;
    for(const auto&z:lex){auto y=x;y.insert(y.begin()+gap,z);test(eng,y,res);}
   }
  }
 }
 for(int a=0;a<=n;a++)for(int c=a;c<=n;c++){
  for(const auto&w:lex)for(const auto&z:lex){auto x=b;x.insert(x.begin()+c,z);x.insert(x.begin()+a,w);test(eng,x,res);}
 }
 for(int a=0;a<n;a++){
  auto x=b;x.erase(x.begin()+a);
  for(int j=0;j<n-1;j++)for(const auto&w:lex){if(w==x[j])continue;auto y=x;y[j]=w;test(eng,y,res);}
  for(int c=a+1;c<n;c++){auto y=x;y.erase(y.begin()+c-1);test(eng,y,res);}
 }
}
int main(int argc,char**argv){
 if(argc!=3){std::cerr<<"Require original notes and MAIL11 paths\n";return 2;}
 const char* pins[]={"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb","f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"};
 for(int i=0;i<2;i++){std::ifstream f(argv[i+1],std::ios::binary);if(!f)return 3;
 std::string src((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 unsigned char digest[32];SHA256((const unsigned char*)src.data(),src.size(),digest);
 if(hex(digest,32)!=pins[i]){std::cerr<<"Original source SHA pin failed\n";return 3;}}
 Engine eng;unsigned char digest[32];
 const std::string known="a good watch leaves the room ready for the next pair of hands";
 eng.run(known.data(),known.size(),digest);
 if(!eqhex(digest,16,"bf889359b0303f2b2b2fd96ae841210b"))return 3;
 auto planted=split(bases[0]);planted[0]="archive";planted[1]="appliance";
 std::string phrase;for(const auto&w:planted){if(!phrase.empty())phrase+=' ';phrase+=w;}
 eng.run(phrase.data(),phrase.size(),digest);SHA256(digest,16,PLANT.data());
 std::cout<<"lexicon="<<lex.size()<<" skeletons="<<bases.size()<<" planted="<<phrase<<"\n";
 std::array<Answer,5> results{};std::vector<std::thread> th;auto start=std::chrono::steady_clock::now();
 for(size_t i=0;i<bases.size();i++)th.emplace_back([&,i]{work(eng,i,results[i]);});
 for(auto& t:th)t.join();Answer sum;
 for(const auto&v:results){sum.checks+=v.checks;sum.hits+=v.hits;sum.plant+=v.plant;}
 std::chrono::duration<double> sec=std::chrono::steady_clock::now()-start;
 std::cout<<"SUMMARY complete_assignments="<<sum.checks<<" original_hits="<<sum.hits<<" planted_hits="<<sum.plant<<" elapsed="<<sec.count()<<" sec\n";
 return sum.plant==1?0:3;
}
