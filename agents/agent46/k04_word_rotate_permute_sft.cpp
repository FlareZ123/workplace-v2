/* SFT: four independent 32-bit word rotations and four-word reordering of
   the original H-17 ESC-N selected ACK2 copied coupon. Source-only mask and
   SHA256 target remain immutable. Needs standard C++17 plus OpenSSL libcrypto.
   argv[1] is the original spool-reconstruction.log path.
   SHA256 source pin and synthetic planted exact full candidate are mandatory. */
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <regex>
#include <stdexcept>
#include <string>
#include <openssl/sha.h>

using Block=std::array<uint8_t,16>;
static const std::string SHA_SPOOL="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const std::string SHA_K04="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static const Block MASK={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};

static std::string tohex(const uint8_t* p,size_t len) {
    const char* digits="0123456789abcdef";
    std::string out;
    for(size_t i=0;i<len;i++){out+=digits[p[i]>>4];out+=digits[p[i]&15];}
    return out;
}
static uint8_t decode(const std::string& s,size_t i) {
    return static_cast<uint8_t>(std::stoul(s.substr(i*2,2),nullptr,16));
}
static uint32_t rol(uint32_t v,int n) {
    return n ? (v<<n)|(v>>(32-n)) : v;
}
static uint32_t word(const Block& a,int index,bool big) {
    uint32_t n=0;
    for(int j=0;j<4;j++)
        if(big)n=(n<<8)|a[index*4+j];
        else n|=uint32_t(a[index*4+j])<<(8*j);
    return n;
}
static void encode(uint8_t* dest,uint32_t val,bool big) {
    for(int j=0;j<4;j++)dest[j]=static_cast<uint8_t>(val >> (8*(big?3-j:j)));
}
static Block transform(const Block& input,const std::array<int,4>& rot,
                       const std::array<int,4>& perm,bool big) {
    Block out{};
    for(int j=0;j<4;j++)encode(out.data()+4*j,rol(word(input,perm[j],big),rot[perm[j]]),big);
    for(int j=0;j<16;j++)out[j]^=MASK[j];
    return out;
}
int main(int argc,char** argv) {
    if(argc!=2)throw std::runtime_error("pass original spool path");
    std::ifstream f(argv[1],std::ios::binary);
    if(!f)throw std::runtime_error("missing original spool");
    const std::string raw((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
    uint8_t digest[32];
    SHA256(reinterpret_cast<const uint8_t*>(raw.data()),raw.size(),digest);
    if(tohex(digest,32)!=SHA_SPOOL)throw std::runtime_error("incorrect spool SHA256");

    std::istringstream input(raw);
    std::regex pattern("PAYLOAD=([0-9A-F]{32})");
    std::string line;
    Block selected{};
    int row=0, selected_count=0;
    while(std::getline(input,line)) {
        if(line.find(" PAYLOAD=")==std::string::npos)continue;
        if(line.find("JOB=PS-261003-0417 ")!=std::string::npos
           &&line.find("ATTEMPT=2 ")!=std::string::npos
           &&line.find("STATE=ACK ")!=std::string::npos
           &&line.find("CLASS=RECOVER ")!=std::string::npos) {
            if(row!=129)throw std::runtime_error("wrong source row");
            std::smatch match;
            if(!std::regex_search(line,match,pattern))throw std::runtime_error("absent payload");
            for(int i=0;i<16;i++)selected[i]=decode(match[1],i);
            selected_count++;
        }
        row++;
    }
    if(row!=133||selected_count!=1||tohex(selected.data(),16)!="a9a9dc5731a5e2ae879c47215c2559d5")
        throw std::runtime_error("unexpected selected event");
    std::array<int,4> plantrot={7,3,19,11}, plantperm={2,0,3,1};
    Block planted=transform(selected,plantrot,plantperm,false);
    uint8_t planted_sha[32];
    SHA256(planted.data(),16,planted_sha);
    uint8_t target_sha[32];
    for(int j=0;j<32;j++)target_sha[j]=decode(SHA_K04,j);
    uint64_t evaluated=0,positive=0,original=0;
    for(int direction=0;direction<2;direction++) {
        bool big=direction==1;
        std::array<std::array<std::array<uint8_t,4>,32>,4> rotates{};
        for(int w=0;w<4;w++)
            for(int r=0;r<32;r++)encode(rotates[w][r].data(),rol(word(selected,w,big),r),big);
        std::array<int,4> perm={0,1,2,3};
        do {
            for(int r0=0;r0<32;r0++)for(int r1=0;r1<32;r1++)
                for(int r2=0;r2<32;r2++)for(int r3=0;r3<32;r3++) {
                    const int shift[]={r0,r1,r2,r3};
                    Block candidate{};
                    for(int out=0;out<4;out++)
                        for(int byte=0;byte<4;byte++)
                            candidate[out*4+byte]=rotates[perm[out]][shift[perm[out]]][byte]^MASK[out*4+byte];
                    SHA256(candidate.data(),16,digest);
                    evaluated++;
                    if(std::memcmp(digest,planted_sha,32)==0)positive++;
                    if(std::memcmp(digest,target_sha,32)==0) {
                        original++;
                        std::cout<<"ORIGINAL_HIT "<<tohex(candidate.data(),16)<<"\n";
                    }
                }
        }while(std::next_permutation(perm.begin(),perm.end()));
    }
    if(evaluated!=50331648||positive!=1)throw std::runtime_error("coverage/control failure");
    std::cout<<"SOURCE "<<SHA_SPOOL<<"\n"
             <<"SELECTED_COPY "<<tohex(selected.data(),16)<<"\n"
             <<"PLANTED_COMPONENT "<<tohex(planted.data(),16)<<"\n"
             <<"CHECKED "<<evaluated<<" PLANTED_HITS "<<positive<<" K04_HITS "<<original<<"\n";
}