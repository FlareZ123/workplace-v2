/* H17 xorshift128+ complete-coupon SHA256 scan.
 * Two source generator variants: v8 (23,17,26) and vigna (23,18,5).
 * Input is an independently inverted state after the first observed output.
 * Args: variant f|b stateL stateR perm4 big|little 16byte-mask 32byte-target-sha.
 * Verify all 65533 forward or 65535 reverse windows against the unchanged
 * K04 SHA256 commitment. Requires OpenSSL/libcrypto; original files read-only.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

static void step(uint64_t *l,uint64_t *r,unsigned right_a,unsigned right_b){
    uint64_t t=*l;
    t^=t<<23;
    t^=t>>right_a;
    t^=*r;
    t^=*r>>right_b;
    *l=*r; *r=t;
}
static void backward(uint64_t *l,uint64_t *r,unsigned right_a,unsigned right_b){
    uint64_t b=*l;
    uint64_t u=*r^b^(b>>right_b);
    uint64_t v=u;
    for(unsigned shift=right_a;shift<64;shift*=2)v^=v>>shift;
    uint64_t a=v^(v<<23)^(v<<46);
    *l=a;*r=b;
}
static unsigned nib(char c){
    if(c>='0'&&c<='9')return (unsigned)(c-'0');
    if(c>='a'&&c<='f')return (unsigned)(c-'a'+10);
    if(c>='A'&&c<='F')return (unsigned)(c-'A'+10);
    fprintf(stderr,"invalid hex digit\n");exit(2);
}
static void hexbytes(const char *src,unsigned char *out,size_t n){
    if(strlen(src)!=2*n){fprintf(stderr,"bad hex length\n");exit(2);}
    for(size_t i=0;i<n;i++)out[i]=(unsigned char)((nib(src[2*i])<<4)|nib(src[2*i+1]));
}
static void serialize(uint64_t y0,uint64_t y1,const unsigned char perm[4],int little,unsigned char out[16]){
    const uint32_t words[4]={(uint32_t)(y0>>32),(uint32_t)y0,(uint32_t)(y1>>32),(uint32_t)y1};
    for(int i=0;i<4;i++)for(int j=0;j<4;j++){
        unsigned shift=little?8*j:8*(3-j);
        out[perm[i]*4+j]=(unsigned char)(words[i]>>shift);
    }
}
int main(int argc,char **argv){
    if(argc!=9){fprintf(stderr,"usage variant f|b L R perm4 big|little mask32hex sha64hex\n");return 2;}
    unsigned right_a=0,right_b=0;
    if(strcmp(argv[1],"v8")==0){right_a=17;right_b=26;}
    else if(strcmp(argv[1],"vigna")==0){right_a=18;right_b=5;}
    else return 2;
    const int forward=strcmp(argv[2],"f")==0;
    if(!forward && strcmp(argv[2],"b")!=0)return 2;
    uint64_t l=strtoull(argv[3],NULL,16),r=strtoull(argv[4],NULL,16);
    int little=strcmp(argv[6],"little")==0;
    if(!little && strcmp(argv[6],"big")!=0)return 2;
    if(strlen(argv[5])!=4)return 2;
    unsigned char perm[4]={0},seen=0;
    for(int i=0;i<4;i++){
        if(argv[5][i]<'0'||argv[5][i]>'3')return 2;
        perm[i]=(unsigned char)(argv[5][i]-'0');
        if(seen&(1u<<perm[i]))return 2;
        seen|=(unsigned char)(1u<<perm[i]);
    }
    unsigned char mask[16],want[32],component[16],digest[32],coupon[16];
    hexbytes(argv[7],mask,16);hexbytes(argv[8],want,32);
    uint64_t recent=0,older=0;
    if(forward){step(&l,&r,right_a,right_b);step(&l,&r,right_a,right_b);older=l+r;}
    else {backward(&l,&r,right_a,right_b);recent=l+r;
          backward(&l,&r,right_a,right_b);older=l+r;}
    const int n=forward?65533:65535;
    int hits=0;
    for(int i=0;i<n;i++){
        if(forward){step(&l,&r,right_a,right_b);recent=l+r;}
        serialize(older,recent,perm,little,coupon);
        for(int j=0;j<16;j++)component[j]=coupon[j]^mask[j];
        SHA256(component,16,digest);
        if(memcmp(digest,want,32)==0){
            hits++;
            printf("HIT variant=%s direction=%c index=%d coupon=",argv[1],forward?'f':'b',i+2);
            for(int j=0;j<16;j++)printf("%02X",coupon[j]);
            printf(" component=");for(int j=0;j<16;j++)printf("%02X",component[j]);
            printf("\n");
        }
        if(forward)older=recent;
        else {recent=older;backward(&l,&r,right_a,right_b);older=l+r;}
    }
    printf("SUMMARY checked=%d hits=%d variant=%s direction=%c\n",n,hits,argv[1],forward?'f':'b');
    return 0;
}
