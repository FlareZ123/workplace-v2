// H-17 K08 conditional two-word transition source reconstruction, independent scene motif gates.
// Build: g++ -O3 -std=c++17 -fopenmp k08_bigram_sft.cpp -lcrypto -o k08_bigram_sft
// Run: OMP_NUM_THREADS=4 ./k08_bigram_sft /path/to/extracted/archive 14
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
static const char* NSHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb";
static const char* M11SHA="f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29";
static const char* M20SHA="e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71";
static const uint8_t NONCE[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const uint8_t TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static void fail(const string& m){cerr<<"ERROR: "<<m<<"\n";exit(2);}
static string bytes(const string& p){ifstream f(p,ios::binary); if(!f)fail("missing "+p);return string((istreambuf_iterator<char>(f)),istreambuf_iterator<char>());}
static string hex(const uint8_t*p,size_t n){string s;char t[3];for(size_t i=0;i<n;i++){snprintf(t,sizeof t,"%02x",p[i]);s+=t;}return s;}
static string pinned(const string& root,const string& path,const char*expected){string x=bytes(root+"/evidence/"+path);uint8_t h[32];SHA256((uint8_t*)x.data(),x.size(),h);if(hex(h,32)!=expected)fail("SHA pin "+path);return x;}
static vector<string> tokenize(const string& s){vector<string> v;string w;for(unsigned char c:s){if(c>=65&&c<=90)c=(unsigned char)(c+32);if((c>=97&&c<=122)||(c>=48&&c<=57))w.push_back(char(c));else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
static string truncate_signature(string s,const string& signature){size_t p=s.rfind("\n"+signature);if(p!=string::npos)s.resize(p);return s;}
static void replace_all(string& s,const string& a){size_t p=0;while((p=s.find(a,p))!=string::npos)s.erase(p,a.size());}
struct Hashes{SHA256_CTX inner,outer;Hashes(){uint8_t ip[64],op[64];for(int i=0;i<64;i++){uint8_t k=i<16?NONCE[i]:0;ip[i]=k^0x36;op[i]=k^0x5c;}SHA256_Init(&inner);SHA256_Update(&inner,ip,64);SHA256_Init(&outer);SHA256_Update(&outer,op,64);}
void run(const string& s,uint8_t hmac[32],uint8_t commitment[32])const{SHA256_CTX t=inner;SHA256_Update(&t,s.data(),s.size());uint8_t tmp[32];SHA256_Final(tmp,&t);t=outer;SHA256_Update(&t,tmp,32);SHA256_Final(hmac,&t);SHA256(hmac,16,commitment);}};
static int flag(const string& w){if(w=="sea"||w=="water")return 1;if(w=="night"||w=="watch"||w=="morning")return 2;if(w=="table"||w=="voices"||w=="room")return 4;return 0;}
int main(int argc,char** argv){if(argc!=3)fail("usage ROOT MAX_WORDS");int maxw=atoi(argv[2]);if(maxw<5||maxw>14)fail("max must be 5..14");string root=argv[1];
string notes=pinned(root,"crew/noticeboard-and-desk-notes.txt",NSHA);string m11=pinned(root,"mail/11.eml",M11SHA);string m20=pinned(root,"mail/20.eml",M20SHA);
vector<string> source;{size_t pos=0;while(pos<notes.size()){size_t e=notes.find(char(10),pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);if(line.size()>6&&line[0]==char(78)&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"&&e+1<notes.size()){size_t ne=notes.find(char(10),e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-(e+1));size_t col=body.find(char(58));if(col!=string::npos)body=body.substr(col+1);source.push_back(body);}pos=e+1;}}
for(int n:{11,20}){string s=n==11?m11:m20;auto p=s.find("\n\n");if(p==string::npos)fail("email MIME");s=s.substr(p+2);replace_all(s,"Back before the first boat");replace_all(s,"Leave the light on for the next watch");source.push_back(truncate_signature(s,n==11?"Emily":"Gabriel"));}
if(source.size()!=26)fail("expected 24 notes and 2 emails");
map<string,int> names;vector<string> words;vector<set<int>> edges;
auto intern=[&](const string& w)->int {auto it=names.find(w);if(it!=names.end())return it->second;int i=(int)words.size();names[w]=i;words.push_back(w);edges.emplace_back();return i;};
for(const string& s:source){auto toks=tokenize(s);for(size_t i=0;i+1<toks.size();i++){int a=intern(toks[i]);int b=intern(toks[i+1]);edges[a].insert(b);}}
size_t edgeCount=0;for(const auto& e:edges)edgeCount+=e.size();if(edgeCount!=570||words.size()!=331)fail("original source graph changed");
Hashes hasher;uint8_t mac[32],dig[32];hasher.run("a good watch leaves the room ready for the next pair of hands",mac,dig);if(hex(mac,16)!="bf889359b0303f2b2b2fd96ae841210b")fail("original N02 HMAC positive");
const string planted="the sea the end of the night and the voices at the table";uint8_t plantmac[32],plantdigest[32];hasher.run(planted,plantmac,plantdigest);
vector<vector<int>> adj(words.size());for(size_t i=0;i<words.size();i++)adj[i].assign(edges[i].begin(),edges[i].end());
// Exact finite-state reachability: skip prefixes unable to see all three source motifs.
vector<vector<array<uint8_t,8>>> can(maxw+1,vector<array<uint8_t,8>>(words.size()));
for(int remaining=0;remaining<=maxw;remaining++)for(size_t last=0;last<words.size();last++)for(int mask=0;mask<8;mask++){
 bool possible=mask==7;
 if(remaining>0&&!possible)for(int next:adj[last])if(can[remaining-1][next][mask|flag(words[next])]){possible=true;break;}
 can[remaining][last][mask]=(uint8_t)possible;
}
unsigned long long checked=0,synthetic=0,hits=0;string winning;
#pragma omp parallel for schedule(dynamic,1) reduction(+:checked,synthetic,hits)
for(int start=0;start<(int)words.size();start++){
 if(adj[start].empty())continue;
 string candidate=words[start];
 auto visit=[&](auto&&self,int last,int length,int mask)->void {
  if(!can[maxw-length][last][mask])return;
  if(length>=5&&mask==7){uint8_t m[32],h[32];hasher.run(candidate,m,h);checked++;if(memcmp(h,TARGET,32)==0){hits++;
 #pragma omp critical
 {winning=candidate;}}
 if(memcmp(h,plantdigest,32)==0){synthetic++;}}
  if(length==maxw)return;
  for(int v:adj[last]){size_t n=candidate.size();candidate.push_back(
' ');candidate+=words[v];self(self,v,length+1,mask|flag(words[v]));candidate.resize(n);}
 };
 visit(visit,start,1,flag(words[start]));
}
cout<<"K08_BIGRAM_TRIPLE_SCENE_FINAL source_records="<<source.size()<<" words="<<words.size()<<" edges="<<edgeCount<<" max_words="<<maxw<<" checked="<<checked<<" planted="<<synthetic<<" original_hits="<<hits<<"\n";
if(hits)cout<<"ORIGINAL_K08_MATCH "<<winning<<"\n";
if(synthetic!=1)fail("planted source complete phrase not recognized exactly once");
if(maxw==14&&checked!=234309631ULL)fail("expected full path count did not match independent Python DP");
return hits?9:0;
}
