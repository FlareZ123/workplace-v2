/* H17 K04: copied prefix of length k (3 or 4) is extraneous;
 * k original unknown glyphs were lost elsewhere, preserving the order
 * of the remaining 32-k copied hex characters.
 *
 * Exactly C(32,k)*16^k full coupon candidates, k=3 or 4.
 * Source and source-checker pins come from the tested five-glyph SFT.
 */
#define main original_five_glyph_main
#include "k04_five_hex_glyph_sft.c"
#undef main

static int K=0, pos[4];
static uint64_t positive_hits=0;
static uint8_t positive_target[32];

static unsigned source_nib(int i) {
    unsigned v=COPY[i/2];
    return (v>>((i%2)?0:4))&15;
}
static void candidate_base(void) {
    memcpy(candidate,MASK,16);
    int i=0, j=K, selected=0;
    for(;i<32;i++) {
        if(selected<K && i==pos[selected]){ selected++;continue; }
        if(j>=32){fprintf(stderr,"SOURCE INDEX OVERRUN\n");exit(3);}
        unsigned v=source_nib(j++);
        candidate[i/2]^=(uint8_t)(v<<((i%2)?0:4));
    }
    if(j!=32 || selected!=K){fprintf(stderr,"BASE COUNT ERROR\n");exit(3);}
}
static void rec(unsigned depth) {
    if(depth==(unsigned)K) {
        uint8_t digest[32];SHA256(candidate,16,digest);
        checks++;
        if(memcmp(digest,expected,32)==0) {
            hits++;
            printf("ACTUAL K04 HIT k=%d component=",K);
            for(int i=0;i<16;i++)printf("%02X",candidate[i]);
            printf("\n");fflush(stdout);
        }
        if(memcmp(digest,positive_target,32)==0)positive_hits++;
        return;
    }
    unsigned index=(unsigned)pos[depth]/2;
    unsigned shift=(pos[depth]%2)?0:4;
    for(unsigned v=0;v<16;v++) {
        candidate[index]^=(uint8_t)(v<<shift);
        rec(depth+1);
        candidate[index]^=(uint8_t)(v<<shift);
    }
}
static void probe(void) {
    candidate_base();
    rec(0);
}
static void synthetic_positive(void) {
    pos[0]=1;pos[1]=12;pos[2]=24;pos[3]=30;
    candidate_base();
    for(int i=0;i<K;i++)candidate[pos[i]/2]^=(uint8_t)((i+2)<<((pos[i]%2)?0:4));
    SHA256(candidate,16,positive_target);
    prepare(); // restore original target
    checks=hits=positive_hits=0;
    probe();
    uint64_t per=(K==3)?4096ULL:65536ULL;
    if(checks!=per||positive_hits!=1) {
        fprintf(stderr,"SYNTHETIC FAILED k=%d checks=%"PRIu64" positives=%"PRIu64"\n",K,checks,positive_hits);
        exit(3);
    }
    printf("SYNTHETIC PASS k=%d unique planted complete component among %"PRIu64" probes\n",K,per);
    checks=hits=positive_hits=0;
    memset(positive_target,0,32);
    prepare();
}
int main(int argc,char **argv) {
    if(argc<3||argc>6){fprintf(stderr,"Usage: %s RESOURCES k(3|4) [shard shards [max_combos]]\n",argv[0]);return 2;}
    K=atoi(argv[2]);
    int shard=argc>=4?atoi(argv[3]):0, shards=argc>=5?atoi(argv[4]):1;
    uint64_t max_combos=argc>=6?strtoull(argv[5],NULL,10):0;
    if((K!=3&&K!=4)||shards<1||shards>256||shard<0||shard>=shards)return 2;
    verify_file(argv[1],"evidence/print/spool-reconstruction.log",SPOOL_SHA);
    verify_file(argv[1],"evidence/recovery-routing.json",ROUTE_SHA);
    verify_file(argv[1],"acceptance.json",ACCEPT_SHA);
    synthetic_positive();
    uint64_t eligible=0,assigned=0,completed=0;
    for(int a=0;a<((K==3)?30:29);a++)
    for(int b=a+1;b<((K==3)?31:30);b++)
    for(int c=b+1;c<((K==3)?32:31);c++) {
        for(int d=(K==3)?0:c+1;d<((K==3)?1:32);d++) {
            uint64_t ordinal=eligible++;
            if(ordinal%(uint64_t)shards!=(uint64_t)shard)continue;
            ++assigned;
            if(max_combos&&completed>=max_combos)continue;
            pos[0]=a;pos[1]=b;pos[2]=c;pos[3]=d;
            probe();completed++;
            if(completed%100==0){
                fprintf(stderr,"progress k=%d shard=%d completed=%"PRIu64" checks=%"PRIu64"\n",K,shard,completed,checks);
                fflush(stderr);
            }
        }
    }
    uint64_t total=(K==3)?4960ULL:35960ULL, per=(K==3)?4096ULL:65536ULL;
    if(eligible!=total || checks!=completed*per) {
        fprintf(stderr,"COUNT ERROR k=%d eligible=%"PRIu64" completed=%"PRIu64" checks=%"PRIu64"\n",K,eligible,completed,checks);return 3;
    }
    printf("RESULT k=%d shard=%d shards=%d eligible=%"PRIu64" assigned=%"PRIu64" completed=%"PRIu64" checks=%"PRIu64" hits=%"PRIu64" %s\n",K,shard,shards,eligible,assigned,completed,checks,hits,(max_combos&&completed<assigned)?"PILOT":"COMPLETE");
    return hits?10:0;
}
