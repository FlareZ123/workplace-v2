/* H-17 K08: source-pinned exactly +1/+2 nonminimal three-strand supersequence.
   Build: g++ -O3 -std=c++17 -fopenmp agent34_k08_nonminimal_scs.cpp -lcrypto -o k08_nonminimal
   Run: ./k08_nonminimal <resources-directory>
   Read-only; no candidate, evidence, verifier, or commitment changes. */
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <omp.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using Seq=vector<string>;
using Spans=vector<Seq>;
constexpr int MAXLEN=17;
static const string NOTES_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb";
static const string ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const string ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const string TARGET="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747";
static const string PLANTED="9df012e755f08320c21eda41d5d323075097c3437c1ce42ae5ce021575ab3869";
static const array<unsigned char,16> NONCE={0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};
string hex(const unsigned char*buf,size_t n){static const char *h="0123456789abcdef";string out;out.reserve(n*2);for(size_t i=0;i<n;i++){out+=h[buf[i]>>4];out+=h[buf[i]&15];}return out;}
string read(const string&path){ifstream f(path,ios::binary);if(!f)throw runtime_error("cannot read "+path);return string(istreambuf_iterator<char>(f),{});}
string pinned(const string&path,const string&sha){string t=read(path);unsigned char dg[32];SHA256(reinterpret_cast<const unsigned char*>(t.data()),t.size(),dg);if(hex(dg,32)!=sha)throw runtime_error("source SHA256 mismatch "+path);return t;}
Seq tokens(string s){Seq r;string w;for(unsigned char c:s){if(c>='A'&&c<='Z')c=static_cast<unsigned char>(c+32);if((c>='a'&&c<='z')||(c>='0'&&c<='9'))w.push_back(static_cast<char>(c));else if(!w.empty()){r.push_back(w);w.clear();}}if(!w.empty())r.push_back(w);return r;}
Seq note(const string&s,int index){char buf[8];snprintf(buf,sizeof buf,"N%02d /",index);string hdr=buf;size_t pos=s.find(hdr);if(pos==string::npos || (pos && s[pos-1]!='\n'))throw runtime_error("note absent");pos=s.find('\n',pos)+1;size_t end=s.find("\n\nN",pos);string body=s.substr(pos,end==string::npos?string::npos:end-pos);if(index==1 || index==9){auto colon=body.find(':');if(colon==string::npos)throw runtime_error("missing caption delimiter");body=body.substr(colon+1);}return tokens(body);}
Spans spans(const Seq&src,const Seq&motif,int lo,int hi){set<Seq> out;for(size_t i=0;i<src.size();i++)for(size_t j=i+lo;j<=src.size()&&j<=i+(size_t)hi;j++){Seq sub(src.begin()+i,src.begin()+j);auto it=search(sub.begin(),sub.end(),motif.begin(),motif.end());if(it!=sub.end())out.insert(move(sub));}return Spans(out.begin(),out.end());}
struct FastHmac{
 SHA256_CTX i0,o0;
 FastHmac(){unsigned char ip[64],op[64];fill(ip,ip+64,0x36);fill(op,op+64,0x5c);for(int j=0;j<16;j++){ip[j]^=NONCE[j];op[j]^=NONCE[j];}SHA256_Init(&i0);SHA256_Update(&i0,ip,64);SHA256_Init(&o0);SHA256_Update(&o0,op,64);}
 void run(const string&msg,unsigned char mac[32])const{SHA256_CTX c=i0;unsigned char inner[32];SHA256_Update(&c,msg.data(),msg.size());SHA256_Final(inner,&c);c=o0;SHA256_Update(&c,inner,32);SHA256_Final(mac,&c);}
};
thread_local FastHmac fast_hmac;
struct Walker{
 const Seq&a;const Seq&b;const Seq&c;array<int,3> len;int memo[9][9][9]; string current;uint64_t cnt[2]={0,0};uint64_t planted=0;uint64_t hit=0;string solution;
 Walker(const Seq&a_,const Seq&b_,const Seq&c_):a(a_),b(b_),c(c_),len{(int)a.size(),(int)b.size(),(int)c.size()}{fill(&memo[0][0][0],&memo[0][0][0]+9*9*9,-1);}
 struct Adv{string word;int i,j,k;};
 vector<Adv> options(int i,int j,int k){set<string> ww;if(i<len[0])ww.insert(a[i]);if(j<len[1])ww.insert(b[j]);if(k<len[2])ww.insert(c[k]);vector<Adv>o;for(auto&w:ww)o.push_back({w,i+(i<len[0]&&a[i]==w),j+(j<len[1]&&b[j]==w),k+(k<len[2]&&c[k]==w)});return o;}
 int shortest(int i,int j,int k){if(i==len[0]&&j==len[1]&&k==len[2])return 0;int&v=memo[i][j][k];if(v>=0)return v;v=99;for(auto&x:options(i,j,k))v=min(v,1+shortest(x.i,x.j,x.k));return v;}
 void verify(int offset){unsigned char mac[32],d[32];fast_hmac.run(current,mac);SHA256(mac,16,d);auto k=hex(d,32);cnt[offset-1]++;if(k==PLANTED)planted++;if(k==TARGET){hit++;solution=current;}}
 void dfs(int i,int j,int k,int remain,int offset){int shortleft=shortest(i,j,k);if(shortleft>remain || remain>(len[0]-i)+(len[1]-j)+(len[2]-k))return;
 if(!remain){if(i==len[0]&&j==len[1]&&k==len[2])verify(offset);return;}
 for(auto&x:options(i,j,k)){size_t old=current.size();if(old)current.push_back(' ');current+=x.word;dfs(x.i,x.j,x.k,remain-1,offset);current.resize(old);}}
 void run(){int minimal=shortest(0,0,0);for(int off=1;off<=2;off++)if(minimal+off<=MAXLEN)dfs(0,0,0,minimal+off,off);}
};
int main(int argc,char**argv){try{
 if(argc!=2)throw runtime_error("give original resources root");string root=argv[1];string notes=pinned(root+"/evidence/crew/noticeboard-and-desk-notes.txt",NOTES_SHA);string routing=pinned(root+"/evidence/recovery-routing.json",ROUTE_SHA);string acceptance=pinned(root+"/acceptance.json",ACCEPT_SHA);
 if(routing.find("5F933DA6A1BD03C32DA5CBC25344F497")==string::npos||acceptance.find(TARGET)==string::npos)throw runtime_error("original route/target missing");
 Seq a=note(notes,1),b=note(notes,13),c=note(notes,20);
 if(a.size()<5||b.size()<20||c.size()<20)throw runtime_error("unexpected crew note lengths");
 auto A=spans(a,{"sea"},2,6),B=spans(b,{"end","of","the","night"},4,8),C=spans(c,{"voices","at","the","table"},4,8);
 if(A.size()!=10||B.size()!=12||C.size()!=15)throw runtime_error("source spans diverged");
 auto checksum=[&](const string&phrase){unsigned char mac[32];unsigned int n;HMAC(EVP_sha256(),NONCE.data(),16,(const unsigned char*)phrase.data(),phrase.size(),mac,&n);return hex(mac,16);};
 if(checksum("a good watch leaves the room ready for the next pair of hands")!="bf889359b0303f2b2b2fd96ae841210b")throw runtime_error("real N02 HMAC control fails");
 {
 const string phrase="and at sea looks the end of the night voices at the table";
 unsigned char ref[32],mac[32],d[32];unsigned int n;
 HMAC(EVP_sha256(),NONCE.data(),16,(const unsigned char*)phrase.data(),phrase.size(),ref,&n);
 fast_hmac.run(phrase,mac);
 if(hex(ref,32)!=hex(mac,32))throw runtime_error("fast HMAC disagrees with OpenSSL reference");
 SHA256(mac,16,d);if(hex(d,32)!=PLANTED)throw runtime_error("independent planted commitment mismatch");
}
 unsigned long long count1=0,count2=0,planted=0,hits=0;string found;
 double start=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,1) reduction(+:count1,count2,planted,hits)
 for(int idx=0;idx<(int)(A.size()*B.size()*C.size());idx++){
  size_t i=idx/(B.size()*C.size());size_t j=(idx/C.size())%B.size();size_t k=idx%C.size();Walker w(A[i],B[j],C[k]);w.run();count1+=w.cnt[0];count2+=w.cnt[1];planted+=w.planted;hits+=w.hit;if(w.hit){
#pragma omp critical
    {found=w.solution;}
  }
 }
 if(count1!=369357248ULL||count2!=167294491ULL)throw runtime_error("coverage count diverged: "+to_string(count1)+"/"+to_string(count2));
 if(planted<1)throw runtime_error("independent planted positive missed");
 cout<<"NONMINIMAL_SCS_COUNT_PLUS1 "<<count1<<"\nNONMINIMAL_SCS_COUNT_PLUS2 "<<count2<<"\n";
 cout<<"ORIGINAL_K08_HITS "<<hits<<"\nPLANTED_POSITIVE "<<planted<<"\nELAPSED_SECONDS "<<(omp_get_wtime()-start)<<"\n";
 if(hits)cout<<"RECOVERED_PHRASE "<<found<<"\n";
 return hits?10:0;
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<'\n';return 2;}}
