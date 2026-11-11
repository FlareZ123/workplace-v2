// K04 complete selected-coupon reconstruction from two 16-bit checkpoint donors.
// Original source, commitments and selected ACK2 copied bytes are read-only.
// This tests a conditional native-MT19937 two-gap model, not hardware provenance.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>

using Block = std::array<uint8_t, 16>;
using Hash = std::array<uint8_t, 32>;
using Words = std::array<uint32_t, 4>;

static void require(bool b, const std::string& message) {
    if (!b) throw std::runtime_error(message);
}
static int nibble(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    throw std::runtime_error("bad hex digit");
}
template<size_t N> static std::array<uint8_t,N> hex(const std::string& s) {
    require(s.size() == 2*N, "bad hex length");
    std::array<uint8_t,N> out{};
    for(size_t i=0;i<N;++i) out[i]=uint8_t((nibble(s[2*i])<<4)|nibble(s[2*i+1]));
    return out;
}
static Hash digest(const uint8_t* p, size_t n) {
    Hash result{};
    SHA256(p,n,result.data());
    return result;
}
static Hash digest(const Block& b) { return digest(b.data(),b.size()); }
static std::string to_hex(const uint8_t* p, size_t n) {
    const char *h="0123456789ABCDEF";
    std::string s; s.reserve(2*n);
    for(size_t i=0;i<n;++i){s.push_back(h[p[i]>>4]);s.push_back(h[p[i]&15]);}
    return s;
}
static std::vector<uint8_t> read(const std::filesystem::path& p) {
    std::ifstream f(p,std::ios::binary);
    require(bool(f),"unable to read "+p.string());
    return std::vector<uint8_t>(std::istreambuf_iterator<char>(f),{});
}
static void sha_file(const std::filesystem::path& p,const std::string& expected) {
    auto data=read(p);
    auto actual=digest(data.data(),data.size());
    require(to_hex(actual.data(),actual.size())==expected,
            "original-source SHA mismatch: "+p.string());
}
static uint32_t little(const uint8_t* p) {
    return uint32_t(p[0])|(uint32_t(p[1])<<8)|
           (uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);
}
static uint32_t untemper(uint32_t x) {
    uint32_t y=x;
    for(int i=0;i<6;++i)y=x^(y>>18);
    x=y;y=x;
    for(int i=0;i<6;++i)y=x^((y<<15)&0xefc60000u);
    x=y;y=x;
    for(int i=0;i<6;++i)y=x^((y<<7)&0x9d2c5680u);
    x=y;y=x;
    for(int i=0;i<6;++i)y=x^(y>>11);
    return y;
}
static uint32_t temper(uint32_t x) {
    x^=x>>11;
    x^=(x<<7)&0x9d2c5680u;
    x^=(x<<15)&0xefc60000u;
    x^=x>>18;
    return x;
}
static uint32_t twist(uint32_t x,uint32_t y) {
    uint32_t a=(x&0x80000000u)|(y&0x7fffffffu);
    return (a>>1)^((y&1u)?0x9908b0dfu:0u);
}
static Block coupon(uint32_t native327,const Words& a,const Words& b) {
    Block result{};
    for(int j=0;j<4;++j) {
        uint32_t left=j==0?native327:a[j-1];
        uint32_t right=a[j];
        uint32_t value=temper(b[j]^twist(left,right));
        for(int k=0;k<4;++k) result[4*j+k]=uint8_t(value>>(8*k));
    }
    return result;
}
static Block reduce(const Block& coupon,const Block& mask) {
    Block result{};
    for(int i=0;i<16;++i) result[i]=coupon[i]^mask[i];
    return result;
}
static std::vector<Words> views(const Block& block) {
    std::set<Words> unique;
    std::array<int,4> order={0,1,2,3};
    do {
        for(int swapped_pairs=0;swapped_pairs<16;++swapped_pairs)
        for(int halfbyte_reverse=0;halfbyte_reverse<2;++halfbyte_reverse)
        for(int wordbyte_reverse=0;wordbyte_reverse<2;++wordbyte_reverse)
        for(int already_native=0;already_native<2;++already_native) {
            Words native{};
            for(int j=0;j<4;++j){
                uint8_t bytes[4];
                int source_pair=order[j];
                for(int k=0;k<2;++k) {
                    int source_half=2*source_pair+
                        (k^((swapped_pairs>>j)&1));
                    int h=source_half*2;
                    bytes[2*k]=block[h+halfbyte_reverse];
                    bytes[2*k+1]=block[h+1-halfbyte_reverse];
                }
                if(wordbyte_reverse)std::reverse(bytes,bytes+4);
                uint32_t w=little(bytes);
                native[j]=already_native?w:untemper(w);
            }
            unique.insert(native);
        }
    } while(std::next_permutation(order.begin(),order.end()));
    return std::vector<Words>(unique.begin(),unique.end());
}
static void genuine_mt_positive() {
    std::mt19937 rng(20261111u);
    std::vector<uint32_t> output(955);
    for(auto& value:output)value=rng();
    Words a{},b{};
    for(int i=0;i<4;++i){
        a[i]=untemper(output[328+i]);
        b[i]=untemper(output[724+i]);
        require(temper(a[i])==output[328+i],"untemper/temper A");
        require(temper(b[i])==output[724+i],"untemper/temper B");
    }
    const uint32_t anchor=untemper(output[327]);
    Block predicted=coupon(anchor,a,b);
    for(int i=0;i<4;++i)
        require(little(predicted.data()+4*i)==output[951+i],
                "real std::mt19937 stage-reconstruction control failed");
}
int main() {
    try {
        const auto root=std::filesystem::current_path();
        const auto evidence=root/"resources/evidence";
        sha_file(evidence/"print/spool-reconstruction.log",
                 "7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083");
        sha_file(evidence/"telemetry/freeze-export.jsonl",
                 "3787DBD6BAB3930EA5293C25A995175161A1C0D7683DAAD29F498026E057639F");
        sha_file(evidence/"transfers/transfer-audit.jsonl",
                 "32970AD4431A9D610CC12DCCA2813F39DD8FD2E396F9E748DC94B5932CB69ADF");
        sha_file(evidence/"recovery-routing.json",
                 "F8FCBCA73D23BF1066EDB88C088F89CD24CF22E7C78A4A412166254A4764D8A5");
        sha_file(root/"resources/acceptance.json",
                 "681739241B757B471ACCA4C0FEF9D9D97E9493887736D5DB3B92BFB0C137F");

        // K02 GOOD/HOLD greatest-revision DIAG_WORDs, seq0..7,
        // and K07 AX-7782 confirmed highest-attempt checkpoints, seq0..7.
        const Block k02=hex<16>("E1A5E474BAD7E853A2E8C71D3317D507");
        const Block k07=hex<16>("8947CEDCB9CC73BAB7E87BE63302C5C9");
        Hash k02hash=digest(k02), k07hash=digest(k07);
        require(to_hex(k02hash.data(),16)=="0D7E3AB56FB75DA3EB0E2E06786D239E",
                "K02 original prehash reduction");
        require(to_hex(k07hash.data(),16)=="93495F5E425AB8E592123DABAEB68545",
                "K07 original prehash reduction");
        const Block mask=hex<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
        const Hash target=hex<32>(
            "930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");
        const uint32_t x327=0x59e4d0b9u;
        auto spool=read(evidence/"print/spool-reconstruction.log");
        const std::string body(spool.begin(),spool.end());
        require(body.find("JOB=PS-261003-0343 ATTEMPT=1 STATE=ACK CLASS=STORES "
                          "PAYLOAD=FD407A70CADBF57BDB0FDCEF01F48B22")!=std::string::npos,
                "printer row43 source selector changed");
        require(untemper(little(hex<16>("FD407A70CADBF57BDB0FDCEF01F48B22").data()+12))
                ==x327,"printer source native X327");

        genuine_mt_positive();
        auto k02views=views(k02),k07views=views(k07);
        require(k02views.size()==1536 && k07views.size()==1536,
                "unexpected halfword geometry views");

        // Separate planted full-component SHA target checks the original route
        // and enumeration, and is never substituted for the authentic target.
        const Hash planted=digest(reduce(coupon(x327,k02views[13],k07views[911]),mask));
        uint64_t checked=0, original_hits=0, planted_hits=0;
        for(int swapped=0;swapped<2;++swapped){
            const auto& left=swapped?k07views:k02views;
            const auto& right=swapped?k02views:k07views;
            for(const auto& a:left) for(const auto& b:right){
                const auto candidate=reduce(coupon(x327,a,b),mask);
                const Hash d=digest(candidate);
                ++checked;
                if(d==planted)++planted_hits;
                if(d==target){
                    ++original_hits;
                    std::cout<<"ORIGINAL_K04_COMPONENT "
                             <<to_hex(candidate.data(),candidate.size())
                             <<" source_order "<<swapped<<"\n";
                }
            }
        }
        require(checked==2u*1536u*1536u, "incomplete donor search");
        require(planted_hits>=1, "planted full-component control missing");
        std::cout<<"K04_K02_K07_GAP_HALFWORDAFFINE"
                 <<" original_candidate_checks "<<checked
                 <<" donor_views_each "<<k02views.size()
                 <<" original_K04_matches "<<original_hits
                 <<" planted_full_component_hits "<<planted_hits
                 <<" genuine_MT19937_control PASS\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr<<"TEST_FAILURE: "<<e.what()<<"\n";
        return 1;
    }
}
