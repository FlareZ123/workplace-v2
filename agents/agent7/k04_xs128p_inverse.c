/* H17 K04 exact xorshift128+ two-output inversion.
   Algebraic bit-lift follows Scott Contini's MIT-licensed published method:
   https://github.com/ScottContini/a_better_xorshift128-inverter
   This implementation is independently written. The output model is
   x_i = L_i + R_i after each V8-style xorshift128+ state transition.
   Args: x0 x1 [x2] in hex64; x2 is a synthetic-control discriminator.
   Prints all exact states plus four complete forward output predictions. */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

static inline void step(uint64_t *l, uint64_t *r) {
    const uint64_t a = *l, b = *r;
    uint64_t t = a;
    t ^= t << 23;
    t ^= t >> 17;
    t ^= b;
    t ^= b >> 26;
    *l = b;
    *r = t;
}

static inline uint64_t next_r2(uint64_t a, uint64_t b) {
    uint64_t t = a;
    t ^= t << 23;
    t ^= t >> 17;
    return t ^ b ^ (b >> 26);
}

static inline uint64_t recover_r1(uint64_t x0, uint64_t x1, uint64_t guess) {
    uint64_t r = guess, l = (x0-r)&UINT64_C(0x3ffffff),
             r2=(x1-r)&UINT64_C(0x3ffffff), q;
    /* Induce known bits 26..31 from lower 26. */
    q = r2 ^ l ^ (l >> 17) ^ r;
    r |= (q & UINT64_C(0x3f)) << 26;
    l=(x0-r)&UINT64_C(0xffffffff); r2=(x1-r)&UINT64_C(0xffffffff);
    /* Induce bits 32..40 from lower 32. */
    q=r2 ^ (l<<6) ^ l ^ (l>>17) ^ r;
    r|=(q & (UINT64_C(0x1ff)<<6)) << 26;
    l=(x0-r)&((UINT64_C(1)<<41)-1);r2=(x1-r)&((UINT64_C(1)<<41)-1);
    /* Induce bits 41..48. */
    q=r2 ^ (l<<6) ^ l ^ (l>>17) ^ r;
    r|=(q & (UINT64_C(0xff)<<15)) << 26;
    l=(x0-r)&((UINT64_C(1)<<49)-1);r2=(x1-r)&((UINT64_C(1)<<49)-1);
    /* Induce bits 49..56, where the 23-bit shift contributes. */
    q=r2 ^ (l<<23) ^ (l<<6) ^ l ^ (l>>17) ^ r;
    r|=(q & (UINT64_C(0xff)<<23)) << 26;
    l=(x0-r)&((UINT64_C(1)<<57)-1);r2=(x1-r)&((UINT64_C(1)<<57)-1);
    /* Induce bits 57..63. */
    q=r2 ^ (l<<23) ^ (l<<6) ^ l ^ (l>>17) ^ r;
    r|=(q & (UINT64_C(0x7f)<<31)) << 26;
    return r;
}

int main(int argc,char **argv) {
    if(argc<3 || argc>4) {
        fprintf(stderr,"expected: x0 x1 [x2], all hex 64-bit\n");
        return 2;
    }
    const uint64_t x0=strtoull(argv[1],NULL,16);
    const uint64_t x1=strtoull(argv[2],NULL,16);
    const int has_x2=(argc==4);
    const uint64_t x2=has_x2?strtoull(argv[3],NULL,16):0;
    uint64_t matches=0, matches_x2=0;
    for(uint64_t g=0;g<(UINT64_C(1)<<26);g++) {
        uint64_t r=recover_r1(x0,x1,g);
        uint64_t l=x0-r, r2=x1-r;
        if(next_r2(l,r)!=r2)continue;
        matches++;
        uint64_t p[6], ll=l,rr=r;
        p[0]=x0;
        for(int i=1;i<6;i++) {
            step(&ll,&rr);
            p[i]=ll+rr;
        }
        if(p[1]!=x1){fprintf(stderr,"internal state mismatch\n");return 3;}
        if(has_x2 && p[2]==x2)matches_x2++;
        printf("SOLUTION state_after_x0=%016" PRIX64 ":%016" PRIX64
               " x2=%016" PRIX64 " x3=%016" PRIX64
               " x4=%016" PRIX64 " x5=%016" PRIX64
               " synthetic_x2_match=%d\n",l,r,p[2],p[3],p[4],p[5],
               (int)(has_x2 && p[2]==x2));
    }
    printf("SUMMARY first_pair_states=%" PRIu64 " synthetic_x2_states=%" PRIu64 "\n",matches,matches_x2);
    return 0;
}
