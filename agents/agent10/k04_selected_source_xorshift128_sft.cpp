#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <algorithm>
using U = uint32_t;
using State = std::array<U,4>;
using Bytes = std::array<unsigned char,16>;
static inline U undo_r(U v,int n) { U x=v; for(int k=n;k<32;k*=2)x^=(x>>k);return x; }
static inline U undo_l(U v,int n) { U x=v;for(int k=n;k<32;k*=2)x^=(x<<k);return x; }
static State next(State s){U t=s[0]^(s[0]<<11);return {s[1],s[2],s[3],s[3]^(s[3]>>19)^t^(t>>8)};}
static State prev(State s){U ow=s[2], rhs=s[3]^ow^(ow>>19), t=undo_r(rhs,8), ox=undo_l(t,11);return {ox,s[0],s[1],ow};}
static Bytes fromHex(const char* h){Bytes a{}; for(int i=0;i<16;++i){ unsigned v;sscanf(h+2*i,"%2x",&v);a[i]=(unsigned char)v;}return a;}
static State fromBlock(const Bytes& a,int view){State s{};for(int w=0;w<4;++w){int which=view&1?3-w:w;for(int k=0;k<4;++k){int q=view&2?3-k:k;s[w]|=U(a[4*which+q])<<(8*k);}}return s;}
static Bytes toBlock(const State& s,int view){Bytes a{};for(int w=0;w<4;++w){int which=view&1?3-w:w;for(int k=0;k<4;++k){int q=view&2?3-k:k;a[4*which+q]=(s[w]>>(8*k))&255;}}return a;}
static const char* names[]={"K01 signed ink","K02 selected prehash","K05 signed recorder","K06 issued strips","K07 selected prehash"};
static const char* sources[]={"049AAB2E1CDE7A82CD7C60234303C91A","E1A5E474BAD7E853A2E8C71D3317D507","FF8B78200A56E8586DCDA00EF01E4572","5DBF40EE52FAAED9A536D3326CF0D95A","8947CEDCB9CC73BAB7E87BE63302C5C9"};
static constexpr int LIMIT=200000;
static void shaPin(const std::string& path,const char* expected){
 FILE* f=fopen(path.c_str(),"rb");if(!f)throw std::runtime_error("cannot open original "+path);
 SHA256_CTX ctx;SHA256_Init(&ctx);unsigned char buf[32768];size_t n;
 while((n=fread(buf,1,sizeof(buf),f))>0)SHA256_Update(&ctx,buf,n);
 fclose(f);unsigned char d[32];SHA256_Final(d,&ctx);
 char hex[65];for(int i=0;i<32;i++)sprintf(hex+2*i,"%02x",d[i]);hex[64]=0;
 if(strcmp(hex,expected))throw std::runtime_error("original SHA256 pin mismatch: "+path);
}
static bool hasDigest(const Bytes& packet,const Bytes& mask,const unsigned char* goal){
 unsigned char data[16],digest[32];for(int i=0;i<16;i++)data[i]=packet[i]^mask[i];
 SHA256(data,16,digest);return memcmp(goal,digest,32)==0;
}
int main(int argc,char** argv){
 if(argc!=2){fprintf(stderr,"USAGE: ./k04_selected_xorshift_sft /path/to/extracted-original-resources\n");return 2;}
 std::string root=argv[1];
 const std::pair<const char*,const char*> pins[]={
 {"evidence/mail/03.eml","3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889"},
 {"evidence/telemetry/freeze-export.jsonl","3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"},
 {"evidence/recorder/trip-recorder.raw","5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"},
 {"evidence/procedures/RC-17-scans.txt","a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"},
 {"evidence/transfers/transfer-audit.jsonl","32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"},
 {"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}};
 try{for(const auto& pin:pins)shaPin(root+"/"+pin.first,pin.second);}catch(const std::exception& ex){fprintf(stderr,"SOURCE_FAIL %s\n",ex.what());return 2;}
 fprintf(stderr,"ORIGINAL_SOURCE_PINS_PASS files=%zu\n",sizeof(pins)/sizeof(pins[0]));
 auto m=fromHex("8556C8CB6140A7F9A5123AC7571BEE1C");
 const unsigned char commitment[32]={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
 std::array<Bytes,5> blocks{};for(int i=0;i<5;i++)blocks[i]=fromHex(sources[i]);
 State t={0x12345678u,0x87654321u,0xaabbccddu,0x0f1e2d3cu};for(int j=0;j<1000;j++){auto n=next(t);if(prev(n)!=t||next(prev(t))!=t){fprintf(stderr,"inverse mismatch %d\n",j);return 2;}t=n;}
 for(int view=0;view<4;view++)if(fromBlock(toBlock(t,view),view)!=t){fprintf(stderr,"serializer failed\n");return 2;}
 fprintf(stderr,"SYNTHETIC_INVERSION_PASS 1000 state round trips all4 serializers\n");
 State seed={0x941ac589u,0xd7b0c451u,0x8fe116b2u,0x9071436bu};
 Bytes plantedAnchor=toBlock(seed,1),plantedHoldout{};
 State cur=seed;for(int i=1;i<=137;i++){cur=next(cur);if(i==57)plantedHoldout=toBlock(cur,3);}
 Bytes plantedTargetPacket=toBlock(cur,2);
 unsigned char plantedTargetDigest[32];
 {unsigned char v[16];for(int i=0;i<16;i++)v[i]=plantedTargetPacket[i]^m[i];SHA256(v,16,plantedTargetDigest);}
 bool targetPositive=false,holdoutPositive=false;
 for(int view=0;view<4;view++)for(int dir:{1,-1}){
  State test=fromBlock(plantedAnchor,view);
  for(int off=1;off<=250;off++){
   test=dir>0?next(test):prev(test);
   for(int outview=0;outview<4;outview++){
    Bytes packet=toBlock(test,outview);
    if(packet==plantedHoldout)holdoutPositive=true;
    if(hasDigest(packet,m,plantedTargetDigest))targetPositive=true;
   }
  }
 }
 if(!targetPositive||!holdoutPositive){fprintf(stderr,"SYNTHETIC_COMPLETE_COUPON_OR_HOLDOUT_FAILED\n");return 2;}
 fprintf(stderr,"SYNTHETIC_COMPLETE_COUPON_PASS offset=137 positive_holdout=57\n");
 unsigned char digest[32],candidate[16];unsigned long long checked=0,overlaps=0;
 for(int anchor=0;anchor<5;anchor++)for(int view=0;view<4;view++)for(int direction:{1,-1}){
  State s=fromBlock(blocks[anchor],view);
  for(int offset=1;offset<=LIMIT;offset++){
   s=direction>0?next(s):prev(s);
   for(int hold=0;hold<5;hold++)if(hold!=anchor)for(int holdview=0;holdview<4;holdview++){
    if(toBlock(s,holdview)==blocks[hold]){overlaps++;fprintf(stderr,"CONTROL_LINK anchor=%s view=%d dir=%d step=%d heldout=%s view=%d\n",names[anchor],view,direction,offset,names[hold],holdview);}
   }
   for(int outview=0;outview<4;outview++){
    auto packet=toBlock(s,outview);for(int j=0;j<16;j++)candidate[j]=packet[j]^m[j];
    SHA256(candidate,16,digest);checked++;
    if(memcmp(digest,commitment,32)==0){fprintf(stderr,"FOUND_K04 anchor=%s view=%d dir=%d step=%d outview=%d coupon=",names[anchor],view,direction,offset,outview);for(auto x:packet)fprintf(stderr,"%02X",x);fprintf(stderr,"\n");return 0;}
   }
  }
  fprintf(stderr,"ANCHOR_DONE %s view=%d direction=%+d checked=%llu holdouts=%llu\n",names[anchor],view,direction,checked,overlaps);
 }
 printf("ORIGINAL_NO_MATCH complete_sha256_checks=%llu original_source_holdouts=%llu source_anchors=5 views=4 directions=2 offsets=1..%d\n",checked,overlaps,LIMIT);
 return 0;
}
