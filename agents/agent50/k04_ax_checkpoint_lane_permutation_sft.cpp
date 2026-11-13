// H-17 K04: complete lane-permutation search over original AX checkpoint vectors.
// Source-only candidate construction; acceptance is read only at the final SHA gate.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <stdexcept>
#include <vector>

static const char *AUDIT_SHA="32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf";
static const char *ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const char *ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *HEX="0123456789abcdef";

static std::string read_file(const std::string &p) {
  std::ifstream f(p,std::ios::binary);
  if(!f) throw std::runtime_error("cannot open "+p);
  std::ostringstream s; s<<f.rdbuf(); return s.str();
}
static std::string shahex(const unsigned char *p,size_t n) {
  unsigned char d[32]; SHA256(p,n,d); std::string out; out.reserve(64);
  for(auto b:d){out.push_back(HEX[b>>4]);out.push_back(HEX[b&15]);}
  return out;
}
static std::string shahex(const std::string &s) {
  return shahex((const unsigned char*)s.data(),s.size());
}
static std::string lower(std::string s) {
  for(char &c:s) if(c>='A'&&c<='Z') c=char(c-'A'+'a');
  return s;
}
static std::vector<unsigned char> unhex(const std::string &s) {
  if(s.size()%2) throw std::runtime_error("odd hex length");
  std::vector<unsigned char> v;
  auto nib=[](char c)->int {
    if(c>='0'&&c<='9') return c-'0';
    if(c>='a'&&c<='f') return c-'a'+10;
    if(c>='A'&&c<='F') return c-'A'+10;
    return -1;
  };
  for(size_t i=0;i<s.size();i+=2) {
    int a=nib(s[i]),b=nib(s[i+1]);
    if(a<0||b<0) throw std::runtime_error("invalid hex");
    v.push_back((a<<4)|b);
  }
  return v;
}
static std::string match1(const std::string &s,const std::regex &r,const char *what) {
  std::smatch m;
  if(!std::regex_search(s,m,r)) throw std::runtime_error(std::string("missing ")+what);
  return m[1].str();
}
static std::array<std::array<unsigned char,16>,8> parse_vectors(const std::string &audit) {
  std::regex kind_re("\\\"kind\\\"\\s*:\\s*\\\"CHUNK\\\"");
  std::regex transfer_re("\\\"transfer\\\"\\s*:\\s*\\\"(AX-7778|AX-7781|AX-7782|AX-7783)\\\"");
  std::regex seq_re("\\\"seq\\\"\\s*:\\s*([0-7])");
  std::regex attempt_re("\\\"attempt\\\"\\s*:\\s*([12])");
  std::regex cp_re("\\\"checkpoint\\\"\\s*:\\s*\\\"([0-9A-Fa-f]{4})\\\"");
  std::array<std::array<std::array<bool,8>,2>,4> seen{};
  std::array<std::array<std::array<unsigned char,2>,8>,8> chunks{};
  const char *ids[4]={"AX-7778","AX-7781","AX-7782","AX-7783"};
  std::istringstream lines(audit); std::string line;
  while(std::getline(lines,line)) {
    if(!std::regex_search(line,kind_re)) continue;
    std::string t=match1(line,transfer_re,"transfer");
    int seq=std::stoi(match1(line,seq_re,"seq"));
    int att=std::stoi(match1(line,attempt_re,"attempt"));
    std::string cp=match1(line,cp_re,"checkpoint");
    int ti=0; while(ti<4&&t!=ids[ti]) ti++;
    if(ti==4) throw std::runtime_error("unexpected transfer");
    if(seen[ti][att-1][seq]) throw std::runtime_error("duplicate transfer/attempt/seq row");
    seen[ti][att-1][seq]=true;
    auto b=unhex(cp);
    chunks[ti*2+(att-1)][seq][0]=b[0];
    chunks[ti*2+(att-1)][seq][1]=b[1];
  }
  std::array<std::array<unsigned char,16>,8> out{};
  for(int ti=0;ti<4;ti++) for(int ai=0;ai<2;ai++) {
    int v=ti*2+ai;
    for(int seq=0;seq<8;seq++) {
      if(!seen[ti][ai][seq]) throw std::runtime_error("incomplete transfer checkpoint vector");
      out[v][2*seq]=chunks[v][seq][0];
      out[v][2*seq+1]=chunks[v][seq][1];
    }
  }
  return out;
}
static bool eq(const unsigned char *d,const std::string &target) {
  char s[65];
  for(int i=0;i<32;i++){s[2*i]=HEX[d[i]>>4];s[2*i+1]=HEX[d[i]&15];}
  s[64]=0; return target==s;
}
static void usage() {
  std::cerr<<"usage: sft [--source PATH] [--acceptance PATH] [--routing PATH] [--start 0..7] [--end 1..8] [--target SHA256]\n";
}
int main(int argc,char **argv) {
  std::string source="resources/evidence/transfers/transfer-audit.jsonl";
  std::string acceptance="resources/acceptance.json";
  std::string routing="resources/evidence/recovery-routing.json";
  std::string target; int start=0,end=8;
  for(int i=1;i<argc;i++) {
    std::string a=argv[i];
    if(a=="--source"&&i+1<argc) source=argv[++i];
    else if(a=="--acceptance"&&i+1<argc) acceptance=argv[++i];
    else if(a=="--routing"&&i+1<argc) routing=argv[++i];
    else if(a=="--start"&&i+1<argc) start=std::atoi(argv[++i]);
    else if(a=="--end"&&i+1<argc) end=std::atoi(argv[++i]);
    else if(a=="--target"&&i+1<argc) target=lower(argv[++i]);
    else {usage();return 2;}
  }
  try {
    if(start<0||end>8||start>=end) throw std::runtime_error("invalid vector range");
    std::string audit=read_file(source),acc=read_file(acceptance),route=read_file(routing);
    if(shahex(audit)!=AUDIT_SHA) throw std::runtime_error("transfer-audit source SHA256 mismatch");
    if(shahex(acc)!=ACCEPT_SHA) throw std::runtime_error("acceptance source SHA256 mismatch");
    if(shahex(route)!=ROUTE_SHA) throw std::runtime_error("routing source SHA256 mismatch");
    auto vectors=parse_vectors(audit);
    if(target.empty()) target=match1(acc,std::regex("\\\"K04\\\"\\s*:\\s*\\\"([0-9a-fA-F]{64})\\\""),"K04 acceptance hash");
    if(target.size()!=64) throw std::runtime_error("target must be 64 hex characters");
    auto mb=unhex(match1(route,std::regex("\\\"masked_component\\\"\\s*:\\s*\\\"([0-9A-Fa-f]{32})\\\""),"K04 mask"));
    if(mb.size()!=16) throw std::runtime_error("mask must be 16 bytes");
    uint64_t candidates=0,hashes=0,hits=0;
    for(int v=start;v<end;v++) {
      std::array<int,8> perm={0,1,2,3,4,5,6,7};
      do {
        for(unsigned swaps=0;swaps<256;swaps++) {
          unsigned char b[16],masked[16],d[32];
          for(int lane=0;lane<8;lane++) {
            unsigned char x=vectors[v][2*perm[lane]],y=vectors[v][2*perm[lane]+1];
            if((swaps>>lane)&1) std::swap(x,y);
            b[2*lane]=x; b[2*lane+1]=y;
          }
          SHA256(b,16,d); hashes++;
          if(eq(d,target)) {
            std::cout<<"HIT direct vector="<<v<<" permutation=";
            for(int x:perm) std::cout<<x;
            std::cout<<" swaps="<<std::hex<<swaps<<" bytes=";
            for(auto x:b) printf("%02X",x);
            std::cout<<std::dec<<"\n"; hits++;
          }
          for(int i=0;i<16;i++) masked[i]=b[i]^mb[i];
          SHA256(masked,16,d); hashes++;
          if(eq(d,target)) {
            std::cout<<"HIT masked vector="<<v<<" permutation=";
            for(int x:perm) std::cout<<x;
            std::cout<<" swaps="<<std::hex<<swaps<<" payload=";
            for(auto x:b) printf("%02X",x);
            std::cout<<" component=";
            for(auto x:masked) printf("%02X",x);
            std::cout<<std::dec<<"\n"; hits++;
          }
          candidates++;
        }
      } while(std::next_permutation(perm.begin(),perm.end()));
      std::cout<<"completed vector "<<v<<" candidates="<<candidates<<" hashes="<<hashes<<" hits="<<hits<<"\n"<<std::flush;
    }
    std::cout<<"FINAL vectors="<<(end-start)<<" permutations_per_vector=40320 byte_swap_patterns=256 complete_candidates="<<candidates<<" full_SHA256_tests="<<hashes<<" hits="<<hits<<" target="<<target<<"\n";
    return 0;
  } catch(const std::exception &e) {
    std::cerr<<"ERROR: "<<e.what()<<"\n"; return 2;
  }
}
