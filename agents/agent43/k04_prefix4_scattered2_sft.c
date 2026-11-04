/* Agent 43: original K04 exact six-hex-character scattered-copy substitution search.
 *
 * The search changes exactly six among the 32 copied coupon hexadecimal
 * glyphs: all four at positions 0..3, plus two at distinct, nonadjacent trailing bytes. Each changed glyph has the other 15 possible values, generated
 * as nonzero XOR nibble deltas. No other payload nibble is modified.
 *
 * The two trailing edits occur in bytes separated by at least one intact byte.
 * This is disjoint from an adjacent-two-byte second burst model.
 *
 * Each whole 16-byte coupon is XORed with the untouched route mask, and
 * SHA256 of the resulting 16-byte K04 component is compared in full.
 * A positive planted six-change control is enumerated before every run.
 * Source file SHA256 pins prevent accidental use of changed evidence.
 */
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

static const uint8_t COPY[16]={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
static const uint8_t MASK[16]={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
static const uint8_t TARGET[32]={0x93,0x0A,0x52,0xA1,0xBA,0xB9,0x7C,0xA2,0x96,0x63,0x32,0x13,0x7C,0x99,0xE9,0x92,0x98,0xEA,0x61,0x82,0xFB,0x32,0xAB,0x63,0xA3,0x42,0x1D,0xFB,0x4F,0xD8,0xC9,0xE0};
static const char *SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";

static uint8_t candidate[16], expected[32];
static uint64_t checks=0, hits=0;
static int selected_positions[6];
static void enumerate_deltas(unsigned depth) {
    if(depth==6) {
        uint8_t h[32];
        SHA256(candidate,16,h);
        ++checks;
        if(memcmp(h,expected,32)==0) {
            ++hits;
            printf("FOUND K04 component=");
            for(int k=0;k<16;k++)printf("%02X",candidate[k]);
            printf(" pos=%d,%d,%d,%d,%d,%d\n",selected_positions[0],selected_positions[1],selected_positions[2],selected_positions[3],selected_positions[4],selected_positions[5]);
            fflush(stdout);
        }
        return;
    }
    unsigned idx=(unsigned)selected_positions[depth]/2;
    unsigned shift=(selected_positions[depth]%2==0)?4:0;
    for(unsigned d=1;d<=15;d++) {
        candidate[idx]^=(uint8_t)(d<<shift);
        enumerate_deltas(depth+1);
        candidate[idx]^=(uint8_t)(d<<shift);
    }
}
static void run_combo(const int pos[6]) {
    for(int i=0;i<6;i++)selected_positions[i]=pos[i];
    enumerate_deltas(0);
}
static void prepare(void) {
    for(int k=0;k<16;k++)candidate[k]=COPY[k]^MASK[k];
    memcpy(expected,TARGET,32);
}
static void synthetic_control(void) {
    static const int p[6]={0,1,2,3,4,8};
    static const int d[6]={1,2,3,4,5,6};
    prepare();
    for(int i=0;i<6;i++)candidate[p[i]/2]^=(uint8_t)(d[i]<<((p[i]%2==0)?4:0));
    uint8_t planted[32];
    SHA256(candidate,16,planted);
    prepare();
    memcpy(expected,planted,32);
    checks=hits=0;
    run_combo(p);
    if(checks!=11390625ULL || hits!=1ULL) {
        fprintf(stderr,"Synthetic six-glyph control FAIL checks=%"PRIu64" hits=%"PRIu64"\n",checks,hits);
        exit(3);
    }
    puts("Synthetic six-glyph control PASS: 11390625 candidates, unique hit");
    prepare();
    checks=hits=0;
}
static void verify_file(const char *root,const char *path,const char *expected_hex) {
    char filename[2048];
    if(snprintf(filename,sizeof(filename),"%s/%s",root,path)>=(int)sizeof(filename))exit(2);
    FILE *f=fopen(filename,"rb");if(!f){perror(filename);exit(2);}
    if(fseek(f,0,SEEK_END)!=0){perror("fseek");exit(2);}
    long n=ftell(f);
    if(n<0||n>20000000L){fprintf(stderr,"Bad input size: %s\n",path);exit(2);}
    rewind(f);
    unsigned char *buf=malloc(n?(size_t)n:1);
    if(!buf){perror("malloc");exit(2);}
    if(fread(buf,1,(size_t)n,f)!=(size_t)n){perror("fread");exit(2);}
    fclose(f);
    unsigned char digest[32];SHA256(buf,(size_t)n,digest);free(buf);
    char actual[65];for(int i=0;i<32;i++)sprintf(actual+i*2,"%02x",digest[i]);
    if(strcmp(actual,expected_hex)){
        fprintf(stderr,"Source pin mismatch for %s, got %s\n",path,actual);exit(2);
    }
}
int main(int argc,char **argv) {
    if(argc<2||argc>5) {
        fprintf(stderr,"Usage: %s RESOURCES_DIR [SHARD SHARDS [MAX_COMBOS]]\n",argv[0]);return 2;
    }
    int shard=argc>=3?atoi(argv[2]):0, shards=argc>=4?atoi(argv[3]):1;
    uint64_t max_combos=argc>=5?strtoull(argv[4],NULL,10):0;
    if(shards<1||shards>256||shard<0||shard>=shards){fprintf(stderr,"Invalid shard\n");return 2;}
    verify_file(argv[1],"evidence/print/spool-reconstruction.log",SPOOL_SHA);
    verify_file(argv[1],"evidence/recovery-routing.json",ROUTE_SHA);
    verify_file(argv[1],"acceptance.json",ACCEPT_SHA);
    synthetic_control();
    uint64_t eligible=0,mine=0,completed=0;
    for(int p4=4;p4<31;p4++) for(int p5=p4+1;p5<32;p5++) {
        if(p5/2 - p4/2 < 2)continue;
        uint64_t index=eligible++;
        if(index%(uint64_t)shards!=(uint64_t)shard)continue;
        ++mine;
        if(max_combos && completed>=max_combos)continue;
        int p[6]={0,1,2,3,p4,p5};
        run_combo(p);
        ++completed;
        fprintf(stderr,"Progress shard=%d/%d combos=%"PRIu64" checks=%"PRIu64"\n",shard,shards,completed,checks);
        fflush(stderr);
    }
    if(eligible!=312ULL||checks!=completed*11390625ULL) {
        fprintf(stderr,"Enumeration count mismatch eligible=%"PRIu64" checks=%"PRIu64"\n",eligible,checks);
        return 3;
    }
    printf("RESULT mode=prefix4-scattered2 shard=%d shards=%d eligible=%"PRIu64" assigned=%"PRIu64" completed=%"PRIu64" checks=%"PRIu64" hits=%"PRIu64" %s\n",shard,shards,eligible,mine,completed,checks,hits,(max_combos&&completed<mine)?"PILOT":"COMPLETE");
    if(hits)return 10;
    return 0;
}
