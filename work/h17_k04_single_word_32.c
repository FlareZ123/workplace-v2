#define OPENSSL_SUPPRESS_DEPRECATED
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const unsigned char BASE[16] = {
  0x2c,0xff,0x14,0x9c, 0x50,0xe5,0x45,0x57,
  0x22,0x8e,0x7d,0xe6, 0x0b,0x3e,0xb7,0xc9
};
static const unsigned char TARGET[32] = {
  0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,
  0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,
  0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,
  0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0
};

static double seconds_between(struct timespec a, struct timespec b) {
  return (double)(b.tv_sec-a.tv_sec) + (double)(b.tv_nsec-a.tv_nsec)/1e9;
}
static void print_hex(const unsigned char *p, size_t n) {
  for (size_t i=0; i<n; ++i) printf("%02X", p[i]);
}
static int selftest(void) {
  unsigned char known[16] = {0,1,2,3,4,5,6,7,0,0,0,0,12,13,14,15};
  unsigned char expected[16], probe[16], target[32], digest[32];
  memcpy(expected, known, 16);
  expected[8]=0x00; expected[9]=0x00; expected[10]=0xBE; expected[11]=0xEF;
  SHA256(expected, 16, target);
  memcpy(probe, known, 16);
  for (uint32_t x=0; x<=0x00BEEFU; ++x) {
    probe[8]=(unsigned char)(x>>24);
    probe[9]=(unsigned char)(x>>16);
    probe[10]=(unsigned char)(x>>8);
    probe[11]=(unsigned char)x;
    SHA256(probe, 16, digest);
    if (memcmp(digest, target, 32)==0 && x==0xBEEF) {
      puts("SELFTEST PASS: recovered a planted 32-bit word");
      return 0;
    }
  }
  puts("SELFTEST FAIL");
  return 1;
}
int main(int argc, char **argv) {
  if (argc>1 && strcmp(argv[1], "--selftest")==0) return selftest();
  if (argc<2 || argc>3) {
    fprintf(stderr, "usage: %s OFFSET_BYTES [LIMIT]\n", argv[0]);
    return 2;
  }
  int offset=atoi(argv[1]);
  if (!(offset==0 || offset==4 || offset==8 || offset==12)) {
    fprintf(stderr, "offset must be one of 0,4,8,12\n");
    return 2;
  }
  uint64_t limit=argc==3?strtoull(argv[2],NULL,0):0x100000000ULL;
  if (limit>0x100000000ULL) return 2;
  unsigned char block[16], digest[32];
  memcpy(block, BASE, 16);
  struct timespec start, now;
  clock_gettime(CLOCK_MONOTONIC, &start);
  printf("START offset=%d limit=%llu base=", offset, (unsigned long long)limit);
  print_hex(BASE,16); printf(" target="); print_hex(TARGET,32); puts("");
  fflush(stdout);
  for (uint64_t x=0; x<limit; ++x) {
    block[offset+0]=(unsigned char)(x>>24);
    block[offset+1]=(unsigned char)(x>>16);
    block[offset+2]=(unsigned char)(x>>8);
    block[offset+3]=(unsigned char)x;
    SHA256(block,16,digest);
    if (memcmp(digest,TARGET,32)==0) {
      printf("HIT offset=%d word=%08llX block=",offset,(unsigned long long)x);
      print_hex(block,16); printf(" sha256="); print_hex(digest,32); puts("");
      fflush(stdout);
      return 0;
    }
    if ((x & 0x0fffffffULL)==0x0fffffffULL) {
      clock_gettime(CLOCK_MONOTONIC,&now);
      printf("PROGRESS offset=%d tested=%llu elapsed=%.1fs rate=%.2f Mhash/s\n",
        offset,(unsigned long long)(x+1),seconds_between(start,now),
        (double)(x+1)/seconds_between(start,now)/1e6);
      fflush(stdout);
    }
  }
  clock_gettime(CLOCK_MONOTONIC,&now);
  printf("NO_HIT offset=%d tested=%llu elapsed=%.1fs rate=%.2f Mhash/s\n",
    offset,(unsigned long long)limit,seconds_between(start,now),
    (double)limit/seconds_between(start,now)/1e6);
  return 0;
}
