/* K04 adjacent-stage one-unknown-output exhaustive coupon test.
 * Purely historical source data; only original immutable commitment compared.
 * C11, OpenSSL libcrypto, OpenMP. Source preflight is in manual CI workflow.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/sha.h>
#include <omp.h>

typedef struct {const char *tag; const char *bytes; int unknown_word;} Stage;
static const Stage stages[]={
  {"943_prev_ack_plus_gap", "78FFE61C33320BCB9417848000000000",3},
  {"946_gap_before_req1", "00000000CD3E4F216ADB2FB180DA2AA9",0},
  {"948_req1_to_ACK2", "6ADB2FB180DA2AA90B33F7A400000000",3},
  {"954_ACK2_to_req3", "0000000044D53DFC29D7943A95D89371",0}
};
static uint8_t mask[16],wanted[32];
static void fromhex(const char *s,uint8_t *out,size_t n){
 for(size_t i=0;i<n;i++){
  unsigned x;if(sscanf(s+2*i,"%2x",&x)!=1){fprintf(stderr,"BAD HEX\n");exit(3);}
  out[i]=(uint8_t)x;
 }
}
static int run(int index,uint64_t begin,uint64_t end,int threads){
 Stage st=stages[index];uint8_t data[16];fromhex(st.bytes,data,16);
 uint64_t control_val=UINT64_C(0xD3E19F20);
 uint8_t planted[16],ctrl[32];memcpy(planted,data,16);
 for(int i=0;i<4;i++)planted[4*st.unknown_word+i]=(uint8_t)(control_val>>(8*i));
 for(int i=0;i<16;i++)planted[i]^=mask[i];
 SHA256(planted,16,ctrl);
 uint64_t hits=0,positives=0;
 double start=omp_get_wtime();
 #pragma omp parallel num_threads(threads) reduction(+:hits,positives)
 {
  uint8_t buf[16],digest[32];memcpy(buf,data,16);
  for(int i=0;i<16;i++)buf[i]^=mask[i];
  #pragma omp for schedule(static)
  for(uint64_t v=begin;v<end;v++){
   for(int i=0;i<4;i++)buf[4*st.unknown_word+i]=mask[4*st.unknown_word+i]^(uint8_t)(v>>(8*i));
   SHA256(buf,16,digest);
   if(memcmp(digest,wanted,32)==0){
     #pragma omp critical
     fprintf(stdout,"ORIGINAL_HIT stage=%s word=%08" PRIX64 "\n",st.tag,v);
     ++hits;
   }
   if(memcmp(digest,ctrl,32)==0){
     #pragma omp critical
     fprintf(stdout,"SYNTHETIC_POSITIVE stage=%s word=%08" PRIX64 "\n",st.tag,v);
     ++positives;
   }
  }
 }
 uint64_t expected=(begin<=control_val && control_val<end)?1:0;
 fprintf(stdout,"RESULT stage=%s begin=%" PRIu64 " end=%" PRIu64 " total=%" PRIu64 " original_hits=%" PRIu64 " positive_hits=%" PRIu64 " expected_positives=%" PRIu64 " seconds=%.3f\n",st.tag,begin,end,end-begin,hits,positives,expected,omp_get_wtime()-start);
 fflush(stdout);
 return positives==expected?(hits?2:0):3;
}
int main(int argc,char**argv){
 if(argc!=5){fprintf(stderr,"usage: program stage[0..3] begin end threads\n");return 3;}
 int stage=atoi(argv[1]),threads=atoi(argv[4]);
 uint64_t begin=strtoull(argv[2],NULL,10),end=strtoull(argv[3],NULL,10);
 if(stage<0||stage>=4||threads<1||threads>32||begin>=end||end>UINT64_C(4294967296))return 3;
 fromhex("8556C8CB6140A7F9A5123AC7571BEE1C",mask,16);
 fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",wanted,32);
 return run(stage,begin,end,threads);
}
