// H-17 native std::mt19937 incident-clock source gate; never reads selected ACK2 hex.
// Standalone: g++ -O3 -std=c++17 k04_native_mt32_clock_allpacket_sft.cpp -o mt32gate
//             mt32gate resources/evidence/print/spool-reconstruction.log
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <random>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
using U=std::uint32_t;
using Packet=std::array<std::array<std::uint8_t,4>,4>;

static Packet parse_hex(const std::string& s) {
  assert(s.size()==32);
  Packet p{};
  for(int i=0;i<16;++i){unsigned v=0;assert(std::sscanf(s.c_str()+2*i,"%2x",&v)==1);p[i/4][i%4]=v;}
  return p;
}
static U native(const std::array<std::uint8_t,4>& a,bool reverse) {
  U out=0;
  for(int i=0;i<4;++i)out|=static_cast<U>(a[reverse?3-i:i])<<(8*i);
  return out;
}
static bool match(U const* w,Packet const& p) {
  std::array<int,4> perm{0,1,2,3};
  do{
    bool yes=true;
    for(int i=0;i<4&&yes;++i)yes=w[i]==native(p[perm[i]],false)||w[i]==native(p[perm[i]],true);
    if(yes)return true;
  }while(std::next_permutation(perm.begin(),perm.end()));
  return false;
}
static Packet serialize(U const* w){
  const int perm[4]={2,0,3,1};
  Packet p{};
  for(int i=0;i<4;++i){U v=w[perm[i]];bool reverse=(i==1||i==3);
    for(int j=0;j<4;++j)p[i][j]=static_cast<std::uint8_t>(v>>(8*(reverse?3-j:j)));}
  return p;
}
static std::vector<Packet> read_source(const std::string& path){
  std::ifstream in(path);assert(in);
  std::vector<Packet> source;
  std::string line;
  int row=0;
  while(std::getline(in,line)){
    if(line.empty()||line[0]=='#')continue;
    std::istringstream parts(line);
    std::string token,job,attempt,state,klass,payload,dest;
    parts>>token>>job>>attempt>>state>>klass>>payload>>dest;
    assert(token.substr(0,4)=="2026"&&job.substr(0,4)=="JOB="&&payload.substr(0,8)=="PAYLOAD=");
    if(row==129){
      assert(job=="JOB=PS-261003-0417"&&attempt=="ATTEMPT=2"&&state=="STATE=ACK"&&klass=="CLASS=RECOVER");
      // Exclude before interpreting the suspect 16-byte copy.
    } else {
      if(row==0)assert(job=="JOB=PS-261003-0300"&&payload=="PAYLOAD=FBBBC54356483F5864BB3F06794518A5");
      source.push_back(parse_hex(payload.substr(8)));
    }
    ++row;
  }
  assert(row==133&&source.size()==132);
  return source;
}

int main(int argc,char**argv){
  assert(argc==2);
  auto source=read_source(argv[1]);
  // Test the source packet serializer using a seeded genuine generator.
  constexpr U positive_seed=1791079160U;
  std::mt19937 planted(positive_seed);
  for(int i=0;i<431;++i)(void)planted();
  U word[4]={static_cast<U>(planted()),static_cast<U>(planted()),static_cast<U>(planted()),static_cast<U>(planted())};
  Packet witness=serialize(word);
  assert(match(word,witness));
  witness[0][0]^=1;
  assert(!match(word,witness));
  std::puts("PLANTED_ACTUAL_CXX_MT POSITIVE_WITHHELD_EXACT_PACKET_AND_TAMPER PASS");

  std::unordered_map<U,std::vector<unsigned>> index;
  std::array<bool,1<<16> low{};
  for(unsigned r=0;r<source.size();++r)for(int j=0;j<4;++j)for(bool reverse:{false,true}){
    U key=native(source[r][j],reverse);
    index[key].push_back(r);low[key&0xffff]=true;
  }
  constexpr U start=1790812800U, end=1791158400U;
  constexpr int windows=8192;
  auto start_time=std::chrono::steady_clock::now();
  std::uint64_t firstword=0,full=0;
  for(U seed=start;seed<end;++seed){
    std::mt19937 mt(seed);
    U buffer[4]{};
    for(int i=0;i<windows+3;++i){
      U v=static_cast<U>(mt());
      buffer[i&3]=v;
      if(i<3||!low[buffer[(i-3)&3]&0xffff])continue;
      auto found=index.find(buffer[(i-3)&3]);
      if(found==index.end())continue;
      ++firstword;
      U w[4]={buffer[(i-3)&3],buffer[(i-2)&3],buffer[(i-1)&3],buffer[i&3]};
      for(unsigned row:found->second)if(match(w,source[row])){
        ++full;
        std::printf("AUTHENTIC_INTACT_SOURCE_MATCH seed=%u firstword_phase=%d source_index_excluding_row129=%u words=%08X,%08X,%08X,%08X\n",seed,i-3,row,w[0],w[1],w[2],w[3]);
      }
    }
    if((seed-start+1)%86400==0){
      auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start_time).count();
      std::printf("DAY %u/%u seconds=%0.2f candidate_firstword=%llu complete_source=%llu\n",(seed-start+1)/86400,(end-start)/86400,seconds,(unsigned long long)firstword,(unsigned long long)full);std::fflush(stdout);
    }
  }
  std::printf("ORIGINAL_SOURCE_RESULT full_packets=%zu seeds=%u windows_per_seed=%d total_4word_windows=%llu firstword_hits=%llu authentic_whole_packet_matches=%llu\n",source.size(),end-start,windows,(unsigned long long)(end-start)*windows,(unsigned long long)firstword,(unsigned long long)full);
  return full?2:0;
}
