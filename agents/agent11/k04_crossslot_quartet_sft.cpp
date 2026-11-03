#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
using B16=std::array<unsigned char,16>;
using B32=std::array<unsigned char,32>;
static B16 decode(const char* hex){B16 a{}; for(int i=0;i<16;i++){unsigned k=0;std::sscanf(hex+2*i,"%2x",&k);a[i]=(unsigned char)k;}return a;}
static B32 decode32(const char* hex){B32 a{};for(int i=0;i<32;i++){unsigned k=0;std::sscanf(hex+2*i,"%2x",&k);a[i]=(unsigned char)k;}return a;}
static constexpr int SOURCE_COUNT=9,LANES=4,REVERSE=2,OPTS=SOURCE_COUNT*LANES*REVERSE;
int main(){
 const std::array<B16,SOURCE_COUNT> src{
 decode("049AAB2E1CDE7A82CD7C60234303C91A"),
 decode("0D7E3AB56FB75DA3EB0E2E06786D239E"),
 decode("1384AF96E25D6ADA666209CB55E062FA"),
 decode("FF8B78200A56E8586DCDA00EF01E4572"),
 decode("5DBF40EE52FAAED9A536D3326CF0D95A"),
 decode("93495F5E425AB8E592123DABAEB68545"),
 decode("E1A5E474BAD7E853A2E8C71D3317D507"),
 decode("D7DAD6BC9714519B7DAD0AD4BE8E87FD"),
 decode("8947CEDCB9CC73BAB7E87BE63302C5C9")};
 const B16 mask=decode("8556C8CB6140A7F9A5123AC7571BEE1C");
 const B32 target=decode32("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
 std::array<std::array<unsigned char,4>,OPTS> opts{};
 for(int s=0;s<SOURCE_COUNT;s++)for(int w=0;w<LANES;w++)for(int r=0;r<REVERSE;r++){
   const int id=(s*LANES+w)*REVERSE+r;
   for(int b=0;b<4;b++)opts[id][b]=src[s][4*w+(r?3-b:b)];
 }
 const int planted[]{10,32,52,70};
 B16 synthetic{};for(int k=0;k<4;k++)for(int b=0;b<4;b++)synthetic[4*k+b]=opts[planted[k]][b]^mask[4*k+b];
 B32 synthSHA{};SHA256(synthetic.data(),16,synthSHA.data());
 uint64_t checked=0, hits=0, positive=0;B16 buffer{}, masked{}; B32 dig{};
 for(int a=0;a<OPTS;a++){
  for(int i=0;i<4;i++)buffer[i]=opts[a][i];
  for(int b=0;b<OPTS;b++){
   for(int i=0;i<4;i++)buffer[4+i]=opts[b][i];
   for(int c=0;c<OPTS;c++){
    for(int i=0;i<4;i++)buffer[8+i]=opts[c][i];
    for(int d=0;d<OPTS;d++){
     for(int i=0;i<4;i++)buffer[12+i]=opts[d][i];
     SHA256(buffer.data(),16,dig.data());
     hits+=std::equal(dig.begin(),dig.end(),target.begin());
     for(int i=0;i<16;i++)masked[i]=buffer[i]^mask[i];
     SHA256(masked.data(),16,dig.data());
     hits+=std::equal(dig.begin(),dig.end(),target.begin());
     positive+=std::equal(dig.begin(),dig.end(),synthSHA.begin());
     checked+=2;
    }
   }
  }
 }
 std::cout<<"Complete assignments: "<<checked<<" accepted K04: "<<hits<<" planted matched: "<<positive<<"\n";
 return checked==53747712ULL&&positive==1?0:1;
}
