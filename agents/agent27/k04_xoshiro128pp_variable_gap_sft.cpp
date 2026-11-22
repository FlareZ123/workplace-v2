// H17 K04: xoshiro128++ unknown output gap after first intact request.
// Exact 2^32 root inversion reuses the proven original source-pinned SFT.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main prior_exact_inverse_main
#include "k04_xoshiro128pp_exact_inverse_sft.cpp"
#undef main
#pragma GCC diagnostic pop
#include <stdexcept>
#include <iterator>
#include <cctype>
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
Score scan(S state,int view,const S& holdout,const B&mask,const Hash& target,std::uint32_t maxstart){
 Score score;S ring{};
 for(std::uint32_t i=0;i<maxstart+4;i++){
  ring[i%4]=advance(state);
  if(i<7)continue;
  const auto start=i-3;
  S window{};for(int j=0;j<4;j++)window[j]=ring[(start+j)%4];
  auto coupon=encode(window,view);
  if(masked_sha256(coupon,mask)==target){score.sha_hits++;score.sha_positions.push_back(start);}
  if(start>=8&&window==holdout){score.holdout_hits++;score.holdout_positions.push_back(start);}
  ++score.windows;
 }
 return score;
}
void seeded_positive(){
 S seed{0xDEADBEEF,0xA1B2C3D4,0x13579BDF,0x2468ACE0};
 S s=seed;S coupon{},third{};
 for(int i=0;i<=2049+3;i++){
  U word=advance(s);
  if(i>=33&&i<37)coupon[i-33]=word;
  if(i>=2049&&i<2053)third[i-2049]=word;
 }
 B mask=unhex(MASK);
 auto digest=masked_sha256(encode(coupon,1),mask);
 auto score=scan(seed,1,third,mask,digest,4096);
 if(score.sha_hits!=1||score.holdout_hits!=1||score.sha_positions[0]!=33||score.holdout_positions[0]!=2049)
  throw std::runtime_error("seeded variable-gap positive failed");
 std::cerr<<"SYNTHETIC_HIDDEN_COUPON_STAGE_33_AND_HOLDOUT_STAGE_2049_PASS\n";
}
int main(int argc,char**argv){
 try{
  seeded_positive();
  const std::string path=argc>=2?argv[1]:"resources/evidence/print/spool-reconstruction.log";
  const std::uint32_t maxstart=argc>=3?static_cast<std::uint32_t>(std::stoul(argv[2])):1048575;
  if(maxstart<12||maxstart>1048575)throw std::runtime_error("scan range 12..1048575");
  std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing source");
  std::string spool(std::istreambuf_iterator<char>{f},{});
  unsigned char digest[32];SHA256(reinterpret_cast<const unsigned char*>(spool.data()),spool.size(),digest);
  std::string sha=hex(digest,32);std::transform(sha.begin(),sha.end(),sha.begin(),::tolower);
  if(sha!=SPOOL_SHA)throw std::runtime_error("source SHA mismatch");
  B first=record(spool,1,"REQUESTED"),last=record(spool,3,"REQUESTED"),mask=unhex(MASK);
  Hash target=target_sha();
  for(int view=0;view<4;view++){
   S o=decode(first,view),hold=decode(last,view);
   std::atomic<int> roots{0},sha_hits{0},holdout_hits{0};
   std::mutex output_lock;
   const auto begin=std::chrono::steady_clock::now();
   #pragma omp parallel for schedule(static)
   for(std::int64_t k=0;k<(1LL<<32);k++){
    U a2=static_cast<U>(k);
    if(!fourth(o[0],o[1],o[2],o[3],a2))continue;
    S state=invert(o[0],o[1],o[2],a2);
    auto check=emit(state);if(!std::equal(o.begin(),o.end(),check.begin()))throw std::runtime_error("inverse inconsistent");
    ++roots;
    auto result=scan(state,view,hold,mask,target,maxstart);
    sha_hits+=result.sha_hits;holdout_hits+=result.holdout_hits;
    std::lock_guard<std::mutex> lock(output_lock);
    std::cout<<"ROOT view="<<view<<" trial="<<std::hex<<a2<<std::dec<<" windows="<<result.windows
      <<" original_k04_hits="<<result.sha_hits<<" intact_request3_hits="<<result.holdout_hits;
    for(auto n:result.sha_positions)std::cout<<" sha_at="<<n;
    for(auto n:result.holdout_positions)std::cout<<" hold_at="<<n;
    std::cout<<"\n";
   }
   double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
   std::cout<<"SUMMARY view="<<view<<" root_trials=4294967296 roots="<<roots
      <<" windows_each="<<(maxstart-3)<<" original_k04_hits="<<sha_hits
      <<" intact_request3_hits="<<holdout_hits<<" seconds="<<sec<<"\n"<<std::flush;
  }
 }catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 2;}
}
