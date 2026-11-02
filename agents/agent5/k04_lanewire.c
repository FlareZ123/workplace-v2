#include <openssl/sha.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

/* Read-only hypothesis: 4 independently byte-permuted 32-bit words,
 * followed by any of 24 four-word orders. Only the selected 18:02 ACK2
 * 16-byte copied row is used; no byte substitutions or arbitrary edits. */
static const unsigned char ack[16] = {
0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const unsigned char mask[16] = {
0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const unsigned char target[32] = {
0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};

static unsigned char perm[24][4];
static int count=0;
static void permute(unsigned char used, unsigned char v[4], int k) {
    if(k==4){memcpy(perm[count++],v,4);return;}
    for(int i=0;i<4;i++)if(!(used&(1<<i))){v[k]=i;permute(used|(1<<i),v,k+1);}
}
static void calculate(const int p[4],const int order[4],unsigned char out[16]) {
    for(int w=0;w<4;w++)for(int b=0;b<4;b++)out[4*w+b]=ack[4*order[w]+perm[p[order[w]]][b]]^mask[4*w+b];
}
int main(void) {
    unsigned char v[4], component[16],digest[32],synthetic[32];
    permute(0,v,0);
    if(count!=24){fprintf(stderr,"permutation count error\n");return 2;}
    const int order_control[4]={2,0,3,1};
    const int pcontrol[4]={17,3,13,23};
    calculate(pcontrol,order_control,component);
    SHA256(component,16,synthetic);
    unsigned long long examined=0, hits=0, controls=0;
    /* Four independent byte maps (24^4), then 24 permutations of words. */
    for(int a=0;a<24;a++)for(int b=0;b<24;b++)for(int c=0;c<24;c++)for(int d=0;d<24;d++) {
        const int positions[4]={a,b,c,d};
        for(int i=0;i<24;i++) {
            int order[4];for(int j=0;j<4;j++)order[j]=perm[i][j];
            calculate(positions,order,component);
            SHA256(component,16,digest);
            examined++;
            if(!memcmp(digest,synthetic,32))controls++;
            if(!memcmp(digest,target,32)) {
                hits++;
                printf("K04 FOUND candidate ");for(int j=0;j<16;j++)printf("%02X",component[j]);printf("\n");
            }
        }
    }
    printf("assignments=%llu synthetic_control_hits=%llu original_matches=%llu\n",examined,controls,hits);
    if(examined!=7962624ULL||!controls){fputs("selftest failure\n",stderr);return 2;}
    return hits?0:1;
}
