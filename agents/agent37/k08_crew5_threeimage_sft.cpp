// H-17 source-pinned five-word crew-note, three-image K08 full-caption search.
// Requires C++17 and OpenSSL libcrypto. Run with notes file path.
// Model: 24 authentic N01-N24 note bodies -> 222 word types; five words,
// including literal sea, night and at least one of room/table/voices.
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <vector>

static const unsigned char nonce[16] = {0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32] = {0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char known_n18[16] = {0xa3,0x10,0x0a,0xe1,0xab,0xb9,0xc8,0xd5,0x83,0x15,0xd9,0xeb,0xf3,0x26,0x97,0x8b};
static unsigned char planted[32];
static std::vector<std::string> vocab;
static std::array<const std::string*,5> chosen;
static uint64_t checks=0, positives=0, hits=0;

void reduce(const std::string& text,unsigned char hmac16[16],unsigned char digest[32]){
    unsigned char hm[32]; unsigned int n=0;
    HMAC(EVP_sha256(),nonce,16,(const unsigned char*)text.data(),text.size(),hm,&n);
    if(n!=32)std::abort();
    std::copy(hm,hm+16,hmac16);
    SHA256(hm,16,digest);
}

void walk(int depth,unsigned mask){
    const int missing=((mask&1)==0)+((mask&2)==0)+((mask&4)==0);
    if(missing>5-depth)return;
    if(depth==5){
        std::string phrase=*chosen[0];
        for(int i=1;i<5;++i){phrase.push_back(' ');phrase+=*chosen[i];}
        unsigned char hm[16],digest[32];reduce(phrase,hm,digest);
        ++checks;
        if(std::equal(digest,digest+32,planted)){
            ++positives;
            if(phrase!="sea night voices table room")std::abort();
        }
        if(std::equal(digest,digest+32,target)){
            ++hits;std::cout<<"ORIGINAL K08 HIT: "<<phrase<<"\n";
        }
        return;
    }
    for(const auto& word:vocab){
        chosen[depth]=&word;
        unsigned nextmask=mask;
        if(word=="sea")nextmask|=1;
        if(word=="night")nextmask|=2;
        if(word=="room"||word=="table"||word=="voices")nextmask|=4;
        walk(depth+1,nextmask);
    }
}

int main(int argc,char** argv){
    if(argc!=2){std::cerr<<"pass path to crew notes\n";return 2;}
    std::ifstream f(argv[1]);
    if(!f){std::cerr<<"no crew notes\n";return 3;}
    const std::string source((std::istreambuf_iterator<char>(f)),{});
    unsigned char digest[32],hm[16];
    SHA256((const unsigned char*)source.data(),source.size(),digest);
    std::string hex;static const char* alphabet="0123456789abcdef";
    for(auto b:digest){hex+=alphabet[b>>4];hex+=alphabet[b&15];}
    if(hex!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"){
        std::cerr<<"source SHA mismatch\n";return 4;
    }
    std::set<std::string> words;
    const std::regex header(R"(^N[0-9][0-9] / [A-Za-z]+ \[censored\]$)");
    const std::regex word_regex(R"([a-z0-9]+)");
    std::istringstream in(source);std::string line;int notes=0;
    while(std::getline(in,line)){
        if(!std::regex_match(line,header))continue;
        std::string body;
        if(!std::getline(in,body))std::abort();
        ++notes;
        for(char& c:body)c=(char)std::tolower((unsigned char)c);
        for(auto i=std::sregex_iterator(body.begin(),body.end(),word_regex);
            i!=std::sregex_iterator();++i)words.insert(i->str());
    }
    if(notes!=24||words.size()!=222){std::cerr<<"source tokens mismatch\n";return 5;}
    vocab.assign(words.begin(),words.end());
    reduce("back before the first boat",hm,digest);
    if(!std::equal(hm,hm+16,known_n18))std::abort();
    reduce("sea night voices table room",hm,planted);
    walk(0,0);
    if(checks!=8672610||positives!=1)std::abort();
    std::cout<<"K08_CREW5 source_words="<<vocab.size()<<" original_checks="<<checks
             <<" original_hits="<<hits<<" planted_hits="<<positives<<" controls=PASS\n";
    return 0;
}
