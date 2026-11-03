// H-17 K04: exhaustive global hex-glyph involution copied-media model.
// One-file C++17/OpenSSL SFT. Run from repository root after compilation.
// 46,206,736 involutions * three distinct copy stages = 138,620,208 assignments.
// Historical original K04 source/route/checksum are never modified.
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <openssl/sha.h>

constexpr char const* SRC = "A9A9DC5731A5E2AE879C47215C2559D5";
constexpr char const* MASK = "8556C8CB6140A7F9A5123AC7571BEE1C";
constexpr char const* TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
constexpr char const* SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
int perm[16], source[32], mask[32], component[32];
unsigned char target_digest[32], planted_digest[3][32];
unsigned long long mappings = 0, target_hits = 0, planted_hits[3] = {};

char hexchar(int x) { return "0123456789ABCDEF"[x]; }
int digit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return c - 'A' + 10;
}
void decode(const char* text, unsigned char* out, int bytes) {
    for (int i = 0; i < bytes; ++i)
        out[i] = static_cast<unsigned char>((digit(text[2*i]) << 4) | digit(text[2*i+1]));
}
std::string read_file(const char* path) {
    std::ifstream stream(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>());
}
bool source_control() {
    std::string spool = read_file("resources/evidence/print/spool-reconstruction.log");
    if (spool.empty()) return false;
    unsigned char digest[32];
    SHA256(reinterpret_cast<const unsigned char*>(spool.data()), spool.size(), digest);
    char text[65];
    for (int i=0; i<32; ++i) std::sprintf(text+2*i,"%02x",digest[i]);
    text[64]='\0';
    if (std::strcmp(text,SPOOL_SHA)) return false;
    const std::string selected = std::string("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=")+SRC;
    if (spool.find(selected) == std::string::npos) return false;
    std::string routing = read_file("resources/evidence/recovery-routing.json");
    std::string acceptance = read_file("resources/acceptance.json");
    return routing.find(MASK) != std::string::npos && acceptance.find(TARGET) != std::string::npos;
}
void construct(unsigned char out[3][16]) {
    for (int i=0; i<16; ++i) {
        int native = (source[2*i]<<4) | source[2*i+1];
        int route = (mask[2*i]<<4) | mask[2*i+1];
        int payload_swap = (perm[source[2*i]]<<4) | perm[source[2*i+1]];
        int route_swap = (perm[mask[2*i]]<<4) | perm[mask[2*i+1]];
        out[0][i] = static_cast<unsigned char>(payload_swap ^ route);
        out[1][i] = static_cast<unsigned char>(native ^ route_swap);
        out[2][i] = static_cast<unsigned char>((perm[component[2*i]]<<4) | perm[component[2*i+1]]);
    }
}
void evaluate() {
    unsigned char candidates[3][16], digest[32];
    construct(candidates);
    for (int stage=0; stage<3; ++stage) {
        SHA256(candidates[stage],16,digest);
        if (!std::memcmp(digest,target_digest,32)) {
            ++target_hits;
            std::printf("AUTHENTIC_HIT stage=%d map=",stage);
            for (int j=0;j<16;++j) std::putchar(hexchar(perm[j]));
            std::printf(" component=");
            for (unsigned char b: candidates[stage]) std::printf("%02X",b);
            std::putchar('\n');
        }
        if (!std::memcmp(digest,planted_digest[stage],32)) ++planted_hits[stage];
    }
    ++mappings;
}
void generate(int start) {
    while (start<16 && perm[start]>=0) ++start;
    if (start==16) { evaluate(); return; }
    perm[start]=start;
    generate(start+1);
    for (int t=start+1;t<16;++t) if (perm[t]<0) {
        perm[start]=t;
        perm[t]=start;
        generate(start+1);
        perm[t]=-1;
    }
    perm[start]=-1;
}
int main() {
    if (!source_control()) { std::puts("ERROR original source pin"); return 2; }
    for (int i=0;i<32;++i) {
        source[i]=digit(SRC[i]); mask[i]=digit(MASK[i]);
    }
    for (int i=0;i<16;++i) {
        int b = ((source[2*i]<<4)|source[2*i+1]) ^ ((mask[2*i]<<4)|mask[2*i+1]);
        component[2*i]=b>>4; component[2*i+1]=b&15;
    }
    decode(TARGET,target_digest,32);
    for (int i=0;i<16;++i) perm[i]=i;
    // A planted non-affine multi-pair map. These controls exercise all three stages.
    perm[0]=5;perm[5]=0;perm[1]=10;perm[10]=1;perm[2]=15;perm[15]=2;
    unsigned char synthetic[3][16];
    construct(synthetic);
    for (int stage=0;stage<3;++stage) SHA256(synthetic[stage],16,planted_digest[stage]);
    for (int i=0;i<16;++i) perm[i]=-1;
    generate(0);
    std::printf("mappings=%llu assignments=%llu target_hits=%llu planted_hits=%llu,%llu,%llu\n",
        mappings, mappings*3ULL, target_hits, planted_hits[0], planted_hits[1], planted_hits[2]);
    const bool pass = mappings==46206736ULL && target_hits==0
        && planted_hits[0] && planted_hits[1] && planted_hits[2];
    std::puts(pass ? "SOURCE_AND_SYNTHETIC_CONTROLS_PASS; NO_ORIGINAL_K04_MATCH"
                   : "UNEXPECTED_RESULT");
    return pass ? 0 : 1;
}
