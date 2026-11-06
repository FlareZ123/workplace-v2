// H17 K08: exhaustive short normalized captions from the original evidence vocabulary.
// C++17/OpenSSL, read-only. Usage: k08_short_word_product_sft [resources/evidence]
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;namespace fs=std::filesystem;
string hx(const unsigned char*p,size_t n){static const char H[]="0123456789abcdef";string s;for(size_t i=0;i<n;i++){s+=H[p[i]>>4];s+=H[p[i]&15];}return s;}
vector<unsigned char> fromhex(string s){vector<unsigned char> a;for(size_t i=0;i<s.size();i+=2)a.push_back(static_cast<unsigned char>(stoi(s.substr(i,2),nullptr,16)));return a;}
string read(const fs::path&p){ifstream f(p,ios::binary);if(!f)throw runtime_error("missing "+p.string());return string(istreambuf_iterator<char>(f),istreambuf_iterator<char>());}
void tokenize(const string&text,set<string>&words){string word;for(unsigned char c:text){if((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9'))word+=char(c>='A'&&c<='Z'?c+32:c);else if(!word.empty()){words.insert(word);word.clear();}}if(!word.empty())words.insert(word);}
struct Checker{
 vector<unsigned char> key=fromhex("5F933DA6A1BD03C32DA5CBC25344F497");
 vector<unsigned char> target=fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
 vector<unsigned char> planted=fromhex("efcdd8a1f71e32ca72c8dac703344fe78848f8f4a7bc86dc1565330bf4cc40e2");
 SHA256_CTX ibase{},obase{};
 uint64_t tests=0,hits=0,planted_hits=0;
 Checker(){unsigned char ipad[64],opad[64];memset(ipad,0x36,64);memset(opad,0x5c,64);for(size_t i=0;i<key.size();i++){ipad[i]^=key[i];opad[i]^=key[i];}
 SHA256_Init(&ibase);SHA256_Update(&ibase,ipad,64);SHA256_Init(&obase);SHA256_Update(&obase,opad,64);}
 void check(const string&s){unsigned char inner[32],mac[32],digest[32];
    SHA256_CTX ic=ibase,oc=obase;SHA256_Update(&ic,s.data(),s.size());SHA256_Final(inner,&ic);
    SHA256_Update(&oc,inner,32);SHA256_Final(mac,&oc);SHA256(mac,16,digest);tests++;
    if(memcmp(digest,target.data(),32)==0){hits++;cout<<"ORIGINAL_K08 "<<s<<" "<<hx(mac,16)<<"\n";}
    if(memcmp(digest,planted.data(),32)==0){planted_hits++;if(s!="mugs sea")throw runtime_error("synthetic collision");}
 }
 void n02(){const string s="a good watch leaves the room ready for the next pair of hands";unsigned char mac[32];unsigned int len=0;
    HMAC(EVP_sha256(),key.data(),16,reinterpret_cast<const unsigned char*>(s.data()),s.size(),mac,&len);
    if(len!=32||hx(mac,16)!="bf889359b0303f2b2b2fd96ae841210b")throw runtime_error("authentic N02 control failed");
 }
};
int main(int argc,char**argv){try{
 fs::path root=argc>1?argv[1]:"resources/evidence";
 string crew=read(root/"crew/noticeboard-and-desk-notes.txt");unsigned char sum[32];SHA256(reinterpret_cast<const unsigned char*>(crew.data()),crew.size(),sum);
 if(hx(sum,32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw runtime_error("source sha pin mismatch");
 const set<string> allowed={".eml",".txt",".log",".md",".html",".json",".jsonl",".ini",".csv"};
 set<string> all,crewwords;size_t count=0;
 for(auto&e:fs::recursive_directory_iterator(root)){if(!e.is_regular_file()||!allowed.count(e.path().extension().string()))continue;
   string raw=read(e.path());tokenize(raw,all);if(e.path().parent_path().filename()=="crew")tokenize(raw,crewwords);count++;
 }
 vector<string> word(all.begin(),all.end()),cw(crewwords.begin(),crewwords.end());
 if(count!=40||word.size()!=2285||cw.size()!=321)throw runtime_error("original text cardinality changed");
 auto wordpin=[](const vector<string>&v){string j;for(const string&w:v){j+=w;j+='\n';}unsigned char h[32];SHA256(reinterpret_cast<const unsigned char*>(j.data()),j.size(),h);return hx(h,32);};
 if(wordpin(word)!="b5acd81fe80f294cd3e0a4c01ca5e298aef1cf4879a3df9cb948294816013df3"||wordpin(cw)!="399ddef7c8cce60aa1e78d3ec85683b0188c08b4346ad0bd824d4068d8dc29ba")throw runtime_error("vocabulary SHA pin mismatch");
 Checker c;c.n02();c.check("");for(auto&a:word)c.check(a);
 for(auto&a:word){string lead=a+" ";for(auto&b:word)c.check(lead+b);}
 uint64_t short_count=c.tests;
 if(argc<3||string(argv[2])=="triples")for(size_t i=0;i<cw.size();++i){
    auto&a=cw[i];for(auto&b:cw){string lead=a+" "+b+" ";for(auto&d:cw)c.check(lead+d);}
    if(i%64==0){cout<<"CREW_TRIPLE_PREFIX "<<i<<"/"<<cw.size()<<"\n"<<flush;}
 }
 if(short_count!=5223511||c.tests!=(argc>2&&string(argv[2])=="short"?5223511ULL:38299672ULL)||c.planted_hits!=1)throw runtime_error("enumeration or planted control failed");
 cout<<"K08_SHORT_SOURCE COMPLETE files="<<count<<" vocab="<<word.size()<<" crew_vocab="<<cw.size()<<" source_0_1_2="<<short_count<<" crew_3="<<c.tests-short_count<<" checks="<<c.tests<<" genuine="<<c.hits<<" synthetic="<<c.planted_hits<<"\n";
 return c.hits?2:0;
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<"\n";return 3;}}
