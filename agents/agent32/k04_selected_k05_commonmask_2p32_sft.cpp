// H-17 K04: direct selected-K05 fourword common XOR whitening and full target.
// Original candidate, routing, acceptance and raw spool are read only.
// Hypothesis: the selected printer's actual 128-bit paper coupon is the
// independent accepted K05 recorder value XOR one repeated 32-bit mask.
// A physical producer is NOT authenticated by this mathematical hypothesis.
// SFT includes actual recovered K05 hash, original spool hash, a synthetic
// full SHA256 planted positive, and complete 64-shard partitioning.
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>

using Buf16 = std::array<unsigned char, 16>;
using Hash32 = std::array<unsigned char, SHA256_DIGEST_LENGTH>;

constexpr Buf16 K05 = {0xFF,0x8B,0x78,0x20,0x0A,0x56,0xE8,0x58,
                       0x6D,0xCD,0xA0,0x0E,0xF0,0x1E,0x45,0x72};
constexpr Buf16 MASK = {0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
                        0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
constexpr Hash32 K05_TARGET = {0xB1,0x84,0x09,0x66,0x4D,0x81,0x8B,0x4E,
                                0x35,0x74,0x00,0x04,0x9D,0xE6,0xC1,0xA7,
                                0xF0,0x6B,0x78,0xE5,0x76,0xAE,0xC7,0x8C,
                                0x14,0xC8,0xC6,0xBC,0x3F,0xE0,0x68,0xF9};
constexpr Hash32 K04_TARGET = {0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,
                                0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
                                0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,
                                0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
constexpr Hash32 SPOOL_TARGET = {0x7D,0x71,0xD8,0xBE,0xF7,0xF0,0x15,0x96,
                                  0xE7,0x05,0xAC,0x14,0xE2,0x4C,0x5C,0x43,
                                  0x52,0x04,0x25,0x12,0xB3,0x08,0x81,0x25,
                                  0xAF,0xCA,0x40,0xF3,0x84,0x1B,0x60,0x83};
constexpr uint32_t PLANT_MASK = 0xDEADBEEF;
constexpr int PLANT_VIEW = 3;
constexpr uint64_t N_SHARDS = 64;
constexpr uint64_t TOTAL_MASKS = uint64_t{1} << 32;

std::string read_file(const char* path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) {std::fprintf(stderr, "source unavailable: %s\n", path); std::exit(10);}
    return {std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()};
}

Hash32 sha(const unsigned char* data, std::size_t n) {
    Hash32 out{};
    SHA256(data, n, out.data());
    return out;
}

Buf16 candidate(uint32_t mask, int view) {
    Buf16 out{};
    for (int w=0; w<4; ++w) {
        const int oldw = (view & 1) ? (3-w) : w;
        for (int b=0; b<4; ++b) {
            const int oldb = (view & 2) ? (3-b) : b;
            const unsigned char m = static_cast<unsigned char>(mask >> (8*b));
            out[w*4+b] = K05[oldw*4+oldb] ^ m ^ MASK[w*4+b];
        }
    }
    return out;
}

int main(int argc, char** argv) {
    if (argc != 2) {std::fprintf(stderr, "one shard argument required 0..63\n"); return 2;}
    char* tail = nullptr;
    const unsigned long shard_ul = std::strtoul(argv[1], &tail, 10);
    if (tail == argv[1] || *tail || shard_ul >= N_SHARDS) return 2;
    const uint64_t shard = shard_ul;

    if (sha(K05.data(), 16) != K05_TARGET) return 11;
    const std::string spool=read_file("resources/evidence/print/spool-reconstruction.log");
    if (sha(reinterpret_cast<const unsigned char*>(spool.data()),spool.size()) != SPOOL_TARGET) return 12;
    if (spool.find("PS-261003-0417") == std::string::npos || spool.find("A9A9DC5731A5E2AE879C47215C2559D5") == std::string::npos) return 13;
    const std::string originalCandidate=read_file("resources/candidate.json");
    if (originalCandidate.find("FF8B78200A56E8586DCDA00EF01E4572") == std::string::npos) return 14;
    const std::string acceptance=read_file("resources/acceptance.json");
    if (acceptance.find("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0") == std::string::npos) return 15;
    std::printf("ORIGINAL_SOURCE_K05_HASH_AND_SPOOL_PINS_PASS shard=%lu\n",shard_ul);
    const Buf16 planted=candidate(PLANT_MASK,PLANT_VIEW);
    const Hash32 synthetic=sha(planted.data(),planted.size());
    if (synthetic==K04_TARGET) return 16;
    const uint64_t lo=shard*(TOTAL_MASKS/N_SHARDS);
    const uint64_t hi=(shard+1)*(TOTAL_MASKS/N_SHARDS);
    uint64_t synthetic_hits=0, original_hits=0, checks=0;
    for (uint64_t mask=lo; mask<hi; ++mask) {
        for (int view=0;view<4;++view) {
            const Buf16 output=candidate(static_cast<uint32_t>(mask),view);
            const Hash32 fingerprint=sha(output.data(),output.size());
            ++checks;
            if (fingerprint==synthetic) ++synthetic_hits;
            if (fingerprint==K04_TARGET) {
                ++original_hits;
                std::printf("ORIGINAL_HIT seed=%08X view=%d component=",static_cast<uint32_t>(mask),view);
                for (auto ch:output) std::printf("%02X",ch);
                std::puts("");
                std::fflush(stdout);
            }
        }
    }
    const uint64_t expected=(PLANT_MASK>=lo && uint64_t(PLANT_MASK)<hi)?1:0;
    std::printf("COMPLETE shard=%lu lo=%llu hi=%llu checks=%llu original=%llu planted=%llu expected=%llu\n",
        shard_ul, (unsigned long long)lo,(unsigned long long)hi,
        (unsigned long long)checks,(unsigned long long)original_hits,
        (unsigned long long)synthetic_hits,(unsigned long long)expected);
    std::fflush(stdout);
    if (checks != 4*(TOTAL_MASKS/N_SHARDS) || synthetic_hits!=expected || original_hits) return 3;
    return 0;
}
