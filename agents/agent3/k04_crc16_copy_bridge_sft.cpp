// Conditional K04/K07 cyclic-CRC coupon inversion + source-ACK test.
// No original source bytes, keyed hashes, candidate values or target bytes printed.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>
using namespace std;
using Packet=array<uint8_t,16>;

static string read_file(const string& s){ifstream f(s);if(!f)throw runtime_error("missing required input file: "+s);return string(istreambuf_iterator<char>(f),{});}
static string strfield(const string& line,const string& key){regex r("\\\""+key+"\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"");smatch m;if(!regex_search(line,m,r))throw runtime_error("missing field "+key);return m[1];}
static int intfield(const string& line,const string& key){regex r("\\\""+key+"\\\"\\s*:\\s*([0-9]+)");smatch m;if(!regex_search(line,m,r))throw runtime_error("missing integer field "+key);return stoi(m[1]);}
static uint8_t unhex(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;throw runtime_error("bad hex");}
static vector<uint8_t> hexparse(const string&s){if(s.size()%2)throw runtime_error("odd hex length");vector<uint8_t>r;for(size_t i=0;i<s.size();i+=2)r.push_back((unhex(s[i])<<4)|unhex(s[i+1]));return r;}
static Packet array16(const vector<uint8_t>& v){if(v.size()!=16)throw runtime_error("not 16 bytes");Packet o;copy(v.begin(),v.end(),o.begin());return o;}
struct Source{array<array<array<uint8_t,2>,3>,8> check{};Packet copied{},mask{};array<uint8_t,32> target{};};
static Source load(const string& root){
 Source S{};bool seen[8][3]{};
 istringstream file(read_file(root+"/evidence/transfers/transfer-audit.jsonl"));string line;
 while(getline(file,line)){
  if(line.find("\"transfer\": \"AX-7782\"")==string::npos || line.find("\"kind\": \"CHUNK\"")==string::npos)continue;
  int seq=intfield(line,"seq"),attempt=intfield(line,"attempt");if(seq<0||seq>=8||attempt<1||attempt>2)throw runtime_error("bad selector");
  auto x=hexparse(strfield(line,"checkpoint"));if(x.size()!=2||seen[seq][attempt])throw runtime_error("duplicate/bad checkpoint");
  S.check[seq][attempt]={x[0],x[1]};seen[seq][attempt]=true;
 }
 for(int i=0;i<8;i++)for(int a=1;a<=2;a++)if(!seen[i][a])throw runtime_error("missing transfer checkpoint");
 istringstream pf(read_file(root+"/evidence/print/spool-reconstruction.log"));int matches=0;
 while(getline(pf,line)){
  if(line.find("JOB=PS-261003-0417")==string::npos || line.find("ATTEMPT=2")==string::npos || line.find("STATE=ACK")==string::npos || line.find("CLASS=RECOVER")==string::npos)continue;
  auto pos=line.find("PAYLOAD=");if(pos==string::npos)throw runtime_error("no payload");
  auto stop=line.find(' ',pos+8);auto p=hexparse(line.substr(pos+8,(stop==string::npos?line.size():stop)-(pos+8)));
  S.copied=array16(p);matches++;
 }
 if(matches!=1)throw runtime_error("source selector mismatch");
 {string r=read_file(root+"/evidence/recovery-routing.json");S.mask=array16(hexparse(strfield(r,"masked_component")));}
 {string a=read_file(root+"/acceptance.json");auto h=hexparse(strfield(a,"K04"));if(h.size()!=32)throw runtime_error("target digest malformed");copy(h.begin(),h.end(),S.target.begin());}
 return S;
}
static inline uint16_t mul16(uint16_t a,uint16_t b,uint16_t p){
 uint32_t prod=0,aa=a;for(int i=0;i<16;i++){if((b>>i)&1)prod^=aa;aa<<=1;}
 const uint32_t mod=0x10000u|p;
 for(int i=30;i>=16;i--)if((prod>>i)&1)prod^=mod<<(i-16);
 return uint16_t(prod);
}
static inline int degree64(uint64_t u){return u?63-__builtin_clzll(u):-1;}
static uint16_t inv16(uint16_t a,uint16_t p){
 if(!a)throw runtime_error("zero inverse");
 uint64_t u=a,v=uint64_t(0x10000u|p),g1=1,g2=0;
 for(int step=0;step<60&&u!=1;step++){
  if(!u)throw runtime_error("non-invertible CRC polynomial");
  int d=degree64(u)-degree64(v);
  if(d<0){swap(u,v);swap(g1,g2);d=-d;}
  u^=v<<d;g1^=g2<<d;
 }
 if(u!=1)throw runtime_error("unexpected polynomial inversion failure");
 while(degree64(g1)>=16){int d=degree64(g1)-16;g1^=uint64_t(0x10000u|p)<<d;}
 return uint16_t(g1);
}
static uint16_t x128_mod(uint16_t p){uint16_t x=1;for(int i=0;i<128;i++)x=mul16(x,2,p);return x;}
static uint16_t crc16(const uint8_t* s,size_t n,uint16_t p,uint16_t init=0){
 uint16_t c=init;for(size_t i=0;i<n;i++){c^=uint16_t(s[i])<<8;for(int j=0;j<8;j++)c=uint16_t((c<<1)^((c&0x8000)?p:0));}return c;
}
static uint16_t bitreverse16(uint16_t x){uint16_t r=0;for(int j=0;j<16;j++)r=uint16_t((r<<1)|((x>>j)&1));return r;}
static uint8_t bitreverse8(uint8_t x){x=uint8_t((x>>4)|(x<<4));x=uint8_t(((x&0xcc)>>2)|((x&0x33)<<2));return uint8_t(((x&0xaa)>>1)|((x&0x55)<<1));}
static Packet derive(const array<uint16_t,8>& c,uint16_t p,uint16_t invQ,uint16_t invX){
 Packet o{};
 for(int i=0;i<8;i++){
  uint16_t next=mul16(c[i],p,p), q=c[(i+1)%8]^next;
  uint16_t d=mul16(q,invQ,p),word=mul16(d,invX,p);
  o[2*i]=uint8_t(word>>8);o[2*i+1]=uint8_t(word);
 }
 return o;
}
static Packet transform(Packet x,int offset,bool reverse,bool swapword,bool reversebits){
 Packet out{};for(int i=0;i<8;i++){
  int j=(i+offset)&7;out[2*i]=x[2*j];out[2*i+1]=x[2*j+1];
 }
 if(reverse)std::reverse(out.begin(),out.end());
 if(swapword)for(int i=0;i<16;i+=2)swap(out[i],out[i+1]);
 if(reversebits)for(auto &t:out)t=bitreverse8(t);
 return out;
}
struct Metric{int residual,maj,ntie;array<uint16_t,8> diffs;};
static Metric score(const Packet&P,const Packet&M){
 Metric k{};k.residual=0;k.maj=0;k.ntie=0;
 for(int i=0;i<8;i++)k.diffs[i]=(uint16_t(P[2*i])<<8|P[2*i+1])^(uint16_t(M[2*i])<<8|M[2*i+1]);
 for(int b=0;b<16;b++){
  int count=0;for(int i=0;i<8;i++)count+=(k.diffs[i]>>b)&1;
  k.residual+=min(count,8-count);
  if(count>4)k.maj|=1<<b;
  if(count==4)k.ntie++;
 }
 return k;
}
static bool check_k04(const Packet &P,uint16_t w,const Source&S){
 Packet component{};for(int i=0;i<16;i++)component[i]=P[i]^uint8_t((i%2)?w:(w>>8))^S.mask[i];
 unsigned char out[32];SHA256(component.data(),component.size(),out);
 return memcmp(out,S.target.data(),32)==0;
}
static void synthetic_controls(){
 Packet P{};for(int i=0;i<16;i++)P[i]=uint8_t((37*i+11)%256);
 for(uint16_t poly:{uint16_t(0xc867),uint16_t(0x8bb7),uint16_t(0x5935),uint16_t(0x1023),uint16_t(0x0003)}){
  uint16_t invQ=inv16(uint16_t(1^x128_mod(poly)),poly),invX=inv16(poly,poly);
  array<uint16_t,8> c{};
  for(int i=0;i<8;i++){Packet rotated=transform(P,i,false,false,false);c[i]=crc16(rotated.data(),16,poly);}
  if(derive(c,poly,invQ,invX)!=P)throw runtime_error("synthetic coupon CRC inversion failed");
  uint16_t secret=0xC0DE;Packet M=P;
  for(int i=0;i<16;i++)M[i]^=uint8_t((i%2)?secret:(secret>>8));
  M[0]^=1;M[4]^=2;M[11]^=4;M[15]^=8;
  auto m=score(P,M);if(m.maj!=secret || m.residual!=4)throw runtime_error("synthetic noisy-copy source recovery failed");
 }
}
int main(int argc,char**argv){
 try{
  if(const char* v=getenv("GITHUB_ACTIONS")){if(string(v)=="true")throw runtime_error("Source-bearing original checks must remain local, not public CI");}
  if(argc<4){cerr<<"usage: "<<argv[0]<<" SOURCE_ROOT start_poly end_poly [bit_mirror_mode 0|1|2|3] [local_hit_output_path]\n";return 2;}
  synthetic_controls();Source S=load(argv[1]);int start=max(1,atoi(argv[2])),end=min(65536,atoi(argv[3]));
  int bitsmode=argc>4?atoi(argv[4]):0; // bit0: reflect checkpoint word; bit1: reflect coupon bytes
  if(bitsmode<0||bitsmode>3)throw runtime_error("invalid mode");
  uint64_t models=0,seenpolys=0,checked=0,hits=0,under20=0,under24=0,under28=0,under32=0;
  int best=129,baselineBest=129;uint64_t baselineUnder24=0;
  Packet Mbaseline{};uint64_t rng=0x104c871527a034bdULL;
  for(auto &z:Mbaseline){rng^=rng>>12;rng^=rng<<25;rng^=rng>>27;z=uint8_t((rng*2685821657736338717ull)>>56);}
  auto writehit=[&](const Packet&P,uint16_t w){
   if(argc<6)throw runtime_error("accepted K04 hit, but no private output path was specified");
   ofstream f(argv[5],ios::trunc);for(int i=0;i<16;i++)f<<uppercase<<hex<<setfill('0')<<setw(2)<<int(P[i]^uint8_t((i%2)?w:(w>>8))^S.mask[i]);f<<"\n";
  };
  for(int poly=start;poly<end;poly++){
   if((poly&1)==0 || (__builtin_popcount(uint32_t(poly))&1))continue;
   seenpolys++;
   uint16_t p=uint16_t(poly),invQ=inv16(uint16_t(1^x128_mod(p)),p),invX=inv16(p,p);
   for(int byteswap=0;byteswap<2;byteswap++)for(int dir=0;dir<2;dir++){
    array<uint16_t,8> cs{};
    for(int i=0;i<8;i++){
     auto pair=S.check[dir?((8-i)&7):i][2];
     uint16_t a=byteswap?(uint16_t(pair[1])<<8|pair[0]):(uint16_t(pair[0])<<8|pair[1]);
     if(bitsmode&1)a=bitreverse16(a);cs[i]=a;
    }
    Packet abstract=derive(cs,p,invQ,invX);
    for(int off=0;off<8;off++)for(int rev=0;rev<2;rev++)for(int wordswap=0;wordswap<2;wordswap++){
     Packet P=transform(abstract,off,rev,wordswap,bool(bitsmode&2));models++;
     auto m=score(P,S.copied);best=min(best,m.residual);
     under20+=(m.residual<=20);under24+=(m.residual<=24);under28+=(m.residual<=28);under32+=(m.residual<=32);
     auto b=score(P,Mbaseline);baselineBest=min(baselineBest,b.residual);baselineUnder24+=(b.residual<=24);
     uint16_t tries[9];tries[0]=uint16_t(m.maj);for(int i=0;i<8;i++)tries[i+1]=m.diffs[i];
     for(int i=0;i<9;i++){
      if(any_of(tries,tries+i,[&](uint16_t z){return z==tries[i];}))continue;
      checked++;
      if(check_k04(P,tries[i],S)){hits++;writehit(P,tries[i]);}
     }
    }
   }
  }
  cout<<"poly_count="<<dec<<seenpolys<<" source_models="<<models<<" complete_checks="<<checked
      <<" original_k04_matches="<<hits<<" best_copied_residual_bits="<<best
      <<" comparator_best_residual_bits="<<baselineBest
      <<" copied_models_le20="<<under20<<" copied_models_le24="<<under24
      <<" copied_models_le28="<<under28<<" copied_models_le32="<<under32
      <<" comparator_models_le24="<<baselineUnder24<<" synthetic_controls=PASS\n";
  return 0;
 }catch(const exception &e){cerr<<"Error: "<<e.what()<<"\n";return 3;}
}
