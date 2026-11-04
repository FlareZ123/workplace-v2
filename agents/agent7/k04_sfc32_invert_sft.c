/*
 * H-17 printer SFC32 inverse, read-only single-file test.
 * gcc -O3 -fopenmp k04_sfc32_invert_sft.c -lcrypto -o sfc32_check
 * Run from repo root with OpenMP and OpenSSL libcrypto installed.
 * Consumes four intact original 07:00..07:15 printer packets.
 * The 0417 selected ACK2 packet is withheld from all inference.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <omp.h>
#define SOURCE_SHA "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
typedef struct { uint32_t a,b,c,d; } State;
static inline uint32_t rot21(uint32_t x) { return (x<<21)|(x>>11); }
static inline uint32_t unshift9(uint32_t x) { return x^(x>>9)^(x>>18)^(x>>27); }
static inline uint32_t next(State *s) {
    uint32_t t=s->a+s->b+s->d;
    s->a=s->b^(s->b>>9); s->b=9u*s->c;
    s->c=rot21(s->c)+t; s->d++;
    return t;
}
static State invert(uint32_t c,uint32_t t0,uint32_t t1,uint32_t t2) {
    uint32_t c1=rot21(c)+t0, b1=9u*c;
    uint32_t d=t2-(b1^(b1>>9))-9u*c1-2u;
    uint32_t b=unshift9(t1-9u*c-d-1u);
    return (State){t0-b-d,b,c,d};
}
static inline uint32_t fourth(uint32_t c,uint32_t t0,uint32_t t1,uint32_t t2) {
    uint32_t c1=rot21(c)+t0,c2=rot21(c1)+t1;
    uint32_t b1=9u*c,b2=9u*c1;
    uint32_t d=t2-(b1^(b1>>9))-9u*c1-2u;
    return (b2^(b2>>9))+9u*c2+d+3u;
}
static int replays(State s,const uint32_t w[4]) {
    for(int i=0;i<4;i++) if(next(&s)!=w[i]) return 0;
    return 1;
}
static int full_search(const uint32_t w[4],const char *name,int synthetic,uint32_t expected) {
    int count=0,planted=0;
    double start=omp_get_wtime();
    #pragma omp parallel for reduction(+:count) reduction(|:planted) schedule(static)
    for(uint64_t i=0;i<(UINT64_C(1)<<32);i++) {
        uint32_t c=(uint32_t)i;
        if(fourth(c,w[0],w[1],w[2])!=w[3]) continue;
        State s=invert(c,w[0],w[1],w[2]);
        if(!replays(s,w)) continue;
        count++;
        if(synthetic && c==expected) planted=1;
        #pragma omp critical
        printf("PREIMAGE %s %08" PRIX32 " : %08" PRIX32 ",%08" PRIX32 ",%08" PRIX32 ",%08" PRIX32 "\n",
            name,c,s.a,s.b,s.c,s.d);
    }
    printf("COMPLETE %s examined=4294967296 preimages=%d planted=%d seconds=%.3f\n",
        name,count,planted,omp_get_wtime()-start);
    fflush(stdout);
    if(synthetic && !planted) exit(3);
    return count;
}
static void load_source(unsigned char out[4][16],const char *file) {
    FILE *fp=fopen(file,"rb");
    if(!fp) { perror(file); exit(2); }
    if(fseek(fp,0,SEEK_END)!=0) exit(2);
    long len=ftell(fp); rewind(fp);
    if(len<=0 || len>1000000) exit(2);
    char *buf=malloc((size_t)len+1);
    if(!buf || fread(buf,1,(size_t)len,fp)!=(size_t)len) exit(2);
    fclose(fp);buf[len]=0;
    unsigned char md[32]; unsigned int mlen=0; char digest[65];
    if(!EVP_Digest(buf,(size_t)len,md,&mlen,EVP_sha256(),NULL)||mlen!=32) exit(2);
    for(int i=0;i<32;i++) sprintf(digest+2*i,"%02x",md[i]);
    if(strcmp(digest,SOURCE_SHA)) { fprintf(stderr,"Source SHA mismatch %s\n",digest);exit(2); }
    unsigned n=0;
    for(char *p=buf;*p && n<4;) {
        char *e=strchr(p,'\n');if(e)*e=0;
        if(strncmp(p,"2026-10-03T07:",14)==0 && strstr(p," STATE=ACK ") && strstr(p," ATTEMPT=1 ")) {
            char *v=strstr(p," PAYLOAD=");if(!v)exit(2);v+=9;
            for(int k=0;k<16;k++) { unsigned a;
                if(sscanf(v+2*k,"%2x",&a)!=1) exit(2);
                out[n][k]=(unsigned char)a;
            }
            printf("SOURCE %u ",n);
            for(int k=0;k<16;k++) printf("%02X",out[n][k]);
            printf("\n");n++;
        }
        if(!e) break;
        p=e+1;
    }
    free(buf);
    if(n!=4) exit(2);
    printf("Original spool SHA256 %s PASS\n",digest);
}
static void words(const unsigned char bytes[16],int little,uint32_t out[4]) {
    for(int i=0;i<4;i++) { uint32_t v=0;
        for(int j=0;j<4;j++) v=(v<<8)|bytes[4*i+(little?3-j:j)];
        out[i]=v;
    }
}
int main(int argc,char **argv) {
    const char *path=argc>1?argv[1]:"resources/evidence/print/spool-reconstruction.log";
    unsigned char records[4][16];load_source(records,path);
    State seed={0xDEADBEEFu,0x3BADF00Du,0x12345678u,0x1337u},s=seed;
    uint32_t planted[4];
    for(int i=0;i<4;i++) planted[i]=next(&s);
    if(!replays(invert(seed.c,planted[0],planted[1],planted[2]),planted)) exit(3);
    full_search(planted,"planted",1,seed.c);
    int counts[4][2]={0};
    for(int i=0;i<4;i++) for(int endian=0;endian<2;endian++) {
        uint32_t w[4]; words(records[i],endian,w);
        char name[32];snprintf(name,sizeof(name),"row%d_%s",i,endian?"LE":"BE");
        counts[i][endian]=full_search(w,name,0,0);
    }
    for(int i=0;i<4;i++)
        printf("SUMMARY row%d BE=%d LE=%d\n",i,counts[i][0],counts[i][1]);
    if(counts[0][0]!=1 || counts[0][1]!=0 || counts[2][0]!=0 || counts[3][0]!=0) exit(4);
    puts("CONCLUSION: fixed BE and fixed LE fourword SFC32 each contradict at least one intact original row.");
    puts("Mixed per-record serializers remain hypothetical. No selected K04 material was recovered.");
    return 0;
}
