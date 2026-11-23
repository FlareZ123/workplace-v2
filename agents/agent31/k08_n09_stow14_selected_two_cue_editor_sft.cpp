// Agent31, 23 Nov 2026: N09 source-selected ordered-subsequence + two/three literal cue spans.
// The N09 base is conditionally selected by the earlier STOW14/N23->N09 locator.
// Compile: g++ -O3 -std=c++17 <this-file>.cpp -lcrypto -o k08_n09_editor
// Run: k08_n09_editor resources/evidence/crew/noticeboard-and-desk-notes.txt <rewrite> [three]
// Four predeclared rewrite flags actually executed: 0, 1, 6, 7; do not claim all 16 ran.
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
#include <algorithm>
#include <stdexcept>
using namespace std;
static const array<unsigned char,16> NONCE={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const array<unsigned char,32> TARGET={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static vector<string> CORE={"nobody","should","have","to","make","their","first","cup","alone","after","a","bad","night"};
static const vector<string> SEA={"the sea","the sea looks different","the water","water outside"};
static const vector<string> SOCIAL={"voices at the table","the voices at the table","people making room for each other","late crew making room for one another"};
static uint64_t candidate_count=0,orig_hits=0,plant_hits=0;
static string plant="the sea nobody should have to make their first cup alone after a bad night voices at the table";
static array<unsigned char,32> planted;
array<unsigned char,32> digest(const string &phrase) {
 unsigned char h[EVP_MAX_MD_SIZE];unsigned int l=0;array<unsigned char,32> d{};
 if(!HMAC(EVP_sha256(),NONCE.data(),NONCE.size(),(const unsigned char*)phrase.data(),phrase.size(),h,&l)||l!=32) throw runtime_error("HMAC failed");
 SHA256(h,16,d.data());return d;
}
static void check(const string &s) {
 auto d=digest(s);++candidate_count;
 if(d==TARGET){++orig_hits;cout<<"ORIGINAL_K08_HIT "<<s<<endl;}
 if(d==planted){++plant_hits;if(s!=plant)throw runtime_error("plant hash collision");}
}
int main(int argc,char**argv) {
 if(argc!=3&&argc!=4) {cerr<<"Pass original note file, rewrite flag 0..15, optional mode=three"<<endl;return 2;}
 bool three=argc==4; if(three&&string(argv[3])!="three")throw runtime_error("Third arg must be three");
 int rewrite=stoi(argv[2]);if(rewrite<0||rewrite>15)throw runtime_error("Invalid rewrite flag");
 for(string &word:CORE) {
  if((rewrite&1)&&word=="first")word="last"; // N10: after the last cup
  if((rewrite&2)&&word=="bad")word="long"; // MAIL11: after a long watch
  if((rewrite&4)&&word=="night")word="watch"; // MAIL11: a long watch
  if((rewrite&8)&&word=="cup")word="mug"; // N11: chipped blue mug
 }
 plant=three?"the sea at the end of the night":"the sea";for(const string &word:CORE)plant+=" "+word;plant+=three?" the voices at the table":" voices at the table";
 ifstream f(argv[1],ios::binary);string original((istreambuf_iterator<char>(f)),{});
 unsigned char h[32];SHA256((const unsigned char*)original.data(),original.size(),h);
 const unsigned char sha[32]={0x13,0xf2,0x31,0x8c,0xcc,0x54,0xf3,0x5b,0x59,0x0a,0x2d,0x76,0xb3,0xa8,0x02,0x44,0xfe,0x24,0xd7,0x0f,0x06,0x99,0xc6,0x7c,0x05,0x85,0x8e,0x8b,0x89,0x83,0xc5,0xcb};
 if(!equal(h,h+32,sha))throw runtime_error("Original source SHA mismatch");
 if(original.find("N09 / Zoey [censored]\nCaption for the galley board: Nobody should have to make their first cup alone after a bad night.")==string::npos)throw runtime_error("N09 source text mismatch");
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
  if(three){
   static const array<string,3> CUES={"the sea","at the end of the night","the voices at the table"};
   for(int a=0;a<=k;++a)for(int b=0;b<=k;++b)for(int c=0;c<=k;++c){
    array<int,3> pos={a,b,c};array<int,3> perm={0,1,2};
    do {
     if(pos[perm[0]]>pos[perm[1]]||pos[perm[1]]>pos[perm[2]])continue;
     string phrase;
     for(int t=0;t<=k;++t){
      for(int m:perm)if(pos[m]==t){if(!phrase.empty())phrase+=' ';phrase+=CUES[m];}
      if(t<k){if(!phrase.empty())phrase+=' ';phrase+=w[t];}
     }
     check(phrase);
    }while(next_permutation(perm.begin(),perm.end()));
   }
   expected+=(uint64_t)(k+1)*(k+2)*(k+3);
  } else {
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
 }
 if(candidate_count!=expected)throw runtime_error("candidate count mismatch");
 if(plant_hits!=1)throw runtime_error("planted complete phrase missing or duplicated");
 cout<<"ORIGINAL_SHA_PIN=PASS NOTE_N09=PASS N02_HMAC=PASS PLANT_HIT="<<plant_hits<<" CANDIDATES="<<candidate_count<<" REWRITE_FLAGS="<<rewrite<<" MODE="<<(three?"three":"two")<<" ORIGINAL_HITS="<<orig_hits<<" SECONDS="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"\n";
 return orig_hits?0:1;
}
