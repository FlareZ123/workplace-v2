// H-17 K08 source-bigram, three full-clause ordered witnesses, lengths 16..25.
// Purpose: test bounded complete authoring/copy model, preserve immutable originals.
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;
static const char* NSHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb";
static const char* M11SHA="f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29";
static const char* M20SHA="e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71";
static const unsigned char NONCE[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned long long EXPECTED[]={66,325,1958,11784,64305,349454,1826504,9489982,48324704,243053327};
static const char* PLANTED[]={
 "a593f2a54c2435a9a362928561e4f9bb633bc89827ae09f5f1a6c5787a2af6dc",
 "e8992b328c7970069f2da15d2adf04c9afcf99db1bc2b4b237811b8f62049a88",
 "cdad19124571b7e33a4a143f631c6899905c15848cb08d85da6fa4371d307a64",
 "0deb1f5c9a3c75304d5609b9a72c9cf675b7d56be563b635e9cf7403a446b66b",
 "d0e6c973e4e6d82e031c19e74943d0cb3597f24c59df838ce8ff2dc71a3e5458",
 "d51bc4ab957e0c45bbd847b49f2b2361462509247dbe53d44596e3f3ee38a381",
 "e8b551a98e14e41d7cd8788aceec7ac91fa747ca4f6ed66e000302a6c0cb236f",
 "f2f54a8174eb1e3dd03018f80f6d9eee5ec9a5e6675bdfa406521f4dbc58f222",
 "3839c8d559fbdd23a3ae17e70b51cd2d1d0bb4cc340e835c941484fd60da3543",
 "1dd8e0bbe5b2a8b8710b27fe57046bce7d44a2caa1bea2ce2914a394196839b0"};
void bad(const string& m){cerr<<"FAIL "<<m<<"\n";exit(2);}
string hex(const unsigned char* p,int n){char b[3];string s;for(int i=0;i<n;i++){snprintf(b,3,"%02x",p[i]);s+=b;}return s;}
string read(const string&p){ifstream f(p,ios::binary);if(!f)bad("missing "+p);return string(istreambuf_iterator<char>(f),istreambuf_iterator<char>());}
string pinned(const string&root,const string&path,const char*sha){string x=read(root+"/evidence/"+path);unsigned char h[32];SHA256((const unsigned char*)x.data(),x.size(),h);if(hex(h,32)!=sha)bad("source hash "+path);return x;}
vector<string> tokenize(const string& s){vector<string> v;string w;for(unsigned char c:s){if(c>='A'&&c<='Z')c+=32;if((c>='a'&&c<='z')||(c>='0'&&c<='9'))w.push_back(char(c));else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
void replaceall(string& s,const string& t){size_t i=0;while((i=s.find(t,i))!=string::npos)s.erase(i,t.size());}
string truncsig(string s,const string&sig){size_t p=s.rfind("\n"+sig);if(p!=string::npos)s.resize(p);return s;}
struct Hmac{SHA256_CTX inner,outer;Hmac(){unsigned char a[64],b[64];for(int i=0;i<64;i++){unsigned char k=i<16?NONCE[i]:0;a[i]=k^0x36;b[i]=k^0x5c;}SHA256_Init(&inner);SHA256_Update(&inner,a,64);SHA256_Init(&outer);SHA256_Update(&outer,b,64);}void digest(const SHA256_CTX&ctx,unsigned char out[32])const{unsigned char x[32],h[32];SHA256_CTX t=ctx;SHA256_Final(x,&t);t=outer;SHA256_Update(&t,x,32);SHA256_Final(h,&t);SHA256(h,16,out);}};
int step(const vector<string>&word,int stage,int progress,const string&w){
 if(stage==0)return (w=="sea"||w=="water")?8:0;
 if(stage==3)return 24;
 const vector<string>&pat=word;
 if(progress>=(int)pat.size())return stage*8;
 vector<string> ss(pat.begin(),pat.begin()+progress);ss.push_back(w);
 for(int k=min((int)pat.size(),(int)ss.size());k>=1;k--){
   bool yes=true;for(int i=0;i<k;i++)if(ss[ss.size()-k+i]!=pat[i]){yes=false;break;}
   if(yes)return k==(int)pat.size()?((stage+1)*8):(stage*8+k);
 }
 return stage*8;
}
int main(int argc,char**argv){if(argc!=4)bad("args: ROOT MIN_LENGTH MAX_LENGTH");string root=argv[1];int lo=atoi(argv[2]),hi=atoi(argv[3]);if(lo<16||hi>25||lo>hi)bad("length bounds must lie in [16,25]");
 string notes=pinned(root,"crew/noticeboard-and-desk-notes.txt",NSHA),m11=pinned(root,"mail/11.eml",M11SHA),m20=pinned(root,"mail/20.eml",M20SHA);
 vector<string> source;{size_t pos=0;while(pos<notes.size()){size_t e=notes.find('\n',pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);if(line.size()>6&&line[0]=='N'&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"&&e+1<notes.size()){size_t ne=notes.find('\n',e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-e-1);size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);source.push_back(body);}pos=e+1;}}
 for(int n:{11,20}){string s=n==11?m11:m20;size_t p=s.find("\n\n");if(p==string::npos)bad("mime");s=s.substr(p+2);replaceall(s,"Back before the first boat");replaceall(s,"Leave the light on for the next watch");source.push_back(truncsig(s,n==11?"Emily":"Gabriel"));}
 if(source.size()!=26)bad("source count");map<string,int> idx;vector<string> words;vector<set<int>> edge;auto intern=[&](const string&w)->int{auto it=idx.find(w);if(it!=idx.end())return it->second;int id=words.size();idx[w]=id;words.push_back(w);edge.emplace_back();return id;};for(auto&s:source){auto toks=tokenize(s);for(size_t i=0;i+1<toks.size();i++){int a=intern(toks[i]),b=intern(toks[i+1]);edge[a].insert(b);}}
 size_t ne=0;for(auto&e:edge)ne+=e.size();if(words.size()!=331||ne!=570||words[22]!="somebody")bad("graph mismatch");vector<vector<int>> adj(331);for(int i=0;i<331;i++)adj[i].assign(edge[i].begin(),edge[i].end());
 const vector<string> a={"at","the","end","of","the","night"},b={"voices","at","the","table"};
 int transition[32][331];for(int st=0;st<32;st++)for(int v=0;v<331;v++)transition[st][v]=(st<8?step(a,0,0,words[v]):st<16?step(a,1,st-8,words[v]):st<24?step(b,2,st-16,words[v]):24);
 Hmac hmac;unsigned long long total=0;vector<array<unsigned char,32>> plants(10);
 for(int n=0;n<10;n++)for(int i=0;i<32;i++){unsigned int b=0;sscanf(PLANTED[n]+2*i,"%2x",&b);plants[n][i]=(unsigned char)b;}
 for(int len=lo;len<=hi;len++){
  vector<array<array<unsigned char,32>,331>> can(len);for(int u=0;u<331;u++)can[0][u][24]=1;
  for(int rem=1;rem<len;rem++)for(int u=0;u<331;u++)for(int st=0;st<32;st++){
   for(int v:adj[u]){int ns=transition[st][v];if(can[rem-1][v][ns]){can[rem][u][st]=1;break;}}
  }
  unsigned long long checked=0,synthetic=0,hits=0;string winner;
  #pragma omp parallel for schedule(dynamic,1) reduction(+:checked,synthetic,hits)
  for(int u=0;u<331;u++){
   int st=transition[0][u];if(!can[len-1][u][st])continue;string phrase=words[u];SHA256_CTX initial=hmac.inner;SHA256_Update(&initial,phrase.data(),phrase.size());
   auto walk=[&](auto&&self,int node,int depth,int state,const SHA256_CTX& ctx)->void{
    if(depth==len){if(state==24){unsigned char h[32];hmac.digest(ctx,h);checked++;if(memcmp(h,plants[len-16].data(),32)==0)synthetic++;if(memcmp(h,TARGET,32)==0){hits++;
    #pragma omp critical
     {winner=phrase;}
    }}return;}
    for(int v:adj[node]){int ns=transition[state][v];if(!can[len-depth-1][v][ns])continue;size_t prev=phrase.size();phrase.push_back(' ');phrase+=words[v];SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[v].data(),words[v].size());self(self,v,depth+1,ns,next);phrase.resize(prev);}
   };walk(walk,u,1,st,initial);
  }
  cout<<"K08_ANCHOR_CHAIN length="<<len<<" checked="<<checked<<" expected="<<EXPECTED[len-16]<<" synthetic="<<synthetic<<" original_hits="<<hits<<"\n"<<flush;
  if(checked!=EXPECTED[len-16]||synthetic!=1)bad("count or planted mismatch");if(hits){cout<<"ORIGINAL_K08_PHRASE "<<winner<<"\n";return 9;}total+=checked;
 }
 cout<<"K08_ANCHOR_CHAIN_COMPLETE total="<<total<<" original_hits=0\n";return 0;
}
