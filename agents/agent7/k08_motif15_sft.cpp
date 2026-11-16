// K08 source bigram graph, complete 15-word/mask=7 path search.
// Inputs: exact 3 pinned source texts. No source, verifier, or commitment edits.
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cstring>
using namespace std;
static const char* NSHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb";
static const char* M11SHA="f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29";
static const char* M20SHA="e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71";
static const unsigned char NONCE[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char PLANT[32]={0x6c,0xc1,0x6c,0x3e,0x14,0x1e,0xa5,0x6a,0x57,0x1b,0x68,0xfd,0x2b,0x19,0x57,0x12,0x47,0x0f,0xaa,0xb0,0xda,0xe4,0x20,0xab,0x59,0x32,0x51,0xc5,0x67,0x61,0xfa,0xa7};
void bad(const string& m){cerr<<"FAIL "<<m<<"\n";exit(2);}
string hex(const unsigned char* p,int n){char b[3];string s;for(int i=0;i<n;i++){snprintf(b,3,"%02x",p[i]);s+=b;}return s;}
string read(const string&p){ifstream f(p,ios::binary);if(!f)bad("missing "+p);return string(istreambuf_iterator<char>(f),istreambuf_iterator<char>());}
string pinned(const string&root,const string&path,const char*sha){string x=read(root+"/evidence/"+path);unsigned char h[32];SHA256((const unsigned char*)x.data(),x.size(),h);if(hex(h,32)!=sha)bad("source hash "+path);return x;}
vector<string> tokenize(const string& s){vector<string> v;string w;for(unsigned char c:s){if(c>='A'&&c<='Z')c+=32;if((c>='a'&&c<='z')||(c>='0'&&c<='9'))w.push_back(char(c));else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
void replaceall(string& s,const string& t){size_t i=0;while((i=s.find(t,i))!=string::npos)s.erase(i,t.size());}
string truncsig(string s,const string&sig){size_t p=s.rfind("\n"+sig);if(p!=string::npos)s.resize(p);return s;}
int motif(const string&w){return (w=="sea"||w=="water"?1:0)|(w=="night"||w=="watch"||w=="morning"?2:0)|(w=="table"||w=="voices"||w=="room"?4:0);}
struct Hmac{SHA256_CTX inner,outer;Hmac(){unsigned char a[64],b[64];for(int i=0;i<64;i++){unsigned char k=i<16?NONCE[i]:0;a[i]=k^0x36;b[i]=k^0x5c;}SHA256_Init(&inner);SHA256_Update(&inner,a,64);SHA256_Init(&outer);SHA256_Update(&outer,b,64);}void digest(const SHA256_CTX&ctx,unsigned char out[32])const{unsigned char x[32],h[32];SHA256_CTX t=ctx;SHA256_Final(x,&t);t=outer;SHA256_Update(&t,x,32);SHA256_Final(h,&t);SHA256(h,16,out);}};
int main(int argc,char**argv){if(argc!=5)bad("args: ROOT LENGTH START_BEGIN START_END");string root=argv[1];int len=atoi(argv[2]),begin=atoi(argv[3]),end=atoi(argv[4]);if(len!=15&&len!=16)bad("only length15/16 source motivated");if(begin<0||end>331||begin>=end)bad("range");
string notes=pinned(root,"crew/noticeboard-and-desk-notes.txt",NSHA);string m11=pinned(root,"mail/11.eml",M11SHA);string m20=pinned(root,"mail/20.eml",M20SHA);
vector<string> source;{size_t pos=0;while(pos<notes.size()){size_t e=notes.find('\n',pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);if(line.size()>6&&line[0]=='N'&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"&&e+1<notes.size()){size_t ne=notes.find('\n',e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-e-1);size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);source.push_back(body);}pos=e+1;}}
for(int n:{11,20}){string s=n==11?m11:m20;size_t p=s.find("\n\n");if(p==string::npos)bad("mime");s=s.substr(p+2);replaceall(s,"Back before the first boat");replaceall(s,"Leave the light on for the next watch");source.push_back(truncsig(s,n==11?"Emily":"Gabriel"));}
if(source.size()!=26)bad("record count");map<string,int> idx;vector<string> words;vector<set<int>> edge;auto intern=[&](const string&w)->int{auto it=idx.find(w);if(it!=idx.end())return it->second;int id=words.size();idx[w]=id;words.push_back(w);edge.emplace_back();return id;};for(auto&s:source){auto toks=tokenize(s);for(size_t i=0;i+1<toks.size();i++){int a=intern(toks[i]),b=intern(toks[i+1]);edge[a].insert(b);}}
size_t ne=0;for(auto&e:edge)ne+=e.size();if(words.size()!=331||ne!=570||words[22]!="somebody")bad("graph mismatch");vector<vector<int>> adj(331);vector<int> flag(331);for(int i=0;i<331;i++){adj[i].assign(edge[i].begin(),edge[i].end());flag[i]=motif(words[i]);}Hmac hmac;
// Independent Python-derived positive lives in graph at length15/mask7.
const string planted="the sea the sea the sea the sea the sea the room for the night";SHA256_CTX c=hmac.inner;SHA256_Update(&c,planted.data(),planted.size());unsigned char pd[32];hmac.digest(c,pd);if(memcmp(pd,PLANT,32))bad("planted HMAC/SHA mismatch");
// Exact suffix feasibility oracle: prune prefixes that cannot reach all 3 motifs.
vector<vector<array<unsigned char,8>>> can(len,vector<array<unsigned char,8>>(331));
for(int u=0;u<331;u++)can[0][u][7]=1;
for(int rem=1;rem<len;rem++)for(int u=0;u<331;u++)for(int m=0;m<8;m++)
 for(int v:adj[u])if(can[rem-1][v][m|flag[v]]){can[rem][u][m]=1;break;}
unsigned long long checked=0,found=0,synthetic=0;string winner;
#pragma omp parallel for schedule(dynamic,1) reduction(+:checked,found,synthetic)
for(int start=begin;start<end;start++){if(!can[len-1][start][flag[start]])continue;string phrase=words[start];SHA256_CTX initial=hmac.inner;SHA256_Update(&initial,phrase.data(),phrase.size());
  auto walk=[&](auto&&self,int u,int depth,int mask,const SHA256_CTX&inner)->void{
    if(depth==len){if(mask==7){unsigned char d[32];hmac.digest(inner,d);checked++;if(memcmp(d,PLANT,32)==0)synthetic++;if(memcmp(d,TARGET,32)==0){found++;
#pragma omp critical
    {winner=phrase;}}}return;}
    for(int v:adj[u]){if(!can[len-depth-1][v][mask|flag[v]])continue;size_t old=phrase.size();phrase.push_back(' ');phrase+=words[v];SHA256_CTX next=inner;SHA256_Update(&next," ",1);SHA256_Update(&next,words[v].data(),words[v].size());self(self,v,depth+1,mask|flag[v],next);phrase.resize(old);}
  };walk(walk,start,1,flag[start],initial);
}
cout<<"K08_MOTIF7 length="<<len<<" range=["<<begin<<","<<end<<") checked="<<checked<<" synthetic="<<synthetic<<" original_hits="<<found<<"\n";if(found)cout<<"ORIGINAL_K08_PHRASE "<<winner<<"\n";if(begin==0&&end==331){if(len==15&&checked!=1018097847ULL)bad("length15 count");if(len==16&&checked!=5322526095ULL)bad("length16 count");}if(len==15 && begin<=0 && end>0 && synthetic!=1)bad("planted positive absent");if(len==16&&synthetic!=0)bad("wrong length positive");if(found)return 9;return 0;}
