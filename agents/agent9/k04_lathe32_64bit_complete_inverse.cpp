/**
 * H-17 Lathe32RNG (xoroshiro64++) complete 64-bit-state inversion.
 * Every candidate low word of the 64-bit internal state is enumerated exactly
 * once. Given first emitted 32-bit y0, the second state word is recovered
 * algebraically; both subsequent outputs are independent exact holdouts.
 *
 * C++17 standard library only, no repository sources changed.
 * Reference: yellowstonegames/SquidLib Lathe32RNG.java nextInt().
 */
#include <atomic>
#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <vector>
using U = uint32_t;
using Q = uint64_t;
static inline U rol(U x, unsigned k) { return (x << k) | (x >> (32-k)); }
static inline U ror(U x, unsigned k) { return (x >> k) | (x << (32-k)); }
static inline U next(U &a, U &b) {
    const U out = rol(a+b, 10)+a;
    const U t = a^b;
    a = rol(a, 13)^t^(t<<5);
    b = rol(t, 28);
    return out;
}
int main(int argc, char** argv) {
    if(argc != 7) {
        std::fprintf(stderr, "usage: %s Y0 Y1 Y2 Y3 THREADS LIMIT_A(0 for full)\n", argv[0]);
        return 2;
    }
    const U y0=U(std::strtoul(argv[1],nullptr,16)), y1=U(std::strtoul(argv[2],nullptr,16));
    const U y2=U(std::strtoul(argv[3],nullptr,16)), y3=U(std::strtoul(argv[4],nullptr,16));
    const unsigned n=unsigned(std::strtoul(argv[5],nullptr,10));
    const Q supplied=std::strtoull(argv[6],nullptr,10),limit=supplied?supplied:(1ULL<<32);
    if(!n||n>64||limit>(1ULL<<32))return 2;
    std::atomic<Q> count{0}, prefix{0}, m3{0}, m4{0};
    std::vector<std::thread> workers;
    const auto start=std::chrono::steady_clock::now();
    for(unsigned t=0;t<n;t++)workers.emplace_back([&,t] {
        Q tested=0,first_two=0,third=0,fourth=0;
        for(Q x=t;x<limit;x+=n) {
            const U a=U(x), b=ror(y0-a,10)-a;
            const U xor_pair=a^b;
            U aa=rol(a,13)^xor_pair^(xor_pair<<5),bb=rol(xor_pair,28);
            if(rol(aa+bb,10)+aa==y1) {
                first_two++;
                next(aa,bb);
                if(next(aa,bb)==y2) {
                    third++;
                    if(next(aa,bb)==y3) {
                        fourth++;
                        std::printf("FULL_PACKET_MATCH_STATE a=%08X b=%08X\n",a,b);
                    }
                }
            }
            tested++;
        }
        count.fetch_add(tested);prefix.fetch_add(first_two);
        m3.fetch_add(third);m4.fetch_add(fourth);
    });
    for(auto& worker:workers)worker.join();
    const double elapsed=std::chrono::duration<double>(
        std::chrono::steady_clock::now()-start).count();
    std::printf("COMPLETE tested=%" PRIu64 " prefix2_states=%" PRIu64
        " heldout_word2=%" PRIu64 " heldout_word3=%" PRIu64 " seconds=%.3f\n",
        count.load(),prefix.load(),m3.load(),m4.load(),elapsed);
    return count==limit?0:3;
}
