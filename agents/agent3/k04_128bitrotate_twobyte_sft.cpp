// H17 K04: circular 128-bit copy desynchronization + any two bad byte positions.
// Read-only source-pinned original acceptance check. Speculative physical-copy model.
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <stdexcept>
#include <chrono>
#include <openssl/sha.h>
#ifdef _OPENMP
#include <omp.h>
#endif

using B16 = std::array<unsigned char, 16>;
using B32 = std::array<unsigned char, 32>;

std::string hex(const unsigned char* x, size_t n) {
    const char *tab = "0123456789ABCDEF";
    std::string s;
    s.reserve(n * 2);
    for (size_t i = 0; i < n; ++i) { s += tab[x[i] >> 4]; s += tab[x[i] & 15]; }
    return s;
}

B16 parse16(const std::string& s) {
    if (s.size() != 32) throw std::runtime_error("incorrect hex size");
    B16 x{};
    for (int i = 0; i < 16; ++i)
        x[i] = static_cast<unsigned char>(std::stoul(s.substr(2*i, 2), nullptr, 16));
    return x;
}

B32 parse32(const std::string& s) {
    if (s.size() != 64) throw std::runtime_error("incorrect digest size");
    B32 x{};
    for (int i = 0; i < 32; ++i)
        x[i] = static_cast<unsigned char>(std::stoul(s.substr(2*i, 2), nullptr, 16));
    return x;
}

std::string read(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("failed to open " + path);
    return std::string(std::istreambuf_iterator<char>(f), {});
}

void require_sha(const std::string& path, const char* expected) {
    auto s = read(path);
    B32 got{};
    SHA256(reinterpret_cast<const unsigned char*>(s.data()), s.size(), got.data());
    if (hex(got.data(), got.size()) != expected) throw std::runtime_error("source SHA mismatch " + path);
}

B16 rotate128(const B16& in, int bits) {
    B16 out{};
    for (int dst = 0; dst < 128; ++dst) {
        const int src = (dst + bits) & 127; // MSB-first circular left shift
        out[dst / 8] |= static_cast<unsigned char>(
            ((in[src / 8] >> (7 - (src & 7))) & 1) << (7 - (dst & 7))
        );
    }
    return out;
}

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "usage: <extracted-archive-dir>\n"; return 2; }
    std::string root = argv[1], spool = root + "/evidence/print/spool-reconstruction.log",
                route = root + "/evidence/recovery-routing.json",
                acceptance = root + "/acceptance.json";
    require_sha(spool, "7D71D8BEF7F01596E705AC14E24C5C4352042512B3088125AFCA40F3841B6083");
    require_sha(route, "F8FCBCA73D23BF1066EDB88C088F89CD24CF22E7C78A4A412166254A4764D8A5");
    require_sha(acceptance, "681739241B757B471ACCA4C0FEF9D9D97E9493883887736D5DB3B92BFB0C137F");
    auto spooldata = read(spool);
    const std::string locator = "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
    size_t off = spooldata.find(locator);
    if (off == std::string::npos || spooldata.find(locator, off+1) != std::string::npos)
        throw std::runtime_error("selected printer record absent or ambiguous");
    B16 copy = parse16(spooldata.substr(off + locator.size(), 32));
    B16 mask = parse16("8556C8CB6140A7F9A5123AC7571BEE1C");
    B32 real = parse32("930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0");

    const int planted_rotation = 37, planted_pos1 = 5, planted_pos2 = 12;
    B16 planted = rotate128(copy, planted_rotation);
    planted[planted_pos1] = 0x3C;
    planted[planted_pos2] = 0xD9;
    for (int i = 0; i < 16; ++i) planted[i] ^= mask[i];
    B32 synthetic{};
    SHA256(planted.data(), planted.size(), synthetic.data());

    unsigned long long tests = 0, planted_found = 0, original_found = 0;
    auto start = std::chrono::steady_clock::now();
    #pragma omp parallel for reduction(+:tests,planted_found,original_found) schedule(dynamic,1)
    for (int rot = 0; rot < 128; ++rot) {
        B16 rotated = rotate128(copy, rot);
        for (int i = 0; i < 16; ++i) rotated[i] ^= mask[i];
        for (int p = 0; p < 15; ++p) for (int q = p + 1; q < 16; ++q) {
            B16 candidate = rotated;
            for (int a = 0; a < 256; ++a) {
                candidate[p] = static_cast<unsigned char>(a ^ mask[p]);
                for (int b = 0; b < 256; ++b) {
                    candidate[q] = static_cast<unsigned char>(b ^ mask[q]);
                    B32 digest{};
                    SHA256(candidate.data(), 16, digest.data());
                    ++tests;
                    if (digest == synthetic) ++planted_found;
                    if (digest == real) {
                        ++original_found;
                        #pragma omp critical
                        std::cout << "ORIGINAL_K04_PASS rotation=" << rot
                            << " positions=" << p << "," << q
                            << " coupon=" << hex(candidate.data(), 16) << "\n";
                    }
                }
            }
        }
    }
    double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    std::cout << "SUMMARY rotations=128 position_pairs=120 each_values=65536 "
              << "complete_assignments=" << tests
              << " original_hits=" << original_found
              << " planted_hits=" << planted_found
              << " seconds=" << seconds << "\n";
    if (tests != 128ull*120*65536 || planted_found == 0) return 1;
    return 0;
}
