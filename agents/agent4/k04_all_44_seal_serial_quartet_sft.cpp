// Agent 4: source-pinned exhaustive four-receipt K04 coupon assembly SFT.
// Build with C++17 and OpenSSL libcrypto. Original input is resources/evidence/maintenance/seal-receipts.jsonl.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>

using Coupon = std::array<unsigned char,16>;
static const char* seal_pin="c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32";
static const char* K04="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const char* mask="8556C8CB6140A7F9A5123AC7571BEE1C";

std::vector<unsigned char> parsehex(const std::string& h) {
    if(h.size()%2) throw std::runtime_error("odd hex");
    std::vector<unsigned char> a;
    for(std::size_t i=0;i<h.size();i+=2)
        a.push_back(static_cast<unsigned char>(std::stoul(h.substr(i,2),nullptr,16)));
    return a;
}
std::string printhex(const unsigned char* a, std::size_t n) {
    static const char* c="0123456789abcdef";
    std::string s(n*2,'0');
    for(std::size_t i=0;i<n;++i){s[2*i]=c[a[i]>>4];s[2*i+1]=c[a[i]&15];}
    return s;
}
int main(int argc,char** argv) {
    if(argc!=2) {std::cerr<<"Usage: sft <original seal-receipts.jsonl>\n";return 2;}
    std::ifstream f(argv[1],std::ios::binary);
    if(!f) throw std::runtime_error("source not readable");
    const std::string raw((std::istreambuf_iterator<char>(f)),{});
    unsigned char sum[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(raw.data()),raw.size(),sum);
    if(printhex(sum,sizeof(sum))!=seal_pin) throw std::runtime_error("source SHA256 mismatch");
    std::regex r(R"r("serial"\s*:\s*"SG-([A-F0-9]{8})")r");
    std::vector<std::array<unsigned char,4>> receipts;
    for(auto i=std::sregex_iterator(raw.begin(),raw.end(),r);i!=std::sregex_iterator();++i){
        const auto v=parsehex((*i)[1].str());
        std::array<unsigned char,4> x{};
        std::copy(v.begin(),v.end(),x.begin());
        receipts.push_back(x);
    }
    if(receipts.size()!=44) throw std::runtime_error("must recover 44 original receipts");
    const auto m=parsehex(mask), t=parsehex(K04);
    using Word = std::array<unsigned char,4>;
    std::array<std::array<std::array<Word,2>,44>,4> chunks{};
    for(int lane=0;lane<4;lane++)
        for(int k=0;k<44;k++)
            for(int e=0;e<2;e++)
                for(int j=0;j<4;j++)
                    chunks[lane][k][e][j]=receipts[k][e?3-j:j]^m[4*lane+j];
    const int pidx[4]={1,7,13,37};
    const int pe[4]={1,0,1,0};
    Coupon synthetic{};
    for(int lane=0;lane<4;lane++)
        std::copy(chunks[lane][pidx[lane]][pe[lane]].begin(),
                  chunks[lane][pidx[lane]][pe[lane]].end(),
                  synthetic.begin()+4*lane);
    unsigned char planted[SHA256_DIGEST_LENGTH];
    SHA256(synthetic.data(),synthetic.size(),planted);
    const auto start=std::chrono::steady_clock::now();
    std::uint64_t total=0;
    int matches=0, positive=0;
    Coupon coupon{};
    for(int a=0;a<44;a++)
        for(int b=0;b<44;b++) if(a!=b)
            for(int c=0;c<44;c++) if(c!=a&&c!=b)
                for(int d=0;d<44;d++) if(d!=a&&d!=b&&d!=c)
                    for(int e=0;e<16;e++){
                        const int ids[4]={a,b,c,d};
                        for(int lane=0;lane<4;lane++)
                            std::copy(chunks[lane][ids[lane]][(e>>lane)&1].begin(),
                                      chunks[lane][ids[lane]][(e>>lane)&1].end(),
                                      coupon.begin()+4*lane);
                        unsigned char dig[SHA256_DIGEST_LENGTH];
                        SHA256(coupon.data(),coupon.size(),dig);
                        total++;
                        if(!std::memcmp(dig,t.data(),32)){
                            matches++;
                            std::cout<<"K04 FULL HIT "<<printhex(coupon.data(),16)<<"\n";
                        }
                        if(!std::memcmp(dig,planted,32)){
                            positive++;
                            if(a!=1||b!=7||c!=13||d!=37||e!=5)
                                throw std::runtime_error("planted match wrong");
                        }
                    }
    if(total!=static_cast<std::uint64_t>(44)*43*42*41*16||positive!=1)
        throw std::runtime_error("incomplete run or planted control failed");
    const auto elapsed=std::chrono::duration<double>(
        std::chrono::steady_clock::now()-start).count();
    std::cout<<"COMPLETE tested="<<total<<" original_hits="<<matches
             <<" synthetic_positive="<<positive<<" seconds="<<elapsed<<"\n";
}
