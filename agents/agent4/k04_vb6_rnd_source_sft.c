/* H-17 historical spool; source-only 24-bit Visual Basic Rnd LCG model.
 * Model constants: x[n+1]=(1140671485*x[n]+12820163) mod 2^24.
 * Run with spool source as argv[1]; original evidence remains read-only.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MASK 0xFFFFFFu
#define A 1140671485u
#define C 12820163u

static uint32_t advance(uint32_t state) { return (state*A+C)&MASK; }
static uint8_t output(uint32_t state, unsigned view) { return (uint8_t)(state >> (view*8)); }

static int matches(uint32_t start, const uint8_t *p, unsigned view, unsigned reverse) {
    uint32_t x=start;
    for(unsigned i=0;i<16;i++){
        if(output(x,view)!=p[reverse ? 15-i : i]) return 0;
        x=advance(x);
    }
    return 1;
}

static uint32_t full_scan(const uint8_t *p,unsigned view,unsigned reverse,uint32_t *hits){
    uint32_t survivors=0;*hits=0;
    uint8_t first=p[reverse?15:0];
    /* Exactly every 24-bit state with first output byte fixed. */
    for(uint32_t other=0;other<(1u<<16);other++){
        uint32_t state;
        if(view==0) state=(other<<8)|first;
        else if(view==1) state=((other>>8)<<16)|((uint32_t)first<<8)|(other&255u);
        else state=((uint32_t)first<<16)|other;
        if(output(advance(state),view)!=p[reverse?14:1]) continue;
        survivors++;
        if(matches(state,p,view,reverse)) (*hits)++;
    }
    return survivors;
}

static void packet24(uint32_t start,uint8_t *dst,unsigned view){
    uint32_t x=start;
    for(unsigned i=0;i<16;i++){dst[i]=output(x,view);x=advance(x);}
}

static unsigned scan_packed(const uint8_t *p,unsigned reverse,unsigned order){
    uint8_t a=p[reverse?15:0],b=p[reverse?14:1],c=p[reverse?13:2];
    uint32_t state=order==0?((uint32_t)a<<16)|((uint32_t)b<<8)|c:
                            ((uint32_t)c<<16)|((uint32_t)b<<8)|a;
    uint32_t x=state;
    for(unsigned i=0;i<16;i++){
        uint8_t value=order==0?(x>>(16-(i%3)*8))&255:(x>>((i%3)*8))&255;
        if(value!=p[reverse?15-i:i]) return 0;
        if(i%3==2) x=advance(x);
    }
    return 1;
}

int main(int argc,char **argv){
    if(argc!=2){fprintf(stderr,"Require original spool path\n");return 2;}
    FILE *file=fopen(argv[1],"rb");
    if(!file){perror("spool source");return 2;}
    char line[2048];uint8_t p[16];unsigned n=0;
    while(fgets(line,sizeof(line),file)){
        if(!strstr(line,"+00:00")) continue;
        char *s=strstr(line,"PAYLOAD=");if(!s)continue;s+=8;
        if(n==0) for(unsigned i=0;i<16;i++){
            unsigned k;char hx[3]={s[2*i],s[2*i+1],0};
            if(sscanf(hx,"%x",&k)!=1)return 2;p[i]=(uint8_t)k;
        }
        n++;
    }
    fclose(file);
    if(n!=128){fprintf(stderr,"Expected 128 ordinary source rows, got %u\n",n);return 2;}
    const uint32_t seeds[]={0,42,1234567,16777215,327680};
    for(unsigned k=0;k<5;k++)for(unsigned view=0;view<3;view++){
        uint8_t buf[16];uint32_t hits;packet24(seeds[k],buf,view);
        full_scan(buf,view,0,&hits);
        if(!hits||!matches(seeds[k],buf,view,0)){
            fprintf(stderr,"Planted validation failed seed %u view %u\n",seeds[k],view);return 1;
        }
    }
    puts("PLANTED 15/15 PASS");
    for(unsigned reverse=0;reverse<2;reverse++)for(unsigned view=0;view<3;view++){
        uint32_t hits=0;uint32_t survivors=full_scan(p,view,reverse,&hits);
        printf("ORIGINAL reverse=%u view=%u second-byte survivors=%u complete_matches=%u\n",
               reverse,view,survivors,hits);
    }
    for(unsigned reverse=0;reverse<2;reverse++)for(unsigned order=0;order<2;order++){
        printf("ORIGINAL packed-24 reverse=%u order=%u match=%u\n",
               reverse,order,scan_packed(p,reverse,order));
    }
    return 0;
}
