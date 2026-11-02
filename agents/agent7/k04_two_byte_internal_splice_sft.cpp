// H-17 selected ESC-N K04: exact contiguous two-byte internal copy-slip sieve.
// Original printer SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
// Source: incident-date 18:02Z PS-261003-0417 ACK2 and original REC8/1 K04 commitment.
// Remove a contiguous two-byte observed span, insert two arbitrary bytes at any
// contiguous destination span; retain the other 14 source bytes in their order.
// This speculative copier hypothesis does not authenticate any physical error.
// Compile as C++17 with OpenSSL libcrypto and run without modifying case files.
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <openssl/sha.h>

using B16 = std::array<unsigned char, 16>;
static const B16 observed = {0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const B16 route_mask = {0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char target[32] = {0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};

static B16 splice(int deleted, int inserted, uint16_t added) {
    unsigned char retained[14];
    for (int i=0,j=0;i<16;i++) if (i<deleted || i>=deleted+2) retained[j++]=observed[i];
    B16 r;
    for (int i=0,j=0;i<16;i++) {
        if (i==inserted) r[i]=static_cast<unsigned char>(added>>8);
        else if (i==inserted+1) r[i]=static_cast<unsigned char>(added);
        else r[i]=retained[j++];
    }
    return r;
}

int main() {
    const B16 positive=splice(0,7,0xC0DE);
    if (positive[7]!=0xC0 || positive[8]!=0xDE || positive[0]!=observed[2] || positive[15]!=observed[15]) {
        std::puts("SYNTHETIC_STRUCTURE_CONTROL_FAIL");return 2;
    }
    B16 candidate,component;
    unsigned char digest[32], synthetic_target[32];
    for (int i=0;i<16;i++) component[i]=positive[i]^route_mask[i];
    SHA256(component.data(),16,synthetic_target);
    bool synthetic_found=false;
    for (uint32_t u=0;u<65536;u++) {
        candidate=splice(0,7,static_cast<uint16_t>(u));
        for (int i=0;i<16;i++) component[i]=candidate[i]^route_mask[i];
        SHA256(component.data(),16,digest);
        if (!std::memcmp(digest,synthetic_target,32)) {
            if (u!=0xC0DE) {std::puts("SYNTHETIC_INTEGRITY_CONTROL_FAIL");return 2;}
            synthetic_found=true;break;
        }
    }
    if (!synthetic_found) {std::puts("SYNTHETIC_SEARCH_CONTROL_FAIL");return 2;}
    std::puts("SYNTHETIC_HASH_SEARCH_PASS");

    uint64_t assignments=0;
    for (int del=0;del<=14;del++) {
        for (int ins=0;ins<=14;ins++) {
            for (uint32_t u=0;u<65536;u++) {
                candidate=splice(del,ins,static_cast<uint16_t>(u));
                for (int i=0;i<16;i++) component[i]=candidate[i]^route_mask[i];
                SHA256(component.data(),16,digest);
                assignments++;
                if (!std::memcmp(digest,target,32)) {
                    std::printf("K04_PASS deleted=%d inserted=%d added=%04X candidate=",del,ins,u);
                    for (auto x:component) std::printf("%02X",x);
                    std::puts("");return 0;
                }
            }
        }
        std::printf("Completed deletion offset %d/14 total=%llu\n",del,(unsigned long long)assignments);
        std::fflush(stdout);
    }
    std::printf("NO_MATCH original K04 commitment; assignments=%llu (15*15*65536)\n",(unsigned long long)assignments);
    return 1;
}
