// H17 K04: xoshiro128++ earlier 16:45 LABEL/ACK packet anchors unknown-gap followup.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main prior_exact_inverse_main
#include "k04_xoshiro128pp_exact_inverse_sft.cpp"
#undef main
#pragma GCC diagnostic pop
#include <iterator>
using Hash=std::array<unsigned char,32>;
struct Score {std::uint64_t windows=0;int sha_hits=0;int holdout_hits=0;std::vector<std::uint32_t> sha_positions, holdout_positions;};
inline U advance(S &s){
 U output=L(s[0]+s[3],7)+s[0];
 U t=s[1]<<9;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=L(s[3],11);
 return output;
}
Hash masked_sha256(const B &candidate,const B&mask){
 B comp{};for(int i=0;i<16;i++)comp[i]=candidate[i]^mask[i];
 Hash h{};SHA256(comp.data(),comp.size(),h.data());return h;
}
Hash target_sha(){
 std::string expected=K04_SHA;Hash h{};
 for(size_t i=0;i<32;i++){
  auto hval=[](char c)->int {if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;throw std::runtime_error("bad target");};
  h[i]=(hval(expected[2*i])<<4)|hval(expected[2*i+1]);
 }
 return h;
}

struct Counts {std::uint64_t windows=0;std::vector<U> selected,first_request,last_request;};
B label_record(const std::string& spool){
 const std::string sig="JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=";
 auto i=spool.find(sig);
 if(i==std::string::npos||spool.find(sig,i+1)!=std::string::npos)throw std::runtime_error("label missing or ambiguous");
 if(spool.substr(i+sig.size()+32,11)!=" DEST=bench")throw std::runtime_error("label wrong destination");
 return unhex(spool.substr(i+sig.size(),32));
}
Counts search_label(S state,int view,const S&first,const S&third,const B&mask,const Hash&target,U maxstart){
 Counts c;S ring{};
 for(U i=0;i<maxstart+4;i++){
  ring[i%4]=advance(state);
  if(i<7)continue;
  U start=i-3;
  S window{};for(int k=0;k<4;k++)window[k]=ring[(start+k)%4];
  if(start>=4&&window==first)c.first_request.push_back(start);
  if(start>=12&&window==third)c.last_request.push_back(start);
  if(start>=8&&masked_sha256(encode(window,view),mask)==target)c.selected.push_back(start);
  ++c.windows;
 }
 return c;
}
void planted_early_label(){
 S state{0xDEADBEEF,0xA1B2C3D4,0x13579BDF,0x2468ACE0};
 S s=state, req1{},coupon{},req3{};
 for(U i=0;i<=82+3;i++){
  U w=advance(s);
  if(i>=17&&i<21)req1[i-17]=w;
  if(i>=33&&i<37)coupon[i-33]=w;
  if(i>=82&&i<86)req3[i-82]=w;
 }
 B mask=unhex(MASK);
 auto target=masked_sha256(encode(coupon,3),mask);
 auto result=search_label(state,3,req1,req3,mask,target,256);
 if(result.first_request!=std::vector<U>{17}||result.selected!=std::vector<U>{33}||result.last_request!=std::vector<U>{82})
  throw std::runtime_error("planted triple-stage LABEL source positive failed");
 std::cerr<<"SYNTHETIC_LABEL_REQUEST_17_COUPON_33_REQUEST_82_PASS\n";
}
int main(int argc,char**argv){
 try{
  planted_early_label();
  const std::string path=argc>=2?argv[1]:"resources/evidence/print/spool-reconstruction.log";
  const U maxstart=argc>=3?static_cast<U>(std::stoul(argv[2])):1048575;
  if(maxstart<12||maxstart>1048575)throw std::runtime_error("scan bound 12..1048575");
  std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing source");
  std::string spool(std::istreambuf_iterator<char>{f},{});
  unsigned char dig[32];SHA256(reinterpret_cast<const unsigned char*>(spool.data()),spool.size(),dig);
  std::string pin=hex(dig,32);std::transform(pin.begin(),pin.end(),pin.begin(),::tolower);
  if(pin!=SPOOL_SHA)throw std::runtime_error("source SHA mismatch");
  const std::string mode=argc>=4?argv[3]:"label";
  B label{},request1{},request3{},mask=unhex(MASK);
  if(mode=="label"){
   label=label_record(spool);
   request1=record(spool,1,"REQUESTED");
   request3=record(spool,3,"REQUESTED");
  }else if(mode=="ordinary"){
   const std::string a="JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=FBBBC54356483F5864BB3F06794518A5 DEST=store";
   const std::string b="JOB=PS-261003-0301 ATTEMPT=1 STATE=ACK CLASS=STORES PAYLOAD=64176B6C3A91BD06B12FC0D90B3A7DB4 DEST=bench";
   const std::string c="JOB=PS-261003-0302 ATTEMPT=1 STATE=ACK CLASS=STORES PAYLOAD=3531D8AB362BB040E7702CE23A8D5420 DEST=store";
   if(spool.find(a)==std::string::npos||spool.find(b)==std::string::npos||spool.find(c)==std::string::npos)
    throw std::runtime_error("original source early printer anchors mismatch");
   label=unhex("FBBBC54356483F5864BB3F06794518A5");
   request1=unhex("64176B6C3A91BD06B12FC0D90B3A7DB4");
   request3=unhex("3531D8AB362BB040E7702CE23A8D5420");
  }else throw std::runtime_error("mode must be label or ordinary");
  Hash target=target_sha();
  for(int view=0;view<4;view++){
   S o=decode(label,view),first=decode(request1,view),third=decode(request3,view);
   std::atomic<int> roots{0},first_hits{0},sha_hits{0},third_hits{0};
   std::mutex mutex;auto begin=std::chrono::steady_clock::now();
   #pragma omp parallel for schedule(static)
   for(std::int64_t trial=0;trial<(1LL<<32);trial++){
    U a2=static_cast<U>(trial);
    if(!fourth(o[0],o[1],o[2],o[3],a2))continue;
    S seed=invert(o[0],o[1],o[2],a2);
    auto generated=emit(seed);
    if(!std::equal(o.begin(),o.end(),generated.begin()))throw std::runtime_error("label inverse inconsistent");
    ++roots;
    Counts result=search_label(seed,view,first,third,mask,target,maxstart);
    first_hits+=result.first_request.size();sha_hits+=result.selected.size();third_hits+=result.last_request.size();
    std::lock_guard<std::mutex> lock(mutex);
    std::cout<<"ROOT mode="<<mode<<" view="<<view<<" trial="<<std::hex<<a2<<std::dec<<" windows="<<result.windows
      <<" request1_hits="<<result.first_request.size()<<" original_K04_hits="<<result.selected.size()
      <<" request3_hits="<<result.last_request.size();
    for(U i:result.first_request)std::cout<<" request1_at="<<i;
    for(U i:result.selected)std::cout<<" K04_at="<<i;
    for(U i:result.last_request)std::cout<<" request3_at="<<i;
    std::cout<<"\n";
   }
   double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
   std::cout<<"SUMMARY mode="<<mode<<" view="<<view<<" exact_trials=4294967296 roots="<<roots
     <<" windows_each="<<(maxstart-3)<<" REQUESTED1="<<first_hits
     <<" K04_SHA="<<sha_hits<<" REQUESTED3="<<third_hits<<" seconds="<<sec<<"\n"<<std::flush;
  }
 }catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 2;}
}
