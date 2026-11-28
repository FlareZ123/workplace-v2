// LOCAL-ONLY original-state xoroshiro128++ K04 complete-coupon expansion.
// Original intact REQUESTED1 state is supplied in a PRIVATE 0600 file.
// Selected ACK2 never fitted. Full unmodified K04 SHA256 check comes first.
// Original source processing forbidden in public CI; outputs aggregate only.
// Build: c++ -O3 -std=c++17 this.cpp -lcrypto -o private_binary
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <chrono>
#include <vector>
#include <iterator>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <openssl/sha.h>
using u64=std::uint64_t;
using Data=std::array<unsigned char,16>;
using Hash=std::array<unsigned char,32>;
static constexpr const char* SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static constexpr const char* ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static constexpr const char* ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static inline u64 rol(u64 x,unsigned n){return (x<<n)|(x>>(64-n));}
static inline u64 ror(u64 x,unsigned n){return (x>>n)|(x<<(64-n));}
struct State{u64 a,b;};
static u64 draw(State s){return rol(s.a+s.b,17)+s.a;}
static u64 next(State &s){u64 y=draw(s),t=s.a^s.b;s.a=rol(s.a,49)^t^(t<<21);s.b=rol(t,28);return y;}
static State prev(State s){u64 t=ror(s.b,28);u64 a=ror(s.a^t^(t<<21),49);return {a,a^t};}
static Data pack(u64 a,u64 b,bool little,bool swap){
 if(swap)std::swap(a,b);
 Data result{};
 for(int j=0;j<8;++j){int shift=little?8*j:8*(7-j);result[j]=(a>>shift)&255;result[j+8]=(b>>shift)&255;}
 return result;
}
static std::string hex(const unsigned char* v,std::size_t n){static const char T[]="0123456789abcdef";std::string result;result.reserve(2*n);for(std::size_t j=0;j<n;++j){result.push_back(T[v[j]>>4]);result.push_back(T[v[j]&15]);}return result;}
static std::vector<unsigned char> unhex(std::string s){
 if(s.size()%2)throw std::runtime_error("Odd-length hex");
 std::vector<unsigned char> result;
 for(std::size_t i=0;i<s.size();i+=2){char *end=nullptr;auto value=std::strtoul(s.substr(i,2).c_str(),&end,16);
  if(!end||*end||value>255)throw std::runtime_error("Bad hex");
  result.push_back((unsigned char)value);}
 return result;
}
static std::string textfile(const std::string& filename){std::ifstream f(filename,std::ios::binary);if(!f)throw std::runtime_error("Cannot open named source");return {std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>()};}
static std::string pinned(const std::string& filename,const char* expected){std::string s=textfile(filename);Hash digest{};SHA256((const unsigned char*)s.data(),s.size(),digest.data());if(hex(digest.data(),32)!=expected)throw std::runtime_error("Original source checksum mismatch");return s;}
static Data bytes16(std::string h){auto x=unhex(h);if(x.size()!=16)throw std::runtime_error("Not exactly sixteen bytes");Data out;std::copy(x.begin(),x.end(),out.begin());return out;}
static Hash bytes32(std::string h){auto x=unhex(h);if(x.size()!=32)throw std::runtime_error("Not SHA256 digest length");Hash out;std::copy(x.begin(),x.end(),out.begin());return out;}
static std::string findone(const std::string &src,std::string re){std::regex pattern(re);std::smatch result;if(!std::regex_search(src,result,pattern))throw std::runtime_error("Original required source token absent");return result[1].str();}
static u64 parse_u64(std::string s){if(s.size()!=16||s.find_first_not_of("0123456789abcdefABCDEF")!=std::string::npos)throw std::runtime_error("Private state words require exactly 16 hex digits");return std::stoull(s,nullptr,16);}
static State private_state(const std::string &path){
 struct stat st{};if(lstat(path.c_str(),&st)<0||!S_ISREG(st.st_mode)||((st.st_mode&077)!=0))throw std::runtime_error("Private state must be a mode 0600 regular file, not symlink");
 int fd=open(path.c_str(),O_RDONLY|O_NOFOLLOW);if(fd<0)throw std::runtime_error("Cannot open private state");char buf[256];ssize_t n=read(fd,buf,sizeof(buf)-1);close(fd);if(n<=0||n>=200)throw std::runtime_error("Invalid private state length");buf[n]=0;std::istringstream in(buf);std::string a,b,trailing;if(!(in>>a>>b)||(in>>trailing))throw std::runtime_error("Private state must contain exactly two 64-bit hex words");return {parse_u64(a),parse_u64(b)};
}
static void secure_escrow(const std::string &file,const Data& value){
 int fd=open(file.c_str(),O_WRONLY|O_APPEND|O_CREAT|O_NOFOLLOW,0600);if(fd<0)throw std::runtime_error("Could not open private hit escrow");
 if(fchmod(fd,0600)<0){close(fd);throw std::runtime_error("Could not protect hit escrow");}
 std::string s=hex(value.data(),16)+"\n";ssize_t n=write(fd,s.data(),s.size());if(n!=(ssize_t)s.size()){close(fd);throw std::runtime_error("Could not escrow entire hit");}fsync(fd);close(fd);
}
struct Metrics{std::uint64_t pairs=0,checks=0,hits=0,later_holdout_replays=0;};
struct Trial{
 Data mask,source,later;Hash target;bool has_later=false;
 bool source_little=false,source_swap=false;std::string escrow;Metrics counts;
 void check(u64 a,u64 b){
  ++counts.pairs;
  if(has_later&&pack(a,b,source_little,source_swap)==later)++counts.later_holdout_replays;
  for(int layout=0;layout<4;++layout){
   Data coupon=pack(a,b,(layout&2)!=0,(layout&1)!=0),component{};
   for(int i=0;i<16;++i)component[i]=coupon[i]^mask[i];
   Hash digest{};SHA256(component.data(),component.size(),digest.data());++counts.checks;
   if(digest==target){++counts.hits;if(!escrow.empty())secure_escrow(escrow,component);}
  }
 }
};
static Metrics scan(State initial,Trial& trial,std::uint64_t forward,std::uint64_t reverse){
 State source=initial;u64 s0=next(source),s1=next(source);
 if(pack(s0,s1,trial.source_little,trial.source_swap)!=trial.source)throw std::runtime_error("PRIVATE STATE DOES NOT EXACTLY REPLAY intact REQUESTED1");
 if(forward){u64 older=next(source);for(std::uint64_t i=0;i<forward;++i){u64 newer=next(source);trial.check(older,newer);older=newer;}}
 if(reverse){State earlier=prev(initial);u64 newer=draw(earlier);for(std::uint64_t i=0;i<reverse;++i){earlier=prev(earlier);u64 older=draw(earlier);trial.check(older,newer);newer=older;}}
 return trial.counts;
}
static bool envci(){const char* a=getenv("CI"),*b=getenv("GITHUB_ACTIONS");return (a&&*a)||(b&&*b);}
static void synthetic(){
 State initial{0x915D2A7F0939C8E1ULL,0xD7AE014FC1132049ULL};State f=initial;u64 x0=next(f),x1=next(f);
 Data source=pack(x0,x1,false,true),mask{};for(int j=0;j<16;++j)mask[j]=(31*j+17)&255;
 for(int direction=0;direction<2;++direction){
  Trial t{};t.mask=mask;t.source=source;t.source_swap=true;
  u64 older=0,newer=0;const unsigned chosen=direction?41:512;
  if(!direction){State state=initial;next(state);next(state);older=next(state);for(unsigned i=0;i<=chosen;++i){newer=next(state);if(i<chosen)older=newer;}}
  else{State state=prev(initial);newer=draw(state);for(unsigned i=0;i<=chosen;++i){state=prev(state);older=draw(state);if(i<chosen)newer=older;}}
  auto coupon=pack(older,newer,true,true);Data component{};for(int j=0;j<16;++j)component[j]=coupon[j]^mask[j];SHA256(component.data(),16,t.target.data());
  auto m=scan(initial,t,direction?0:1024,direction?128:0);
  if(m.hits!=1)throw std::runtime_error("Synthetic planted complete commitment missing");
  std::cout<<"SYNTHETIC_ONLY direction="<<(direction?"reverse":"forward")<<" pair_count="<<m.pairs<<" full_SHA256_checks="<<m.checks<<" planted_hits="<<m.hits<<"\n";
 }
}
int main(int argc,char** argv){
 try{
  bool syn=false;std::string root="resources",state_file,escrow,view="big/ba";std::uint64_t forward=10000000,reverse=0;
  for(int i=1;i<argc;++i){std::string arg=argv[i];auto val=[&](){if(i+1>=argc)throw std::runtime_error("Missing argument value");return std::string(argv[++i]);};
   if(arg=="--synthetic")syn=true;else if(arg=="--resources-root")root=val();else if(arg=="--state-file")state_file=val();else if(arg=="--hit-escrow")escrow=val();else if(arg=="--source-view")view=val();else if(arg=="--forward-pairs")forward=std::stoull(val());else if(arg=="--reverse-pairs")reverse=std::stoull(val());else throw std::runtime_error("Unknown flag "+arg);
  }
  if(syn){synthetic();return 0;}
  if(envci())throw std::runtime_error("Original-source run forbidden in CI");
  if(state_file.empty()||escrow.empty())throw std::runtime_error("Private state and out-of-repository hit escrow required");
  if(view!="big/ab"&&view!="big/ba"&&view!="little/ab"&&view!="little/ba")throw std::runtime_error("Invalid source serializer");
  if(forward>1000000000ULL||reverse>1000000000ULL)throw std::runtime_error("Excessive scan bound");
  auto spool=pinned(root+"/evidence/print/spool-reconstruction.log",SPOOL_SHA);
  auto routing=pinned(root+"/evidence/recovery-routing.json",ROUTE_SHA);
  auto acceptance=pinned(root+"/acceptance.json",ACCEPT_SHA);
  auto source=bytes16(findone(spool,"JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench"));
  auto later=bytes16(findone(spool,"JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench"));
  auto mask=bytes16(findone(routing,"\\\"masked_component\\\"[[:space:]]*:[[:space:]]*\\\"([0-9A-F]{32})\\\""));
  auto target=bytes32(findone(acceptance,"\\\"K04\\\"[[:space:]]*:[[:space:]]*\\\"([0-9a-f]{64})\\\""));
  Trial trial{};trial.mask=mask;trial.target=target;trial.source=source;trial.later=later;trial.has_later=true;trial.source_little=(view.rfind("little",0)==0);trial.source_swap=(view.substr(view.find('/')+1)=="ba");trial.escrow=escrow;
  State state=private_state(state_file);
  auto started=std::chrono::steady_clock::now();auto m=scan(state,trial,forward,reverse);
  double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  std::cout<<"AGGREGATE_ONLY producer=xoroshiro128++ view="<<view<<" forward_pairs="<<forward<<" reverse_pairs="<<reverse<<" pairs="<<m.pairs<<" complete_SHA256_checks="<<m.checks<<" original_K04_hits="<<m.hits<<" later_request_replay_count="<<m.later_holdout_replays<<" elapsed_seconds="<<std::fixed<<std::setprecision(2)<<elapsed<<"\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<"FAILED "<<e.what()<<"\n";return 2;}
}
