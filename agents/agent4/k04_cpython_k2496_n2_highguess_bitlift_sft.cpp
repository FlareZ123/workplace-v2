
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
using U = uint32_t;
using U64 = uint64_t;
constexpr U F1=1664525u,F2=1566083941u,IF2=0x6A76AE6Du;
constexpr U S6=0xE403BB7Du,S7=0x1F7B301Fu,A7=0x2AED5290u;
constexpr U S2M=0x09CC1C00u,S2V=0x00C40000u;
constexpr U S5M=0x8000001Fu,S5V=0x00000011u;
constexpr U S8M=0x09CC1C00u,S8V=0x008C1000u;
constexpr U S15M=0x000000FFu,S15V=0x000000B6u;
constexpr U S16M=0x5398BA7Du,S16V=0x4010A820u;
constexpr U S17M=0x01800800u,S17V=0x00000800u;
std::array<U,18> G;
inline U t(U x){return x^(x>>30);}
inline U f1(U x){return F1*t(x);}
inline U f2(U x){return F2*t(x);}
inline U inv2(U x,U hi){return (IF2*x)^hi;}
struct Counts {
    U64 nodes=0, at10=0, at29=0, at32=0, source15=0, source16=0, source17=0;
    std::array<U64,33> levels{};
    U64 originalSurvivors=0,planted=0;
};
static bool checkPlant=false;
static U expectedK0=0,expectedK1=0;
struct Obs {
    U s6,s7,a7,s2m,s2v,s5m,s5v,s8m,s8v,s15m,s15v,s16m,s16v,s17m,s17v;
};
Obs original{S6,S7,A7,S2M,S2V,S5M,S5V,S8M,S8V,S15M,S15V,S16M,S16V,S17M,S17V};
U c8;
inline void first7(U k0,U k1,int ah,U* a) {
    a[0]=G[0];
    for(int i=1;i<8;++i) {
        U hi=(i==1)?(a[0]>>30):((U(ah)>>(2*(i-2)))&3u);
        U j=U((i-1)&1);
        a[i]=(G[i]^(F1*(a[i-1]^hi)))+((i&1)?k0:k1)+j;
    }
}
inline U backwards(U ai,U si,int index,U hi) {
    return inv2(ai^(si+U(index)),hi);
}
void dfs(int bit,U k0,U k1,int ah,int sh,int tail,Counts& cnt,const Obs& o) {
    if(bit==32) {
        ++cnt.at32;
        U a[18];
        first7(k0,k1,ah,a);
        U prev=o.s6;
        for(int i=8;i<=17;++i){
            U j=U((i-1)&1);
            a[i]=(G[i]^f1(a[i-1]))+((i&1)?k0:k1)+j;
        }
        for(int i=7;i<=17;++i) {
            prev=(a[i]^f2(prev))-U(i);
            if(i==15){if((prev&o.s15m)!=o.s15v)return;++cnt.source15;}
            if(i==16){if((prev&o.s16m)!=o.s16v)return;++cnt.source16;}
            if(i==17){if((prev&o.s17m)!=o.s17v)return;++cnt.source17;}
        }
        ++cnt.originalSurvivors;
        if(checkPlant) {
            if(k0==expectedK0 && k1==expectedK1) ++cnt.planted;
        } else {
            std::cout<<"SOURCE_SURVIVOR ha="<<ah<<" sh="<<sh<<" tail="<<tail
                     <<" k0="<<std::hex<<k0<<" k1="<<k1<<std::dec<<"\n";
        }
        return;
    }
    U pbit=U(1)<<bit;
    U mask=(bit==31)?0xffffffffu:((U(1)<<(bit+1))-1u);
    U s2mask=o.s2m&mask,s5mask=o.s5m&mask,s8mask=o.s8m&mask;
    U sc8=(G[8]^f1(o.a7));
    // For each two new seed bits, first apply source A7, S8 and S5
    for(U nb=0;nb<4;++nb){
        U x=k0|((nb&1u)?pbit:0u);
        U y=k1|((nb&2u)?pbit:0u);
        U aa[8]; first7(x,y,ah,aa);
        if((aa[7]&mask)!=(o.a7&mask))continue;
        U pred8=(((sc8+y+1u)^f2(o.s7))-8u);
        if((pred8&s8mask)!=(o.s8v&s8mask))continue;
        U s5=backwards(aa[6],o.s6,6,U(sh));
        if((s5&s5mask)!=(o.s5v&s5mask))continue;
        if(bit>=30){
            bool good=true;
            for(int i=1;i<=6;++i){
                U hi=(U(ah)>>(2*(i-1)))&3u;
                if((((aa[i]>>30)^hi)&((bit==30)?1u:3u))!=0u){good=false;break;}
            }
            if(!good || ((((s5>>30)^U(sh))&((bit==30)?1u:3u))!=0u))continue;
        }
        ++cnt.nodes;
        ++cnt.levels[bit+1];
        if(bit==9)++cnt.at10;
        if(bit==28)++cnt.at29;
        if(bit<9){dfs(bit+1,x,y,ah,sh,0,cnt,o);continue;}
        if(bit==9){
            // Source S2's first fixed position is bit10, so delay
            // guessing intermediate S2/S3/S4 highbits until now.
            for(int tt=0;tt<64;++tt)
                dfs(bit+1,x,y,ah,sh,tt,cnt,o);
            continue;
        }
        U s4=backwards(aa[5],s5,5,U(tail)&3u);
        U s3=backwards(aa[4],s4,4,(U(tail)>>2)&3u);
        U s2=backwards(aa[3],s3,3,(U(tail)>>4)&3u);
        if((s2&s2mask)!=(o.s2v&s2mask))continue;
        if(bit>=30){
            U hmask=(bit==30)?1u:3u;
            if(((((s4>>30)^(U(tail)&3u))&hmask)!=0u)||
               ((((s3>>30)^((U(tail)>>2)&3u))&hmask)!=0u)||
               ((((s2>>30)^((U(tail)>>4)&3u))&hmask)!=0u))continue;
        }
        dfs(bit+1,x,y,ah,sh,tail,cnt,o);
    }
}
void init(){
    G[0]=19650218u;
    for(int i=1;i<18;++i)G[i]=1812433253u*t(G[i-1])+U(i);
    c8=G[8]^f1(A7);
}
void control(){
    // Synthetic authentic CPython reference state and first-pass register.
    for(auto pair:std::array<std::pair<U,U>,4>{{
        {0x12345678u,0x23456789u},{0x00001fc3u,0x00001092u},
        {0xffffffffu,0xffffffffu},{0u,0x80000000u}}}){
        U k0=pair.first,k1=pair.second;
        std::array<U,624> s{};
        s[0]=19650218u;
        for(int i=1;i<624;++i)s[i]=1812433253u*t(s[i-1])+U(i);
        auto g=s;
        int i=1,j=0;
        U keys[2]{k0,k1};
        std::array<U,18> a{};
        a[0]=g[0];
        for(int it=0;it<624;++it) {
            s[i]=(s[i]^f1(s[i-1]))+keys[j]+U(j);
            if(i<18 && it<17)a[i]=s[i];
            ++i;++j;
            if(i==624){s[0]=s[623];i=1;}
            if(j==2)j=0;
        }
        for(int it=0;it<623;++it) {
            s[i]=(s[i]^f2(s[i-1]))-U(i);
            ++i;if(i==624){s[0]=s[623];i=1;}
        }
        s[0]=0x80000000u;
        if(k0==0x12345678u && k1==0x23456789u) {
            if(s[1]!=0xA71A9F7Fu||s[3]!=0x719C0F90u||s[4]!=0xF7449605u||
               s[5]!=0x402C36C2u||s[6]!=0x7DCB9D25u||s[13]!=0x5A729D6Cu||
               s[14]!=0xAF2106B6u||s[100]!=0x9134FEA0u||s[623]!=0x17378512u) {
                std::cerr<<"INDEPENDENT_CPYTHON_FIXTURE_FAIL\n";std::exit(2);
            }
            std::cout<<"INDEPENDENT_CPYTHON_FIXTURE_PASS\n";
        }
        U a7=((s[7]+7u)^f2(s[6]));
        if(a7!=a[7]){std::cerr<<"CTRL_A7_FAIL\n";std::exit(2);}
        int ah=0,sh=int(s[5]>>30),tail=int(s[4]>>30)|(int(s[3]>>30)<<2)|(int(s[2]>>30)<<4);
        for(int k=1;k<=6;++k)ah|=int(a[k]>>30)<<(2*(k-1));
        Obs o{s[6],s[7],a7,S2M,s[2]&S2M,S5M,s[5]&S5M,S8M,s[8]&S8M,
              S15M,s[15]&S15M,S16M,s[16]&S16M,S17M,s[17]&S17M};
        // Check exact planted-seed 32 prefix branches.
        for(int bit=0;bit<32;++bit){
            U mm=bit==31?0xffffffffu:((U(1)<<(bit+1))-1u);
            U aa[8];first7(k0&mm,k1&mm,ah,aa);
            U ss5=backwards(aa[6],o.s6,6,U(sh));
            U ss4=backwards(aa[5],ss5,5,U(tail)&3u);
            U ss3=backwards(aa[4],ss4,4,(U(tail)>>2)&3u);
            U ss2=backwards(aa[3],ss3,3,(U(tail)>>4)&3u);
            U ss8=(((G[8]^f1(o.a7))+(k1&mm)+1u)^f2(o.s7))-8u;
            if((aa[7]&mm)!=(o.a7&mm)||((ss5&o.s5m&mm)!=(o.s5v&mm))||
                ((ss2&o.s2m&mm)!=(o.s2v&mm))||((ss8&o.s8m&mm)!=(o.s8v&mm))){
                std::cerr<<"CTRL_PREFIX_FAIL bit="<<bit<<"\n";std::exit(2);
            }
        }
        checkPlant=true; expectedK0=k0;expectedK1=k1;
        Counts pc;
        dfs(0,0,0,ah,sh,0,pc,o);
        checkPlant=false;
        if(pc.planted!=1) {
            std::cerr<<"PLANTED_DFS_FAIL k0="<<std::hex<<k0<<" k1="<<k1<<std::dec
                <<" matches="<<pc.planted<<"\n";
            std::exit(2);
        }
        std::cout<<"PLANTED_FULL32_DFS_PASS k0="<<std::hex<<k0<<" k1="<<k1<<std::dec
                 <<" ha="<<ah<<" s5hi="<<sh<<" s234hi="<<tail
                 <<" nodes="<<pc.nodes<<" planted="<<pc.planted<<"\n";
    }
}
int main(int argc,char**argv){
    init();control();
    if(argc<3)return 0;
    int start=std::atoi(argv[1]),count=std::atoi(argv[2]);
    if(start<0||count<0||start+count>4096)return 2;
    Counts total;
    const auto t0=std::chrono::steady_clock::now();
    for(int ah=start;ah<start+count;++ah){
        for(int sh=0;sh<4;++sh)dfs(0,0,0,ah,sh,0,total,original);
        if(((ah-start+1)%16)==0)
            std::cerr<<"GEOMETRY_PROGRESS start="<<start<<" done="<<(ah-start+1)
                     <<" nodes="<<total.nodes<<" leaves="<<total.at32<<"\n";
    }
    const auto secs=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    std::cout<<"K2496_N2_HIGUESS start="<<start<<" count="<<count
      <<" visited="<<total.nodes<<" bit10="<<total.at10<<" bit29="<<total.at29
      <<" leaves="<<total.at32<<" s15="<<total.source15<<" s16="<<total.source16
      <<" s17="<<total.source17<<" roots="<<total.originalSurvivors
      <<" seconds="<<secs<<"\n";
    for(int b=1;b<=32;++b)std::cerr<<b<<":"<<total.levels[b]<<" ";
    std::cerr<<"\n";
}
