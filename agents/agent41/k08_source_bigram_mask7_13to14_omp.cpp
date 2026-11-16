// H-17 K08: all-order source-bigram walks, lengths 13 and 14, all three literal motifs.
// Build: g++ -O3 -std=c++17 -fopenmp k08_source_bigram_mask7_13to14_omp.cpp -lcrypto -o k08_source_bigram_mask7_13to14_omp
// Run:   OMP_NUM_THREADS=5 ./k08_source_bigram_mask7_13to14_omp /path/to/evidence 13
//        OMP_NUM_THREADS=5 ./k08_source_bigram_mask7_13to14_omp /path/to/evidence 14
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
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
#include <omp.h>
using namespace std;
static const unsigned char KEY[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static void fail(const string&s){cerr<<"FAIL "<<s<<"\n";exit(2);}
static string readfile(const string&p){ifstream f(p,ios::binary);if(!f)fail("missing "+p);return string((istreambuf_iterator<char>(f)),{});}
static string hex(const unsigned char*p,int n){char b[3];string s;for(int i=0;i<n;i++){snprintf(b,3,"%02x",p[i]);s+=b;}return s;}
static string pinned(const string&p,const char*sha){string x=readfile(p);unsigned char h[32];SHA256((const unsigned char*)x.data(),x.size(),h);if(hex(h,32)!=sha)fail("source hash "+p);return x;}
static vector<string> tokenize(const string&s){vector<string>v;string w;for(unsigned char c:s){if(c>='A'&&c<='Z')c+=32;if((c>='a'&&c<='z')||(c>='0'&&c<='9'))w.push_back((char)c);else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
static void replaceall(string&s,const string&t){size_t i=0;while((i=s.find(t,i))!=string::npos)s.erase(i,t.size());}
static int motif(const string&w){return (w=="sea"||w=="water"?1:0)|(w=="night"||w=="watch"||w=="morning"?2:0)|(w=="table"||w=="voices"||w=="room"?4:0);}
struct Hasher{
  SHA256_CTX inner,outer;
  Hasher(){unsigned char a[64],b[64];for(int i=0;i<64;i++){unsigned char k=i<16?KEY[i]:0;a[i]=k^0x36;b[i]=k^0x5c;}SHA256_Init(&inner);SHA256_Update(&inner,a,64);SHA256_Init(&outer);SHA256_Update(&outer,b,64);}
  void digest(const SHA256_CTX&ctx,unsigned char out[32],unsigned char tag16[16])const{unsigned char x[32],h[32];SHA256_CTX t=ctx;SHA256_Final(x,&t);t=outer;SHA256_Update(&t,x,32);SHA256_Final(h,&t);memcpy(tag16,h,16);SHA256(tag16,16,out);}
  void run(const string&s,unsigned char out[32],unsigned char tag16[16])const{SHA256_CTX t=inner;SHA256_Update(&t,s.data(),s.size());digest(t,out,tag16);}
};
struct Stats{unsigned long long checked=0,synthetic=0,found=0,nodes=0;string winner;};
int main(int argc,char**argv){
  if(argc!=3)fail("args: EVIDENCE_ROOT LENGTH(13|14)");
  string root=argv[1];int len=atoi(argv[2]);if(len!=13&&len!=14)fail("only lengths 13 or 14");
  string notes=pinned(root+"/crew/noticeboard-and-desk-notes.txt","13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
  string m11=pinned(root+"/mail/11.eml","f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29");
  string m20=pinned(root+"/mail/20.eml","e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71");
  string route=pinned(root+"/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
  string acceptance=pinned(root+"/../acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
  if(route.find("5F933DA6A1BD03C32DA5CBC25344F497")==string::npos||acceptance.find("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")==string::npos)fail("route/target mismatch");
  vector<string> sources;size_t pos=0;
  while(pos<notes.size()){size_t e=notes.find('\n',pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);
    if(line.size()>6&&line[0]=='N'&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"){size_t ne=notes.find('\n',e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-e-1);size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);sources.push_back(body);}pos=e+1;}
  auto mailbody=[&](string s,const string&sig){size_t p=s.find("\n\n");if(p==string::npos)fail("mail MIME");s=s.substr(p+2);replaceall(s,"Back before the first boat");replaceall(s,"Leave the light on for the next watch");p=s.rfind("\n"+sig);if(p!=string::npos)s.resize(p);return s;};
  sources.push_back(mailbody(m11,"Emily"));sources.push_back(mailbody(m20,"Gabriel"));if(sources.size()!=26)fail("record count");
  map<string,int> ids;vector<string> words;vector<set<int>> edge;
  auto intern=[&](const string&w){auto it=ids.find(w);if(it!=ids.end())return it->second;int id=(int)words.size();ids[w]=id;words.push_back(w);edge.emplace_back();return id;};
  for(auto&s:sources){auto t=tokenize(s);for(size_t i=0;i+1<t.size();i++){int a=intern(t[i]),b=intern(t[i+1]);edge[a].insert(b);}}
  size_t ne=0;for(auto&e:edge)ne+=e.size();if(words.size()!=331||ne!=570)fail("graph mismatch");
  vector<vector<int>>adj(331);vector<int>flag(331);for(int i=0;i<331;i++){adj[i].assign(edge[i].begin(),edge[i].end());flag[i]=motif(words[i]);}
  // Exact suffix feasibility for any ordering of all three motif classes.
  vector<vector<array<unsigned char,8>>> can(len,vector<array<unsigned char,8>>(331));
  for(int u=0;u<331;u++)for(int mask=0;mask<8;mask++)can[0][u][mask]=(mask==7);
  for(int rem=1;rem<len;rem++)for(int u=0;u<331;u++)for(int mask=0;mask<8;mask++)
    for(int v:adj[u])if(can[rem-1][v][mask|flag[v]]){can[rem][u][mask]=1;break;}
  Hasher h;const string n02="a good watch leaves the room ready for the next pair of hands";
  unsigned char n02d[32],n02tag[16];h.run(n02,n02d,n02tag);
  if(hex(n02tag,16)!="bf889359b0303f2b2b2fd96ae841210b")fail("N02 control");
  const string synthetic=len==13?"06 is late crew notes with the sea the night and the table":"06 is late crew notes with it is the sea the night the table";
  unsigned char synth[32],synthTag[16];h.run(synthetic,synth,synthTag);
  vector<Stats> stats(omp_get_max_threads());
  #pragma omp parallel
  {int tid=omp_get_thread_num();Stats&st=stats[tid];Hasher th;
    #pragma omp for schedule(dynamic,1)
    for(int start=0;start<331;start++){int mask=flag[start];if(!can[len-1][start][mask])continue;string phrase=words[start];SHA256_CTX initial=th.inner;SHA256_Update(&initial,phrase.data(),phrase.size());
      auto walk=[&](auto&&self,int u,int depth,int curmask,const SHA256_CTX&inner)->void{
        st.nodes++;
        if(depth==len){if(curmask==7){unsigned char d[32],tag[16];th.digest(inner,d,tag);st.checked++;if(memcmp(d,synth,32)==0)st.synthetic++;if(memcmp(d,TARGET,32)==0){st.found++;st.winner=phrase;}}return;}
        for(int v:adj[u]){int nm=curmask|flag[v];if(!can[len-depth-1][v][nm])continue;size_t old=phrase.size();phrase.push_back(' ');phrase+=words[v];SHA256_CTX next=inner;SHA256_Update(&next," ",1);SHA256_Update(&next,words[v].data(),words[v].size());self(self,v,depth+1,nm,next);phrase.resize(old);}
      };
      walk(walk,start,1,mask,initial);
    }
  }
  unsigned long long checked=0,synthetic_hits=0,found=0,nodes=0;string winner;
  for(auto&s:stats){checked+=s.checked;synthetic_hits+=s.synthetic;found+=s.found;nodes+=s.nodes;if(!s.winner.empty())winner=s.winner;}
  unsigned long long expected=len==13?35053300ULL:191661048ULL;
  cout<<"length="<<len<<" graph=331/570 checked="<<checked<<" nodes="<<nodes<<" threads="<<omp_get_max_threads()<<" synthetic_hits="<<synthetic_hits<<" original_hits="<<found<<"\n";
  cout<<"N02_HMAC16="<<hex(n02tag,16)<<" synthetic_HMAC16="<<hex(synthTag,16)<<"\n";
  if(found)cout<<"ORIGINAL_MATCH="<<winner<<"\n";
  if(checked!=expected||synthetic_hits!=1||found!=0)fail("count/control/target assertion");
  cout<<"RESULT=NO_MATCH any-order motif-mask-7 length "<<len<<"\n";
}
