// H17 K04: exact original MWC64X 32-bit-output 64-bit-state inverse.
// David Thomas multiplier 4294883355, output x XOR c before state update.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main prior_exact_inverse_main
#include "k04_xoshiro128pp_exact_inverse_sft.cpp"
#undef main
#pragma GCC diagnostic pop
#include <cstdint>
#include <stdexcept>
#include <iterator>
constexpr U A=4294883355u;
struct MWC {U x,c;};
U next_mwc(MWC &s){
 U output=s.x^s.c;
 std::uint64_t step=static_cast<std::uint64_t>(A)*s.x+s.c;
 s.x=static_cast<U>(step);s.c=static_cast<U>(step>>32);
 return output;
}
std::array<U,12> emitted(MWC state){
 std::array<U,12> outputs{};for(auto &word:outputs)word=next_mwc(state);return outputs;
}
void synthetic(){
 std::uint64_t z=0x1234ABCDEF998877ULL;
 auto sample=[&](){z^=z<<13;z^=z>>7;z^=z<<17;return static_cast<U>(z);};
 for(int i=0;i<100000;i++){
  MWC s{sample(),sample()%A};auto seq=emitted(s);
  if(seq[0]!=(s.x^s.c))throw std::runtime_error("output first mismatch");
  MWC t=s;for(int j=0;j<12;j++)if(next_mwc(t)!=seq[j])throw std::runtime_error("forward mismatch");
 }
 MWC planted{0x003AC51Fu,0x98ABCDF0u};auto observation=emitted(planted);
 int matches=0;
 for(std::uint64_t trial=0;trial<(1u<<22);trial++){
  U x=static_cast<U>(trial),c=x^observation[0];if(c>=A)continue;
  MWC s{x,c};if(next_mwc(s)!=observation[0]||next_mwc(s)!=observation[1])continue;
  if(next_mwc(s)!=observation[2]||next_mwc(s)!=observation[3])continue;
  if(x!=planted.x||c!=planted.c)throw std::runtime_error("unexpected planted state");
  ++matches;
 }
 if(matches!=1)throw std::runtime_error("blind planted state inversion failed");
 std::cerr<<"100000_FORWARD_CONTROLS_PASS; BLIND_2^22_FULL_STATE_INVERSE_PASS\n";
}
int main(int argc,char**argv){
 try{
  synthetic();
  std::string path=argc>=2?argv[1]:"resources/evidence/print/spool-reconstruction.log";
  std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing source");
  std::string spool(std::istreambuf_iterator<char>{f},{});
  unsigned char digest[32];SHA256(reinterpret_cast<const unsigned char*>(spool.data()),spool.size(),digest);
  std::string sh=hex(digest,32);std::transform(sh.begin(),sh.end(),sh.begin(),::tolower);
  if(sh!=SPOOL_SHA)throw std::runtime_error("source SHA mismatch");
  B first=record(spool,1,"REQUESTED"),third=record(spool,3,"REQUESTED"),mask=unhex(MASK);
  for(int view=0;view<4;view++){
   S o=decode(first,view),h=decode(third,view);
   std::atomic<int> pair_states{0},four_states{0},holdout_matches{0},sha_matches{0};
   std::mutex mutex;
   auto start=std::chrono::steady_clock::now();
   #pragma omp parallel for schedule(static)
   for(std::int64_t trial=0;trial<(1LL<<32);trial++){
    U x=static_cast<U>(trial),c=x^o[0];
    if(c>=A)continue;
    MWC state{x,c};MWC step=state;
    if(next_mwc(step)!=o[0]||next_mwc(step)!=o[1])continue;
    ++pair_states;
    if(next_mwc(step)!=o[2]||next_mwc(step)!=o[3])continue;
    ++four_states;
    auto all=emitted(state);
    S missing{};std::copy(all.begin()+4,all.begin()+8,missing.begin());
    B coupon=encode(missing,view),component{};
    for(int j=0;j<16;j++)component[j]=coupon[j]^mask[j];
    unsigned char hashed[32];SHA256(component.data(),component.size(),hashed);
    std::string sha=hex(hashed,32);std::transform(sha.begin(),sha.end(),sha.begin(),::tolower);
    bool hit=sha==K04_SHA;bool held=std::equal(h.begin(),h.end(),all.begin()+8);
    if(hit)++sha_matches;if(held)++holdout_matches;
    std::lock_guard<std::mutex> lock(mutex);
    std::cout<<"FULLSTATE view="<<view<<" initial_x="<<std::hex<<x<<" c="<<c<<std::dec
      <<" coupon="<<hex(coupon.data(),16)<<" component="<<hex(component.data(),16)
      <<" K04_SHA="<<(hit?"PASS":"MISS")<<" REQUESTED3="<<(held?"PASS":"MISS")<<"\n";
   }
   double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
   std::cout<<"SUMMARY view="<<view<<" exact_trials=4294967296 two_output_states="<<pair_states
     <<" four_output_states="<<four_states<<" SHA_hits="<<sha_matches
     <<" holdout_hits="<<holdout_matches<<" seconds="<<sec<<"\n"<<std::flush;
  }
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
