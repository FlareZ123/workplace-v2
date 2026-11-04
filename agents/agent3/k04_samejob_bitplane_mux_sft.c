/* H-17 source-pinned three genuine preserved 0417 bitplane multiplexer,
 * with independent whole-word permutation / within-word byte reversal /
 * global bit reversal. Build in the same directory as bitplane affine SFT.
 * The original selected ACK2 copy is not a donor.
 */
#define main unused_affine_main
#include "k04_bitplane_affine_sft.c"
#undef main
static void mux(int code,uint8_t out[16]){
 uint8_t sel[8];for(int j=0;j<8;j++){sel[j]=code%3;code/=3;}
 memset(out,0,16);
 for(int i=0;i<16;i++)for(int j=0;j<8;j++)out[i]|=donor[sel[j]][i]&(1<<j);
}
static uint8_t reverse_bits(uint8_t x){
 x=(x>>4)|(x<<4);x=((x&0xcc)>>2)|((x&0x33)<<2);
 return ((x&0xaa)>>1)|((x&0x55)<<1);
}
static void layout(const uint8_t src[16],const int p[4],int endian,int reflect,uint8_t dst[16]){
 for(int i=0;i<16;i++){
  int j=p[i/4]*4 + ((endian>>(i/4)&1)?3-i%4:i%4);
  uint8_t x=reflect?reverse_bits(src[j]):src[j];
  dst[i]=x^mask[i];
 }
}
static int next_perm(int p[4]){
 int i=2;while(i>=0&&p[i]>=p[i+1])i--;if(i<0)return 0;
 int j=3;while(p[j]<=p[i])j--;
 int t=p[i];p[i]=p[j];p[j]=t;
 for(int a=i+1,b=3;a<b;a++,b--){t=p[a];p[a]=p[b];p[b]=t;}return 1;
}
int main(int argc,char **argv){
 if(argc!=2)die("usage: mux /path/to/resources");
 source(argv[1],"evidence/print/spool-reconstruction.log",
 "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",1);
 source(argv[1],"evidence/recovery-routing.json",
 "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",0);
 source(argv[1],"acceptance.json",
 "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",0);
 uint8_t b[16],out[16],hash[32],plant[32];
 mux(2026,b);layout(b,(int[4]){2,0,1,3},5,1,out);SHA256(out,16,plant);
 uint64_t checked=0;unsigned hits=0,synthetic=0;
 int p[4]={0,1,2,3},perms=0;
 do{
  perms++;
  for(int endian=0;endian<16;endian++)for(int reflect=0;reflect<2;reflect++)
  for(int code=0;code<6561;code++){
   mux(code,b);layout(b,p,endian,reflect,out);SHA256(out,16,hash);
   int original_ok=1;
   for(int k=0;k<8;k++)original_ok &= word(hash,k)==original[k];
   hits+=(unsigned)original_ok;
   synthetic+=(memcmp(hash,plant,32)==0);
   checked++;
  }
 }while(next_perm(p));
 printf("SHA_PINNED_ORIGINAL K04 source_mux_bitplane_assignments=%llu perms=%d original_hits=%u synthetic_full_hits=%u\n",
  (unsigned long long)checked,perms,hits,synthetic);
 return checked==5038848ULL&&perms==24&&!hits&&synthetic==1?0:1;
}
