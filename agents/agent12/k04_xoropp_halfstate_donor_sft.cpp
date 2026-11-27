// H-17 K04: exact half-state donor inversion of speculative xoroshiro128++ issuer.
// Reads only permitted spool, route, acceptance and canonical candidate.
// Never reads PDF, never decodes selected ACK2 copy or puts source in public CI.
#include <bits/stdc++.h>
#include <openssl/sha.h>
#include <filesystem>
using namespace std;using U=uint64_t;namespace fs=std::filesystem;
static inline U rol(U x,int n){return (x<<n)|(x>>(64-n));}
static inline int bit(U x,int j){return (x>>j)&1;}
static inline int maj(int a,int b,int c){return (a&b)|(a&c)|(b&c);}
static string readfile(const fs::path&p){if(p.extension()==".pdf")throw runtime_error("no PDF reads");ifstream f(p,ios::binary);if(!f)throw runtime_error("missing input "+p.string());return string(istreambuf_iterator<char>(f),{});}
static string shahex(const string&s){unsigned char d[32];SHA256((const unsigned char*)s.data(),s.size(),d);char o[65];for(int i=0;i<32;i++)sprintf(o+i*2,"%02x",d[i]);return string(o,64);}
static array<uint8_t,16> parsehex16(const string&s){if(s.size()!=32)throw runtime_error("hex length");array<uint8_t,16> r{};for(int i=0;i<16;i++){auto h=s.substr(i*2,2);r[i]=uint8_t(stoul(h,0,16));}return r;}
static string pick(const string&s,const string&name){regex r("\\\""+name+"\\\"\\s*:\\s*\\\"([0-9A-Fa-f]{32,64})\\\"");smatch m;if(!regex_search(s,m,r))throw runtime_error("missing field "+name);return m[1];}
static U word(const array<uint8_t,16>&p,int k,bool little){U x=0;for(int i=0;i<8;i++){int j=k*8+(little?7-i:i);x=(x<<8)|p[j];}return x;}
static pair<U,U> decode(const array<uint8_t,16>&p,int view){U a=word(p,0,view&1),b=word(p,1,view&1);if(view&2)swap(a,b);return {a,b};}
static array<uint8_t,16> encode(U a,U b,int view){array<uint8_t,16>p{};if(view&2)swap(a,b);for(int k=0;k<2;k++){U x=k?b:a;for(int i=0;i<8;i++){int j=(view&1)?i:7-i;p[k*8+j]=uint8_t(x>>(i*8));}}return p;}
static array<U,6> emit(U a,U b){array<U,6>v{};for(int i=0;i<6;i++){v[i]=rol(a+b,17)+a;U t=a^b;a=rol(a,49)^t^(t<<21);b=rol(t,28);}return v;}
// Fast exact inverse: split c=(a<<47)|b, 0<=a<2^17, 0<=b<2^47.
// z = (2^47+1)*a + (2^17+1)*b (mod 2^64).
// Lift by k*2^64, k in {0,1}; gcd(2^47+1, 2^17+1)=3.
// A/3 inverse mod B/3 (43691) = 34956. At most THREE possible a per k.
// Solve b with the modular inverse of B mod 2^64, then verify the exact sum.
// Constant-sized arithmetic inversion rather than 2^17 carry enumeration.
constexpr U ROT_A=(1ULL<<47)+1,ROT_B=(1ULL<<17)+1,ROT_B_INV=0xfff80003fffe0001ULL;
constexpr uint32_t ROT_PERIOD=43691,ROT_A_INV=34956;
template<class F> static inline void invert17(U z,F&&accept){
 unsigned k;
 switch(z%3){case 0:k=0;break;case 2:k=1;break;default:return;}
 U zz=(z%ROT_B)+(k?122881:0);if(zz>=ROT_B)zz-=ROT_B;
 if(zz%3)throw runtime_error("mod inverse divisibility failure");
 U high0=((zz/3)*ROT_A_INV)%ROT_PERIOD;
 for(U high=high0;high<(1ULL<<17);high+=ROT_PERIOD){
  U low=(z-ROT_A*high)*ROT_B_INV;
  if(low>=(1ULL<<47))continue;
  U x=(high<<47)|low;
  if(x+rol(x,17)==z)accept(x);
 }
}
int main(int argc,char**argv){try{
 fs::path root=argc>1?argv[1]:".";fs::path source=fs::exists(root/"resources/acceptance.json")?root/"resources":root;
 string spool=readfile(source/"evidence/print/spool-reconstruction.log");
 string route=readfile(source/"evidence/recovery-routing.json");
 string accept=readfile(source/"acceptance.json");
 string canonical=readfile(root/"candidate.json");
 if(shahex(spool)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083" ||
    shahex(route)!="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5" ||
    shahex(accept)!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")throw runtime_error("original source hash mismatch");
 array<uint8_t,16> mask=parsehex16(pick(route,"masked_component"));
 string target=pick(accept,"K04");transform(target.begin(),target.end(),target.begin(),::tolower);
 regex rowre("JOB=(PS-261003-[0-9]{4}) ATTEMPT=([0-9]+) STATE=([A-Z]+) CLASS=([A-Z]+) PAYLOAD=([0-9A-F]{32}) DEST=([a-z]+)");
 vector<array<uint8_t,16>>donor16;
 array<uint8_t,16> p1{},p3{};int count=0,nack=0,nfuture=0;
 istringstream lines(spool);string line;while(getline(lines,line)){
  smatch m;if(!regex_search(line,m,rowre))continue;count++;
  bool selected=(m[1]=="PS-261003-0417");int attempt=stoi(m[2]);
  if(selected && attempt==2){nack++;continue;}
  if(selected && attempt==3){p3=parsehex16(m[5]);nfuture++;continue;}
  auto packet=parsehex16(m[5]);if(selected && attempt==1)p1=packet;
  donor16.push_back(packet);
 }
 if(count!=133||nack!=1||nfuture!=1||donor16.size()!=131)throw runtime_error("source row mismatch");
 donor16.push_back(mask);donor16.push_back(parsehex16(pick(route,"desk_nonce")));
 for(const char*slot:{"K01","K02","K03","K05","K06","K07"})donor16.push_back(parsehex16(pick(canonical,slot)));
 set<U> donors;for(auto&d:donor16)for(int k=0;k<2;k++)for(int endian=0;endian<2;endian++)donors.insert(word(d,k,endian));
 mt19937_64 r(0x20261127);U planted_a=r(),planted_b=r();auto planted=emit(planted_a,planted_b);int synthetic_all=0;
 invert17(planted[0]+planted_b,[&](U c){U a=c-planted_b;auto out=emit(a,planted_b);if(out==planted&&a==planted_a)synthetic_all++;});
 if(synthetic_all!=1)throw runtime_error("synthetic full-state inversion failed");
 uint64_t inverse_roots=0,first_pair_states=0,commit_matches=0,third_matches=0;
 for(int view=0;view<4;view++){
  auto [y0,y1]=decode(p1,view);auto [future4,future5]=decode(p3,view);
  for(U b0:donors){invert17(y0+b0,[&](U c){inverse_roots++;U a0=c-b0;auto yy=emit(a0,b0);if(yy[0]!=y0||yy[1]!=y1)return;
   first_pair_states++;auto coupon=encode(yy[2],yy[3],view);array<uint8_t,16>comp{};for(int i=0;i<16;i++)comp[i]=coupon[i]^mask[i];
   unsigned char dig[32];SHA256(comp.data(),16,dig);char h[65];for(int i=0;i<32;i++)sprintf(h+i*2,"%02x",dig[i]);
   if(string(h,64)==target)commit_matches++;
   if(yy[4]==future4 && yy[5]==future5)third_matches++;
  });}
  cout<<"view="<<view<<" cumulative_inverse_roots="<<inverse_roots<<" first_pair_states="<<first_pair_states<<" original_commitment_hits="<<commit_matches<<"\n"<<flush;
 }
 cout<<"SUMMARY safe_donor16="<<donor16.size()<<" unique_b0="<<donors.size()<<" views=4 original_compared="<<donors.size()*4<<" synthetic_planted_full_recovery="<<synthetic_all<<" inverse_roots="<<inverse_roots<<" samejob_first_pair_models="<<first_pair_states<<" K04_hits="<<commit_matches<<" REQUESTED3_replay="<<third_matches<<" selected_ACK2_decoded=false restricted_PDF_read=false\n";
 return 0;
 }catch(const exception&e){cerr<<"FATAL: "<<e.what()<<"\n";return 3;}}
