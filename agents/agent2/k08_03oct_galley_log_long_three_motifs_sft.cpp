// H17 original Oct3 galley log longer 12..14word source-bigram paths with all three
// literal N20 scene motifs; require a newly observed 3Oct galley directed edge.
// Exact source-only reachability controls DFS without truncating eligible paths.
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
static const char* M02SHA="a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11";
static const char* M12SHA="4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd";
static const char* LOGSHA="23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46";
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
int main(int argc,char** argv){if(argc<3||argc>6)fail("usage ROOT MAX_WORDS [MIN_WORDS [SHARD [SHARDS]]]");int maxw=atoi(argv[2]);int minw=argc>=4?atoi(argv[3]):2;int shard=argc>=5?atoi(argv[4]):0;int nshards=argc>=6?atoi(argv[5]):1;if(maxw<12||maxw>14||minw<12||minw>maxw||nshards<1||shard<0||shard>=nshards)fail("invalid 12..14 length or shard");string root=argv[1];
string notes=pinned(root,"crew/noticeboard-and-desk-notes.txt",NSHA);string m11=pinned(root,"mail/11.eml",M11SHA);string m20=pinned(root,"mail/20.eml",M20SHA);string m02=pinned(root,"mail/02.eml",M02SHA);string m12=pinned(root,"mail/12.eml",M12SHA);string galley=pinned(root,"crew/galley-and-stores.log",LOGSHA);
vector<string> source;{size_t pos=0;while(pos<notes.size()){size_t e=notes.find(char(10),pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);if(line.size()>6&&line[0]==char(78)&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"&&e+1<notes.size()){size_t ne=notes.find(char(10),e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-(e+1));size_t col=body.find(char(58));if(col!=string::npos)body=body.substr(col+1);source.push_back(body);}pos=e+1;}}
for(int n:{11,20}){string s=n==11?m11:m20;auto p=s.find("\n\n");if(p==string::npos)fail("email MIME");s=s.substr(p+2);replace_all(s,"Back before the first boat");replace_all(s,"Leave the light on for the next watch");source.push_back(truncate_signature(s,n==11?"Emily":"Gabriel"));}
if(source.size()!=26)fail("expected 24 notes and 2 emails");
map<string,int> names;vector<string> words;vector<set<int>> edges;
auto intern=[&](const string& w)->int {auto it=names.find(w);if(it!=names.end())return it->second;int i=(int)words.size();names[w]=i;words.push_back(w);edges.emplace_back();return i;};
for(const string& s:source){auto toks=tokenize(s);for(size_t i=0;i+1<toks.size();i++){int a=intern(toks[i]);int b=intern(toks[i+1]);edges[a].insert(b);}}
size_t oldCount=0;set<pair<int,int>> oldPairs;
for(size_t i=0;i<edges.size();i++)for(int j:edges[i]){oldPairs.insert({(int)i,j});oldCount++;}
if(oldCount!=570||words.size()!=331||source.size()!=26)fail("original source graph changed");
for(auto entry:vector<pair<string,string>>{{m02,"Emily"},{m12,"Zoey"}}){
 string body=entry.first;auto p=body.find("\n\n");if(p==string::npos)fail("extra email body");
 source.push_back(truncate_signature(body.substr(p+2),entry.second));
}
for(size_t k=26;k<source.size();k++){auto toks=tokenize(source[k]);for(size_t i=0;i+1<toks.size();i++){
 int a=intern(toks[i]);int b=intern(toks[i+1]);edges[a].insert(b);
}}
size_t edgeCount=0,novelEdges=0;for(size_t i=0;i<edges.size();i++)for(int j:edges[i]){
 edgeCount++;if(!oldPairs.count({(int)i,j}))novelEdges++;
}
if(source.size()!=28||words.size()!=398||edgeCount!=725||novelEdges!=155)fail("28-record 398/725 graph changed");
set<pair<int,int>> prior28;for(size_t i=0;i<edges.size();i++)for(int j:edges[i])prior28.insert({(int)i,j});
size_t logpos=galley.find("03 Oct: ");if(logpos==string::npos)fail("original galley date");
size_t logend=galley.find('\n',logpos);if(logend==string::npos)logend=galley.size();
string logline=galley.substr(logpos+8,logend-(logpos+8));
if(logline!="night galley left tea, soup and clean mugs for incoming watch")fail("original galley line changed");
source.push_back(logline);
auto logwords=tokenize(logline);
for(size_t i=0;i+1<logwords.size();i++){int a=intern(logwords[i]);int b=intern(logwords[i+1]);edges[a].insert(b);}
edgeCount=0;novelEdges=0;
for(size_t i=0;i<edges.size();i++)for(int j:edges[i]){edgeCount++;if(!prior28.count({(int)i,j}))novelEdges++;}
if(source.size()!=29||words.size()!=400||edgeCount!=734||novelEdges!=9)fail("galley log 29-record 400/734/9 graph");
Hashes hasher;uint8_t mac[32],dig[32];hasher.run("a good watch leaves the room ready for the next pair of hands",mac,dig);if(hex(mac,16)!="bf889359b0303f2b2b2fd96ae841210b")fail("original N02 HMAC positive");
const string planted="the appliance label the desk the sea the room for incoming watch";uint8_t plantmac[32],plantdigest[32];hasher.run(planted,plantmac,plantdigest);
vector<vector<pair<int,bool>>> adj(words.size());
for(size_t i=0;i<words.size();i++)for(int j:edges[i])adj[i].push_back({j,!prior28.count({(int)i,j})});
// Exact source-graph future reachability, including all three theme groups and a new edge.
vector<vector<array<array<unsigned char,2>,8>>> can(maxw+1,vector<array<array<unsigned char,2>,8>>(words.size()));
for(int rem=0;rem<=maxw;rem++)for(size_t u=0;u<words.size();u++)for(int mask=0;mask<8;mask++)for(int novel=0;novel<2;novel++){
 bool possible=(mask==7&&novel);
 if(rem>0&&!possible)for(auto [v,newEdge]:adj[u])if(can[rem-1][v][mask|flag(words[v])][novel||newEdge]){possible=true;break;}
 can[rem][u][mask][novel]=possible;
}
unsigned long long checked=0,synthetic=0,hits=0;string winning;
#pragma omp parallel for schedule(dynamic,1) reduction(+:checked,synthetic,hits)
for(int start=0;start<(int)words.size();start++){
 if(start % nshards != shard)continue;
 if(adj[start].empty())continue;
 string candidate=words[start];
 auto visit=[&](auto&&self,int last,int length,int mask,bool hasNovel)->void {
  if(length>=minw && hasNovel&&mask==7){uint8_t m[32],h[32];hasher.run(candidate,m,h);checked++;if(memcmp(h,TARGET,32)==0){hits++;
 #pragma omp critical
 {winning=candidate;}}
 if(memcmp(h,plantdigest,32)==0){synthetic++;}}
  if(!can[maxw-length][last][mask][hasNovel])return;
  if(length==maxw)return;
  for(auto [v,isNovel]:adj[last]){size_t n=candidate.size();candidate.push_back(
' ');candidate+=words[v];self(self,v,length+1,mask|flag(words[v]),hasNovel||isNovel);candidate.resize(n);}
 };
 visit(visit,start,1,flag(words[start]),false);
}
cout<<"K08_03OCT_GALLEY_LOG_LONG3 source_records="<<source.size()<<" words="<<words.size()<<" edges="<<edgeCount<<" novel_edges="<<novelEdges<<" max_words="<<maxw<<" min_words="<<minw<<" shard="<<shard<<" nshards="<<nshards<<" checked="<<checked<<" planted="<<synthetic<<" original_hits="<<hits<<"\n";
if(hits)cout<<"ORIGINAL_K08_MATCH "<<winning<<"\n";
if(synthetic>1)fail("duplicate planted source caption");
if(nshards==1&&minw<=12&&maxw>=12&&synthetic!=1)fail("planted log 12word caption not found");
if(nshards==1&&maxw==14&&minw==12&&checked!=47946864ULL)fail("12..14 new galley-only total");
return hits?9:0;
}
