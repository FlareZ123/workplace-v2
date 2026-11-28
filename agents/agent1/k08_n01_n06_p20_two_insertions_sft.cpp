// Source-pinned H-17 K08 13-word whole-line editor: all two-motif-word
// insertions into equal-width source-selected N01/N06 crossover rows.
// This runner never prints source candidates, nonce, components or target.
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <vector>
#include <array>
#include <cctype>
#include <atomic>
#include <stdexcept>
#include <numeric>
#include <cstring>
using namespace std;
string slurp(const string& p){ifstream f(p,ios::binary); if(!f)throw runtime_error("can't open "+p);return string(istreambuf_iterator<char>(f),{});}
string hex(const unsigned char* p,size_t n){static const char*h="0123456789abcdef";string s;for(size_t i=0;i<n;i++){s+=h[p[i]>>4];s+=h[p[i]&15];}return s;}
void pin(const string& s,const string& h){unsigned char d[32];SHA256((const unsigned char*)s.data(),s.size(),d);if(hex(d,32)!=h)throw runtime_error("source SHA pin mismatch");}
string match1(const string&s,const string&pattern){smatch m;if(!regex_search(s,m,regex(pattern)))throw runtime_error("missing field");return m[1];}
vector<unsigned char> fromhex(const string&s){if(s.size()%2)throw runtime_error("bad hex");vector<unsigned char>b;for(size_t i=0;i<s.size();i+=2)b.push_back(stoul(s.substr(i,2),nullptr,16));return b;}
string note_body(const string&notes,int id){char idstr[8];snprintf(idstr,sizeof(idstr),"N%02d /",id);size_t p=notes.find(idstr);if(p==string::npos)throw runtime_error("missing note");p=notes.find('\n',p);if(p==string::npos)throw runtime_error("missing note body");size_t e=notes.find("\n\n",p);string body=notes.substr(p+1,e==string::npos?string::npos:e-p-1);size_t colon=body.find(": ");if(colon!=string::npos)body=body.substr(colon+2);return body;}
vector<string> words(const string& s){vector<string>r;string w;auto push=[&](){if(!w.empty()){r.push_back(w);w.clear();}};for(unsigned char c:s){if(isalnum(c))w+=tolower(c);else push();}push();return r;}
string join(const vector<string>& v){string s;for(const auto&w:v){if(!s.empty())s+=' ';s+=w;}return s;}
struct Digest{array<unsigned char,32>v;};
Digest digest(const string&s,const vector<unsigned char>&key){unsigned char out[32];unsigned int len=0;HMAC(EVP_sha256(),key.data(),key.size(),(const unsigned char*)s.data(),s.size(),out,&len);if(len!=32)throw runtime_error("HMAC failed");Digest d;SHA256(out,16,d.v.data());return d;}
string hmac16hex(const string&s,const vector<unsigned char>&key){unsigned char out[32];unsigned int n=0;HMAC(EVP_sha256(),key.data(),key.size(),(const unsigned char*)s.data(),s.size(),out,&n);return hex(out,16);}
int main(int argc,char**argv){try{
if(argc!=2&&argc!=4)throw runtime_error("usage: k08_two_inserts <extracted-archive-root> [mask_start mask_end]");
string root=argv[1];int start=argc==4?stoi(argv[2]):0,stop=argc==4?stoi(argv[3]):2048;if(start<0||stop>2048||start>=stop)throw runtime_error("mask shard invalid");
string notes=slurp(root+"/evidence/crew/noticeboard-and-desk-notes.txt");pin(notes,"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
string route=slurp(root+"/evidence/recovery-routing.json");pin(route,"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
string acceptance=slurp(root+"/acceptance.json");pin(acceptance,"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
vector<unsigned char>key=fromhex(match1(route,"\\\"desk_nonce\\\"[ \\t]*:[ \\t]*\\\"([A-Fa-f0-9]{32})\\\""));
vector<unsigned char>target=fromhex(match1(acceptance,"\\\"K08\\\"[ \\t]*:[ \\t]*\\\"([A-Fa-f0-9]{64})\\\""));
if(target.size()!=32)throw runtime_error("bad target width");
vector<string> a=words(note_body(notes,1)),b=words(note_body(notes,6)),n02=words(note_body(notes,2)),n20=words(note_body(notes,20));
if(a.size()!=11||b.size()!=11||n02.size()!=13||n20.size()!=30)throw runtime_error("source-width mismatch");
if(hmac16hex(join(n02),key)!="bf889359b0303f2b2b2fd96ae841210b")throw runtime_error("N02 historical HMAC control failed");
vector<string>p20(n20.begin()+6,n20.begin()+19);pin(join(p20),"4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c");
string n20raw=note_body(notes,20);if(n20raw.size()<24)throw runtime_error("N20 short");
string op;for(int j=0;j<3;j++){int v=0;for(int k=0;k<8;k++)v|=(int(n20raw[j*8+k])&1)<<k;op+=char(v);}if(op!="MHI")throw runtime_error("MHI control failed");
vector<string>plantwords=a;plantwords.insert(plantwords.begin()+3,p20[1]);plantwords.insert(plantwords.begin()+9,p20[8]);Digest plant=digest(join(plantwords),key);
array<vector<string>,4>As{a,a,vector<string>(a.rbegin(),a.rend()),vector<string>(a.rbegin(),a.rend())};
array<vector<string>,4>Bs{b,vector<string>(b.rbegin(),b.rend()),b,vector<string>(b.rbegin(),b.rend())};
unsigned long long total=0,hits=0,planted=0;
#ifdef _OPENMP
#pragma omp parallel for collapse(2) schedule(dynamic,8) reduction(+:total,hits,planted)
#endif
for(int orientation=0;orientation<4;orientation++)for(int mask=start;mask<stop;mask++){
 array<string,11>base;for(int k=0;k<11;k++)base[k]=((mask>>k)&1)?Bs[orientation][k]:As[orientation][k];
 array<string,13>r;
 for(int insert1=0;insert1<12;insert1++)for(int insert2=insert1+1;insert2<13;insert2++){
  int z=0;for(int k=0;k<13;k++)if(k!=insert1&&k!=insert2)r[k]=base[z++];
  if(z!=11)throw runtime_error("base mismatch");
  for(int i=0;i<13;i++)for(int j=0;j<13;j++){
   r[insert1]=p20[i];r[insert2]=p20[j];
   string phrase;phrase.reserve(130);for(int k=0;k<13;k++){if(k)phrase+=' ';phrase+=r[k];}
   Digest d=digest(phrase,key);
   hits+=memcmp(d.v.data(),target.data(),32)==0;
   planted+=memcmp(d.v.data(),plant.v.data(),32)==0;
   total++;
  }
 }
}
const unsigned long long expected=4ULL*(stop-start)*78ULL*169ULL;
if(total!=expected)throw runtime_error("count mismatch");
if(start==0&&planted<1)throw runtime_error("synthetic positive missed");
cout<<"K08_N01_N06_P20_TWO_INSERTIONS start="<<start<<" stop="<<stop<<" checked="<<total<<" original_hits="<<hits<<" planted_hits="<<planted<<" source=PASS N02=PASS P20=PASS MHI=PASS\n";
return hits?3:0;
}catch(const exception&e){cerr<<"ERROR: "<<e.what()<<"\n";return 2;}
}
