// Agent31 2026-11-23: N09 source-selected ordered-subsequence + two literal cue spans.
// This hypothesis follows the STOW14/N23->N09 locator, not the earlier N13 editor.
// Compile: g++ -O3 -std=c++17 k08_n09_source_editor.cpp -lcrypto -o k08_n09_source_editor
// Run: k08_n09_source_editor <original noticeboard-and-desk-notes.txt> <rewrite flag>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
#include <chrono>
#include <stdexcept>
using namespace std;
static const array<unsigned char,16> NONCE={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const array<unsigned char,32> TARGET={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static vector<string> CORE={"nobody","should","have","to","make","their","first","cup","alone","after","a","bad","night"};
static const vector<string> SEA={"the sea","the sea looks different","the water","water outside"};
static const vector<string> SOCIAL={"voices at the table","the voices at the table","people making room for each other","late crew making room for one another"};
static uint64_t count=0,orig_hits=0,plant_hits=0;
static string plant="the sea nobody should have to make their first cup alone after a bad night voices at the table";
static array<unsigned char,32> planted;
array<unsigned char,32> digest(const string &phrase) {
 unsigned char h[EVP_MAX_MD_SIZE];unsigned int l=0;array<unsigned char,32> d{};
 if(!HMAC(EVP_sha256(),NONCE.data(),NONCE.size(),(const unsigned char*)phrase.data(),phrase.size(),h,&l)||l!=32) throw runtime_error("HMAC failed");
 SHA256(h,16,d.data());return d;
}
static void check(const string &s) {
 auto d=digest(s);++count;
 if(d==TARGET){++orig_hits;cout<<"ORIGINAL_K08_HIT "<<s<<endl;}
 if(d==planted){++plant_hits;if(s!=plant)throw runtime_error("plant hash collision");}
}
int main(int argc,char**argv) {
 if(argc!=3) {cerr<<"Pass original note file and rewrite flag 0..15"<<endl;return 2;}
 int rewrite=stoi(argv[2]);if(rewrite<0||rewrite>15)throw runtime_error("Invalid rewrite flag");
 for(string &word:CORE) {
  if((rewrite&1)&&word=="first")word="last"; // N10: after the last cup
  if((rewrite&2)&&word=="bad")word="long"; // MAIL11: after a long watch
  if((rewrite&4)&&word=="night")word="watch"; // MAIL11: a long watch
  if((rewrite&8)&&word=="cup")word="mug"; // N11: chipped blue mug
 }
 plant="the sea";for(const string &word:CORE)plant+=" "+word;plant+=" voices at the table";
 ifstream f(argv[1],ios::binary);string original((istreambuf_iterator<char>(f)),{});
 unsigned char h[32];SHA256((const unsigned char*)original.data(),original.size(),h);
 const unsigned char sha[32]={0x13,0xf2,0x31,0x8c,0xcc,0x54,0xf3,0x5b,0x59,0x0a,0x2d,0x76,0xb3,0xa8,0x02,0x44,0xfe,0x24,0xd7,0x0f,0x06,0x99,0xc6,0x7c,0x05,0x85,0x8e,0x8b,0x89,0x83,0xc5,0xcb};
 if(!equal(h,h+32,sha))throw runtime_error("Original source SHA mismatch");
 if(original.find("N09 / Zoey [censored]\nCaption for the galley board: Nobody should have to make their first cup alone after a bad night.")==string::npos)throw runtime_error("N09 source text mismatch");
 // Authentic N02 HMAC16 known source test, separate from target domain.
 string known="a good watch leaves the room ready for the next pair of hands";unsigned char mac[32];unsigned int len=0;
 HMAC(EVP_sha256(),NONCE.data(),16,(const unsigned char*)known.data(),known.size(),mac,&len);
 const unsigned char expect[]={0xbf,0x88,0x93,0x59,0xb0,0x30,0x3f,0x2b,0x2b,0x2f,0xd9,0x6a,0xe8,0x41,0x21,0x0b};
 if(len!=32||!equal(mac,mac+16,expect))throw runtime_error("Known authored caption HMAC control failed");
 planted=digest(plant);
 auto start=chrono::steady_clock::now();
 uint64_t expected=0;
 for(unsigned mask=0;mask<(1u<<CORE.size());++mask) {
  vector<string>w;
  for(unsigned t=0;t<CORE.size();++t)if(mask&(1u<<t))w.push_back(CORE[t]);
  int k=w.size();
  for(const string &sea:SEA)for(const string &social:SOCIAL) {
    for(int a=0;a<=k;++a)for(int b=0;b<=k;++b) {
      string phrase;
      for(int t=0;t<=k;++t){
        if(t==a){if(!phrase.empty())phrase+=' ';phrase+=sea;}
        if(t==b){if(!phrase.empty())phrase+=' ';phrase+=social;}
        if(t<k){if(!phrase.empty())phrase+=' ';phrase+=w[t];}
      }
      check(phrase);
      if(a==b){
       phrase.clear();for(int t=0;t<=k;++t){
        if(t==b){if(!phrase.empty())phrase+=' ';phrase+=social;}
        if(t==a){if(!phrase.empty())phrase+=' ';phrase+=sea;}
        if(t<k){if(!phrase.empty())phrase+=' ';phrase+=w[t];}
       }
       check(phrase);
      }
    }
  }
  expected+=16ull*(k+1)*(k+2);
 }
 if(count!=expected)throw runtime_error("candidate count mismatch");
 if(plant_hits!=1)throw runtime_error("planted complete phrase missing or duplicated");
 cout<<"ORIGINAL_SHA_PIN=PASS NOTE_N09=PASS N02_HMAC=PASS PLANT_HIT="<<plant_hits<<" CANDIDATES="<<count<<" REWRITE_FLAGS="<<rewrite<<" ORIGINAL_HITS="<<orig_hits<<" SECONDS="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"\n";
 return orig_hits?0:1;
}
