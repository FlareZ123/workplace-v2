/* K04: full 9^8 per-bitplane donor+one-bit-slip producer.
 * Uses the exact three genuine preserved 0417 nonselected 16byte buffers,
 * original source/digest gates and SHA256 compressor from sibling SFT.
 * Build: cc -O3 -std=c11 -Wno-deprecated-declarations
 *     agents/agent3/k04_bitplane_serdes_slip_sft.c -lcrypto -o serdes
 */
#define main unused_affine_main
#include "k04_bitplane_affine_sft.c"
#undef main

static struct words slip[8][9];
static void slip_init(void){
  for(int bit=0;bit<8;bit++)for(int sel=0;sel<9;sel++){
    int src=sel/3, shift=sel%3-1, from=(bit+shift+8)%8;
    uint8_t b[16];
    for(int j=0;j<16;j++)b[j]=(uint8_t)(((donor[src][j]>>from)&1)<<bit);
    memcpy(&slip[bit][sel].lo,b,8);
    memcpy(&slip[bit][sel].hi,b+8,8);
  }
  /* Each source-bit-plane selector must generate a distinct 16bit vector. */
  for(int bit=0;bit<8;bit++)for(int a=0;a<9;a++)for(int b=0;b<a;b++)
    if(slip[bit][a].lo==slip[bit][b].lo&&slip[bit][a].hi==slip[bit][b].hi)
      die("source bit selector collides");
}
static void slip_component(uint32_t code,uint8_t out[16]){
  uint64_t lo=0,hi=0,ml,mh;
  memcpy(&ml,mask,8);memcpy(&mh,mask+8,8);
  for(int bit=0;bit<8;bit++){
    unsigned sel=code%9;code/=9;
    lo|=slip[bit][sel].lo;hi|=slip[bit][sel].hi;
  }
  lo^=ml;hi^=mh;memcpy(out,&lo,8);memcpy(out+8,&hi,8);
}
int main(int argc,char**argv){
  if(argc!=2)die("usage: serdes resources");
  source(argv[1],"evidence/print/spool-reconstruction.log",
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",1);
  source(argv[1],"evidence/recovery-routing.json",
    "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",0);
  source(argv[1],"acceptance.json",
    "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",0);
  slip_init();
  SHA256_CTX initial;SHA256_Init(&initial);
  uint8_t block[64]={0},plain[16],digest[32];
  block[16]=0x80;block[63]=0x80;
  const uint32_t planted_code=20261104;
  slip_component(planted_code,plain);SHA256(plain,16,digest);
  unsigned planted[8];
  for(int i=0;i<8;i++)planted[i]=word(digest,i);
  SHA256_CTX state=initial;memcpy(block,plain,16);
  SHA256_Transform(&state,block);
  for(int i=0;i<8;i++)if(state.h[i]!=planted[i])die("SHA256 plant discrepancy");
  unsigned long long original_hits=0,synthetic_hits=0;
  for(uint32_t c=0;c<43046721U;c++){
    slip_component(c,block);state=initial;SHA256_Transform(&state,block);
    if(state.h[0]==original[0]){
      int yes=1;for(int i=1;i<8;i++)yes &=state.h[i]==original[i];
      if(yes){original_hits++;printf("ORIGINAL_MATCH code=%u\n",c);}
    }
    if(state.h[0]==planted[0]){
      int yes=1;for(int i=1;i<8;i++)yes &=state.h[i]==planted[i];
      if(yes)synthetic_hits++;
    }
  }
  printf("SOURCE_PINNED complete_k04_bitplane_serdes=43046721 original_matches=%llu planted_positive=%llu\n",original_hits,synthetic_hits);
  return original_hits?9:synthetic_hits!=1?3:0;
}
