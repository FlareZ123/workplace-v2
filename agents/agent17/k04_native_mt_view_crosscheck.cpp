#include <cstdint>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// Independent C++ source-view reproduction for original H-17 spool.
// Source SHA-256 is checked by the companion Python SFT.
// Run: k04_native_mt_view_crosscheck resources/evidence/print/spool-reconstruction.log

uint32_t untemper(uint32_t y) {
    y ^= y >> 18;
    y ^= (y << 15) & 0xefc60000u;
    const uint32_t stage15 = y;
    for (int i = 0; i < 6; ++i) y = stage15 ^ ((y << 7) & 0x9d2c5680u);
    const uint32_t stage7 = y;
    for (int i = 0; i < 4; ++i) y = stage7 ^ (y >> 11);
    return y;
}

uint32_t mix(uint32_t a, uint32_t b) {
    return (((a & 0x80000000u) | (b & 0x7fffffffu)) >> 1)
        ^ ((b & 1u) ? 0x9908b0dfu : 0u);
}

uint64_t count_witnesses(const std::vector<std::vector<uint32_t>>& rows) {
    const int n = static_cast<int>(rows.size());
    std::unordered_map<uint32_t, std::vector<std::pair<int, int>>> pairs;
    for (int k = 0; k < n - 1; ++k)
        for (int l = k + 1; l < n; ++l)
            for (int i = 0; i < 4; ++i)
                for (int j = 0; j < 4; ++j)
                    pairs[rows[k][i] ^ rows[l][j]].emplace_back(k, l);

    uint64_t found = 0;
    for (int r = 0; r < n - 2; ++r)
        for (int j = 1; j < 4; ++j) {
            const uint32_t needed = mix(rows[r][j - 1], rows[r][j]);
            const auto it = pairs.find(needed);
            if (it == pairs.end()) continue;
            for (const auto& match : it->second)
                if (match.first > r) ++found;
        }
    return found;
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream source(argv[1]);
    std::string line;
    const std::regex pattern("PAYLOAD=([A-F0-9]{32})");
    std::smatch match;
    std::vector<std::string> packets;
    bool selected_valid = false;

    while (std::getline(source, line))
        if (std::regex_search(line, match, pattern)) {
            if (packets.size() == 129)
                selected_valid = line.find(
                    "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"
                ) != std::string::npos;
            packets.push_back(match[1].str());
        }
    if (packets.size() != 133 || !selected_valid) return 3;

    for (int endian = 0; endian < 2; ++endian)
        for (int native = 0; native < 2; ++native) {
            std::vector<std::vector<uint32_t>> rows;
            for (int r = 0; r < 133; ++r) {
                if (r == 129) continue; // Withhold selected target before decoding.
                std::vector<uint32_t> words;
                for (int j = 0; j < 16; j += 4) {
                    uint32_t word = 0;
                    for (int k = 0; k < 4; ++k) {
                        const int byte_index = j + (endian ? k : 3 - k);
                        word = (word << 8) | std::stoul(
                            packets[r].substr(2 * byte_index, 2), nullptr, 16
                        );
                    }
                    words.push_back(native ? untemper(word) : word);
                }
                rows.push_back(std::move(words));
            }
            const uint64_t witnesses = count_witnesses(rows);
            std::cout << (endian ? "BE" : "LE") << " "
                      << (native ? "untempered" : "raw") << " "
                      << witnesses << "\n";
            const uint64_t expected = (!endian && native) ? 25 : 0;
            if (witnesses != expected) return 4;
        }
    return 0;
}
