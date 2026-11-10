/* H-17 original-source complete coupon scanner for five rank-32 stage windows.
 * Input: stdout of k04_five_gap_source_sft.py.
 * Each candidate is one complete 16-byte component with the immutable K04 mask.
 * All original comparisons use the full SHA256 commitment, not a prefix.
 */
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct Space {
    int rank, stage;
    std::array<unsigned char, 16> base;
    std::vector<std::array<unsigned char, 16>> directions;
};

static std::array<unsigned char, 16> hex16(const std::string& s) {
    if (s.size() != 32) throw std::runtime_error("invalid 16-byte hex");
    std::array<unsigned char, 16> out{};
    for (int i = 0; i < 16; ++i) {
        unsigned v = 0;
        if (std::sscanf(s.substr(2 * i, 2).c_str(), "%2x", &v) != 1)
            throw std::runtime_error("bad source hex");
        out[i] = static_cast<unsigned char>(v);
    }
    return out;
}
static inline void xor16(unsigned char* a, const unsigned char* b) {
    for (int i = 0; i < 16; ++i) a[i] ^= b[i];
}
static std::array<unsigned char, 32> original_digest() {
    constexpr char hex[] =
        "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
    std::array<unsigned char, 32> out{};
    for (int i = 0; i < 32; ++i) {
        unsigned v = 0;
        if (std::sscanf(std::string(hex + 2 * i, 2).c_str(), "%2x", &v) != 1)
            throw std::runtime_error("bad original acceptance digest");
        out[i] = static_cast<unsigned char>(v);
    }
    return out;
}
static uint64_t scan(
    const Space& s, const std::array<unsigned char, 32>& digest,
    uint64_t total, int threads, const char* label
) {
    const uint32_t iv[8] = {
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    };
    uint32_t target[8];
    for (int i = 0; i < 8; ++i)
        target[i] = (uint32_t(digest[4 * i]) << 24)
                  | (uint32_t(digest[4 * i + 1]) << 16)
                  | (uint32_t(digest[4 * i + 2]) << 8)
                  | digest[4 * i + 3];
    constexpr uint64_t CHUNK = 1ULL << 21;
    const uint64_t chunks = (total + CHUNK - 1) / CHUNK;
    uint64_t hits = 0;
    #pragma omp parallel for num_threads(threads) schedule(dynamic, 1) reduction(+:hits)
    for (uint64_t chunk = 0; chunk < chunks; ++chunk) {
        const uint64_t start = chunk * CHUNK;
        const uint64_t end = std::min(start + CHUNK, total);
        unsigned char value[16];
        std::memcpy(value, s.base.data(), 16);
        const uint64_t gray = start ^ (start >> 1);
        for (int i = 0; i < s.rank; ++i)
            if ((gray >> i) & 1) xor16(value, s.directions[i].data());
        SHA256_CTX ctx;
        unsigned char block[64]{};
        block[16] = 0x80;
        block[63] = 0x80;  // 16 bytes = 128 bits
        for (uint64_t index = start; index < end; ++index) {
            if (index != start)
                xor16(value, s.directions[__builtin_ctzll(index)].data());
            std::memcpy(block, value, 16);
            std::memcpy(ctx.h, iv, sizeof(iv));
            SHA256_Transform(&ctx, block);
            if (ctx.h[0] == target[0] &&
                std::memcmp(ctx.h, target, sizeof(target)) == 0) {
                #pragma omp critical
                {
                    std::printf("%s_MATCH stage=%d index=%llu K04=",
                        label, s.stage, (unsigned long long)index);
                    for (unsigned char x : value)
                        std::printf("%02X", unsigned(x));
                    std::printf("\n");
                    std::fflush(stdout);
                }
                ++hits;
            }
        }
    }
    return hits;
}
int main(int argc, char** argv) {
    try {
        const int threads = argc > 1 ? std::stoi(argv[1]) : 4;
        const uint64_t cap = argc > 2 ? std::stoull(argv[2]) : 0;
        if (threads < 1 || threads > 64)
            throw std::runtime_error("invalid threads");
        int n = 0;
        if (!(std::cin >> n) || n != 5)
            throw std::runtime_error("expected exactly five stages");
        const std::array<int, 5> stages{919, 923, 929, 935, 966};
        const auto digest = original_digest();
        uint64_t total = 0, authentic_hits = 0;
        for (int i = 0; i < n; ++i) {
            Space s{};
            std::string hex;
            if (!(std::cin >> s.rank >> s.stage >> hex) ||
                s.rank != 32 || s.stage != stages[i])
                throw std::runtime_error("unexpected rank or stage");
            s.base = hex16(hex);
            for (int j = 0; j < s.rank; ++j) {
                if (!(std::cin >> hex))
                    throw std::runtime_error("truncated source directions");
                s.directions.push_back(hex16(hex));
            }
            auto planted = s.base;
            constexpr uint64_t selected = 1337;
            const uint64_t gray = selected ^ (selected >> 1);
            for (int j = 0; j < s.rank; ++j)
                if ((gray >> j) & 1)
                    xor16(planted.data(), s.directions[j].data());
            std::array<unsigned char, 32> synthetic{};
            SHA256(planted.data(), 16, synthetic.data());
            if (scan(s, synthetic, 65536, threads, "SYNTHETIC") != 1)
                throw std::runtime_error("whole-coupon synthetic positive failed");
            const uint64_t full = uint64_t(1) << s.rank;
            const uint64_t count = cap ? std::min(cap, full) : full;
            const auto start = std::chrono::steady_clock::now();
            const auto hits = scan(s, digest, count, threads, "ORIGINAL");
            const double seconds = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - start).count();
            total += count;
            authentic_hits += hits;
            std::printf(
                "ORIGINAL_COMPLETE stage=%d rank=%d checked=%llu hits=%llu time=%.3fs\n",
                s.stage, s.rank, (unsigned long long)count,
                (unsigned long long)hits, seconds);
            std::fflush(stdout);
        }
        std::printf("SUMMARY checked=%llu authentic_hits=%llu\n",
            (unsigned long long)total, (unsigned long long)authentic_hits);
        return authentic_hits ? 2 : 0;
    } catch (const std::exception& x) {
        std::cerr << "ERROR " << x.what() << "\n";
        return 1;
    }
}
