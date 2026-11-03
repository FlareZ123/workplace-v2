// K04 source-only .NET Framework Random.Next(256) first-packet seed inverter.
// C++17 standard library; compile and run from repository root.
// Tests ALL 2^31 seed magnitudes under eight reversible byte geometries.
// Reconstructed source packet: job PS-261003-0300, 07:00 UTC.
// Original spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <algorithm>
using U = std::uint64_t;
constexpr U M = 2147483647ULL;
constexpr U INV = 1796695496ULL;
constexpr U base[16] = {
    1559595546,1755192844,1649316166,1198642031,
    442452829,1200195957,1945678308,949569752,
    2099272109,587775847,626863973,1003550677,
    1358625013,1008269081,2109153755,65212616
};
constexpr U slope[16] = {
    1121899819,630111683,1501065279,458365203,
    969558243,1876681249,962194431,1077359051,
    265679591,791886952,1582116761,1676571504,
    1476289907,1117239683,1503178135,1341148412
};
using Packet = std::array<std::uint8_t,16>;
constexpr Packet original = {
    0xFB,0xBB,0xC5,0x43,0x56,0x48,0x3F,0x58,
    0x64,0xBB,0x3F,0x06,0x79,0x45,0x18,0xA5
};
constexpr Packet planted = {
    0xD3,0xA6,0x70,0xC2,0x48,0x08,0xCE,0xCD,
    0xC9,0x3E,0x66,0x41,0x57,0x10,0x0C,0x3C
};

Packet unpack(const Packet& wire, int geometry) {
    Packet raw{};
    for(int output=0;output<16;++output) {
        int row=output/4, col=output%4;
        if(geometry & 4) std::swap(row,col);
        if(geometry & 2) row=3-row;
        if(geometry & 1) col=3-col;
        raw[row*4+col]=wire[output];
    }
    return raw;
}

struct Result {
    U prefix[5]{};
    U complete=0;
    bool planted_seed_found=false;
};

Result invert(const Packet& bytes, U expected_seed=0, bool positive_control=false) {
    Result result{};
    // floor(raw * 256 / M) gives Random.Next(256). The interval formula
    // enumerates each raw integer consistent with the observed first byte.
    const U first=(U(bytes[0])*M+255)/256;
    const U last=(U(bytes[0]+1)*M+255)/256;
    for(U raw=first;raw<last;++raw) {
        const U seed=(((raw+M-base[0])%M)*INV)%M;
        ++result.prefix[0];
        int i=1;
        for(;i<16;++i) {
            const U value=(slope[i]*seed+base[i])%M;
            if(value*256/M!=bytes[i]) break;
            if(i<5) ++result.prefix[i];
        }
        if(i==16) {
            ++result.complete;
            if(positive_control && seed==expected_seed) {
                result.planted_seed_found=true;
            }
        }
    }
    return result;
}

int main() {
    std::ifstream spool("resources/evidence/print/spool-reconstruction.log");
    if(!spool) { std::cerr<<"SPOOL_MISSING\n"; return 2; }
    std::string line;
    bool original_present=false;
    while(std::getline(spool,line)) {
        if(line.find("JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK")!=std::string::npos &&
           line.find("PAYLOAD=FBBBC54356483F5864BB3F06794518A5")!=std::string::npos) {
            original_present=true;
        }
    }
    if(!original_present) { std::cerr<<"ORIGINAL_PACKET_CHANGED\n"; return 3; }

    // Independent seeded reference output from classic Random(20261103)
    // through sixteen calls to Random.Next(256).
    Result control=invert(planted,20261103,true);
    if(!control.planted_seed_found || control.complete==0) {
        std::cerr<<"PLANTED_SEED_INVERSION_FAILED\n"; return 4;
    }
    std::cout<<"PLANTED_20261103 PASS\n";
    for(int mode=0;mode<8;++mode) {
        Result r=invert(unpack(original,mode));
        std::cout<<"MODE "<<mode<<" prefixes "
                 <<r.prefix[0]<<" "<<r.prefix[1]<<" "<<r.prefix[2]<<" "
                 <<r.prefix[3]<<" "<<r.prefix[4]
                 <<" complete "<<r.complete<<"\n";
        if(r.prefix[0] != (1ULL<<23) || r.complete != 0) return 5;
    }
    std::cout<<"ORIGINAL_ALL_SEEDED_NEXT256_GEOMETRIES_NO_MATCH\n";
}
