
#include <algorithm>
#include <array>
#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <vector>
using U=uint32_t;
constexpr U F1M=1664525u, F2M=1566083941u;
inline U T(U x) {return x^(x>>30);}
inline U f1(U x){return F1M*T(x);}
inline U f1h(U x,U h){return F1M*(x^h);}
inline U f2(U x){return F2M*T(x);}
std::array<U,624> G;
void initG(){
    G[0]=19650218u;
    for(int i=1;i<624;++i) G[i]=1812433253u*T(G[i-1])+U(i);
}
std::array<U,624> seedState(U k0,U k1) {
    auto s=G;
    U key[2]={k0,k1};
    int i=1,j=0;
    for(int n=0;n<624;++n) {
        s[i] = (s[i]^f1(s[i-1]))+key[j]+U(j);
        ++i; ++j;
        if(i>=624){s[0]=s[623];i=1;}
        if(j>=2)j=0;
    }
    for(int n=0;n<623;++n) {
        s[i]=(s[i]^f2(s[i-1]))-U(i);
        ++i;
        if(i>=624){s[0]=s[623];i=1;}
    }
    s[0]=0x80000000u;
    return s;
}
struct Observed{
 U s3,s4,s5,s6mask,s6value,s13mask,s13value,s14mask,s14value;
};
struct Counts {
 uint64_t roots=0, hbits=0, s13=0, s14=0;
 bool planted=false;
};
Counts searchS3(const Observed& o, U plant0=0, U plant1=0, bool planted=false) {
    Counts totals;
    const U a5=(o.s5+5u)^f2(o.s4);
    const U a4=(o.s4+4u)^f2(o.s3);
    const U k0=a5-(G[5]^f1(a4));
    const U a1=(G[1]^f1(G[0]))+k0;
    const U b2=G[2]^f1(a1);
    const U c6=G[6]^f1(a5), f2s5=f2(o.s5);
    std::vector<U> curr, next;
    curr.reserve(128); next.reserve(128);
    for(U h2=0;h2<4;h2++) for(U h3=0;h3<4;h3++){
        curr.clear(); curr.push_back(0);
        for(int bit=0;bit<32 && !curr.empty();++bit){
            U high=U(1)<<bit;
            U mask=(bit==31)?0xffffffffu:((U(1)<<(bit+1))-1);
            U s6test=o.s6mask & mask, s6expect=o.s6value & s6test;
            next.clear();
            for(U prefix:curr){
                for(U k1 : {prefix, U(prefix|high)}) {
                    U s6=((c6+k1+1u)^f2s5)-6u;
                    if((s6&s6test)!=s6expect)continue;
                    U a2=b2+k1+1u;
                    U a3=(G[3]^f1h(a2,h2))+k0;
                    U predA4=(G[4]^f1h(a3,h3))+k1+1u;
                    if((predA4&mask)!= (a4&mask))continue;
                    next.push_back(k1);
                }
            }
            curr.swap(next);
        }
        totals.roots+=curr.size();
        for(U k1:curr) {
            U a2=b2+k1+1u;
            U a3=(G[3]^f1(a2))+k0;
            if((a2>>30)!=h2 || (a3>>30)!=h3) continue;
            if(((G[4]^f1(a3))+k1+1u)!=a4)continue;
            ++totals.hbits;
            U prev=((c6+k1+1u)^f2s5)-6u;
            U before=c6+k1+1u;
            for(int i=7;i<=14;++i){
                U ai = (G[i]^f1(before))+((i&1)?k0:k1)+U((i-1)&1);
                prev=(ai^f2(prev))-U(i);
                before=ai;
                if(i==13){
                    if((prev&o.s13mask)!=o.s13value)break;
                    ++totals.s13;
                }
                if(i==14){
                    if((prev&o.s14mask)!=o.s14value)break;
                    ++totals.s14;
                    if(planted && k0==plant0 && k1==plant1)totals.planted=true;
                    if(!planted)
                        std::cout<<"ORIGINAL_SURVIVOR S3="<<std::hex<<o.s3<<" k0="<<k0<<" k1="<<k1<<std::dec<<"\n";
                }
            }
        }
    }
    return totals;
}
void selftest(){
    for(auto [k0,k1]: std::array<std::pair<U,U>,5>{{
      {0x12345678u,0x23456789u},{0x00001fc3u,0x00001092u},
      {0xffffffffu,0xffffffffu},{0x00000000u,0x80000000u},
      {0x80000000u,0x00000001u}}}){
        auto s=seedState(k0,k1);
        if(k0==0x12345678u && k1==0x23456789u) {
            if(s[1]!=0xA71A9F7Fu || s[3]!=0x719C0F90u || s[4]!=0xF7449605u ||
               s[5]!=0x402C36C2u || s[6]!=0x7DCB9D25u || s[13]!=0x5A729D6Cu ||
               s[14]!=0xAF2106B6u || s[100]!=0x9134FEA0u || s[623]!=0x17378512u) {
                 std::cerr<<"INDEPENDENT_PYTHON_FIXTURE_FAIL\n"; std::exit(3);
            }
            std::cout<<"INDEPENDENT_PYTHON_FIXTURE_PASS\n";
        }
        Observed o{s[3],s[4],s[5],0x09cc1c00u,s[6]&0x09cc1c00u,0x000000ffu,s[13]&0xffu,0x5398ba7du,s[14]&0x5398ba7du};
        auto c=searchS3(o,k0,k1,true);
        if(!c.planted){
            std::cerr<<"PLANTED_FAIL k0="<<std::hex<<k0<<" k1="<<k1<<std::dec<<"\n";
            std::exit(2);
        }
        std::cout<<"PLANTED_PASS k0="<<std::hex<<k0<<" k1="<<k1<<std::dec
            <<" roots="<<c.roots<<" hbits="<<c.hbits<<" s13="<<c.s13<<" s14="<<c.s14<<"\n";
    }
}
int main(int argc,char**argv){
    initG();
    selftest();
    if(argc<3) return 0;
    uint64_t start=std::strtoull(argv[1],nullptr,0), count=std::strtoull(argv[2],nullptr,0);
    if(start>=(1ull<<26) || count>(1ull<<26)-start){std::cerr<<"RANGE_ERROR\n";return 2;}
    constexpr Observed base{0,0xE403BB7Du,0x1F7B301Fu,0x09CC1C00u,0x008C1000u,0xffu,0xb6u,0x5398ba7du,0x4010a820u};
    Counts total;
    auto begin=std::chrono::steady_clock::now();
    for(uint64_t i=start;i<start+count;i++){
        Observed o=base; o.s3=(U(i)<<5)|0x11u;
        auto c=searchS3(o);
        total.roots+=c.roots;total.hbits+=c.hbits;total.s13+=c.s13;total.s14+=c.s14;
    }
    double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    std::cout<<"K2494_N2 start="<<start<<" count="<<count<<" roots="<<total.roots
        <<" hbits="<<total.hbits<<" s13="<<total.s13<<" s14="<<total.s14
        <<" seconds="<<sec<<"\n";
}
