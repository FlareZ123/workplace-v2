// Source-pinned full-byte bit-lane permutation copier; read-only original.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using B = array<unsigned char,16>;
static B source, mask;
static unsigned char actual[32], planted[32];
static atomic<unsigned long long> checked(0), actualHits(0), plantedHits(0);
static string getfile(const string&path){ifstream f(path,ios::binary);if(!f)throw runtime_error("missing "+path);return string((istreambuf_iterator<char>(f)),{});}
static string shahex(const string&data){unsigned char d[32];SHA256((const unsigned char*)data.data(),data.size(),d);string s;const char *hx="0123456789abcdef";for(auto b:d){s+=hx[b>>4];s+=hx[b&15];}return s;}
static int dig(char x){if(x>='0'&&x<='9')return x-'0';if(x>='A'&&x<='F')return x-'A'+10; if(x>='a'&&x<='f')return x-'a'+10;throw runtime_error("hex");}
static B unhex(const string &s){if(s.size()!=32)throw runtime_error("length");B o;for(int i=0;i<16;i++)o[i]=(dig(s[2*i])<<4)|dig(s[2*i+1]);return o;}
static unsigned char bitmap(unsigned char b,const array<int,8>&p){unsigned char out=0;for(int i=0;i<8;i++)out|=((b>>p[i])&1)<<i;return out;}
static int origin(int j,int mode){switch(mode){case 0:return j;case 1:return 15-j;case 2:return (j&~3)+(3-(j&3));default:return 4*(3-j/4)+j%4;}}
static void hashcoupon(const B&b,unsigned char out[32]){B c;for(int j=0;j<16;j++)c[j]=b[j]^mask[j];SHA256(c.data(),16,out);}
int main(int argc,char**argv){try{
 if(argc!=2)throw runtime_error("usage: sft <extracted-archive-root>");string root=argv[1];
 string s=getfile(root+"/evidence/print/spool-reconstruction.log");
 if(shahex(s)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")throw runtime_error("bad printer source sha");
 if(shahex(getfile(root+"/evidence/recovery-routing.json"))!="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5")throw runtime_error("bad route sha");
 if(shahex(getfile(root+"/acceptance.json"))!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")throw runtime_error("bad acceptance sha");
 const string q="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
 size_t pos=s.find(q);if(pos==string::npos||s.find(q,pos+q.size())!=string::npos)throw runtime_error("selected ACK identity");source=unhex(s.substr(pos+q.size(),32));mask=unhex("8556C8CB6140A7F9A5123AC7571BEE1C");
 const string target="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
 for(int i=0;i<32;i++)actual[i]=(dig(target[2*i])<<4)|dig(target[2*i+1]);
 vector<array<int,8>> perm;array<int,8>p={0,1,2,3,4,5,6,7};do{perm.push_back(p);}while(next_permutation(p.begin(),p.end()));
 if(perm.size()!=40320)throw runtime_error("bad permutation count");
 array<int,8> pp={7,0,6,1,5,2,4,3};B plantedCoupon;
 for(int j=0;j<16;j++)plantedCoupon[j]=bitmap(source[origin(j,3)],pp)^0x5a;
 hashcoupon(plantedCoupon,planted);
 #pragma omp parallel for schedule(dynamic)
 for(int idx=0;idx<(int)perm.size();idx++){
  unsigned char lut[256];for(int i=0;i<256;i++)lut[i]=bitmap((unsigned char)i,perm[idx]);
  unsigned char d[32];B b;
  for(int mode=0;mode<4;mode++){
   B t;for(int j=0;j<16;j++)t[j]=lut[source[origin(j,mode)]];
   for(int maskbyte=0;maskbyte<256;maskbyte++){
    for(int j=0;j<16;j++)b[j]=t[j]^maskbyte;
    hashcoupon(b,d);
    checked.fetch_add(1,memory_order_relaxed);
    if(memcmp(d,actual,32)==0)actualHits.fetch_add(1,memory_order_relaxed);
    if(memcmp(d,planted,32)==0)plantedHits.fetch_add(1,memory_order_relaxed);
   }
  }
 }
 cout<<"Source original copied ACK="<<s.substr(pos+q.size(),32)<<" full candidate assignments="<<checked.load()<<" original_matches="<<actualHits.load()<<" planted_positive="<<plantedHits.load()<<endl;
 return (checked.load()==40320ULL*256*4 && actualHits.load()==0 && plantedHits.load()==1)?0:2;
}catch(exception&e){cerr<<e.what()<<endl;return 3;}}
