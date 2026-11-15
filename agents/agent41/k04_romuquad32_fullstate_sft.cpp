/* H-17 K04 RomuQuad32 full-state inversion and original commitment test.
 * C++17 + OpenMP + OpenSSL libcrypto; direct source constants from the
 * unchanged spool PS-261003-0417 REQUESTED1 and REQUESTED3.
 * Uses exact algebraic reduction from unknown 96-bit state to one 32-bit
 * state variable, exhaustively visits all 2^32 possibilities per serializer.
 * Selected copied 18:02 ACK2 bytes are never used for state reconstruction.
 *
 * Build with C++17, OpenMP and OpenSSL libcrypto; run from any directory.
 */
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <openssl/sha.h>

static constexpr uint32_t C = 3323815723u;
static inline uint32_t rol(uint32_t v, unsigned n) {return (v << n) | (v >> (32 - n));}
static inline uint32_t ror(uint32_t v, unsigned n) {return (v >> n) | (v << (32 - n));}
struct State {uint32_t w, x, y, z;};

static uint32_t next(State& s) {
    uint32_t w=s.w, x=s.x, y=s.y, z=s.z;
    s.w=C*z; s.x=z+rol(w,26); s.y=y-x; s.z=rol(y+w,9);
    return x;
}
static void from_hex(const char* hex, uint8_t* output, int bytes) {
    for(int i=0;i<bytes;i++) {
        unsigned n; std::sscanf(hex+2*i,"%2x",&n);output[i]=uint8_t(n);
    }
}
static void pack(const uint32_t* words, bool le, bool rev, uint8_t out[16]) {
    for(int i=0;i<4;i++) {
        uint32_t w=words[rev?3-i:i];
        for(int j=0;j<4;j++)out[i*4+j]=uint8_t(w>>(8*(le?j:3-j)));
    }
}
static void unpack(const uint8_t raw[16], bool le, bool rev, uint32_t out[4]) {
    for(int i=0;i<4;i++) {
        uint32_t w=0;
        for(int j=0;j<4;j++) w|=uint32_t(raw[i*4+j])<<(8*(le?j:3-j));
        out[rev?3-i:i]=w;
    }
}
static uint32_t pred4(uint32_t x0,uint32_t x1,uint32_t x2,uint32_t z0) {
    uint32_t w0=ror(x1-z0,26);
    uint32_t z1=x2-rol(C*z0,26);
    uint32_t y0=ror(z1,9)-w0;
    return rol(y0-x0+C*z0,9)+rol(C*z1,26);
}
static State inverse(uint32_t x0,uint32_t x1,uint32_t x2,uint32_t z0) {
    uint32_t w0=ror(x1-z0,26);
    uint32_t z1=x2-rol(C*z0,26);
    uint32_t y0=ror(z1,9)-w0;
    return {w0,x0,y0,z0};
}
static void planted() {
    for(uint32_t q=0;q<1000;q++) {
        State seed{0x12345678u+q,0x9ABCDEF0u-q,0xA55A5AA5u+q,0xF0E1D2C3u-q};
        State st=seed; uint32_t x[4];
        for(int i=0;i<4;i++)x[i]=next(st);
        if(pred4(x[0],x[1],x[2],seed.z)!=x[3])std::abort();
        State restored=inverse(x[0],x[1],x[2],seed.z);
        if(std::memcmp(&seed,&restored,sizeof(seed)))std::abort();
    }
    std::puts("1000 planted full-state inversions: PASS");
}
int main() {
    planted();
    const char* FIRST="CD3E4F216ADB2FB180DA2AA90B33F7A4";
    const char* LATER="44D53DFC29D7943A95D89371DA58EC64";
    const char* MASK="8556C8CB6140A7F9A5123AC7571BEE1C";
    const char* COMMITMENT="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
    uint8_t early[16], late[16], mask[16], wanted[32];
    from_hex(FIRST,early,16);from_hex(LATER,late,16);
    from_hex(MASK,mask,16);from_hex(COMMITMENT,wanted,32);
    uint64_t candidates=0, accepted=0, late_matches=0;
    for(int endian=0;endian<2;endian++)for(int reverse=0;reverse<2;reverse++) {
        uint32_t x[4];unpack(early,endian,reverse,x);
        std::vector<uint32_t> solutions;
        #pragma omp parallel
        {
            std::vector<uint32_t> local;
            #pragma omp for schedule(static)
            for(uint64_t z=0;z<(uint64_t(1)<<32);z++) {
                if(pred4(x[0],x[1],x[2],uint32_t(z))==x[3])
                    local.push_back(uint32_t(z));
            }
            #pragma omp critical
            solutions.insert(solutions.end(),local.begin(),local.end());
        }
        candidates += solutions.size();
        std::printf("%s %s: %zu recovered complete states\n",
                    endian?"little":"big",reverse?"reversed":"normal",solutions.size());
        for(uint32_t z:solutions) {
            State state=inverse(x[0],x[1],x[2],z);
            uint32_t emitted[12];
            for(int i=0;i<12;i++)emitted[i]=next(state);
            for(int i=0;i<4;i++)if(emitted[i]!=x[i])std::abort();
            uint8_t physical[16],later[16],component[16],digest[32];
            pack(emitted+4,endian,reverse,physical);
            pack(emitted+8,endian,reverse,later);
            for(int i=0;i<16;i++)component[i]=physical[i]^mask[i];
            SHA256(component,16,digest);
            bool hit=std::memcmp(digest,wanted,32)==0;
            bool heldout=std::memcmp(later,late,16)==0;
            accepted+=hit;late_matches+=heldout;
            std::printf("  z0=%08X candidate=",z);
            for(uint8_t byte:component)std::printf("%02X",byte);
            std::printf(" K04=%u later_18:03=%u\n",unsigned(hit),unsigned(heldout));
        }
    }
    std::printf("FINAL complete states=%llu, K04 exact hits=%llu, 18:03 whole-object holdouts=%llu\n",
                (unsigned long long)candidates,(unsigned long long)accepted,
                (unsigned long long)late_matches);
    return (candidates==6 && !accepted && !late_matches)?0:2;
}
