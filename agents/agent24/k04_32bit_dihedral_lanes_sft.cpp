// H-17 K04 independent 32-bit-lane cyclic bit-shift model, read-only original acceptance.
// Each 32-bit lane is independently rotated (32 shifts) or bit-reflected then rotated (32 more).
// Six families: dihedral word symmetries on PAYLOAD, MASK, or COMPONENT, in BE/LE views.
// C++17 / OpenSSL libcrypto; original and planted 16-byte SHA256 slot checks.
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <stdexcept>
using namespace std;
using Block=array<uint8_t,16>;
const Block payload={0xA9,0xA9,0xDC,0x57,0x31,0xA5,0xE2,0xAE,0x87,0x9C,0x47,0x21,0x5C,0x25,0x59,0xD5};
const Block mask={0x85,0x56,0xC8,0xCB,0x61,0x40,0xA7,0xF9,0xA5,0x12,0x3A,0xC7,0x57,0x1B,0xEE,0x1C};
const array<uint8_t,32> want={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
uint32_t rd32(const Block &b,int k,bool little){uint32_t x=0;for(int i=0;i<4;i++)x=(x<<8)|b[k*4+(little?3-i:i)];return x;}
void put32(Block &b,int k,uint32_t x,bool little){for(int i=0;i<4;i++){b[k*4+(little?i:3-i)]=uint8_t(x);x>>=8;}}
uint32_t rotate32(uint32_t x,unsigned n){return n?((x<<n)|(x>>(32-n))):x;}
uint32_t reverse32(uint32_t x){x=((x&0x55555555u)<<1)|((x>>1)&0x55555555u);x=((x&0x33333333u)<<2)|((x>>2)&0x33333333u);x=((x&0x0f0f0f0fu)<<4)|((x>>4)&0x0f0f0f0fu);x=((x&0x00ff00ffu)<<8)|((x>>8)&0x00ff00ffu);return(x<<16)|(x>>16);}
Block mix(Block const&p,Block const&m){Block b;for(int i=0;i<16;i++)b[i]=p[i]^m[i];return b;}
Block lane_shift(Block const&source,bool little, array<unsigned,4> const&steps){Block b{};for(int k=0;k<4;k++)put32(b,k,rotate32((steps[k]&32)?reverse32(rd32(source,k,little)):rd32(source,k,little),steps[k]&31),little);return b;}
Block result_for(int mode,bool little,array<unsigned,4> const&steps){if(mode==0)return mix(lane_shift(payload,little,steps),mask);if(mode==1)return mix(payload,lane_shift(mask,little,steps));return lane_shift(mix(payload,mask),little,steps);}
array<uint8_t,32> digest(Block const& b){array<uint8_t,32> h{};SHA256(b.data(),b.size(),h.data());return h;}
string ashex(Block const&b){static const char* h="0123456789ABCDEF";string s;for(auto v:b){s+=h[v>>4];s+=h[v&15];}return s;}
int main(){
    if(ashex(mix(payload,mask))!="2CFF149C50E54557228E7DE60B3EB7C9")throw runtime_error("Baseline mismatch");
    const array<unsigned,4> planted={35,7,43,19};
    for(bool little:{true,false})for(int mode=0;mode<3;mode++){
        auto artificial=digest(result_for(mode,little,planted));
        uint64_t originalHits=0,positiveHits=0,checks=0;
        for(unsigned a=0;a<64;a++)for(unsigned b=0;b<64;b++)for(unsigned c=0;c<64;c++)for(unsigned d=0;d<64;d++){
            Block v=result_for(mode,little,{a,b,c,d});auto h=digest(v);checks++;
            if(h==artificial)positiveHits++;
            if(h==want){originalHits++;cerr<<"ORIGINAL_MATCH "<<ashex(v)<<"\n";}
        }
        if(checks!=16777216 || positiveHits!=1)throw runtime_error("Incomplete sweep or failed synthetic unique control");
        cout<<"MODE="<<(mode==0?"PAYLOAD":mode==1?"MASK":"COMPONENT")<<" WORD_ENDIAN="<<(little?"LE":"BE")<<" checked="<<checks<<" synthetic_positive="<<positiveHits<<" original_hits="<<originalHits<<"\n";
        if(originalHits) return 1;
    }
}
