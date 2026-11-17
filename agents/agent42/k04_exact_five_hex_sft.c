/* H17 K04 original source, exactly five altered hex glyphs in copied ACK2.
   argv: SHARD TOTAL_SHARDS [SOURCE_ROOT], where SOURCE_ROOT contains
   evidence/ and acceptance.json; default SOURCE_ROOT='resources'.
   Compile: cc -O3 -march=native -std=c11 agent42_k04_5hex.c -lcrypto -o k04_5hex
*/
#define _POSIX_C_SOURCE 200809L
#include <openssl/sha.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t component[16] = {0x2c,0xff,0x14,0x9c,0x50,0xe5,0x45,0x57,0x22,0x8e,0x7d,0xe6,0x0b,0x3e,0xb7,0xc9};
static const uint8_t target[32] = {0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,
                                    0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static const char *pin_spool="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *pin_route="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *pin_accept="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static void fatal(const char *s){fprintf(stderr,"FAIL: %s\n",s);exit(2);}
static void pin(const char *root,const char *sub,const char *want){
    char path[1024]; snprintf(path,sizeof(path),"%s/%s",root,sub);
    FILE *f=fopen(path,"rb");if(!f) fatal(path);
    SHA256_CTX ctx; SHA256_Init(&ctx); uint8_t block[16384];size_t n;
    while((n=fread(block,1,sizeof(block),f))>0) SHA256_Update(&ctx,block,n);
    if(ferror(f))fatal("source read");fclose(f);
    uint8_t h[32];SHA256_Final(h,&ctx);char actual[65];
    for(unsigned i=0;i<32;i++)sprintf(actual+2*i,"%02x",h[i]);
    if(strcmp(actual,want))fatal(path);
}
static inline void nibxor(uint8_t blk[64],int pos,unsigned value){
    blk[pos/2] ^= (uint8_t)(value << ((pos&1)?0:4));
}
static inline int equalhash(const uint8_t blk[64],const SHA256_CTX *zero){
    SHA256_CTX ctx=*zero;
    SHA256_Transform(&ctx,blk);
    for(unsigned j=0;j<8;j++){
        uint32_t t=((uint32_t)target[4*j]<<24)|((uint32_t)target[4*j+1]<<16)|((uint32_t)target[4*j+2]<<8)|target[4*j+3];
        if(ctx.h[j]!=t)return 0;
    }
    return 1;
}
static void print_hit(const uint8_t blk[64],int p[5],int deltas[5]){
    printf("ORIGINAL_K04_HIT glyphs=%d,%d,%d,%d,%d deltas=%x%x%x%x%x coupon=",p[0],p[1],p[2],p[3],p[4],deltas[0],deltas[1],deltas[2],deltas[3],deltas[4]);
    uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
    for(int j=0;j<16;j++)printf("%02X",blk[j]^mask[j]);
    printf(" component=");for(int j=0;j<16;j++)printf("%02X",blk[j]);printf("\n");fflush(stdout);
}
static void selftest(const SHA256_CTX *zero){
    uint8_t blk[64]={0};memcpy(blk,component,16);blk[16]=0x80;blk[63]=0x80;
    SHA256_CTX ctx=*zero;SHA256_Transform(&ctx,blk);
    uint8_t direct[32];SHA256(component,16,direct);
    for(int j=0;j<8;j++){
        uint32_t want=((uint32_t)direct[4*j]<<24)|((uint32_t)direct[4*j+1]<<16)|((uint32_t)direct[4*j+2]<<8)|direct[4*j+3];
        if(ctx.h[j]!=want)fatal("oneblock SHA256 parity");
    }
    if(equalhash(blk,zero))fatal("historical copied ACK accepted unexpectedly");
    int p[5]={0,5,10,15,31},d[5]={1,2,3,4,5};
    for(int k=0;k<5;k++)nibxor(blk,p[k],d[k]);
    uint8_t synthetic[32];SHA256(blk,16,synthetic);
    ctx=*zero; SHA256_Transform(&ctx,blk);
    for(int j=0;j<8;j++){
        uint32_t want=((uint32_t)synthetic[4*j]<<24)|((uint32_t)synthetic[4*j+1]<<16)|((uint32_t)synthetic[4*j+2]<<8)|synthetic[4*j+3];
        if(ctx.h[j]!=want)fatal("synthetic five-glyph SHA256 parity");
    }
    /* Exhaustively recover the independently planted full five-glyph string
       from its complete synthetic SHA256; every other delta must fail. */
    uint64_t found=0;
    uint8_t probe[64]={0};memcpy(probe,component,16);probe[16]=0x80;probe[63]=0x80;
    for(int x0=1;x0<=15;x0++){
        nibxor(probe,p[0],(unsigned)x0);
        for(int x1=1;x1<=15;x1++){
            nibxor(probe,p[1],(unsigned)x1);
            for(int x2=1;x2<=15;x2++){
                nibxor(probe,p[2],(unsigned)x2);
                for(int x3=1;x3<=15;x3++){
                    nibxor(probe,p[3],(unsigned)x3);
                    for(int x4=1;x4<=15;x4++){
                        nibxor(probe,p[4],(unsigned)x4);
                        SHA256_CTX test=*zero;SHA256_Transform(&test,probe);
                        unsigned match=1;
                        for(int j=0;j<8;j++){
                            uint32_t want=((uint32_t)synthetic[4*j]<<24)|((uint32_t)synthetic[4*j+1]<<16)|((uint32_t)synthetic[4*j+2]<<8)|synthetic[4*j+3];
                            if(test.h[j]!=want){match=0;break;}
                        }
                        found+=match;
                        nibxor(probe,p[4],(unsigned)x4);
                    }
                    nibxor(probe,p[3],(unsigned)x3);
                }
                nibxor(probe,p[2],(unsigned)x2);
            }
            nibxor(probe,p[1],(unsigned)x1);
        }
        nibxor(probe,p[0],(unsigned)x0);
    }
    if(found!=1) fatal("synthetic five-glyph enumeration");
    printf("SYNTHETIC_FIVE_NIBBLE_FULL_SHA256_PASS hits=1/759375\n");fflush(stdout);
}
int main(int argc,char **argv){
    if(argc<3 || argc>4){fprintf(stderr,"usage: %s SHARD TOTAL_SHARDS [SOURCE_ROOT]\n",argv[0]);return 2;}
    char *end=NULL;unsigned long shard=strtoul(argv[1],&end,10);if(!end||*end)fatal("shard parse");
    unsigned long total=strtoul(argv[2],&end,10);if(!end||*end||!total||shard>=total)fatal("shard range");
    const char *root=argc>=4?argv[3]:"resources";
    pin(root,"evidence/print/spool-reconstruction.log",pin_spool);
    pin(root,"evidence/recovery-routing.json",pin_route);
    pin(root,"acceptance.json",pin_accept);
    SHA256_CTX zero;SHA256_Init(&zero);selftest(&zero);
    uint8_t blk[64]={0};memcpy(blk,component,16);blk[16]=0x80;blk[63]=0x80;
    uint64_t tuples=0,checks=0,hits=0,ordinal=0;
    for(int a=0;a<28;a++)for(int b=a+1;b<29;b++)for(int c=b+1;c<30;c++)for(int d=c+1;d<31;d++)for(int e=d+1;e<32;e++,ordinal++){
        if(ordinal%total!=shard)continue;
        int p[5]={a,b,c,d,e},v[5];tuples++;
        for(v[0]=1;v[0]<=15;v[0]++){
            nibxor(blk,a,(unsigned)v[0]);
            for(v[1]=1;v[1]<=15;v[1]++){
                nibxor(blk,b,(unsigned)v[1]);
                for(v[2]=1;v[2]<=15;v[2]++){
                    nibxor(blk,c,(unsigned)v[2]);
                    for(v[3]=1;v[3]<=15;v[3]++){
                        nibxor(blk,d,(unsigned)v[3]);
                        for(v[4]=1;v[4]<=15;v[4]++){
                            nibxor(blk,e,(unsigned)v[4]);
                            if(equalhash(blk,&zero)){print_hit(blk,p,v);hits++;}
                            checks++;
                            nibxor(blk,e,(unsigned)v[4]);
                        }
                        nibxor(blk,d,(unsigned)v[3]);
                    }
                    nibxor(blk,c,(unsigned)v[2]);
                }
                nibxor(blk,b,(unsigned)v[1]);
            }
            nibxor(blk,a,(unsigned)v[0]);
        }
    }
    if(ordinal!=201376ULL)fatal("tuple domain mismatch");
    if(checks!=tuples*759375ULL)fatal("count mismatch");
    printf("DONE shard=%lu total=%lu tuples=%" PRIu64 " checks=%" PRIu64 " original_hits=%" PRIu64 "\n",shard,total,tuples,checks,hits);
    return hits?1:0;
}
