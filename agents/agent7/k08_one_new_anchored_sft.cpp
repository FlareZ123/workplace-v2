// H-17 K08 source-bigram with one new editorial transition, anchored clauses, lengths 14..21.
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
static const unsigned long long EXPECTED[]={212,2256,14974,143947,892964,6036241,37264964,220564218};
static const char* PLANTED[]={
 "0000000000000000000000000000000000000000000000000000000000000000",
 "0000000000000000000000000000000000000000000000000000000000000000",
 "f633e8952f9736f33cbfeabbb6c54748f0357c957edcf85ee32ae6f72e9a8c06",
 "feed1563f1914f984402e3d96ebbf1b5102cae4f65b3c8cdc169aa4b26a0e2c8",
 "67075759982cbb7cad6da45d0069f0501caba07e7d64e87fc7f64de597bfcfb1",
 "8b81ec072d116766ab4df09276f9c943140663a1d8edf5461f96162ee58d1838",
 "ba27b55b8a98fecad1aa62474747e648d7a1ccb623ba7763e9862f075a31d505",
 "60eafd767eca63328e5c1e4a229f5cacf465e004437c849e2edef0b468bc7965"};
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
int main(int argc,char**argv){if(argc!=4)bad("args: ROOT MIN_LENGTH MAX_LENGTH");string root=argv[1];int lo=atoi(argv[2]),hi=atoi(argv[3]);if(lo<14||hi>21||lo>hi)bad("length bounds must lie in [14,21]");
 string notes=pinned(root,"crew/noticeboard-and-desk-notes.txt",NSHA),m11=pinned(root,"mail/11.eml",M11SHA),m20=pinned(root,"mail/20.eml",M20SHA);
 vector<string> source;{size_t pos=0;while(pos<notes.size()){size_t e=notes.find('\n',pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);if(line.size()>6&&line[0]=='N'&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"&&e+1<notes.size()){size_t ne=notes.find('\n',e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-e-1);size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);source.push_back(body);}pos=e+1;}}
 for(int n:{11,20}){string s=n==11?m11:m20;size_t p=s.find("\n\n");if(p==string::npos)bad("mime");s=s.substr(p+2);replaceall(s,"Back before the first boat");replaceall(s,"Leave the light on for the next watch");source.push_back(truncsig(s,n==11?"Emily":"Gabriel"));}
 if(source.size()!=26)bad("source count");map<string,int> idx;vector<string> words;vector<set<int>> edge;auto intern=[&](const string&w)->int{auto it=idx.find(w);if(it!=idx.end())return it->second;int id=words.size();idx[w]=id;words.push_back(w);edge.emplace_back();return id;};for(auto&s:source){auto toks=tokenize(s);for(size_t i=0;i+1<toks.size();i++){int a=intern(toks[i]),b=intern(toks[i+1]);edge[a].insert(b);}}
 size_t ne=0;for(auto&e:edge)ne+=e.size();if(words.size()!=331||ne!=570||words[22]!="somebody")bad("graph mismatch");vector<vector<int>> adj(331);for(int i=0;i<331;i++)adj[i].assign(edge[i].begin(),edge[i].end());
 const vector<string> a={"at","the","end","of","the","night"},b={"voices","at","the","table"};
 int transition[32][331];for(int st=0;st<32;st++)for(int v=0;v<331;v++)transition[st][v]=(st<8?step(a,0,0,words[v]):st<16?step(a,1,st-8,words[v]):st<24?step(b,2,st-16,words[v]):24);
 Hmac hmac;unsigned long long total=0;vector<array<unsigned char,32>> plants(8);
 for(int n=0;n<8;n++)for(int i=0;i<32;i++){unsigned int b=0;sscanf(PLANTED[n]+2*i,"%2x",&b);plants[n][i]=(unsigned char)b;}
 for(int len=lo;len<=hi;len++){
  vector<array<array<array<unsigned char,2>,32>,331>> can(len);for(int u=0;u<331;u++)can[0][u][24][1]=1;
  for(int rem=1;rem<len;rem++)for(int u=0;u<331;u++)for(int st=0;st<32;st++)for(int used=0;used<2;used++){
   if(used){for(int v:adj[u]){int ns=transition[st][v];if(can[rem-1][v][ns][1]){can[rem][u][st][1]=1;break;}}}
   else{for(int v=0;v<331;v++){
    int ns=transition[st][v],nu=!edge[u].count(v);
    if(can[rem-1][v][ns][nu]){can[rem][u][st][0]=1;break;}
   }}
  }
  unsigned long long checked=0,synthetic=0,hits=0;string winner;
  #pragma omp parallel for schedule(dynamic,1) reduction(+:checked,synthetic,hits)
  for(int u=0;u<331;u++){
   int st=transition[0][u];if(!can[len-1][u][st][0])continue;string phrase=words[u];SHA256_CTX initial=hmac.inner;SHA256_Update(&initial,phrase.data(),phrase.size());
   auto walk=[&](auto&&self,int node,int depth,int state,int used,const SHA256_CTX&ctx)->void{
    if(depth==len){if(state==24&&used==1){unsigned char h[32];hmac.digest(ctx,h);checked++;if(memcmp(h,plants[len-14].data(),32)==0)synthetic++;if(memcmp(h,TARGET,32)==0){hits++;
    #pragma omp critical
     {winner=phrase;}
    }}return;}
    auto visit=[&](int v){
     int ns=transition[state][v],nu=used||!edge[node].count(v);
     if(!can[len-depth-1][v][ns][nu])return;
     size_t prev=phrase.size();phrase.push_back(' ');phrase+=words[v];SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[v].data(),words[v].size());self(self,v,depth+1,ns,nu,next);phrase.resize(prev);
    };
    if(used){for(int v:adj[node])visit(v);}else{for(int v=0;v<331;v++)visit(v);}
   };walk(walk,u,1,st,0,initial);
  }
  cout<<"K08_ONE_NEW_ANCHOR length="<<len<<" checked="<<checked<<" expected="<<EXPECTED[len-14]<<" synthetic="<<synthetic<<" original_hits="<<hits<<"\n"<<flush;
  if(checked!=EXPECTED[len-14]||(len>=16?synthetic!=1:synthetic!=0))bad("count or planted mismatch");if(hits){cout<<"ORIGINAL_K08_PHRASE "<<winner<<"\n";return 9;}total+=checked;
 }
 cout<<"K08_ONE_NEW_ANCHOR_COMPLETE total="<<total<<" original_hits=0\n";return 0;
}
