// K04 hexadecimal visual-transcription SFT; original archive remains read-only.
// Run: g++ -O3 -fopenmp k04_optical_recapture_sft.cpp -lcrypto -o k04_optical_recapture_sft
//      OMP_NUM_THREADS=8 ./k04_optical_recapture_sft /path/to/extracted-archive medium
#include <openssl/sha.h>
#include <array>
#include <atomic>
#include <cctype>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using B = array<unsigned char,16>;
static B mask={}, original_input={}, synthetic={};
static unsigned char synth_sha[32], target[32];
static array<vector<unsigned char>,32> opts;
static atomic<unsigned long long> examined(0), original_hits(0), planted_hits(0);
static inline int nibble(char c){if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;throw runtime_error("invalid HEX");}
static B unhex16(const string&s){B b{};if(s.size()!=32)throw runtime_error("hex length");for(int i=0;i<16;i++)b[i]=(nibble(s[i*2])<<4)|nibble(s[i*2+1]);return b;}
static string hex16(const B&b){const char*h="0123456789ABCDEF";string s;for(auto a:b){s+=h[a>>4];s+=h[a&15];}return s;}
static string file(const string&p){ifstream f(p,ios::binary);if(!f)throw runtime_error("missing "+p);return string((istreambuf_iterator<char>(f)),{});}
static string sha256hex(const string&s){unsigned char d[32];SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),d);const char*h="0123456789abcdef";string o;for(auto c:d){o+=h[c>>4];o+=h[c&15];}return o;}
static void eval(const B&payload){B component;for(int i=0;i<16;i++)component[i]=payload[i]^mask[i];unsigned char digest[32];SHA256(component.data(),16,digest);examined.fetch_add(1,memory_order_relaxed);if(memcmp(digest,target,32)==0){original_hits.fetch_add(1,memory_order_relaxed);fprintf(stderr,"ORIGINAL HIT payload=%s component=%s\n",hex16(payload).c_str(),hex16(component).c_str());}if(memcmp(digest,synth_sha,32)==0)planted_hits.fetch_add(1,memory_order_relaxed);}
static void dfs(int p,B&b){if(p==32){eval(b);return;}auto old=b[p/2];for(unsigned char n:opts[p]){if(p%2==0)b[p/2]=(old&0x0f)|(n<<4);else b[p/2]=(old&0xf0)|n;dfs(p+1,b);}b[p/2]=old;}
int main(int argc,char**argv){try{
 if(argc!=3)throw runtime_error("usage: SFT <archive-directory> <strict|medium>");
 string root=argv[1],mode=argv[2];if(mode!="strict"&&mode!="medium")throw runtime_error("mode");
 string spool=file(root+"/evidence/print/spool-reconstruction.log");
 if(sha256hex(spool)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")throw runtime_error("spool SHA mismatch");
 if(sha256hex(file(root+"/evidence/recovery-routing.json"))!="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5")throw runtime_error("routing SHA mismatch");
 if(sha256hex(file(root+"/acceptance.json"))!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")throw runtime_error("acceptance SHA mismatch");
 string chosen="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
 auto pos=spool.find(chosen);if(pos==string::npos||spool.find(chosen,pos+1)!=string::npos)throw runtime_error("selected line nonunique");
 string original=spool.substr(pos+chosen.size(),32);original_input=unhex16(original);
 mask=unhex16("8556C8CB6140A7F9A5123AC7571BEE1C");
 string target_s="930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0";
 for(int i=0;i<32;i++)target[i]=(nibble(target_s[2*i])<<4)|nibble(target_s[2*i+1]);
 for(int p=0;p<32;p++){
  char c=original[p];opts[p].push_back(nibble(c));string alts;
  switch(c){case 'A':alts="4";break;case '4':alts="A";break;case 'B':alts="8";break;case '8':alts="3B";break;case 'D':alts="0";break;case '0':alts="CD";break;case 'C':alts="0";break;case 'E':alts="F";break;case 'F':alts="E";break;case '1':alts="7";break;case '7':alts="12";break;case '2':alts="7";break;case '3':alts="8";break;default:break;}
  if(c=='7'||c=='2'||c=='8')alts=(c=='7'?"1":c=='2'?"":"B");
  if(mode=="medium"&&c=='5')alts="6";
  for(char a:alts)if(a!=c)opts[p].push_back(nibble(a));
 }
 unsigned long long expected=1;for(auto&v:opts)expected*=v.size();
 synthetic=original_input;int planted_positions[]={0,2,5,10,15,19};
 for(int p:planted_positions){if(opts[p].size()<2)throw runtime_error("plant position not ambiguous");unsigned char n=opts[p][1];if(p%2==0)synthetic[p/2]=(synthetic[p/2]&0x0f)|(n<<4);else synthetic[p/2]=(synthetic[p/2]&0xf0)|n;}
 B syncomp;for(int i=0;i<16;i++)syncomp[i]=synthetic[i]^mask[i];SHA256(syncomp.data(),16,synth_sha);
 cout<<"MODE "<<mode<<" source="<<original<<" scope="<<expected<<" synthetic="<<hex16(synthetic)<<endl;
 int depth=0;unsigned long long prefixes=1;while(depth<32&&prefixes<2048){prefixes*=opts[depth].size();depth++;}
 #pragma omp parallel for schedule(dynamic)
 for(long long z=0;z<(long long)prefixes;z++){
  B b=original_input;unsigned long long k=z;
  for(int p=depth-1;p>=0;p--){auto i=k%opts[p].size();k/=opts[p].size();auto a=opts[p][i];if(p%2==0)b[p/2]=(b[p/2]&0x0f)|(a<<4);else b[p/2]=(b[p/2]&0xf0)|a;}
  dfs(depth,b);
 }
 cout<<"RESULT count="<<examined.load()<<" original_matches="<<original_hits.load()<<" planted_matches="<<planted_hits.load()<<endl;
 if(examined!=expected||planted_hits!=1)return 2;return 0;
}catch(exception&e){cerr<<"ERROR "<<e.what()<<endl;return 3;}}
