#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
static const unsigned char K08_NONCE[16] = {0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};
static const unsigned char K08_TARGET[32] = {0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char N02_HMAC16[16] = {0xBF,0x88,0x93,0x59,0xB0,0x30,0x3F,0x2B,0x2B,0x2F,0xD9,0x6A,0xE8,0x41,0x21,0x0B};
string read_file(const string& path) { ifstream f(path,ios::binary); if(!f) throw runtime_error("cannot read "+path); return string((istreambuf_iterator<char>(f)),{}); }
string hex(const unsigned char* p,size_t n) { static const char*d="0123456789abcdef"; string s; s.reserve(2*n); for(size_t i=0;i<n;++i){s.push_back(d[p[i]>>4]);s.push_back(d[p[i]&15]);} return s; }
string sha256_hex(const string&s){unsigned char d[32];SHA256((const unsigned char*)s.data(),s.size(),d);return hex(d,32);}
vector<string> words(const string&s){vector<string>v;string w;for(unsigned char c:s){if(isalnum(c))w.push_back((char)tolower(c));else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
string normalize(const vector<string>&v){string s;for(size_t i=0;i<v.size();++i){if(i)s.push_back(' ');s+=v[i];}return s;}
string note_body(const string&all,const string&tag){size_t p=all.find(tag);if(p==string::npos)throw runtime_error("missing note "+tag);p=all.find('\n',p);if(p==string::npos)throw runtime_error("missing note body "+tag);size_t q=all.find("\n\n",p);if(q==string::npos)q=all.size();return all.substr(p+1,q-p-1);}
array<unsigned char,16> hmac16(const string&s){unsigned char d[EVP_MAX_MD_SIZE];unsigned int n=0;HMAC(EVP_sha256(),K08_NONCE,16,(const unsigned char*)s.data(),s.size(),d,&n);array<unsigned char,16>o{};copy(d,d+16,o.begin());return o;}
array<unsigned char,32> commitment(const string&s){auto h=hmac16(s);array<unsigned char,32>o{};SHA256(h.data(),h.size(),o.data());return o;}
bool equal32(const array<unsigned char,32>&a,const unsigned char*b){return equal(a.begin(),a.end(),b);}
bool equal32(const array<unsigned char,32>&a,const array<unsigned char,32>&b){return equal(a.begin(),a.end(),b.begin());}
int main(int argc,char**argv){try{
 const string root=argc>1?argv[1]:"resources/evidence";
 const string acceptance_path=argc>2?argv[2]:"resources/acceptance.json";
 const string notes=read_file(root+"/crew/noticeboard-and-desk-notes.txt");
 const string mail11=read_file(root+"/mail/11.eml");
 const string acceptance=read_file(acceptance_path);
 if(sha256_hex(notes)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw runtime_error("noticeboard source pin failed");
 if(sha256_hex(mail11)!="f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29")throw runtime_error("MAIL-11 source pin failed");
 if(sha256_hex(acceptance)!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")throw runtime_error("acceptance source pin failed");
 const size_t kp=acceptance.find("\"K08\": \"");
 if(kp==string::npos||acceptance.substr(kp+8,64)!="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")throw runtime_error("K08 commitment mismatch");
 const vector<string>lex={"sea","voices","table","people","room","water","outside","watch","long","each","other","line"};
 const set<string>lexset(lex.begin(),lex.end());if(lexset.size()!=lex.size())throw runtime_error("duplicate lexicon token");
 set<string>n20mail;for(const auto&w:words(note_body(notes,"N20 /")))n20mail.insert(w);for(const auto&w:words(mail11))n20mail.insert(w);
 for(const auto&w:lex)if(!n20mail.count(w))throw runtime_error("lexicon token is not source-literal: "+w);
 vector<pair<string,vector<string>>>bases;
 for(const auto&item:vector<pair<string,string>>{{"N02","N02 /"},{"N06","N06 /"},{"N13","N13 /"}}){
  string body=note_body(notes,item.second);if(item.first!="N13"){size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);}bases.push_back({item.first,words(body)});
 }
 if(bases[0].second.size()!=13||bases[1].second.size()!=11||bases[2].second.size()!=22)throw runtime_error("source note word-count mismatch");
 const auto n02h=hmac16(normalize(bases[0].second));if(!equal(n02h.begin(),n02h.end(),N02_HMAC16))throw runtime_error("N02 historical HMAC16 control failed");
 auto calculate=[&](const vector<string>&base,int i,int j,int k,const string&a,const string&b,const string&c){
  char buf[512];size_t len=0;for(size_t z=0;z<base.size();++z){if(z)buf[len++]=' ';const string*w=&base[z];if((int)z==i)w=&a;else if((int)z==j)w=&b;else if((int)z==k)w=&c;memcpy(buf+len,w->data(),w->size());len+=w->size();}
  unsigned char mac[EVP_MAX_MD_SIZE];unsigned int ml=0;HMAC(EVP_sha256(),K08_NONCE,16,(unsigned char*)buf,len,mac,&ml);array<unsigned char,32>out{};SHA256(mac,16,out.data());return out;
 };
 uint64_t assignments=0;bool hit=false;string hitbase,hitphrase;
 auto test=[&](const vector<string>&base,const string&name,int i,int j,int k,const string&a,const string&b,const string&c){
  ++assignments;const auto d=calculate(base,i,j,k,a,b,c);if(equal32(d,K08_TARGET)){hit=true;hitbase=name;vector<string>v=base;if(i>=0)v[i]=a;if(j>=0)v[j]=b;if(k>=0)v[k]=c;hitphrase=normalize(v);}
 };
 for(const auto&e:bases){const auto&base=e.second;const int n=(int)base.size();
  for(int i=0;i<n;++i)for(const auto&a:lex)if(a!=base[i])test(base,e.first,i,-1,-1,a,"","");
  for(int i=0;i<n;++i)for(int j=i+1;j<n;++j)for(const auto&a:lex)if(a!=base[i])for(const auto&b:lex)if(b!=base[j])test(base,e.first,i,j,-1,a,b,"");
  for(int i=0;i<n;++i)for(int j=i+1;j<n;++j)for(int k=j+1;k<n;++k)for(const auto&a:lex)if(a!=base[i])for(const auto&b:lex)if(b!=base[j])for(const auto&c:lex)if(c!=base[k])test(base,e.first,i,j,k,a,b,c);
 }
 if(assignments!=3474251)throw runtime_error("candidate assignment count mismatch");
 cout<<"bases=N02:13,N06:11,N13:22 lexicon=12 assignments="<<assignments<<" original_hits="<<(hit?1:0)<<"\n";
 if(hit)cout<<"HIT "<<hitbase<<" :: "<<hitphrase<<"\n";
 const auto&n13=bases[2].second;
 const string synthetic_phrase=normalize(vector<string>{lex[0],lex[1],lex[2]})+" "+normalize(vector<string>(n13.begin()+3,n13.end()));
 const auto synthetic_target=commitment(synthetic_phrase);uint64_t synthetic_checks=0;bool synthetic_found=false;
 for(int i=0;i<(int)n13.size()&&!synthetic_found;++i)for(int j=i+1;j<(int)n13.size()&&!synthetic_found;++j)for(int k=j+1;k<(int)n13.size()&&!synthetic_found;++k)
  for(const auto&a:lex)if(a!=n13[i]&&!synthetic_found)for(const auto&b:lex)if(b!=n13[j]&&!synthetic_found)for(const auto&c:lex)if(c!=n13[k]&&!synthetic_found){++synthetic_checks;if(equal32(calculate(n13,i,j,k,a,b,c),synthetic_target))synthetic_found=true;}
 if(!synthetic_found)throw runtime_error("synthetic positive was not enumerated");
 cout<<"synthetic_positive=PASS checks_until_hit="<<synthetic_checks<<" phrase=\""<<synthetic_phrase<<"\"\n";
 return hit?10:0;
 }catch(const exception&e){cerr<<"ERROR: "<<e.what()<<"\n";return 2;}}
