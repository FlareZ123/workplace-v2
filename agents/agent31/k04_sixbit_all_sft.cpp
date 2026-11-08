// H17 original-source selected-coupon exact six-bit Hamming shell.
// Evaluates 16-byte SHA256, selected clipboard XOR mask; source SHA pinned.
#include <openssl/sha.h>
#include <omp.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <algorithm>
#include <vector>
#include <utility>
using Block=std::array<unsigned char,16>;
using Digest=std::array<unsigned char,32>;

template<size_t N> std::array<unsigned char,N> hex(const std::string&s){
    if(s.size()!=2*N)std::abort(); std::array<unsigned char,N>r{};
    for(size_t i=0;i<N;++i)r[i]=static_cast<unsigned char>(std::stoul(s.substr(2*i,2),nullptr,16));
    return r;
}
Digest digest(const Block &b){Digest d;SHA256(b.data(),b.size(),d.data());return d;}
void print(const Block&b){const char *x="0123456789ABCDEF";for(auto c:b)std::cout<<x[c>>4]<<x[c&15];std::cout<<'\n';}
int main(int argc,char**argv){
    if(argc!=4){std::cerr<<"usage: h17_k04_sixbit_all_sft <spool-reconstruction.log> <a-start> <a-end>\n";return 2;}
    const int first=std::stoi(argv[2]),last=std::stoi(argv[3]);
    if(first<0||last>123||first>=last)return 2;
    std::ifstream file(argv[1],std::ios::binary);
    if(!file)return 2;
    const std::string raw((std::istreambuf_iterator<char>(file)),{});
    const Digest spoolsha=hex<32>("7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083");
    unsigned char rawsha[32];SHA256(reinterpret_cast<const unsigned char*>(raw.data()),raw.size(),rawsha);
    if(std::memcmp(rawsha,spoolsha.data(),32)!=0){std::cerr<<"SOURCE_MISMATCH\n";return 2;}
    const std::string marker="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
    const auto pos=raw.find(marker);if(pos==std::string::npos || raw.find(marker,pos+1)!=std::string::npos)return 2;
    const Block packet=hex<16>(raw.substr(pos+marker.size(),32));
    const Block mask=hex<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
    const Digest target=hex<32>("930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");
    Block baseline;for(int i=0;i<16;++i)baseline[i]=packet[i]^mask[i];
    Block planted=baseline;const int planted_bits[]={0,11,33,66,99,127};
    for(int bit:planted_bits)planted[bit>>3]^=static_cast<unsigned char>(1u<<(bit&7));
    const Digest planted_sha=digest(planted);
    uint64_t checked=0,hit=0,positive=0;
    const double began=omp_get_wtime();
    std::vector<std::pair<int,int>> pairs;
    for(int a=first;a<last;++a)for(int b=a+1;b<124;++b)pairs.emplace_back(a,b);
    #pragma omp parallel for schedule(dynamic,1) reduction(+:checked,hit,positive)
    for(size_t ix=0;ix<pairs.size();++ix){
        const int a=pairs[ix].first, b=pairs[ix].second;
        Block candidate=baseline;
        candidate[a>>3]^=static_cast<unsigned char>(1u<<(a&7));
        {
            candidate[b>>3]^=static_cast<unsigned char>(1u<<(b&7));
            for(int c=b+1;c<125;++c){
                candidate[c>>3]^=static_cast<unsigned char>(1u<<(c&7));
                for(int d=c+1;d<126;++d){
                    candidate[d>>3]^=static_cast<unsigned char>(1u<<(d&7));
                    for(int e=d+1;e<127;++e){
                        candidate[e>>3]^=static_cast<unsigned char>(1u<<(e&7));
                        for(int f=e+1;f<128;++f){
                        candidate[f>>3]^=static_cast<unsigned char>(1u<<(f&7));
                        const Digest h=digest(candidate);++checked;
                        if(h==planted_sha)++positive;
                        if(h==target){
                            ++hit;
                            #pragma omp critical
                            {std::cout<<"ORIGINAL_PASS=";print(candidate);}
                        }
                        candidate[f>>3]^=static_cast<unsigned char>(1u<<(f&7));
                        }
                        candidate[e>>3]^=static_cast<unsigned char>(1u<<(e&7));
                    }
                    candidate[d>>3]^=static_cast<unsigned char>(1u<<(d&7));
                }
                candidate[c>>3]^=static_cast<unsigned char>(1u<<(c&7));
            }
            candidate[b>>3]^=static_cast<unsigned char>(1u<<(b&7));
        }
    }
    uint64_t expected=0;
    for(int a=first;a<last;++a){const uint64_t n=127-a;expected+=n*(n-1)*(n-2)*(n-3)*(n-4)/120;}
    const uint64_t expected_positive=first<=0&&0<last ? 1:0;
    std::cout<<"SOURCE_PIN=PASS FIRST="<<first<<" LAST="<<last<<" CHECKED="<<checked<<" EXPECTED="<<expected<<" ORIGINAL_HITS="<<hit<<" PLANTED_HITS="<<positive
             <<" RUNTIME_SECONDS="<<(omp_get_wtime()-began)<<'\n';
    return checked==expected && positive==expected_positive ? (hit?3:0):2;
}
