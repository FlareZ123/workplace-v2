#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct U128 {
    uint64_t lo = 0, hi = 0;
    U128& operator^=(const U128& x) { lo ^= x.lo; hi ^= x.hi; return *this; }
};

static uint64_t read_le64(const unsigned char* p) {
    uint64_t x = 0;
    for (int i = 7; i >= 0; --i) x = (x << 8) | p[i];
    return x;
}
static U128 read128(ifstream& f) {
    unsigned char b[16];
    f.read((char*)b, 16);
    return {read_le64(b), read_le64(b + 8)};
}
static void write128(ofstream& f, const U128& x) {
    unsigned char b[16];
    for (int i = 0; i < 8; ++i) {
        b[i] = (x.lo >> (8 * i)) & 255;
        b[i + 8] = (x.hi >> (8 * i)) & 255;
    }
    f.write((char*)b, 16);
}
static uint32_t temper(uint32_t x) {
    x ^= x >> 11;
    x ^= (x << 7) & 0x9D2C5680u;
    x ^= (x << 15) & 0xEFC60000u;
    x ^= x >> 18;
    return x;
}
struct Map {
    U128 constant;
    uint8_t syndrome_constant;
    array<U128, 193> columns;
    array<uint8_t, 193> syndrome_columns;
};

int main(int argc, char** argv) {
    string dir = argc > 1 ? argv[1] : ".";
    ifstream map_file(dir + "/maps_193.bin", ios::binary);
    if (!map_file) { cerr << "maps missing\n"; return 2; }
    array<Map, 7> maps;
    for (auto& m : maps) {
        m.constant = read128(map_file);
        map_file.read((char*)&m.syndrome_constant, 1);
        for (int j = 0; j < 193; ++j) {
            m.columns[j] = read128(map_file);
            map_file.read((char*)&m.syndrome_columns[j], 1);
        }
    }

    ifstream view_file(dir + "/views_193.bin", ios::binary);
    if (!view_file) { cerr << "views missing\n"; return 2; }
    vector<uint32_t> views(11 * 8 * 4);
    view_file.read((char*)views.data(), views.size() * 4);
    if (!view_file) { cerr << "views short\n"; return 2; }

    static U128 table[7][6][4][256];
    static uint8_t syndrome_table[7][6][4][256];
    for (int m = 0; m < 7; ++m)
        for (int pos = 0; pos < 6; ++pos)
            for (int byte = 0; byte < 4; ++byte)
                for (int value = 0; value < 256; ++value) {
                    U128 contribution{};
                    uint8_t syndrome = 0;
                    for (int bit = 0; bit < 8; ++bit)
                        if ((value >> bit) & 1) {
                            int column = pos * 32 + byte * 8 + bit;
                            contribution ^= maps[m].columns[column];
                            syndrome ^= maps[m].syndrome_columns[column];
                        }
                    table[m][pos][byte][value] = contribution;
                    syndrome_table[m][pos][byte][value] = syndrome;
                }

    const int partial_bits[7] = {-1, 2, 9, 13, 20, 27, 31};
    ofstream output(dir + "/candidates_193.bin", ios::binary | ios::trunc);
    if (!output) { cerr << "output open failed\n"; return 2; }
    uint64_t assignments = 0, compatible = 0;
    auto started = chrono::steady_clock::now();

    for (int a = 0; a < 11; ++a)
        for (int b = 0; b < 11; ++b) if (b != a)
            for (int c = 0; c < 11; ++c) if (c != a && c != b)
                for (int ea = 0; ea < 8; ++ea)
                    for (int eb = 0; eb < 8; ++eb)
                        for (int ec = 0; ec < 8; ++ec) {
                            const uint32_t* left = &views[(a * 8 + ea) * 4];
                            const uint32_t* middle = &views[(b * 8 + eb) * 4];
                            const uint32_t* right = &views[(c * 8 + ec) * 4];
                            uint32_t full[6] = {
                                left[1], left[2], middle[0], middle[1], right[0], right[1]
                            };
                            for (int m = 0; m < 7; ++m) {
                                int partial = m == 0
                                    ? ((left[0] >> 31) & 1)
                                    : ((temper(left[0]) >> partial_bits[m]) & 1);
                                U128 component = maps[m].constant;
                                uint8_t syndrome = maps[m].syndrome_constant;
                                for (int pos = 0; pos < 6; ++pos) {
                                    uint32_t word = full[pos];
                                    for (int byte = 0; byte < 4; ++byte) {
                                        int value = (word >> (8 * byte)) & 255;
                                        component ^= table[m][pos][byte][value];
                                        syndrome ^= syndrome_table[m][pos][byte][value];
                                    }
                                }
                                if (partial) {
                                    component ^= maps[m].columns[192];
                                    syndrome ^= maps[m].syndrome_columns[192];
                                }
                                ++assignments;
                                if (syndrome == 0) {
                                    ++compatible;
                                    write128(output, component);
                                }
                            }
                        }

    output.close();
    auto elapsed = chrono::duration_cast<chrono::milliseconds>(
        chrono::steady_clock::now() - started
    ).count();
    cout << "assignments=" << assignments
         << " compatible=" << compatible
         << " elapsed_ms=" << elapsed
         << " output_bytes=" << compatible * 16 << "\n";
}
