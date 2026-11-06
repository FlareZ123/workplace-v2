// Original-source five-distinct-byte, one-bit-per-byte K04 fault search.
// C++17/OpenSSL/OpenMP: original source and verifier are read-only.
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <omp.h>

using Block = std::array<unsigned char,16>;
using Digest = std::array<unsigned char,32>;

std::vector<unsigned char> from_hex(const std::string &hex) {
    std::vector<unsigned char> out;
    for (size_t i=0;i<hex.size();i+=2)
        out.push_back(static_cast<unsigned char>(std::stoul(hex.substr(i,2),nullptr,16)));
    return out;
}

template<size_t N> std::array<unsigned char,N> bytes(const std::string &hex) {
    const auto v = from_hex(hex);
    if (v.size()!=N) std::abort();
    std::array<unsigned char,N> a{};
    std::copy(v.begin(),v.end(),a.begin());
    return a;
}

Digest digest(const Block &b) {
    Digest d{};
    SHA256(b.data(),b.size(),d.data());
    return d;
}

int main(int argc, char **argv) {
    if (argc!=2) { std::cerr<<"usage: executable <path-to-spool-reconstruction.log>\n"; return 2; }
    std::ifstream f(argv[1],std::ios::binary);
    if (!f) return 2;
    const std::string raw((std::istreambuf_iterator<char>(f)),{});
    const Digest source=bytes<32>("7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083");
    Digest actual{};
    SHA256(reinterpret_cast<const unsigned char*>(raw.data()),raw.size(),actual.data());
    if (actual!=source) { std::cerr<<"SOURCE_SHA_MISMATCH\n"; return 2; }
    const std::string marker =
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
    const size_t pos=raw.find(marker);
    if (pos==std::string::npos) return 2;
    const Block original=bytes<16>(raw.substr(pos+marker.size(),32));
    const Block mask=bytes<16>("8556C8CB6140A7F9A5123AC7571BEE1C");
    const Digest target=bytes<32>("930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");
    Block reduced{};
    for(int j=0;j<16;++j) reduced[j]=original[j]^mask[j];

    const int planted_positions[5]={0,3,7,11,15};
    const int planted_bits[5]={2,5,1,4,7};
    Block planted=reduced;
    for(int j=0;j<5;++j)
        planted[planted_positions[j]] ^= static_cast<unsigned char>(1u<<planted_bits[j]);
    const Digest planted_target=digest(planted);

    std::uint64_t checks=0,hit=0,planted_hits=0;
    // Every five-distinct-byte support, each with one bit flipped.
    #pragma omp parallel for reduction(+:checks,hit,planted_hits) schedule(dynamic,1)
    for(int i=0;i<12;++i) for(int j=i+1;j<13;++j) for(int k=j+1;k<14;++k)
    for(int m=k+1;m<15;++m) for(int n=m+1;n<16;++n) {
        Block candidate=reduced;
        for(int a=0;a<8;++a) {
            candidate[i]=reduced[i]^static_cast<unsigned char>(1u<<a);
            for(int b=0;b<8;++b) {
                candidate[j]=reduced[j]^static_cast<unsigned char>(1u<<b);
                for(int c=0;c<8;++c) {
                    candidate[k]=reduced[k]^static_cast<unsigned char>(1u<<c);
                    for(int d=0;d<8;++d) {
                        candidate[m]=reduced[m]^static_cast<unsigned char>(1u<<d);
                        for(int e=0;e<8;++e) {
                            candidate[n]=reduced[n]^static_cast<unsigned char>(1u<<e);
                            Digest calc=digest(candidate);
                            ++checks;
                            if(calc==target) {
                                ++hit;
                                #pragma omp critical
                                {
                                    std::cout<<"ORIGINAL_K04_HIT=";
                                    const char* lut="0123456789ABCDEF";
                                    for(auto q:candidate) std::cout<<lut[q>>4]<<lut[q&15];
                                    std::cout<<'\n';
                                }
                            }
                            if(calc==planted_target) ++planted_hits;
                        }
                    }
                }
            }
        }
    }
    std::cout<<"SOURCE_PIN_PASS CHECKS="<<checks<<" ORIGINAL_HITS="<<hit
             <<" PLANTED_HITS="<<planted_hits<<"\n";
    if(checks!=143130624ull || planted_hits!=1) return 1;
    return hit ? 3 : 0;
}
