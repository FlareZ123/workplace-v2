// Original-source K04 spool emitter test: historical Windows CRT 15-bit rand family.
// Source controls are the intact 07:00, 07:05 and 07:10 original print packets.
// These are held-out original records, never selected disputed ACK2 bytes.
// Copyright-free local reproducibility example; not a claim about actual printer firmware.
#include <array>
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

using Packet = std::array<uint8_t,16>;
static uint32_t step(uint32_t s) { return s*214013u+2531011u; }
static uint8_t emit(uint32_t s,int shift){ return static_cast<uint8_t>((s>>(16+shift))&255u); }
static Packet layout(Packet p,bool reverseWords,bool reverseBytes){
    if(reverseWords)for(int i=0;i<2;i++)for(int b=0;b<4;b++)
        std::swap(p[4*i+b],p[4*(3-i)+b]);
    if(reverseBytes)for(int i=0;i<16;i+=4)
        std::reverse(p.begin()+i,p.begin()+i+4);
    return p;
}
static Packet unhex(const std::string& s){
    assert(s.size()==32); Packet p{};
    for(int i=0;i<16;i++)p[i]=static_cast<uint8_t>(std::stoul(s.substr(i*2,2),nullptr,16));
    return p;
}
static std::pair<uint64_t,uint32_t> recover(const Packet& p,int shift){
    uint64_t found=0;uint32_t recovered=0;
    const unsigned lo=16+static_cast<unsigned>(shift);
    // p[0] gives bits lo..lo+7 of state x1; all 24 unknown bits enumerated.
    for(uint32_t t=0;t<(1u<<24);t++){
        uint32_t x=((t>>lo)<<(lo+8))|(uint32_t(p[0])<<lo)|(t&((1u<<lo)-1u));
        uint32_t y=x;int j=1;
        for(;j<16;j++){y=step(y);if(emit(y,shift)!=p[j])break;}
        if(j==16){++found;recovered=x;}
    }
    return {found,recovered};
}
static Packet make(uint32_t seed,int shift){
    Packet p{};for(auto& b:p){seed=step(seed);b=emit(seed,shift);}return p;
}
int main(){
    // Every true synthetic state recovers; high state bits are unobserved,
    // hence 2^(8-shift) equivalent recovered x1 values.
    for(int shift=0;shift<8;shift++)for(uint32_t seed:{1u,1792u,0x89ABCDEFu}){
        Packet p=make(seed,shift);auto [cnt,x]=recover(p,shift);
        assert(cnt==(1u<<(8-shift)));
        for(uint8_t b:p){assert(emit(x,shift)==b);x=step(x);}
    }
    const std::vector<std::string> original={
        "FBBBC54356483F5864BB3F06794518A5", // 07:00 job0300
        "64176B6C3A91BD06B12FC0D90B3A7DB4", // 07:05 job0301
        "3531D8AB362BB040E7702CE23A8D5420"  // 07:10 job0302
    };
    uint64_t models=0,hits=0;
    for(int i=0;i<3;i++)for(int shift=0;shift<8;shift++)
        for(bool reverseWords:{false,true})for(bool reverseBytes:{false,true}){
            Packet p=layout(unhex(original[i]),reverseWords,reverseBytes);
            auto [n,x]=recover(p,shift);(void)x;models++;hits+=n;
            std::printf("control=%d shift=%d reverse_words=%d reverse_bytes=%d complete_states=%llu\n",
                i,shift,int(reverseWords),int(reverseBytes),(unsigned long long)n);
        }
    std::printf("SUMMARY complete_source_models=%llu original_matches=%llu planted_controls=24\n",
        (unsigned long long)models,(unsigned long long)hits);
    assert(models==96&&hits==0);
}