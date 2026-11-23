/* K04: 65k complete contiguous whole-coupon SHA256 checks from exact state.
 * Two native 128-bit xorshift transitions (v8/vigna) and seven invertible
 * 64-bit emitter functions. The physical original source is never modified.
 *
 * Args: variant f|b stateL stateR perm4 big|little mask32 sha64 emit_mode
 * Requires OpenSSL/libcrypto. No decoder truncates original 16-byte coupons.
 */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#define M1 UINT64_C(0x9E3779B97F4A7C13)
#define M2 UINT64_C(0x2545F4914F6CDD1D)
static void step(uint64_t *l,uint64_t *r,unsigned s,unsigned t){
    uint64_t x=*l;x^=x<<23;x^=x>>s;x^=*r;x^=*r>>t;*l=*r;*r=x;
}
static void back(uint64_t *l,uint64_t *r,unsigned s,unsigned t){
    uint64_t b=*l,u=*r^b^(b>>t),v=u;
    for(unsigned k=s;k<64;k*=2)v^=v>>k;
    *l=v^(v<<23)^(v<<46);*r=b;
}
static uint64_t out(uint64_t l,uint64_t r,const char *mode){
    if(strcmp(mode,"L")==0)return l;
    if(strcmp(mode,"R")==0)return r;
    if(strcmp(mode,"X")==0)return l^r;
    if(strcmp(mode,"LmulM1")==0)return l*M1;
    if(strcmp(mode,"RmulM1")==0)return r*M1;
    if(strcmp(mode,"LmulM2")==0)return l*M2;
    if(strcmp(mode,"RmulM2")==0)return r*M2;
    fprintf(stderr,"invalid mode\n");exit(2);
}
static unsigned nib(char c){
    if(c>='0'&&c<='9')return c-'0';
    if(c>='a'&&c<='f')return c-'a'+10;
    if(c>='A'&&c<='F')return c-'A'+10;
    fprintf(stderr,"invalid hex digit\n");exit(2);
}
static void hexbytes(const char *src,unsigned char *out,size_t n){
    if(strlen(src)!=2*n){fprintf(stderr,"bad hex length\n");exit(2);}
    for(size_t i=0;i<n;i++)out[i]=(nib(src[2*i])<<4)|nib(src[2*i+1]);
}
static void serialize(uint64_t y0,uint64_t y1,const unsigned char p[4],int little,unsigned char b[16]){
    uint32_t w[4]={(uint32_t)(y0>>32),(uint32_t)y0,(uint32_t)(y1>>32),(uint32_t)y1};
    for(int i=0;i<4;i++)for(int j=0;j<4;j++)
        b[p[i]*4+j]=(unsigned char)(w[i]>>(little?8*j:8*(3-j)));
}
int main(int argc,char **argv){
    if(argc!=10){fprintf(stderr,"usage variant direction L R perm4 big|little mask32 sha64 emit_mode\n");return 2;}
    unsigned s,t;
    if(strcmp(argv[1],"v8")==0){s=17;t=26;}
    else if(strcmp(argv[1],"vigna")==0){s=18;t=5;}
    else return 2;
    int f=strcmp(argv[2],"f")==0;
    if(!f&&strcmp(argv[2],"b")!=0)return 2;
    uint64_t l=strtoull(argv[3],NULL,16),r=strtoull(argv[4],NULL,16);
    if(strlen(argv[5])!=4)return 2;
    unsigned char p[4]={0},seen=0;
    for(int i=0;i<4;i++){
        if(argv[5][i]<'0'||argv[5][i]>'3')return 2;
        p[i]=(unsigned char)(argv[5][i]-'0');
        if(seen&(1u<<p[i]))return 2;
        seen|=(unsigned char)(1u<<p[i]);
    }
    int little=strcmp(argv[6],"little")==0;
    if(!little&&strcmp(argv[6],"big")!=0)return 2;
    const char *mode=argv[9];(void)out(l,r,mode);
    unsigned char mask[16],want[32],coupon[16],component[16],digest[32];
    hexbytes(argv[7],mask,16);hexbytes(argv[8],want,32);
    uint64_t older=0,recent=0;
    if(f){step(&l,&r,s,t);step(&l,&r,s,t);older=out(l,r,mode);}
    else{back(&l,&r,s,t);recent=out(l,r,mode);
         back(&l,&r,s,t);older=out(l,r,mode);}
    int hits=0,n=f?65533:65535;
    for(int i=0;i<n;i++){
        if(f){step(&l,&r,s,t);recent=out(l,r,mode);}
        serialize(older,recent,p,little,coupon);
        for(int j=0;j<16;j++)component[j]=coupon[j]^mask[j];
        SHA256(component,16,digest);
        if(memcmp(digest,want,32)==0){
            hits++;
            printf("HIT variant=%s dir=%c mode=%s index=%d coupon=",argv[1],f?'f':'b',mode,i+2);
            for(int j=0;j<16;j++)printf("%02X",coupon[j]);
            printf(" component=");for(int j=0;j<16;j++)printf("%02X",component[j]);
            printf("\n");
        }
        if(f)older=recent;
        else{recent=older;back(&l,&r,s,t);older=out(l,r,mode);}
    }
    printf("SUMMARY checked=%d hits=%d variant=%s direction=%c mode=%s\n",n,hits,argv[1],f?'f':'b',mode);
    return 0;
}
