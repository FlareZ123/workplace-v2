/* Complete 2^18 bottom-bit inversion of Vigna xorshift128+ (23,18,5).
 * Two known adjacent 64-bit modulo-sum outputs x0,x1 determine each
 * state after enumerating only the bottom 18 bits of R1.
 *
 * Let L1=x0-R1 and R2=x1-R1. The state transition implies:
 * R2[i] = L1[i] XOR L1[i-23] XOR L1[i+18] XOR L1[i-5]
 *         XOR R1[i] XOR R1[i+5].
 * Thus guessing R1[0..17] uniquely determines R1[18..63] in order.
 * This is an exact exhaustive inverse, not an SMT approximation.
 *
 * Variant reference: Sebastiano Vigna, "Further scramblings of Marsaglia's
 * xorshift generators", xorshift128+ constants (23,18,5), 2016.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

static uint64_t next_r2(uint64_t a,uint64_t b){
    uint64_t t=a;
    t^=t<<23;
    t^=t>>18;
    t^=b;
    t^=b>>5;
    return t;
}
static void step(uint64_t *l,uint64_t *r) {
    uint64_t newr=next_r2(*l,*r);
    *l=*r; *r=newr;
}
static inline int bit(uint64_t x,int index){
    return index>=0 && index<64 ? (int)((x>>index)&1u) : 0;
}
static uint64_t recover(uint64_t x0,uint64_t x1,uint64_t r) {
    for(int i=0;i<=45;i++){
        const int j=i+18;
        uint64_t l=x0-r,r2=x1-r;
        int required=bit(r2,i)^bit(l,i)^bit(l,i-23)^bit(l,i-5)^bit(r,i)^bit(r,i+5);
        if(required != bit(l,j))r|=UINT64_C(1)<<j;
    }
    return r;
}
int main(int argc,char **argv) {
    if(argc!=3 && argc!=4){fprintf(stderr,"expected x0 x1 [synthetic x2] hex64\n");return 2;}
    uint64_t x0=strtoull(argv[1],NULL,16),x1=strtoull(argv[2],NULL,16);
    int plant=argc==4;
    uint64_t x2=plant?strtoull(argv[3],NULL,16):0;
    uint64_t models=0,selected=0;
    for(uint64_t g=0;g<(UINT64_C(1)<<18);g++){
        uint64_t b=recover(x0,x1,g),a=x0-b;
        if(next_r2(a,b)!=x1-b)continue;
        uint64_t p[6],l=a,r=b;
        p[0]=l+r;
        for(int j=1;j<6;j++){step(&l,&r);p[j]=l+r;}
        if(p[0]!=x0 ||p[1]!=x1){fprintf(stderr,"internal replay mismatch\n");return 3;}
        models++;
        if(plant && p[2]==x2)selected++;
        printf("SOLUTION state_after_x0=%016" PRIX64 ":%016" PRIX64
               " x2=%016" PRIX64 " x3=%016" PRIX64
               " x4=%016" PRIX64 " x5=%016" PRIX64
               " synthetic_x2_match=%d\n",a,b,p[2],p[3],p[4],p[5],plant && p[2]==x2);
    }
    printf("SUMMARY first_pair_states=%" PRIu64 " planted_x2_states=%" PRIu64 "\n",models,selected);
    return 0;
}
