// Agent4: original H17 selected K04 packet via speculative earlier-state two-donor MT bridge.
// Corpus: run agents/agent11/build_donor_corpus.py original.zip corpus.tsv
// Build: g++ -O3 -std=c++20 -Wall k04_past_gap_two_donor.cpp -lcrypto -o past_gap
// Run: past_gap corpus.tsv
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <openssl/sha.h>
using U=uint32_t;
constexpr U Mag=0x9908b0df;
constexpr std::array<unsigned char,16> Mask={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
constexpr std::array<unsigned char,32> Target={0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
U temper(U x){x^=x>>11;x^=(x<<7)&0x9d2c5680;x^=(x<<15)&0xefc60000;x^=x>>18;return x;}
U untemper(U x){U y=x;for(int i=0;i<6;i++)y=x^(y>>18);x=y;for(int i=0;i<6;i++)y=x^((y<<15)&0xefc60000);x=y;for(int i=0;i<6;i++)y=x^((y<<7)&0x9d2c5680);x=y;for(int i=0;i<6;i++)y=x^(y>>11);return y;}
U word(const unsigned char* b,bool big){if(big)return(U(b[0])<<24)|(U(b[1])<<16)|(U(b[2])<<8)|U(b[3]);return(U(b[3])<<24)|(U(b[2])<<16)|(U(b[1])<<8)|U(b[0]);}
void store(U x,unsigned char*out){for(int j=0;j<4;j++)out[j]=static_cast<unsigned char>(x>>(8*j));}
U tw(U a,U b){U y=(a&0x80000000)|(b&0x7fffffff);return(y>>1)^((y&1)?Mag:0);}
using Block=std::array<U,4>;
struct Donor{std::string label;std::array<std::array<U,4>,4> states;};
Donor make(std::array<unsigned char,16> raw,std::string label){Donor d;d.label=label;for(int e=0;e<2;e++)for(int mode=0;mode<2;mode++)for(int k=0;k<4;k++){U v=word(raw.data()+4*k,e);d.states[2*e+mode][k]=(mode==0)?untemper(v):v;}return d;}
void infer(const Block&a,const Block&b,U missingHigh,Block&out){out[0]=b[0]^tw(missingHigh,a[0]);for(int k=1;k<4;k++)out[k]=b[k]^tw(a[k-1],a[k]);}
void synthetic(){std::mt19937 mt(20261103);std::array<U,1600> q;for(auto&v:q)v=mt();Block a,b,x,y;for(int i=0;i<4;i++){a[i]=untemper(q[328+i]);b[i]=untemper(q[724+i]);}bool match=false;for(int bit=0;bit<2;bit++){infer(a,b,U(bit)<<31,x);bool good=true;for(int i=0;i<4;i++){y[i]=untemper(q[951+i]);if(x[i]!=y[i])good=false;}if(good)match=true;}if(!match){std::cerr<<"MT seeded positive control failed\n";std::exit(3);}std::cout<<"SYNTHETIC_MT_PAST_GAP_TWO_DONOR_PASS\n";}
int main(int argc,char**argv){if(argc!=2){std::cerr<<"usage: compiled test donor.tsv\n";return 2;}synthetic();std::ifstream in(argv[1]);if(!in)return 2;std::vector<Donor>d;std::string line;while(std::getline(in,line)){if(line.size()<33)continue;std::array<unsigned char,16> raw{};for(int k=0;k<16;k++)raw[k]=static_cast<unsigned char>(std::stoul(line.substr(2*k,2),nullptr,16));d.push_back(make(raw,line.substr(33)));}if(d.size()!=533)return 3;unsigned long long count=0,hits=0;for(size_t i=0;i<d.size();i++)for(size_t j=0;j<d.size();j++)for(int e=0;e<4;e++)for(int f=0;f<4;f++)for(int bit=0;bit<2;bit++){Block x;infer(d[i].states[e],d[j].states[f],U(bit)<<31,x);unsigned char payload[16],digest[32];for(int k=0;k<4;k++)store(temper(x[k]),payload+4*k);for(int k=0;k<16;k++)payload[k]^=Mask[k];SHA256(payload,16,digest);if(!std::memcmp(digest,Target.data(),32)){hits++;std::cout<<"MATCH i="<<i<<" j="<<j<<" e="<<e<<" f="<<f<<" high="<<bit<<" A="<<d[i].label<<" B="<<d[j].label<<" payload=";for(auto c:payload)printf("%02X",c);std::cout<<"\n";}count++;}
std::cout<<"COMPLETE donors="<<d.size()<<" candidate_checks="<<count<<" original_sha256_hits="<<hits<<"\n";return hits?0:1;}
