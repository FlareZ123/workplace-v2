// K04: exact xoshiro128++ source-packet inverse, without fitting the ACK.
// C++17 + OpenSSL + OpenMP. Source is an unmodified printer spool.
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string>
#include <vector>
#include <algorithm>
#include <openssl/sha.h>
using U=std::uint32_t;
using B=std::array<unsigned char,16>;
using S=std::array<U,4>;
constexpr char DIGITS[]="0123456789ABCDEF";
constexpr char SPOOL_SHA[]="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
constexpr char K04_SHA[]="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
constexpr char MASK[]="8556C8CB6140A7F9A5123AC7571BEE1C";
inline U L(U x,int n){return (x<<n)|(x>>(32-n));}
inline U R(U x,int n){return (x>>n)|(x<<(32-n));}
std::string hex(const unsigned char* a,size_t n){
 std::string s;for(size_t i=0;i<n;i++){s+=DIGITS[a[i]>>4];s+=DIGITS[a[i]&15];}return s;
}
B unhex(const std::string& s){
 if(s.size()!=32)throw std::runtime_error("invalid 16-byte hex length");
 B b{};for(int i=0;i<16;i++){
  auto d=[](char c)->int{if(c>='0'&&c<='9')return c-'0';if(c>='A'&&c<='F')return c-'A'+10;throw std::runtime_error("invalid hex digit");};
  b[i]=(d(s[2*i])<<4)|d(s[2*i+1]);
 }return b;
}
S decode(const B& b,int view){
 S w{};for(int i=0;i<4;i++){
  int k=view<2?i:3-i;
  for(int j=0;j<4;j++)w[i]=(w[i]<<8)|b[4*k+(view%2==0?3-j:j)];
 }return w;
}
B encode(const S& w,int view){
 B b{};for(int i=0;i<4;i++){
  int k=view<2?i:3-i;
  for(int j=0;j<4;j++)b[4*k+(view%2==0?j:3-j)]=static_cast<unsigned char>(w[i]>>(8*j));
 }return b;
}
std::array<U,12> emit(S s){
 std::array<U,12> out{};for(int i=0;i<12;i++){
  out[i]=L(s[0]+s[3],7)+s[0];
  U t=s[1]<<9;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=L(s[3],11);
 }return out;
}
// Any candidate a2=s0 after 2 transitions determines the entire initial state
// given O0,O1,O2, because s3(t+1)=rotl(s0(t) XOR s0(t+1),11).
S invert(U o0,U o1,U o2,U a2){
 U a1=a2^R(R(o2-a2,7)-a2,11);
 U a0=a1^R(R(o1-a1,7)-a1,11);
 U d0=R(o0-a0,7)-a0;
 U b0=a0^d0^a1;
 U c0=(a1^L(a0^a1,11)^a2)^b0^a0;
 return {a0,b0,c0,d0};
}
inline bool fourth(U o0,U o1,U o2,U o3,U a2){
 U a1=a2^R(R(o2-a2,7)-a2,11);
 U a0=a1^R(R(o1-a1,7)-a1,11);
 U d0=R(o0-a0,7)-a0;
 U b0=a0^d0^a1;
 U a3=a2^L(a1^a2,11)^a1^b0^(b0<<9);
 U d3=L(a2^a3,11);
 return L(a3+d3,7)+a3==o3;
}
B record(const std::string& spool,int attempt,const std::string& state){
 auto signature="JOB=PS-261003-0417 ATTEMPT="+std::to_string(attempt)+" STATE="+state+" CLASS=RECOVER PAYLOAD=";
 auto pos=spool.find(signature);
 if(pos==std::string::npos||spool.find(signature,pos+1)!=std::string::npos)throw std::runtime_error("expected exactly one source record");
 if(spool.substr(pos+signature.size()+32,11)!=" DEST=bench")throw std::runtime_error("wrong job destination");
 return unhex(spool.substr(pos+signature.size(),32));
}
void controls(){
 std::uint64_t x=0xDEADBEEFBAD5EED1ULL;
 auto next=[&]()->U{x^=x<<13;x^=x>>7;x^=x<<17;return static_cast<U>(x);};
 S planted{};bool small=false;
 for(int i=0;i<100000;i++){
  S state{next(),next(),next(),next()};auto w=emit(state);
  S s=state;for(int j=0;j<2;j++){
   U t=s[1]<<9;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=L(s[3],11);
  }
  if(invert(w[0],w[1],w[2],s[0])!=state||!fourth(w[0],w[1],w[2],w[3],s[0]))throw std::runtime_error("synthetic inverse failure");
  if(!small&&s[0]<(1u<<23)){planted=state;small=true;}
 }
 if(!small)throw std::runtime_error("missing synthetic fixture");
 auto w=emit(planted);std::uint64_t matches=0;
 for(std::uint64_t i=0;i<(1u<<23);i++){
  U a2=static_cast<U>(i);
  if(!fourth(w[0],w[1],w[2],w[3],a2))continue;
  auto recovered=invert(w[0],w[1],w[2],a2);
  if(emit(recovered)!=w)continue;
  if(recovered!=planted)throw std::runtime_error("synthetic collision");
  matches++;
 }
 if(matches!=1)throw std::runtime_error("blind planted complete-coupon search failed");
 std::cerr<<"100000_EXACT_STATE_CONTROLS_PASS; BLIND_2^23_PLANTED_COUPON_PASS\n";
}
int main(int argc,char**argv){
 try{
  controls();
  const std::string path=argc>=2?argv[1]:"resources/evidence/print/spool-reconstruction.log";
  std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing original spool");
  std::string spool(std::istreambuf_iterator<char>{f},{});
  unsigned char digest[32];SHA256(reinterpret_cast<const unsigned char*>(spool.data()),spool.size(),digest);
  std::string check=hex(digest,32);std::transform(check.begin(),check.end(),check.begin(),::tolower);
  if(check!=SPOOL_SHA)throw std::runtime_error("spool source SHA mismatch");
  auto first=record(spool,1,"REQUESTED"),copied=record(spool,2,"ACK"),third=record(spool,3,"REQUESTED");
  auto mask=unhex(MASK);
  for(int view=0;view<4;view++){
   auto o=decode(first,view),held=decode(third,view);
   std::atomic<int> states{0},held_pass{0},hash_pass{0};std::mutex mutex;
   auto begin=std::chrono::steady_clock::now();
   #pragma omp parallel for schedule(static)
   for(std::int64_t k=0;k<(1LL<<32);k++){
    U a2=static_cast<U>(k);
    if(!fourth(o[0],o[1],o[2],o[3],a2))continue;
    ++states;auto gen=emit(invert(o[0],o[1],o[2],a2));
    if(!std::equal(o.begin(),o.end(),gen.begin()))throw std::runtime_error("inversion mismatch");
    bool holds=std::equal(held.begin(),held.end(),gen.begin()+8);
    if(holds)++held_pass;
    S mid{};std::copy(gen.begin()+4,gen.begin()+8,mid.begin());
    auto coupon=encode(mid,view);B component{};
    for(int i=0;i<16;i++)component[i]=coupon[i]^mask[i];
    unsigned char h[32];SHA256(component.data(),component.size(),h);
    std::string sha=hex(h,32);std::transform(sha.begin(),sha.end(),sha.begin(),::tolower);
    bool pass=sha==K04_SHA;if(pass)++hash_pass;
    std::lock_guard<std::mutex> lock(mutex);
    std::cout<<"CANDIDATE view="<<view<<" a2="<<std::hex<<a2<<std::dec<<" coupon="<<hex(coupon.data(),16)
      <<" component="<<hex(component.data(),16)<<" heldout3="<<(holds?"PASS":"MISS")
      <<" K04_SHA="<<(pass?"PASS":"MISS")<<" copied_ACK="<<(coupon==copied?"MATCH":"DIFF")<<"\n";
   }
   auto sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
   std::cout<<"SUMMARY view="<<view<<" examined=4294967296 states="<<states
     <<" heldout3_matches="<<held_pass<<" K04_SHA_hits="<<hash_pass<<" seconds="<<sec<<"\n"<<std::flush;
  }
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
