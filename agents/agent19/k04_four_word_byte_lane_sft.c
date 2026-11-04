/*
 * H-17 REC8/1 K04, selected ACK2 copy: independently arbitrary same byte-lane repairs.
 * Each 32-bit word may have exactly one arbitrary replacement byte at the same offset.
 * No selected physical coupon bytes are inferred from the copier. A hit requires the
 * untouched SHA256 commitment, then separate historical authenticity assessment.
 *
 * Build on a repository checkout:
 *   cc -O3 -std=c11 agents/agent19/k04_four_word_byte_lane_sft.c -lcrypto -o k04lane
 *
 * Usage:
 *   k04lane 0 0 16      scan lane 0, shard 0 of 16
 *   k04lane self-test   confirm complete planted 4-byte target is rediscovered
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

static const unsigned char MASK[16] = {
    0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,
    0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C
};
static const unsigned char COPIED[16] = {
    0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,
    0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5
};
static const unsigned char EXPECTED[SHA256_DIGEST_LENGTH] = {
    0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,
    0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,
    0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
static const char * const SOURCES[][2] = {
    {"resources/evidence/print/spool-reconstruction.log",
     "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
    {"resources/evidence/recovery-routing.json",
     "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
    {"resources/acceptance.json",
     "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static void hexprint(const unsigned char *v, size_t n) {
    for (size_t i=0; i<n; i++) printf("%02X",v[i]);
}
static int sources_pinned(void) {
    unsigned char buf[65536], digest[SHA256_DIGEST_LENGTH];
    for (size_t i=0; i<sizeof(SOURCES)/sizeof(SOURCES[0]); i++) {
        FILE *fp=fopen(SOURCES[i][0],"rb");
        if (!fp) {perror(SOURCES[i][0]);return 0;}
        SHA256_CTX ctx;
        SHA256_Init(&ctx);
        size_t n;
        while ((n=fread(buf,1,sizeof(buf),fp))>0) SHA256_Update(&ctx,buf,n);
        int error=ferror(fp);
        fclose(fp);
        if (error) {fputs("Read error\n",stderr);return 0;}
        SHA256_Final(digest,&ctx);
        char actual[SHA256_DIGEST_LENGTH*2+1];
        for (int j=0;j<SHA256_DIGEST_LENGTH;j++)
            snprintf(actual+j*2,3,"%02x",digest[j]);
        if (strcmp(actual,SOURCES[i][1])) {
            fprintf(stderr,"Original source drift at %s: %s\n",SOURCES[i][0],actual);
            return 0;
        }
    }
    return 1;
}
static int search(int lane, uint64_t first, uint64_t count,
                  const unsigned char target[SHA256_DIGEST_LENGTH],
                  int progress) {
    unsigned char candidate[16],digest[SHA256_DIGEST_LENGTH];
    for (int i=0;i<16;i++) candidate[i]=COPIED[i]^MASK[i];
    const int a=lane, b=lane+4, c=lane+8, d=lane+12;
    int found=0;
    for (uint64_t value=first; value<first+count; value++) {
        candidate[a]=(unsigned char)(value>>24);
        candidate[b]=(unsigned char)(value>>16);
        candidate[c]=(unsigned char)(value>>8);
        candidate[d]=(unsigned char)value;
        SHA256(candidate,16,digest);
        if (!memcmp(digest,target,SHA256_DIGEST_LENGTH)) {
            printf("MATCH lane=%d bytes=%08" PRIX64 " component=",lane,value);
            hexprint(candidate,16);
            printf(" physical_coupon=");
            for (int i=0;i<16;i++) printf("%02X",candidate[i]^MASK[i]);
            puts("");
            found++;
        }
        if (progress && ((value-first+1)&0xFFFFFF)==0) {
            printf("CHECKED lane=%d count=%" PRIu64 "\n",lane,value-first+1);
            fflush(stdout);
        }
    }
    return found;
}
static int selftest(void) {
    unsigned char expected[16], digest[SHA256_DIGEST_LENGTH];
    for (int i=0;i<16;i++) expected[i]=COPIED[i]^MASK[i];
    const int lane=2;
    const uint32_t planted=0xDEADBEEFu;
    expected[lane]=(unsigned char)(planted>>24);
    expected[lane+4]=(unsigned char)(planted>>16);
    expected[lane+8]=(unsigned char)(planted>>8);
    expected[lane+12]=(unsigned char)planted;
    SHA256(expected,16,digest);
    int found=search(lane,0xDEAD0000ULL,65536,digest,0);
    printf("Synthetic 4-independent-byte lane positive: %s\n",found==1?"PASS":"FAIL");
    return found==1;
}
int main(int argc,char **argv) {
    if (!sources_pinned()) return 2;
    if (argc==2 && !strcmp(argv[1],"self-test")) return selftest()?0:3;
    if (argc!=4) {
        fprintf(stderr,"Usage: %s LANE(0..3) SHARD(0..N-1) N(1..256)\n",argv[0]);
        return 2;
    }
    char *end;
    long lane=strtol(argv[1],&end,10);
    if (*end||lane<0||lane>3) return 2;
    long shard=strtol(argv[2],&end,10);
    if (*end||shard<0) return 2;
    long shards=strtol(argv[3],&end,10);
    if (*end||shards<1||shards>256||shard>=shards||
        (shards&(shards-1))!=0) return 2;
    uint64_t count=(UINT64_C(1)<<32)/(uint64_t)shards;
    uint64_t first=count*(uint64_t)shard;
    printf("ORIGINAL lane=%ld shard=%ld/%ld range=%" PRIu64 "..%" PRIu64
           " candidates=%" PRIu64 "\n",
           lane,shard,shards,first,first+count-1,count);
    fflush(stdout);
    int found=search((int)lane,first,count,EXPECTED,1);
    printf("DONE lane=%ld shard=%ld complete=%" PRIu64
           " original matches=%d\n",lane,shard,count,found);
    return found?10:0;
}
