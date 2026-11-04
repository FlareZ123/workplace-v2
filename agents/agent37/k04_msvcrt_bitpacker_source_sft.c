/* H17 K04: first intact source packet against 15-bit MSVCRT rand bit packing.
 * Source-only original; all 32bit internal states and 15 phase offsets.
 * Byte serialization + raw bit order both tested; source SHA pin.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint8_t first[16]={0xfb,0xbb,0xc5,0x43,0x56,0x48,0x3f,0x58,0x64,0xbb,0x3f,0x06,0x79,0x45,0x18,0xa5};
static const uint8_t pin[32]={0x7d,0x71,0xd8,0xbe,0xf7,0xf0,0x15,0x96,0xe7,0x05,0xac,0x14,0xe2,0x4c,0x5c,0x43,0x52,0x04,0x25,0x12,0xb3,0x08,0x81,0x25,0xaf,0xca,0x40,0xf3,0x84,0x1b,0x60,0x83};
static uint32_t inverse(){uint32_t x=214013u;for(int i=0;i<5;i++)x*=2-214013u*x;return x;}
static inline uint32_t next(uint32_t x){return x*214013u+2531011u;}
static inline int bit(uint32_t s,int k,int reverse){uint32_t v=(s>>16)&32767u;return (v>>(reverse?k:14-k))&1u;}
static int source(const char *path){FILE *f=fopen(path,"rb");if(!f){perror(path);return 0;}SHA256_CTX c;SHA256_Init(&c);char b[8192],raw[30000]={0};size_t n,total=0;while((n=fread(b,1,sizeof(b),f))){SHA256_Update(&c,b,n);if(total+n>=sizeof(raw)){fclose(f);return 0;}memcpy(raw+total,b,n);total+=n;}int bad=ferror(f);fclose(f);uint8_t sha[32];SHA256_Final(sha,&c);return !bad&&!memcmp(sha,pin,32)&&strstr(raw,"JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL PAYLOAD=FBBBC54356483F5864BB3F06794518A5");}
static void bits(uint8_t out[128],const uint8_t src[16],int byte_reverse){for(int i=0;i<128;i++)out[i]=(src[i>>3]>>(byte_reverse?(i&7):(7-(i&7))))&1;}
static int test(const uint8_t out[128],int phase,int reverse,uint32_t s2,uint32_t inv){
 uint32_t s1=(s2-2531011u)*inv;
 for(int j=phase;j<15;j++)if(bit(s1,j,reverse)!=out[j-phase])return 0;
 uint32_t state=s2;int p=15-phase;
 while(p<128){for(int j=0;j<15&&p<128;j++,p++)if(bit(state,j,reverse)!=out[p])return 0;state=next(state);}return 1;
}
static uint64_t scan(const uint8_t out[128],int phase,int reverse,uint32_t inv){
 uint32_t anchored=0;for(int j=0;j<15;j++){int b=out[15-phase+j];if(reverse)anchored|=(uint32_t)b<<j;else anchored=(anchored<<1)|b;}
 uint64_t found=0;
 for(uint32_t lo=0;lo<65536u;lo++)for(uint32_t hi=0;hi<2u;hi++){
  uint32_t s2=(hi<<31)|(anchored<<16)|lo;
  found+=test(out,phase,reverse,s2,inv);
 }
 return found;
}
static void synth(uint8_t out[128],uint32_t first_state,int phase,int reverse){uint32_t state=first_state;int p=0;int offset=phase;while(p<128){for(int j=offset;j<15&&p<128;j++)out[p++]=(uint8_t)bit(state,j,reverse);state=next(state);offset=0;}}
int main(int argc,char **argv){if(argc!=2||!source(argv[1])){fprintf(stderr,"Source integrity failure\n");return 2;}uint32_t inv=inverse();if(inv*214013u!=1){fprintf(stderr,"bad inverse\n");return 3;}uint8_t observed[128],positive[128];uint64_t assignments=0,hits=0;unsigned controls=0;for(int byte=0;byte<2;byte++){bits(observed,first,byte);for(int rev=0;rev<2;rev++)for(int phase=0;phase<15;phase++){uint64_t n=scan(observed,phase,rev,inv);assignments+=131072;hits+=n;if(n)printf("ORIGINAL_SOURCE_MATCH byte=%d reverse=%d phase=%d count=%llu\n",byte,rev,phase,(unsigned long long)n);if((byte==0&&rev==0&&phase==0)||(byte==1&&rev==1&&phase==13)){synth(positive,0x9c582f13u,phase,rev);uint64_t got=scan(positive,phase,rev,inv);printf("PLANTED phase=%d bit_order=%d byte=%d matches=%llu\n",phase,rev,byte,(unsigned long long)got);if(got!=2)return 5;controls++;}}}printf("PACKED_15BIT original full_source_models=60 constrained_firststates=%llu original_hits=%llu planted_pass=%u inverse=%08X\n",(unsigned long long)assignments,(unsigned long long)hits,controls,inv);return hits||assignments!=7864320||controls!=2?4:0;}
