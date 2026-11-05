// Agent19: finite K08 future-conditional editorial hypothesis; original evidence read-only.
// C++17 / OpenSSL. Argument: archive root containing evidence and acceptance.json.
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

using V=std::vector<std::string>;
static V split(const std::string&s){V v;size_t start=0,end;while((end=s.find('|',start))!=std::string::npos){v.push_back(s.substr(start,end-start));start=end+1;}v.push_back(s.substr(start));return v;}
static std::string readfile(std::string p){std::ifstream f(p,std::ios::binary);assert(f.good());return {std::istreambuf_iterator<char>(f),{}};}
static std::array<unsigned char,32> digest(const std::string&s){std::array<unsigned char,32>h{};SHA256((const unsigned char*)s.data(),s.size(),h.data());return h;}
static std::string hex(const unsigned char*b,size_t n){std::string s;const char*k="0123456789abcdef";for(size_t i=0;i<n;i++){s+=k[b[i]>>4];s+=k[b[i]&15];}return s;}
static constexpr unsigned char key[]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static std::array<unsigned char,32> hashcaption(const std::string&s){
 unsigned char h[EVP_MAX_MD_SIZE];unsigned int n=0;
 HMAC(EVP_sha256(),key,16,(const unsigned char*)s.data(),s.size(),h,&n);assert(n==32);
 std::array<unsigned char,32>d{};SHA256(h,16,d.data());return d;
}
static std::string phrase(const std::string&a,const std::string&link1,const std::string&b,const std::string&link2,const std::string&c){
 std::string s=a;for(const std::string*t:{&link1,&b,&link2,&c})if(!t->empty()){s+=' ';s+=*t;}return s;
}
int main(int argc,char**argv){
 assert(argc==2);std::string root=argv[1];
 std::string notes=readfile(root+"/evidence/crew/noticeboard-and-desk-notes.txt");
 assert(hex(digest(notes).data(),32)=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
 assert(notes.find("The little lamp stays on until the corridor has gone quiet")!=std::string::npos);
 assert(notes.find("hold the sea, the end of the night and the voices at the table")!=std::string::npos);
 assert(hex(digest(readfile(root+"/acceptance.json")).data(),32)=="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
 assert(readfile(root+"/evidence/recovery-routing.json").find("5F933DA6A1BD03C32DA5CBC25344F497")!=std::string::npos);
 unsigned char h[EVP_MAX_MD_SIZE];unsigned int n=0;std::string n02="a good watch leaves the room ready for the next pair of hands";
 HMAC(EVP_sha256(),key,16,(const unsigned char*)n02.data(),n02.size(),h,&n);
 assert(hex(h,16)=="bf889359b0303f2b2b2fd96ae841210b");
 const V SEA=split("the sea is still outside|the water is still outside|the sea waits outside|the water waits outside|the sea is waiting outside|the tide is still outside|the sea is beyond the window|the water is beyond the window|the sea will still be outside|the sea will be waiting outside|the water will still be outside|the tide will be waiting outside|the sea will still be there|the water will still be there|the sea is waiting for morning|the sea will wait for the morning|the water will give back the morning|the sea will give back the morning|the sea will give back the light|the water will give back the light|the sea will return the morning|the waves will still be outside|the water will still be at the window|the sea will be outside the window");
 const V WATCH=split("when the night is over|when the long night is over|when the watch is over|when the long watch is over|when the night is almost over|when the watch is almost over|when the last watch is finished|when the late watch is finished|when morning comes|when the morning comes|when the daylight comes|when daybreak comes|as the morning comes|as morning comes|after the night watch|after the last watch|after a long watch|after the long watch|after the night has ended|after the watch has ended|by the end of the night|at the end of the night|before the first light|before the first boat|as the night gives way to morning|as the night turns to morning");
 const V PROMISE=split("there will always be room at the table|there will be room at the table|there will always be room for another|there will be room for one more|there will always be room for one more|there will be room for the next watch|there will always be room for the next watch|there will be room for whoever comes next|there will always be a place at the table|there will be a place at the table|there will always be a place for the next watch|there will be a place for the next watch|there will always be another chair|there will always be another cup|there will be another cup waiting|there will be a warm cup waiting|there will be a light waiting|there will always be a light on|someone will leave the lamp on|someone will leave a light on|someone will leave room for the next watch|someone will leave room at the table|someone will save you a place|someone will keep a place for you|we will leave room at the table|we will keep a place for one another|we will always make room for one another|we will make room for whoever comes next|we will make room for the next watch|we will keep room for the next watch|we will always leave room for the next watch|we will always leave a light on|the table will have room for another|the table will have room for the next watch|the table will still have room for us|the next watch will find a place at the table|the next pair of hands will find room|the next watch will find a cup waiting|the next watch will always have a place|everyone will have a place at the table|everyone will find a place at the table|we will find room for one another");
 const V LINKS=split("|and|but|while|as");
 assert(SEA.size()==24&&WATCH.size()==26&&PROMISE.size()==42&&LINKS.size()==5);
 std::string expected="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747";
 auto planted=hashcaption("the sea will still be there when the night is over and there will always be room at the table");
 unsigned long long checked=0,original_hits=0,synthetic_hits=0;
 auto test=[&](const std::string&s){
  auto d=hashcaption(s);synthetic_hits+=d==planted;
  bool match=hex(d.data(),32)==expected;original_hits+=match;if(match)std::cout<<"FOUND "<<s<<"\n";++checked;
 };
 for(const auto&a:SEA)for(const auto&b:WATCH)for(const auto&c:PROMISE){
  std::array<std::string,3>w{a,b,c};
  for(int i=0;i<3;i++)for(int j=0;j<3;j++)if(i!=j){
   int k=3-i-j;
   for(const auto&l1:LINKS)for(const auto&l2:LINKS)test(phrase(w[i],l1,w[j],l2,w[k]));
  }
 }
 for(const auto&a:WATCH)for(const auto&b:PROMISE){test(a+" "+b);test(b+" "+a);}
 assert(checked==3933384ULL&&synthetic_hits==1);
 std::cout<<"ORIGINAL_SOURCE_AND_N02_CONTROL_PASS complete_candidates="<<checked
          <<" original_hits="<<original_hits<<" synthetic_hits="<<synthetic_hits<<"\n";
 return original_hits?1:0;
}
