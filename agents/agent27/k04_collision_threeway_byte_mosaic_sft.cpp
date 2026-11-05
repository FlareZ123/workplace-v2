// Source-collision byte mosaic: LABEL attempt1, RECOVER REQUESTED attempt1, copied RECOVER ACK2.
// Build with C++17 and OpenSSL libcrypto; argument is the original spool-reconstruction.log.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

using B16 = std::array<unsigned char,16>;
constexpr B16 label1={0xE1,0xE6,0x0D,0x5F,0x6B,0x6D,0xD2,0x22,0x5F,0xA6,0xD5,0xA2,0xA6,0x3A,0xD9,0x32};
constexpr B16 requested1={0xCD,0x3E,0x4F,0x21,0x6A,0xDB,0x2F,0xB1,0x80,0xDA,0x2A,0xA9,0x0B,0x33,0xF7,0xA4};
constexpr B16 copied2={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
constexpr B16 mask={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr std::array<unsigned char,32> target={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
constexpr std::array<unsigned char,32> spool_hash={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
constexpr B16 source[3]={label1,requested1,copied2};
B16 component{};
std::array<unsigned char,32> planted{};
std::uint64_t checked=0, genuine=0, positives=0;

void recurse(int pos) {
    if (pos == 16) {
        unsigned char out[32];
        SHA256(component.data(), component.size(), out);
        genuine += std::equal(out, out+32, target.begin());
        positives += std::equal(out, out+32, planted.begin());
        ++checked;
        return;
    }
    for (int j=0;j<3;j++) {
        component[pos] = source[j][pos] ^ mask[pos];
        recurse(pos+1);
    }
}
int main(int argc,char**argv){
    assert(argc==2);
    std::ifstream in(argv[1],std::ios::binary);
    assert(in.good());
    std::string text((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
    unsigned char sha[32];
    SHA256(reinterpret_cast<const unsigned char*>(text.data()),text.size(),sha);
    assert(std::equal(sha,sha+32,spool_hash.begin()));
    assert(text.find("2026-10-03T16:45:00+00:00 JOB=PS-261003-0417 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=E1E60D5F6B6DD2225FA6D5A2A63AD932")!=std::string::npos);
    assert(text.find("2026-10-03T18:01:00Z JOB=PS-261003-0417 ATTEMPT=1 STATE=REQUESTED CLASS=RECOVER PAYLOAD=CD3E4F216ADB2FB180DA2AA90B33F7A4")!=std::string::npos);
    assert(text.find("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5")!=std::string::npos);
    B16 planted_component{};
    for (int k=0;k<16;k++) planted_component[k]=source[k%3][k]^mask[k];
    SHA256(planted_component.data(),planted_component.size(),planted.data());
    const auto t0=std::chrono::steady_clock::now();
    recurse(0);
    const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    assert(checked==43046721);
    assert(positives==1);
    std::cout<<"SOURCE_SHA_PIN_PASS collision_LABEL1_REQUESTED1_ACK2 assignments="<<checked
             <<" original_hits="<<genuine<<" planted_hits="<<positives<<" seconds="<<elapsed<<"\n";
}