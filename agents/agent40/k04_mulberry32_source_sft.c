/* Source-only Mulberry32 full-state falsifier for intact H-17 printer row 0300.
   Compile from repository root with GCC/Clang and OpenMP:
     cc -O3 -fopenmp -o k04_mulberry32 agents/agent40/k04_mulberry32_source_sft.c
   Run from repository root, optionally with [begin end) uint32 state bounds.
   The disputed 0417/18:02 coupon and original K04 commitment are never loaded.
*/
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t next32(uint32_t *state) {
    uint32_t t = *state += UINT32_C(0x6D2B79F5);
    t = (t ^ (t >> 15)) * (t | 1u);
    t ^= t + ((t ^ (t >> 7)) * (t | 61u));
    return t ^ (t >> 14);
}
static uint32_t rev32(uint32_t x) {
    return ((x & UINT32_C(0xFF000000)) >> 24) |
           ((x & UINT32_C(0x00FF0000)) >> 8) |
           ((x & UINT32_C(0x0000FF00)) << 8) |
           ((x & UINT32_C(0x000000FF)) << 24);
}
static int matches_four(uint32_t state, const uint32_t *want, int mode) {
    for (int i = 0; i < 4; i++) {
        uint32_t x = next32(&state);
        if (mode & 1) x = rev32(x);
        if (x != want[(mode & 2) ? 3-i : i]) return 0;
    }
    return 1;
}
int main(int argc, char **argv) {
    uint64_t begin = argc > 1 ? strtoull(argv[1], NULL, 0) : 0;
    uint64_t end = argc > 2 ? strtoull(argv[2], NULL, 0) : (UINT64_C(1) << 32);
    assert(begin < end && end <= (UINT64_C(1) << 32));
    FILE *f = fopen("resources/evidence/print/spool-reconstruction.log", "rb");
    assert(f);
    char line[300];
    assert(fgets(line, sizeof(line), f));
    assert(fgets(line, sizeof(line), f));
    fclose(f);
    assert(strstr(line, "JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL "));
    assert(strstr(line, "PAYLOAD=FBBBC54356483F5864BB3F06794518A5"));
    const uint32_t want[4] = {
        UINT32_C(0xFBBBC543), UINT32_C(0x56483F58),
        UINT32_C(0x64BB3F06), UINT32_C(0x794518A5)
    };
    uint32_t st = 417;
    uint32_t planted[4];
    for (int i = 0; i < 4; i++) planted[i] = next32(&st);
    assert(planted[0] == UINT32_C(0xB5C03C5B));
    assert(planted[1] == UINT32_C(0x443263E6));
    assert(planted[2] == UINT32_C(0xE38EC428));
    assert(planted[3] == UINT32_C(0x5BABB68B));
    assert(matches_four(417, planted, 0));
    uint64_t source_first[4] = {0}, source_full[4] = {0}, planted_full = 0;
    for (int mode = 0; mode < 4; mode++) {
        uint32_t first = want[(mode & 2) ? 3 : 0];
        if (mode & 1) first = rev32(first);
        uint64_t nfirst = 0, nfull = 0, nplant = 0;
        #pragma omp parallel for reduction(+:nfirst,nfull,nplant) schedule(static)
        for (uint64_t seed = begin; seed < end; seed++) {
            uint32_t s = (uint32_t)seed;
            uint32_t x = next32(&s);
            if (x == first) {
                nfirst++;
                if (matches_four((uint32_t)seed, want, mode)) nfull++;
            }
            if (mode == 0 && x == planted[0] &&
                matches_four((uint32_t)seed, planted, 0)) nplant++;
        }
        source_first[mode] = nfirst;
        source_full[mode] = nfull;
        planted_full += nplant;
    }
    printf("RANGE [%" PRIu64 ",%" PRIu64 ") source-first [%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "] source-full [%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "] planted-full=%" PRIu64 "\n",
           begin, end, source_first[0], source_first[1], source_first[2], source_first[3],
           source_full[0], source_full[1], source_full[2], source_full[3], planted_full);
    if (begin <= 417 && 417 < end) assert(planted_full == 1);
    else assert(planted_full == 0);
    return (source_full[0]+source_full[1]+source_full[2]+source_full[3]) ? 1 : 0;
}
