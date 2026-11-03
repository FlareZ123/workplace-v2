// Strict source-only xoroshiro128** uneven word stride inversion (no K04 target).
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <fstream>
#include <algorithm>
#include <openssl/sha.h>
#include <chrono>
using U=uint64_t;
struct State{U a,b;};
inline U rol(U x,unsigned n){return (x<<n)|(x>>(64-n));}
inline U ror(U x,unsigned n){return (x>>n)|(x<<(64-n));}
inline U next(State &s){U y=rol(s.a*U(5),7)*U(9),q=s.a^s.b;s.a=rol(s.a,24)^q^(q<<16);s.b=rol(q,37);return y;}
inline U unmix(U y){return ror(y*UINT64_C(0x8e38e38e38e38e39),7)*UINT64_C(0xcccccccccccccccd);}
inline State advance(State s,unsigned gap){while(gap--)next(s);return s;}
inline U load64(const unsigned char* p,bool le){U x=0;if(le)for(unsigned i=0;i<8;i++)x|=U(p[i])<<(8*i);else for(unsigned i=0;i<8;i++)x=(x<<8)|p[i];return x;}
static std::array<unsigned char,16> fromhex(const char* s){std::array<unsigned char,16>b{};for(int i=0;i<16;i++){unsigned x=0;std::sscanf(s+i*2,"%2x",&x);b[i]=(unsigned char)x;}return b;}
static void store64(U x,unsigned char *p,bool le){for(unsigned i=0;i<8;i++)p[i]=(unsigned char)(x>>((le?i:7-i)*8));}
static std::array<unsigned char,16> pack(U a,U b,bool le,bool rev){std::array<unsigned char,16> out{};store64(rev?b:a,out.data(),le);store64(rev?a:b,out.data()+8,le);return out;}
struct Inv{std::vector<U> states;unsigned rank;bool consistent;};
static Inv invert_gap(U first,U second,unsigned gap){
    U a=unmix(first),b=unmix(second);
    U base=advance({a,0},gap).a;
    U rhs=b^base;
    std::array<U,64> basis{},combo{};
    std::vector<U> nulls;
    for(unsigned j=0;j<64;j++){
        U v=advance({0,U(1)<<j},gap).a;
        U coeff=U(1)<<j;
        bool inserted=false;
        for(int bit=63;bit>=0;bit--){
            if(!((v>>bit)&1))continue;
            if(basis[bit]){v^=basis[bit];coeff^=combo[bit];}
            else{basis[bit]=v;combo[bit]=coeff;inserted=true;break;}
        }
        if(!inserted){if(v)std::abort();nulls.push_back(coeff);}
    }
    U sol=0;
    for(int bit=63;bit>=0;bit--){
        if(!((rhs>>bit)&1))continue;
        if(!basis[bit])return {{},64-(unsigned)nulls.size(),false};
        rhs^=basis[bit];sol^=combo[bit];
    }
    if(rhs)std::abort();
    if(nulls.size()>8){std::fprintf(stderr,"too many null freedoms gap=%u\n",gap);return {{},64-(unsigned)nulls.size(),true};}
    std::vector<U> states;
    for(unsigned mask=0;mask<(1u<<nulls.size());mask++){
        U x=sol;
        for(unsigned n=0;n<nulls.size();n++)if((mask>>n)&1)x^=nulls[n];
        if(advance({a,x},gap).a!=b)std::abort();
        states.push_back(x);
    }
    return {states,64-(unsigned)nulls.size(),true};
}
static unsigned long long scan(State initial,unsigned gap,
               const std::array<unsigned char,16> &dest,unsigned long long count){
    U target0[4],target1[4];unsigned t=0;
    for(bool le:{false,true})for(bool rev:{false,true}){
        target0[t]=load64(dest.data()+(rev?8:0),le);
        target1[t]=load64(dest.data()+(rev?0:8),le);
        t++;
    }
    State s=initial;
    unsigned long long hits=0;
    for(unsigned long long index=0;index<count;index++){
        U y=next(s);
        if(index<=gap)continue;
        for(unsigned q=0;q<4;q++){
            if(y!=target0[q])continue;
            State later=s;
            for(unsigned g=1;g<=32;g++){
                U z=next(later);
                if(z==target1[q]){std::printf("ORIGINAL CROSSFIELD offset=%llu gap2=%u\n",index,g);hits++;}
            }
        }
    }
    return hits;
}
static void pin_route(const std::string &file){
    std::ifstream in(file,std::ios::binary);
    if(!in){std::fprintf(stderr,"missing original source %s\n",file.c_str());std::exit(2);}
    std::string body((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
    unsigned char h[SHA256_DIGEST_LENGTH];SHA256((const unsigned char*)body.data(),body.size(),h);
    char digest[65];for(unsigned i=0;i<32;i++)std::sprintf(digest+i*2,"%02x",h[i]);digest[64]=0;
    if(std::strcmp(digest,"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5")){
        std::fprintf(stderr,"original routing SHA mismatch\n");std::exit(2);
    }
}
int main(int argc,char**argv){
    std::string root=argc>3 ? argv[3] : "resources/";
    if(root.back()!='/')root.push_back('/');
    pin_route(root+"evidence/recovery-routing.json");
    unsigned long long count=argc>1?std::strtoull(argv[1],nullptr,10):1000000;
    unsigned maxgap=argc>2?std::strtoul(argv[2],nullptr,10):32;
    if(!count||count>100000000||!maxgap||maxgap>64)return 2;
    auto mask=fromhex("8556C8CB6140A7F9A5123AC7571BEE1C"),nonce=fromhex("5F933DA6A1BD03C32DA5CBC25344F497");
    // Synthetic genuine producer across two different nonconsecutive gaps.
    State planted{UINT64_C(0x518f5e0a9726db40),UINT64_C(0x34127fabc52b067d)};
    State s=planted;U p0=next(s);for(unsigned i=1;i<5;i++)next(s);U p5=next(s);
    auto srcsynthetic=pack(p0,p5,true,true);
    s=advance(planted,700);U d0=next(s);for(unsigned i=1;i<11;i++)next(s);U d11=next(s);
    auto dstsynthetic=pack(d0,d11,false,true);
    unsigned npos=0;
    for(unsigned g=1;g<=maxgap;g++){
        U o0=load64(srcsynthetic.data()+8,true),o1=load64(srcsynthetic.data(),true);
        Inv inv=invert_gap(o0,o1,g);
        if(g==5){if(!inv.consistent)std::abort();for(U x:inv.states)if(x==planted.b){npos++;if(scan({unmix(o0),x},g,dstsynthetic,900)==0)std::abort();}}
    }
    if(maxgap>=5&&npos!=1)std::abort();
    std::printf("SYNTHETIC gap5 and gap11 with source offset700: %s\n",maxgap>=5?"PASS":"skipped");

    auto begin=std::chrono::steady_clock::now();
    unsigned long long states=0,recovered=0,cross=0,unfit=0;unsigned minrank=64;
    for(unsigned field=0;field<2;field++){
        const auto &src=field?nonce:mask,&dst=field?mask:nonce;
        for(bool le:{false,true})for(bool rev:{false,true}){
            U y0=load64(src.data()+(rev?8:0),le),y1=load64(src.data()+(rev?0:8),le);
            for(unsigned gap=1;gap<=maxgap;gap++){
                Inv r=invert_gap(y0,y1,gap);
                if(!r.consistent){unfit++;continue;}
                minrank=std::min(minrank,r.rank);
                recovered++;
                for(U b:r.states){states++;cross+=scan({unmix(y0),b},gap,dst,count);}
            }
        }
    }
    double secs=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
    std::printf("ORIGINAL configurations=%u inverse_consistent=%llu inconsistent=%llu states=%llu minrank=%u offsets_per_state=%llu cross_matches=%llu wall=%.3fs\n",
               8*maxgap,recovered,unfit,states,minrank,count,cross,secs);
}
