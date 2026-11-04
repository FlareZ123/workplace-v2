#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <openssl/sha.h>

using Block = std::array<unsigned char,16>;
static Block hexblock(const std::string &s){
    if(s.size()!=32) throw std::runtime_error("expected 32 hex digits");
    Block b{};
    for(int i=0;i<16;i++) b[i]=static_cast<unsigned char>(std::stoi(s.substr(2*i,2),nullptr,16));
    return b;
}
static std::string hex32(const unsigned char *p, int n){
    std::ostringstream out; out<<std::hex<<std::setfill('0');
    for(int i=0;i<n;i++) out<<std::setw(2)<<static_cast<int>(p[i]);
    return out.str();
}
static unsigned char gf8(unsigned char a,unsigned char b){
    unsigned char r=0;
    for(int k=0;k<8;k++){if(b&1)r^=a;bool hi=a&128;a<<=1;if(hi)a^=0x1b;b>>=1;}
    return r;
}
static unsigned char rot8(unsigned char a, int b){b&=7;return static_cast<unsigned char>((a<<b)|(a>>((8-b)&7)));}
static Block decode(Block p,int mode,int a,int b,int reverse,int lag,int previous,int initial){
    Block q{};
    for(int step=0;step<16;step++){
        int pos=reverse?15-step:step;
        int prior=pos+(reverse?lag:-lag);
        unsigned char v = prior>=0&&prior<16 ? (previous?q[prior]:p[prior]) :
                          initial==0?0:initial==1?p[reverse?15:0]:initial==2?p[reverse?0:15]:0xA9;
        unsigned char f = mode<2?static_cast<unsigned char>(a*v+b):
                          mode<4?static_cast<unsigned char>(rot8(v,a)+b):
                          static_cast<unsigned char>(gf8(v,static_cast<unsigned char>(a))+b);
        q[pos]= (mode%2==0)?static_cast<unsigned char>(p[pos]^f):static_cast<unsigned char>(p[pos]-f);
    }
    return q;
}
static Block xorblock(Block a,Block b){for(int i=0;i<16;i++)a[i]^=b[i];return a;}
static bool digest_equals(Block x,const unsigned char* sha){unsigned char got[SHA256_DIGEST_LENGTH]; SHA256(x.data(),16,got);return !std::memcmp(got,sha,32);}
int main(int argc,char** argv){
    if(argc!=2)throw std::runtime_error("provide original spool file path");
    std::ifstream file(argv[1],std::ios::binary);
    if(!file)throw std::runtime_error("missing spool source");
    std::string raw((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());
    unsigned char sourceSha[32];SHA256(reinterpret_cast<const unsigned char*>(raw.data()),raw.size(),sourceSha);
    if(hex32(sourceSha,32)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083") throw std::runtime_error("spool SHA mismatch");
    std::string marker="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=";
    size_t found=raw.find(marker);
    if(found==std::string::npos || raw.find(marker,found+1)!=std::string::npos)throw std::runtime_error("selected ACK not unique");
    Block p=hexblock(raw.substr(found+marker.size(),32));
    Block m=hexblock("8556C8CB6140A7F9A5123AC7571BEE1C");
    unsigned char target[32];
    auto targetBytes=[](const std::string &s){std::array<unsigned char,32> x{};for(int i=0;i<32;i++)x[i]=static_cast<unsigned char>(std::stoi(s.substr(2*i,2),nullptr,16));return x;};
    auto targetArr=targetBytes("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
    std::memcpy(target,targetArr.data(),32);
    Block plantedQ=decode(p,5,41,87,1,2,1,3);
    Block plantedC=xorblock(plantedQ,m);
    unsigned char synthetic[32];SHA256(plantedC.data(),16,synthetic);
    uint64_t original=0,synthetic_hits=0,checks=0;
    for(int stage=0;stage<2;stage++){
        Block input=stage?xorblock(p,m):p;
        for(int mode=0;mode<6;mode++)for(int reverse=0;reverse<2;reverse++)for(int lag:{1,2,4})for(int previous=0;previous<2;previous++)for(int initial=0;initial<4;initial++)for(int a=0;a<(mode>=2&&mode<4?8:256);a++){
                int aa=a;
                for(int b=0;b<256;b++){
                    Block q=decode(input,mode,aa,b,reverse,lag,previous,initial);
                    Block c=stage?q:xorblock(q,m);
                    original+=digest_equals(c,target);
                    synthetic_hits+=digest_equals(c,synthetic);
                    checks++;
                    if(original)std::cout<<"FOUND "<<hex32(c.data(),16)<<" mode="<<mode<<" reverse="<<reverse<<" lag="<<lag<<" previous="<<previous<<" iv="<<initial<<" a="<<aa<<" b="<<b<<" stage="<<stage<<'\n';
                }
        }
    }
    if(!synthetic_hits)throw std::runtime_error("planted positive not found");
    std::cout<<"spool_sha256="<<hex32(sourceSha,32)<<"\nselected_copied_ack="<<hex32(p.data(),16)<<"\n";
    std::cout<<"tested_assignments="<<checks<<" original_matches="<<original<<" synthetic_positive_hits="<<synthetic_hits<<"\n";
}
