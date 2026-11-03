// Source-only exhaustive PCG64 XSL-RR known-increment lattice search.
// Requires C++20, GCC/Clang __int128; original-source three-packet model.
// Search only normal spool rows 0300..0302; selected K04 row is never read.
// Bouillaguet/Martinez/Sauvage (2020) CVP method with a certified 3x3 basis.
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

using u64 = std::uint64_t;
using i64 = std::int64_t;
using u128 = unsigned __int128;
using i128 = __int128;
static constexpr u128 A = ((u128)0x2360ED051FC65DA4ULL << 64) | 0x4385DF649FCCF645ULL;
static constexpr u128 C = ((u128)0x5851F42D4C957F2DULL << 64) | 0x14057B7EF767814FULL;
static constexpr i64 B[3][3] = {
    {-1241281756092, 3827459685972, -728312298332},
    {-5001120657083, -2117155768935, 5479732607037},
    {8655886039732, 3303731088004, 6319848582548}
};
// EXACT B inverse is N / 2^64, verified on startup.
static constexpr i64 N[3][3] = {
    {-1706733, -1441724, 1053384},
    {4284673, -83512, 566185},
    {97768, 2018292, 1180131}
};
static constexpr i128 HALF = (i128)1 << 63;
static constexpr i128 MOD = (i128)1 << 64;

static inline u64 output(u128 s) {
    u64 hi = (u64)(s >> 64), lo = (u64)s;
    return std::rotr(hi ^ lo, (int)(hi >> 58));
}
static inline i64 nearest(i128 x) {
    return x >= 0 ? (i64)((x + HALF) / MOD) : -(i64)((-x + HALF) / MOD);
}
static bool recover_three(u64 x0, u64 x1, u64 x2, u128 increment,
                          unsigned ell, u64 low, int r0, int r1, int r2, u128* out) {
    const u64 obs[3] = {x0, x1, x2};
    const int r[3] = {r0, r1, r2};
    const u128 k[3] = {low, A * low + increment, A * A * low + (A + 1) * increment};
    const unsigned t = ell + 6, shift = 58 - ell;
    const u64 mask = (1ULL << t) - 1;
    u64 center[3];
    for (int i = 0; i < 3; ++i) {
        u64 unrotated = std::rotl(obs[i], r[i]);
        u64 observed_slice = ((r[i] ^ (unrotated >> 58)) & 63)
            | (((u64)(k[i] ^ unrotated) & ((1ULL << ell) - 1)) << 6);
        u64 difference = (observed_slice - ((u64)(k[i] >> 58) & mask)) & mask;
        center[i] = (difference << shift) + (1ULL << (shift - 1));
    }
    i64 z[3];
    for (int j = 0; j < 3; ++j) {
        i128 n = 0;
        for (int i = 0; i < 3; ++i) n += (i128)center[i] * N[i][j];
        z[j] = nearest(n);
    }
    u64 u = (u64)((i128)z[0] * B[0][0] + (i128)z[1] * B[1][0]
                  + (i128)z[2] * B[2][0]);
    u64 low64 = (u64)k[0] + ((u & ((1ULL << (64 - ell)) - 1)) << ell);
    u64 high64 = low64 ^ std::rotl(x0, r0);
    if ((high64 >> 58) != (unsigned)r0) return false;
    u128 s0 = ((u128)high64 << 64) | low64;
    u128 s1 = A * s0 + increment;
    if (output(s1) != x1) return false;
    u128 s2 = A * s1 + increment;
    if (output(s2) != x2) return false;
    *out = s0;
    return true;
}

static std::array<u64, 6> source(int view) {
    // Immutable first three intact original spool packets, SHA256 spool:
    // 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
    const char* packets[] = {
        "FBBBC54356483F5864BB3F06794518A5",
        "64176B6C3A91BD06B12FC0D90B3A7DB4",
        "3531D8AB362BB040E7702CE23A8D5420"
    };
    std::array<u64, 6> words{};
    for (int i = 0; i < 3; ++i) {
        u64 v[2]{};
        for (int j = 0; j < 2; ++j) {
            for (int k = 0; k < 8; ++k) {
                unsigned b = 0;
                std::sscanf(packets[i] + 2 * (8 * j + k), "%2x", &b);
                if (view & 1) v[j] = (v[j] << 8) | b;
                else v[j] |= (u64)b << (8 * k);
            }
        }
        words[2*i] = (view & 2) ? v[1] : v[0];
        words[2*i+1] = (view & 2) ? v[0] : v[1];
    }
    return words;
}

int main(int argc, char** argv) {
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j) {
            i128 sum = 0;
            for (int k = 0; k < 3; ++k) sum += (i128)B[i][k] * N[k][j];
            if (sum != (i == j ? MOD : 0)) {
                std::fputs("FAIL exact basis inverse\n", stderr);
                return 3;
            }
        }
    // Genuine NumPy PCG64(1234) state/increment/output control.
    constexpr u128 initial = ((u128)0x160AD84006FE21EAULL << 64) | 0xF69B873D9FE45409ULL;
    constexpr u128 inc = ((u128)0x50C8FB163C7CEA4EULL << 64) | 0xD0F51CE6006E4325ULL;
    u128 s0 = A * initial + inc, s1 = A * s0 + inc, s2 = A * s1 + inc;
    if (output(s0) != 0xFA08FEF3FAB6BBBAULL
        || output(s1) != 0x615481F7FCE9AC81ULL
        || output(s2) != 0xEC59DD7C2BDE3CB4ULL) return 4;
    for (unsigned ell = 18; ell <= 20; ++ell) {
        u128 recovered = 0;
        if (!recover_three(output(s0), output(s1), output(s2), inc, ell,
                           (u64)s0 & ((1ULL << ell) - 1),
                           (int)(s0 >> 122), (int)(s1 >> 122),
                           (int)(s2 >> 122), &recovered) || recovered != s0) return 5;
    }
    std::puts("PASS NumPy planted state, ell18/19/20 CVP and exact basis inverse");
    if (argc == 1) return 0;
    if (argc != 4) return 2;
    int view = std::atoi(argv[1]);
    unsigned begin = (unsigned)std::strtoul(argv[2], nullptr, 10);
    unsigned count = (unsigned)std::strtoul(argv[3], nullptr, 10);
    if (view < 0 || view > 3 || begin >= (1U << 19)
        || count > (1U << 19) || begin + count > (1U << 19)) return 2;
    const auto x = source(view);
    u64 fits3 = 0, fits6 = 0;
    auto start = std::chrono::steady_clock::now();
    for (unsigned low = begin; low < begin + count; ++low) {
        for (int r0 = 0; r0 < 64; ++r0)
            for (int r1 = 0; r1 < 64; ++r1)
                for (int r2 = 0; r2 < 64; ++r2) {
                    u128 candidate = 0;
                    if (recover_three(x[0], x[1], x[2], C, 19, low,
                                      r0, r1, r2, &candidate)) {
                        ++fits3;
                        int matched = 3;
                        for (int j = 3; j < 6; ++j) {
                            candidate = A * candidate + C;
                            if (output(candidate) != x[j]) break;
                            ++matched;
                        }
                        if (matched == 6) {
                            ++fits6;
                            std::printf("SIX_WORD_HIT view=%d low=%u r=%d,%d,%d\n",
                                        view, low, r0, r1, r2);
                        }
                    }
                }
    }
    double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - start).count();
    std::printf("DONE view=%d range=%u..%u exact_hypotheses=%llu "
                "source3_fits=%llu source6_fits=%llu seconds=%.3f\n",
                view, begin, begin + count,
                (unsigned long long)count * 64 * 64 * 64,
                (unsigned long long)fits3,
                (unsigned long long)fits6, seconds);
    return 0;
}
