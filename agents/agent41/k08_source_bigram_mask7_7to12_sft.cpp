// H-17 K08: complete source-bigram graph walks, lengths 7..12, all three literal motifs.
// Exploratory conditional lexical model; not an authenticated author-final selector.
// Build: g++ -O3 -std=c++17 k08_source_bigram_mask7_7to12_sft.cpp -lcrypto -o k08_source_bigram_mask7_7to12_sft
// Run:   ./k08_source_bigram_mask7_7to12_sft /path/to/h17/evidence
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
using namespace std;

static const unsigned char KEY[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char TARGET[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};

static void fail(const string &s){cerr<<"ERROR: "<<s<<"\n";exit(2);}
static string readfile(const string&p){ifstream f(p,ios::binary);if(!f)fail("missing "+p);return string((istreambuf_iterator<char>(f)),{});}
static string hex(const unsigned char*p,size_t n){char b[3];string s;for(size_t i=0;i<n;i++){snprintf(b,sizeof b,"%02x",p[i]);s+=b;}return s;}
static string pinned(const string&p,const char*expected){string s=readfile(p);unsigned char h[32];SHA256((const unsigned char*)s.data(),s.size(),h);if(hex(h,32)!=expected)fail("source SHA-256 mismatch: "+p);return s;}
static vector<string> tokenize(const string&s){vector<string>v;string w;for(unsigned char c:s){if(c>=65&&c<=90)c+=32;if((c>=97&&c<=122)||(c>=48&&c<=57))w.push_back((char)c);else if(!w.empty()){v.push_back(w);w.clear();}}if(!w.empty())v.push_back(w);return v;}
static int motif(const string&w){return (w=="sea"||w=="water"?1:0)|(w=="night"||w=="watch"||w=="morning"?2:0)|(w=="table"||w=="voices"||w=="room"?4:0);}
static void replace_all(string&s,const string&needle){size_t p=0;while((p=s.find(needle,p))!=string::npos)s.erase(p,needle.size());}

struct Hasher{
  SHA256_CTX inner,outer;
  Hasher(){unsigned char ip[64],op[64];for(int i=0;i<64;i++){unsigned char k=i<16?KEY[i]:0;ip[i]=k^0x36;op[i]=k^0x5c;}SHA256_Init(&inner);SHA256_Update(&inner,ip,64);SHA256_Init(&outer);SHA256_Update(&outer,op,64);}
  void run(const string&s,unsigned char commitment[32],unsigned char tag16[16])const{
    SHA256_CTX t=inner;SHA256_Update(&t,s.data(),s.size());unsigned char tmp[32],full[32];SHA256_Final(tmp,&t);t=outer;SHA256_Update(&t,tmp,32);SHA256_Final(full,&t);memcpy(tag16,full,16);SHA256(tag16,16,commitment);
  }
};

int main(int argc,char**argv){
  if(argc!=2)fail("usage: binary EVIDENCE_ROOT");
  const string root=argv[1];
  string notes=pinned(root+"/crew/noticeboard-and-desk-notes.txt","13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
  string m11=pinned(root+"/mail/11.eml","f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29");
  string m20=pinned(root+"/mail/20.eml","e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71");
  string route=pinned(root+"/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
  string acceptance=pinned(root+"/../acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
  if(route.find("\"desk_nonce\": \"5F933DA6A1BD03C32DA5CBC25344F497\"")==string::npos)fail("route nonce mismatch");
  if(acceptance.find("\"K08\": \"285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747\"")==string::npos)fail("K08 commitment mismatch");

  vector<string> sources;size_t pos=0;
  while(pos<notes.size()){
    size_t e=notes.find('\n',pos);if(e==string::npos)e=notes.size();string line=notes.substr(pos,e-pos);
    if(line.size()>6&&line[0]=='N'&&isdigit((unsigned char)line[1])&&isdigit((unsigned char)line[2])&&line.substr(3,2)==" /"){
      size_t ne=notes.find('\n',e+1);if(ne==string::npos)ne=notes.size();string body=notes.substr(e+1,ne-(e+1));size_t c=body.find(':');if(c!=string::npos)body=body.substr(c+1);sources.push_back(body);
    }
    pos=e+1;
  }
  auto email_body=[&](string s,const string&signature){size_t p=s.find("\n\n");if(p==string::npos)fail("email MIME separator missing");s=s.substr(p+2);replace_all(s,"Back before the first boat");replace_all(s,"Leave the light on for the next watch");p=s.rfind("\n"+signature);if(p!=string::npos)s.resize(p);return s;};
  sources.push_back(email_body(m11,"Emily"));sources.push_back(email_body(m20,"Gabriel"));
  if(sources.size()!=26)fail("expected 24 notes plus MAIL-11 and MAIL-20");

  map<string,int> ids;vector<string> words;vector<set<int>> edge_sets;
  auto intern=[&](const string&w){auto it=ids.find(w);if(it!=ids.end())return it->second;int id=(int)words.size();ids[w]=id;words.push_back(w);edge_sets.emplace_back();return id;};
  for(const string&s:sources){auto t=tokenize(s);for(size_t i=0;i+1<t.size();i++){int a=intern(t[i]),b=intern(t[i+1]);edge_sets[a].insert(b);}}
  size_t edge_count=0;for(const auto&e:edge_sets)edge_count+=e.size();
  if(words.size()!=331||edge_count!=570)fail("source graph cardinality mismatch");
  vector<vector<int>> adj(words.size());vector<int> flags(words.size());
  for(size_t i=0;i<words.size();i++){adj[i].assign(edge_sets[i].begin(),edge_sets[i].end());flags[i]=motif(words[i]);}

  // can[u][r][mask] means an exact r-edge continuation from u can finish with motif mask 7.
  static unsigned char can[331][12][8];memset(can,0,sizeof(can));
  for(size_t u=0;u<words.size();u++)for(int mask=0;mask<8;mask++)can[u][0][mask]=(mask==7);
  for(int r=1;r<=11;r++)for(size_t u=0;u<words.size();u++)for(int mask=0;mask<8;mask++)
    for(int v:adj[u])if(can[v][r-1][mask|flags[v]]){can[u][r][mask]=1;break;}

  Hasher hasher;
  const string n02="a good watch leaves the room ready for the next pair of hands";
  unsigned char n02_commit[32],n02_tag[16];hasher.run(n02,n02_commit,n02_tag);
  if(hex(n02_tag,16)!="bf889359b0303f2b2b2fd96ae841210b")fail("N02 known HMAC control failed");
  // A valid graph walk used only as a planted positive control for the full search path.
  const string synthetic="06 is late crew notes with the night the sea the table";
  unsigned char synthetic_commit[32],synthetic_tag[16];hasher.run(synthetic,synthetic_commit,synthetic_tag);

  unsigned long long checked=0,by_length[13]={0},synthetic_hits=0,original_hits=0,nodes=0;
  string candidate,original_match;
  auto dfs=[&](auto&&self,int last,int length,int mask)->void{
    nodes++;
    if(length>=7&&length<=12&&mask==7){unsigned char digest[32],tag[16];hasher.run(candidate,digest,tag);checked++;by_length[length]++;if(memcmp(digest,TARGET,32)==0){original_hits++;original_match=candidate;}if(memcmp(digest,synthetic_commit,32)==0)synthetic_hits++;}
    if(length==12)return;
    int min_r=max(0,7-length),max_r=12-length;bool possible=false;
    for(int r=min_r;r<=max_r;r++)if(can[last][r][mask]){possible=true;break;}
    if(!possible)return;
    for(int v:adj[last]){size_t old=candidate.size();if(old)candidate.push_back(' ');candidate+=words[v];self(self,v,length+1,mask|flags[v]);candidate.resize(old);}
  };
  for(size_t start=0;start<words.size();start++){
    int mask=flags[start];bool possible=false;for(int r=6;r<=11;r++)if(can[start][r][mask]){possible=true;break;}
    if(!possible)continue;candidate=words[start];dfs(dfs,(int)start,1,mask);
  }

  const unsigned long long expected[13]={0,0,0,0,0,0,0,554,4154,26189,188363,1061762,6314210};
  cout<<"source_records="<<sources.size()<<" words="<<words.size()<<" unique_edges="<<edge_count<<"\n";
  cout<<"checked="<<checked<<" dfs_nodes="<<nodes<<" synthetic_hits="<<synthetic_hits<<" original_hits="<<original_hits<<"\n";
  for(int l=7;l<=12;l++){cout<<"length_"<<l<<"="<<by_length[l]<<"\n";if(by_length[l]!=expected[l])fail("per-length candidate count mismatch");}
  cout<<"N02_HMAC16="<<hex(n02_tag,16)<<"\nsynthetic_HMAC16="<<hex(synthetic_tag,16)<<"\n";
  if(original_hits)cout<<"ORIGINAL_K08_MATCH="<<original_match<<"\n";
  if(checked!=7595232||synthetic_hits!=1||original_hits!=0)fail("final count/control/target assertion failed");
  cout<<"RESULT=NO_MATCH; all 7,595,232 source-bigram motif-mask-7 walks of lengths 7..12 checked\n";
}
