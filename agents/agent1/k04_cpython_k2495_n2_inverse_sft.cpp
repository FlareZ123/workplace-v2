// Source-pinned CPython MT19937 two-word integer-seed inversion, true offset k=2495.
// Run with [start count] in 23-bit free-source-S7 space. Original selected printer ACK2 is excluded.
// C++17, no external dependencies.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <string>

using U = uint32_t;
static constexpr U F1M=1664525u,F2M=1566083941u;
static std::array<U,624> G{};
static inline U F1(U x) { return F1M*(x^(x>>30)); }
static inline U F2(U x) { return F2M*(x^(x>>30)); }
static inline U F1guess(U x,U h) { return F1M*(x^h); }
static void init_g() {
  G[0]=19650218u;
  for(int i=1;i<624;i++) G[i]=1812433253u*(G[i-1]^(G[i-1]>>30))+U(i);
}
static std::array<U,624> init_python(U k0,U k1) {
  std::array<U,624> a=G;
  const U key[2]={k0,k1};
  int i=1,j=0;
  for(int k=624;k>0;--k) {
    a[i]=(a[i]^F1(a[i-1]))+key[j]+U(j);
    i++;j++;
    if(i>=624){a[0]=a[623];i=1;}
    if(j>=2)j=0;
  }
  for(int k=623;k>0;--k) {
    a[i]=(a[i]^F2(a[i-1]))-U(i);
    i++;
    if(i>=624){a[0]=a[623];i=1;}
  }
  a[0]=0x80000000u;
  return a;
}
struct Fixed {
  U s5,s6,a6,base7;
  U m7,v7,m14,v14,m15,v15,m4,v4;
};
static Fixed original={0xE403BB7Du,0x1F7B301Fu,0,0,0x09CC1C00u,0x008C1000u,
   0x000000FFu,0x000000B6u,0x5398BA7Du,0x4010A820u,0x8000001Fu,0x00000011u};
static inline U directA6(U k0,U k1,U h2,U h3,U h4,U h5,U q2) {
  U a2=q2+k1+1u;
  U a3=(G[3]^F1guess(a2,h2))+k0;
  U a4=(G[4]^F1guess(a3,h3))+k1+1u;
  U a5=(G[5]^F1guess(a4,h4))+k0;
  return (G[6]^F1guess(a5,h5))+k1+1u;
}
static inline void forward_real(U k0,U k1,U a6,U s7,U& s14,U& s15) {
  U a=(G[7]^F1(a6))+k0;
  U s=s7;
  for(int i=8;i<=15;i++) {
    a=(G[i]^F1(a)) + ((i&1)?k0:k1+1u);
    s=(a^F2(s))-U(i);
    if(i==14)s14=s;
  }
  s15=s;
}
static U scatter23(U compact,U mask,U fixed) {
  U res=fixed;
  for(int i=0;i<32;i++) if(!(mask&(U(1)<<i))) {
    res |= (compact&1u)<<i;
    compact>>=1;
  }
  return res;
}
static U gather23(U full,U mask) {
  U compact=0,bit=0;
  for(int i=0;i<32;i++) if(!(mask&(U(1)<<i))) {
    compact |= ((full>>i)&1u)<<bit++;
  }
  return compact;
}
struct Counters { uint64_t paths=0,complete=0,source14=0,source15=0,source5=0; };
static bool solve_one(U k0,U s7,const Fixed& f,Counters& c,bool verbose) {
  const U a6=f.a6;
  const U q2=(G[2]^F1((G[1]^F1(G[0]))+k0));
  for(U geom=0;geom<256;geom++) {
    U h2=(geom>>0)&3u,h3=(geom>>2)&3u,h4=(geom>>4)&3u,h5=(geom>>6)&3u;
    c.paths++;
    U k1=0;
    // For each bit of k1, output A6 has derivative one, under frozen high-two-bit guesses.
    // Flip the least unmatched bit. Higher bits never affect previously matched lower bits.
    U a6p=directA6(k0,k1,h2,h3,h4,h5,q2);
    int turns=0;
    while(a6p!=a6) {
      if(++turns>32){std::cerr<<"NONTRIANGULAR_GEOMETRY k0="<<std::hex<<k0<<" geom="<<geom<<" k1="<<k1<<" a6p="<<a6p<<" a6="<<a6<<std::dec<<"\n";std::exit(4);}
      U diff=a6p^a6;
      U bit=diff & (U(0)-diff);
      k1 ^= bit;
      a6p=directA6(k0,k1,h2,h3,h4,h5,q2);
    }
    U a2=q2+k1+1u;
    if((a2>>30)!=h2)continue;
    U a3=(G[3]^F1(a2))+k0;
    if((a3>>30)!=h3)continue;
    U a4=(G[4]^F1(a3))+k1+1u;
    if((a4>>30)!=h4)continue;
    U a5=(G[5]^F1(a4))+k0;
    if((a5>>30)!=h5)continue;
    if((G[6]^F1(a5))+k1+1u != a6) {std::cerr<<"INVERSE MISMATCH\n";std::exit(3);}
    c.complete++;
    U s14=0,s15=0;
    forward_real(k0,k1,a6,s7,s14,s15);
    if((s14&f.m14)!=f.v14)continue;
    c.source14++;
    if((s15&f.m15)!=f.v15)continue;
    c.source15++;
    const auto st=init_python(k0,k1);
    if(st[5]==f.s5 && st[6]==f.s6 && (st[4]&f.m4)==f.v4 && (st[7]&f.m7)==f.v7 && (st[14]&f.m14)==f.v14 && (st[15]&f.m15)==f.v15){
      c.source5++;
      std::cout<<"PLANTED_FULL_SEED "<<std::hex<<std::uppercase<<std::setw(8)<<std::setfill('0')<<k0<<" "<<std::setw(8)<<k1<<std::dec<<"\n";
      if(verbose)std::cout<<"SOURCE MATCH\n";
    }
  }
  return c.source5!=0;
}
static void check_controls() {
  struct Test {U a,b;std::array<U,8> s;};
  const std::array<Test,5> ts={{{0x12345678,0x23456789,{0xF7449605,0x402C36C2,0x7DCB9D25,0x944C26C6,0xAF2106B6,0xA44F8FDC,0x9134FEA0,0x17378512}},
  {0x00001FC3,0x00001092,{0xE8BE4653,0x4E7B8A5E,0xAE252E23,0x6FD74B60,0x8F867BA0,0xD8139D5D,0x3074D2F9,0xF82461E5}},
  {0xFFFFFFFF,0xFFFFFFFF,{0xCA9D2966,0xEF92B101,0x47CCC608,0xFCAD5217,0x8C8071FF,0x0183D04D,0x8EC4105B,0x3353F842}},
  {0x00000000,0x80000000,{0xB7FEC2F5,0x97E8F781,0x818EF22F,0x692279EF,0x08F2DF7E,0xA8B42163,0xB8EA1BAA,0xDF49050E}},
  {0x80000000,0x00000001,{0x18FAFCEE,0xD5DEC709,0x49D589C7,0xA01B609B,0x49F24D92,0x34206080,0xA3EECCE3,0xF36BC0AE}}}};
  for(const auto& t:ts){
    const auto st=init_python(t.a,t.b);
    for(int i=0;i<8;i++)if(st[std::array<int,8>{4,5,6,7,14,15,100,623}[i]]!=t.s[i]){
      std::cerr<<"GENUINE PYTHON 624-WORD INITIALIZER FAILURE\n";std::exit(2);
    }
    Fixed f=original;
    f.s5=st[5];f.s6=st[6];f.a6=(st[6]+6u)^F2(st[5]);
    f.m7=original.m7;f.v7=st[7]&f.m7;
    f.m14=original.m14;f.v14=st[14]&f.m14;
    f.m15=original.m15;f.v15=st[15]&f.m15;
    f.m4=original.m4;f.v4=st[4]&f.m4;
    U packed=gather23(st[7],f.m7);
    if(scatter23(packed,f.m7,f.v7)!=st[7]){std::cerr<<"S7 SCATTER ERROR\n";std::exit(2);}
    const U k0=( (st[7]+7u)^F2(st[6]) )-(G[7]^F1(f.a6));
    if(k0!=t.a){std::cerr<<"A7 INVERSE ERROR\n";std::exit(2);}
    Counters c;
    solve_one(k0,st[7],f,c,false);
    if(c.source5==0){std::cerr<<"POSITIVE KEY NOT RETAINED\n";std::exit(2);}
    std::cout<<"CONTROL_PASS k0="<<std::hex<<k0<<" k1="<<t.b<<std::dec<<" roots="<<c.complete<<" source14="<<c.source14<<" source15="<<c.source15<<" recovered="<<c.source5<<"\n";
  }
}
int main(int argc,char**argv){
  init_g();check_controls();
  if(argc==1){std::cout<<"CONTROL_ONLY\n";return 0;}
  if(argc!=3){std::cerr<<"use: program start count\n";return 2;}
  uint64_t start=std::stoull(argv[1]),count=std::stoull(argv[2]);
  if(start>8388608ULL || count>8388608ULL-start){std::cerr<<"invalid 23bit window\n";return 2;}
  original.a6=(original.s6+6u)^F2(original.s5);
  original.base7=(G[7]^F1(original.a6));
  Counters c; const auto begin=std::chrono::steady_clock::now();
  for(uint64_t pos=start;pos<start+count;pos++){
    U s7=scatter23(U(pos),original.m7,original.v7);
    U k0=((s7+7u)^F2(original.s6))-original.base7;
    solve_one(k0,s7,original,c,false);
  }
  auto dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
  std::cout<<"K2495_N2 start="<<start<<" count="<<count<<" hi_paths="<<c.paths<<" genuine_roots="<<c.complete<<" source14="<<c.source14<<" source15="<<c.source15<<" full_original="<<c.source5<<" seconds="<<dt<<"\n";
  return 0;
}
