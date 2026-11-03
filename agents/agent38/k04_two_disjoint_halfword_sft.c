/* H-17 Agent38 K04 dual-disjoint aligned halfword repair.
 * Original sources/commitments are read-only; see preregistration .md.
 * Compile: cc -O3 -std=c11 -fopenmp THIS.c -lcrypto -o tester
 * Usage: tester selftest | tester run <support_id 0..18>
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

static const uint8_t base[16] = {
  0x2C,0xFF,0x14,0x9C,0x50,0xE5,0x45,0x57,
  0x22,0x8E,0x7D,0xE6,0x0B,0x3E,0xB7,0xC9
};
static const uint8_t target[32] = {
  0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,
  0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,
  0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,
  0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0
};
/* All 19 new supports, with old contiguous, 0/8 and 0/14 pairs excluded. */
static const uint8_t pairs[19][2] = {
  {0,4},{0,6},{0,10},{0,12},
  {2,6},{2,8},{2,10},{2,12},{2,14},
  {4,8},{4,10},{4,12},{4,14},
  {6,10},{6,12},{6,14},
  {8,12},{8,14},{10,14}
};

static void candidate(uint8_t dst[16],int a,int b,uint32_t x) {
  memcpy(dst,base,16);
  dst[a]=(uint8_t)x;
  dst[a+1]=(uint8_t)(x>>8);
  dst[b]=(uint8_t)(x>>16);
  dst[b+1]=(uint8_t)(x>>24);
}
static void showhex(const uint8_t *buf,size_t n) {
  for (size_t j=0;j<n;j++) printf("%02X",buf[j]);
}
static int selftest(void) {
  uint8_t buf[16],dig[32],planted_digest[32];
  const uint32_t planted=0x00001337u;
  candidate(buf,pairs[0][0],pairs[0][1],planted);
  SHA256(buf,16,planted_digest);
  unsigned positives=0;
  for (uint32_t i=0;i<65536u;i++) {
    candidate(buf,pairs[0][0],pairs[0][1],i);
    SHA256(buf,16,dig);
    if (memcmp(dig,planted_digest,32)==0) {
      if (i!=planted) return 2;
      positives++;
    }
    if (memcmp(dig,target,32)==0) return 3;
  }
  if (positives!=1) return 4;
  SHA256(base,16,dig);
  if (memcmp(dig,target,32)==0) return 5;
  puts("SELFTEST_PASS planted_complete_fourbyte_positive=1 comparison_count=65536 original_hits=0");
  return 0;
}
static int exhaustive(int index) {
  const int a=pairs[index][0],b=pairs[index][1];
  unsigned long long count=0;
  unsigned hits=0;
  printf("START support_id=%d positions=%d,%d,%d,%d\n",index,a,a+1,b,b+1);
  fflush(stdout);
  #pragma omp parallel for schedule(static) reduction(+:count,hits)
  for (int hi=0;hi<256;hi++) {
    uint8_t buf[16],dig[32];
    for (uint32_t lo=0;lo<0x1000000u;lo++) {
      const uint32_t x=((uint32_t)hi<<24)|lo;
      candidate(buf,a,b,x);
      SHA256(buf,16,dig);
      if (memcmp(dig,target,32)==0) {
        #pragma omp critical
        {
          printf("ORIGINAL_K04_MATCH support_id=%d x=%08X component=",index,x);
          showhex(buf,16);
          putchar('\n');
          fflush(stdout);
        }
        hits++;
      }
      count++;
    }
  }
  printf("DONE support_id=%d complete_candidates=%llu original_hits=%u\n",
         index,count,hits);
  fflush(stdout);
  return count==4294967296ULL?0:6;
}
int main(int argc,char **argv) {
  if (argc==2 && strcmp(argv[1],"selftest")==0) return selftest();
  if (argc==3 && strcmp(argv[1],"run")==0) {
    char *end=0;
    long id=strtol(argv[2],&end,10);
    if (end==argv[2]||*end!='\0'||id<0||id>=19) return 7;
    return exhaustive((int)id);
  }
  fputs("usage: tester selftest | tester run support_id_0..18\n",stderr);
  return 8;
}
