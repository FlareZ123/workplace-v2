/* H17 K08: first-person MAIL11 caption ancestor, exhaustive <=2 word edits.
 * The original selected final margin is absent; this is conditional.
 * Read-only, SHA-pinned sources and true N02 plus planted full-target checks.
 * C++17, OpenSSL libcrypto. Supply the original resources directory as argv[1].
 */
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using Words=std::vector<std::string>;
static constexpr unsigned char NONCE[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static constexpr unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static std::string read_file(const std::string&p){
 std::ifstream f(p,std::ios::binary);assert(f);
 return std::string((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
}
static void pin(const std::string&data,const char*expected){
 unsigned char h[32];SHA256(reinterpret_cast<const unsigned char*>(data.data()),data.size(),h);
 char hex[65];for(int i=0;i<32;i++)std::sprintf(hex+2*i,"%02x",h[i]);hex[64]=0;
 assert(std::string(hex)==expected);
}
static Words tokenize(const std::string&s){
 Words out;std::string part;
 for(unsigned char c:s){
  if((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9'))part+=char(std::tolower(c));
  else if(!part.empty()){out.push_back(part);part.clear();}
 }
 if(!part.empty())out.push_back(part);
 return out;
}
static std::string join(const Words&w){
 std::string out;
 for(const auto& s:w){if(!out.empty())out+=' ';out+=s;}
 return out;
}
static void component_hash(const std::string&s,unsigned char h[32]){
 unsigned char mac[EVP_MAX_MD_SIZE];unsigned int n=0;
 const unsigned char*msg=reinterpret_cast<const unsigned char*>(s.data());
 assert(HMAC(EVP_sha256(),NONCE,16,msg,s.size(),mac,&n)==mac&&n==32);
 SHA256(mac,16,h);
}
static std::string digest16(const std::string&s){
 unsigned char mac[EVP_MAX_MD_SIZE];unsigned int n=0;
 assert(HMAC(EVP_sha256(),NONCE,16,reinterpret_cast<const unsigned char*>(s.data()),s.size(),mac,&n)==mac&&n==32);
 char hex[33];for(int i=0;i<16;i++)std::sprintf(hex+2*i,"%02X",mac[i]);hex[32]=0;
 return hex;
}
int main(int argc,char**argv){
 assert(argc==2);
 std::string root=argv[1];
 const std::string notes=read_file(root+"/evidence/crew/noticeboard-and-desk-notes.txt");
 const std::string mail=read_file(root+"/evidence/mail/11.eml");
 pin(notes,"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
 pin(mail,"f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29");
 assert(digest16("a good watch leaves the room ready for the next pair of hands")=="BF889359B0303F2B2B2FD96AE841210B");
 const Words base=tokenize("people making room for each other after a long watch with the water outside and the night almost finished");
 assert(base.size()==19);
 std::set<std::string> lex;
 std::istringstream stream(notes);std::string line;
 const std::set<std::string> allowed={"N02","N06","N10","N13","N20","N23"};
 while(std::getline(stream,line)){
  const std::string id=line.substr(0,std::min<size_t>(3,line.size()));
  if(!allowed.count(id)||line.find(" / Emily ")==std::string::npos)continue;
  assert(std::getline(stream,line));
  auto pos=line.find(':');if(pos!=std::string::npos)line=line.substr(pos+1);
  for(const auto&t:tokenize(line))lex.insert(t);
 }
 const auto start=mail.find("For this envelope\nI wanted");
 assert(start!=std::string::npos);
 const auto stop=mail.find("\n\nEmily",start);assert(stop!=std::string::npos);
 for(const auto&t:tokenize(mail.substr(start,stop-start)))lex.insert(t);
 assert(lex.size()==100);
 for(const auto&t:base)assert(lex.count(t));
 const Words choices(lex.begin(),lex.end());
 Words planted=base;planted[12]="sea";planted[17]="voices";
 unsigned char synth[32];component_hash(join(planted),synth);
 uint64_t count=0,original=0,positive=0;
 auto check=[&](const Words&w){
  const std::string s=join(w);
  unsigned char h[32];component_hash(s,h);count++;
  if(!std::memcmp(h,TARGET,32)){std::cout<<"ORIGINAL_MATCH "<<s<<"\n";original++;}
  if(!std::memcmp(h,synth,32))positive++;
 };
 const int N=int(base.size());
 check(base);
 for(int i=0;i<N;i++)for(const auto&a:choices)if(a!=base[i]){
  Words w=base;w[i]=a;check(w);
 }
 for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
  Words w=base;
  for(const auto&a:choices)if(a!=base[i]){
   w[i]=a;
   for(const auto&b:choices)if(b!=base[j]){w[j]=b;check(w);}
  }
 }
 for(int g=0;g<=N;g++)for(const auto&a:choices){
  Words w=base;w.insert(w.begin()+g,a);check(w);
 }
 for(int g=0;g<=N;g++)for(int h=g;h<=N;h++){
  for(const auto&a:choices)for(const auto&b:choices){
   Words w=base;w.insert(w.begin()+g,a);w.insert(w.begin()+h+1,b);check(w);
  }
 }
 for(int g=0;g<=N;g++)for(int i=0;i<N;i++){
  for(const auto&a:choices)for(const auto&b:choices)if(b!=base[i]){
   Words w=base;w[i]=b;w.insert(w.begin()+g,a);check(w);
  }
 }
 for(int i=0;i<N;i++){
  Words w=base;w.erase(w.begin()+i);check(w);
 }
 for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
  Words w=base;w.erase(w.begin()+j);w.erase(w.begin()+i);check(w);
 }
 for(int i=0;i<N;i++)for(int j=0;j<N;j++)if(i!=j){
  for(const auto&b:choices)if(b!=base[j]){
   Words w=base;w[j]=b;w.erase(w.begin()+i);check(w);
  }
 }
 for(int i=0;i<N;i++)for(int g=0;g<N;g++)for(const auto&a:choices){
  Words w=base;w.erase(w.begin()+i);w.insert(w.begin()+g,a);check(w);
 }
 std::cout<<"SOURCE_PIN_PASS notes_and_MAIL11 true_n02_hmac_pass lexicon="<<choices.size()<<" base_words="<<base.size()<<"\n";
 std::cout<<"SUMMARY assignments="<<count<<" original_hits="<<original<<" planted_hits="<<positive<<"\n";
 assert(count==7612001&&positive==1);
 return original?5:0;
}
