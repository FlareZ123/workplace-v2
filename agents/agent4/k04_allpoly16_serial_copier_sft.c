/*
 * H-17 K04: full 16-bit unknown-feedback serial scrambler of selected ACK copy.
 * Each shard covers 1024 complete feedback polynomials, 8 orientations,
 * every one of 65536 initial states. Uses original SHA256 of full K04 component.
 * Positive planted single-state check covers the same SHA/coupon pipeline.
 * Original accepted target and source files never modified.
 */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

enum {POLY_BITS=16, STATES=65536, POLYS_PER_SHARD=1024, SHARDS=64};
static const char *spool_hash="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *route_hash="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *accept_hash="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const char *base_hex="2CFF149C50E54557228E7DE60B3EB7C9";
static const char *target_hex="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";

static unsigned unhex(char ch){
    if(ch>='0'&&ch<='9')return (unsigned)(ch-'0');
    if(ch>='a'&&ch<='f')return (unsigned)(ch-'a'+10);
    if(ch>='A'&&ch<='F')return (unsigned)(ch-'A'+10);
    fprintf(stderr,"invalid hex digit\n");exit(2);
}
static void parse_hex(const char *s,uint8_t *dst,size_t count){
    assert(strlen(s)==2*count);
    for(size_t i=0;i<count;i++)dst[i]=(uint8_t)((unhex(s[2*i])<<4)|unhex(s[2*i+1]));
}
static void emit_hex(const uint8_t *src,size_t n){
    for(size_t i=0;i<n;i++)printf("%02X",src[i]);
}
static void pin_file(const char *path,const char *expect){
    FILE *f=fopen(path,"rb");
    if(!f){perror(path);exit(2);}
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    uint8_t buf[16384],digest[SHA256_DIGEST_LENGTH];
    size_t got;
    while((got=fread(buf,1,sizeof buf,f))>0)SHA256_Update(&ctx,buf,got);
    if(ferror(f)){perror(path);exit(2);}
    fclose(f);
    SHA256_Final(digest,&ctx);
    uint8_t want[SHA256_DIGEST_LENGTH];parse_hex(expect,want,sizeof want);
    if(memcmp(digest,want,sizeof want)){fprintf(stderr,"SOURCE_PIN_FAILED %s\n",path);exit(2);}
}
static uint16_t rev16(uint16_t x){
    uint16_t r=0;
    for(int i=0;i<16;i++){r=(uint16_t)((r<<1)|(x&1));x>>=1;}
    return r;
}
static void bitstream(uint16_t seed,uint16_t poly,int mode,uint8_t out[16]){
    const int reverse_clock=(mode>>2)&1;
    const int lsb_first=(mode>>1)&1;
    const int reverse_bytes=mode&1;
    const uint16_t feedback=reverse_clock?rev16(poly):poly;
    uint16_t state=seed;
    memset(out,0,16);
    for(int i=0;i<128;i++){
        const unsigned bit=reverse_clock?(state&1):(state>>15);
        if(reverse_clock)state=(uint16_t)((state>>1)^(bit?feedback:0));
        else state=(uint16_t)(((state<<1)&65535)^(bit?feedback:0));
        const int b=reverse_bytes?15-i/8:i/8;
        const int k=lsb_first?i%8:7-i%8;
        out[b]|=(uint8_t)(bit<<k);
    }
}
int main(int argc,char **argv){
    if(argc!=2){fprintf(stderr,"usage: %s shard_0_to_63\n",argv[0]);return 2;}
    char *end=0;
    const long shard=strtol(argv[1],&end,10);
    if(*end||shard<0||shard>=SHARDS){fprintf(stderr,"invalid shard\n");return 2;}
    pin_file("resources/evidence/print/spool-reconstruction.log",spool_hash);
    pin_file("resources/evidence/recovery-routing.json",route_hash);
    pin_file("resources/acceptance.json",accept_hash);

    uint8_t base[16],target[32],test_digest[32];
    parse_hex(base_hex,base,16);parse_hex(target_hex,target,32);
    SHA256(base,16,test_digest);
    assert(memcmp(test_digest,target,32)!=0);

    const uint16_t start=(uint16_t)(shard*POLYS_PER_SHARD);
    const uint32_t stop=(uint32_t)(shard+1)*POLYS_PER_SHARD;
    const uint16_t synth_poly=(uint16_t)(start+0x155);
    const uint16_t synth_seed=0xA53D;
    const int synth_mode=(int)(shard%8);
    uint8_t synthetic_stream[16],synthetic_coupon[16],synthetic_target[32];
    bitstream(synth_seed,synth_poly,synth_mode,synthetic_stream);
    for(int j=0;j<16;j++)synthetic_coupon[j]=base[j]^synthetic_stream[j];
    SHA256(synthetic_coupon,16,synthetic_target);
    assert(memcmp(synthetic_target,target,32)!=0);

    uint64_t checks=0;
    unsigned originals=0,planted=0;
    for(uint32_t p=start;p<stop;p++){
        for(int mode=0;mode<8;mode++){
            uint8_t basis[16][16],candidate[16],digest[32];
            for(int bit=0;bit<16;bit++)bitstream((uint16_t)(1u<<bit),(uint16_t)p,mode,basis[bit]);
            memcpy(candidate,base,16);
            uint16_t lastgray=0;
            for(uint32_t i=0;i<STATES;i++){
                uint16_t gray=(uint16_t)(i^(i>>1));
                uint16_t changed=(uint16_t)(gray^lastgray);
                if(changed){
                    const int idx=__builtin_ctz((unsigned)changed);
                    for(int j=0;j<16;j++)candidate[j]^=basis[idx][j];
                }
                lastgray=gray;
                SHA256(candidate,16,digest);
                checks++;
                if(!memcmp(digest,target,32)){
                    originals++;
                    printf("ORIGINAL_K04_FOUND shard=%ld poly=%04X mode=%d state=%04X component=",shard,(unsigned)p,mode,(unsigned)gray);
                    emit_hex(candidate,16);printf("\n");fflush(stdout);
                }
                if((uint16_t)p==synth_poly&&mode==synth_mode&&!memcmp(digest,synthetic_target,32)){
                    if(gray!=synth_seed||memcmp(candidate,synthetic_coupon,16)){fprintf(stderr,"SYNTHETIC_MISMATCH\n");return 2;}
                    planted++;
                }
            }
        }
        if(((p-start+1)%128)==0){
            printf("ORIGINAL_SCAN_PROGRESS shard=%ld polynomials=%u complete_checks=%llu hits=%u\n",shard,(unsigned)(p-start+1),(unsigned long long)checks,originals);
            fflush(stdout);
        }
    }
    const uint64_t expected=(uint64_t)POLYS_PER_SHARD*8*STATES;
    if(checks!=expected||planted!=1){fprintf(stderr,"CHECK_ERROR shard=%ld checks=%llu expected=%llu planted=%u\n",shard,(unsigned long long)checks,(unsigned long long)expected,planted);return 2;}
    printf("ALLPOLY16_SHARD_COMPLETE shard=%ld begin=%u end_exclusive=%u checks=%llu planted=%u original=%u\n",
           shard,start,(unsigned)stop,(unsigned long long)checks,planted,originals);
    return 0;
}
