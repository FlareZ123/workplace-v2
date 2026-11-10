#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>

using Hex32 = std::array<uint8_t, 16>;
using Nibbles = std::array<uint8_t, 32>;
using Digest = std::array<uint8_t, 32>;

static const std::string spool_sha = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const std::string route_sha = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const std::string acceptance_sha = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const std::string target = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";

static uint8_t hex_digit(char c) {
    if (c >= '0' && c <= '9') return static_cast<uint8_t>(c - '0');
    if (c >= 'A' && c <= 'F') return static_cast<uint8_t>(c - 'A' + 10);
    if (c >= 'a' && c <= 'f') return static_cast<uint8_t>(c - 'a' + 10);
    throw std::runtime_error("invalid hex");
}
static std::string hex(const uint8_t *data, size_t n) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string out;
    out.reserve(n * 2);
    for (size_t i=0; i<n; ++i) {out.push_back(digits[data[i] >> 4]);out.push_back(digits[data[i] & 15]);}
    return out;
}
static Hex32 load16(const std::string &s) {
    if(s.size()!=32)throw std::runtime_error("16-byte hex length");
    Hex32 o{};
    for(size_t i=0;i<16;++i)o[i] = (hex_digit(s[2*i])<<4)|hex_digit(s[2*i+1]);
    return o;
}
static Digest sha(const Hex32 &v){ Digest d{}; SHA256(v.data(),v.size(),d.data());return d; }
static Digest sha_file(const std::filesystem::path &p){
    std::ifstream f(p,std::ios::binary);
    if(!f)throw std::runtime_error("cannot read "+p.string());
    std::string data(std::istreambuf_iterator<char>{f},{});
    Digest d{};SHA256(reinterpret_cast<const unsigned char*>(data.data()),data.size(),d.data());return d;
}
static void check_file(const std::filesystem::path &p,const std::string &expected){
    auto s=sha_file(p);if(hex(s.data(),s.size())!=expected)throw std::runtime_error("source SHA mismatch "+p.string());
}
static Nibbles split(const Hex32 &v){Nibbles n{};for(size_t i=0;i<16;++i){n[i*2]=v[i]>>4;n[i*2+1]=v[i]&15;}return n;}
static Hex32 pack(const Nibbles &v){Hex32 o{};for(size_t i=0;i<16;++i)o[i]=(v[i*2]<<4)|v[i*2+1];return o;}
static Hex32 bitxor(const Hex32 &a,const Hex32 &b){Hex32 r{};for(size_t i=0;i<16;++i)r[i]=a[i]^b[i];return r;}
static Nibbles transform(const Nibbles &in,int rows,int cols, const std::array<int,8> &rp,const std::array<int,8> &cp, bool snake){
    Nibbles out{};
    for(int r=0;r<rows;++r)for(int c=0;c<cols;++c){
        int dst=r*cols+c;int src=rp[r]*cols+cp[snake && (r&1)?cols-1-c:c];out[dst]=in[src];
    }
    return out;
}
static Hex32 construction(const Hex32 &payload,const Hex32 &mask,int stage,const Hex32 &reordered){
    if(stage==0)return bitxor(reordered,mask);
    if(stage==1)return bitxor(payload,reordered);
    return reordered;
}
int main(int argc, char**argv){
    try{
        const std::filesystem::path root=argc>=2?argv[1]:"resources";
        check_file(root/"evidence/print/spool-reconstruction.log",spool_sha);
        check_file(root/"evidence/recovery-routing.json",route_sha);
        check_file(root/"acceptance.json",acceptance_sha);
        const Hex32 payload=load16("A9A9DC5731A5E2AE879C47215C2559D5");
        const Hex32 mask=load16("8556C8CB6140A7F9A5123AC7571BEE1C");
        const Hex32 reduced=bitxor(payload,mask);
        const std::array<Hex32,3> sources{payload,mask,reduced};
        const std::array<Nibbles,3> nib{split(payload),split(mask),split(reduced)};
        const auto expected=target;
        std::array<Digest,3> planted{};
        // Independently planted nonidentity transformations, isolated from the original commitment.
        for(int stage=0;stage<3;++stage){
            std::array<int,8> rp{2,0,3,1,4,5,6,7};
            std::array<int,8> cp{3,6,1,4,7,0,5,2};
            auto s=pack(transform(nib[stage],4,8,rp,cp,true));
            planted[stage]=sha(construction(payload,mask,stage,s));
        }
        std::array<uint64_t,3> hit{},controls{};
        uint64_t layouts=0;
        for(int rows:{4,8}){
            int cols=32/rows;
            std::array<int,8> rp{},cp{};
            for(int r=0;r<rows;++r)rp[r]=r;
            do{
                for(int c=0;c<cols;++c)cp[c]=c;
                do{
                    for(int snake=0;snake<2;++snake){
                        ++layouts;
                        for(int stage=0;stage<3;++stage){
                            auto x=pack(transform(nib[stage],rows,cols,rp,cp,snake!=0));
                            auto d=sha(construction(payload,mask,stage,x));
                            if(hex(d.data(),d.size())==expected){++hit[stage];std::cout<<"ORIGINAL HIT stage="<<stage<<" rows="<<rows<<" snake="<<snake<<" candidate="<<hex(construction(payload,mask,stage,x).data(),16)<<"\n";}
                            if(d==planted[stage])++controls[stage];
                        }
                    }
                }while(std::next_permutation(cp.begin(),cp.begin()+cols));
            }while(std::next_permutation(rp.begin(),rp.begin()+rows));
        }
        std::cout<<"layout_assignments="<<layouts<<" full_slot_hashes="<<layouts*3<<" original_hits="<<hit[0]<<","<<hit[1]<<","<<hit[2]<<" planted_hits="<<controls[0]<<","<<controls[1]<<","<<controls[2]<<"\n";
        if(layouts!=3870720 || !controls[0] || !controls[1] || !controls[2])return 2;
        return (hit[0]||hit[1]||hit[2])?3:0;
    }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 2;}
}
