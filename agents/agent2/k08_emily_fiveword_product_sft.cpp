// Historical K08 five-word exact author-vocabulary candidate search.
// Run: k08_emily_fiveword_sft <path-to-original-notes> <first-prefix-index> <end-index>
// Example: k08_emily_fiveword_sft resources/evidence/crew/noticeboard-and-desk-notes.txt 0 9
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <regex>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Digest = std::array<unsigned char, 32>;
Digest sha(const void* p, size_t size) {
    Digest result{};
    SHA256(static_cast<const unsigned char*>(p), size, result.data());
    return result;
}
std::string hex(const unsigned char* data, size_t size) {
    const char* digits = "0123456789abcdef";
    std::string s;
    for (size_t i=0; i<size; ++i) {
        s.push_back(digits[data[i]>>4]);
        s.push_back(digits[data[i]&15]);
    }
    return s;
}
std::vector<unsigned char> unhex(const std::string& s) {
    if (s.size()%2) throw std::runtime_error("odd hex");
    std::vector<unsigned char> bytes;
    for (size_t i=0;i<s.size();i+=2)
        bytes.push_back(static_cast<unsigned char>(std::stoi(s.substr(i,2), nullptr, 16)));
    return bytes;
}
struct Reducer {
    SHA256_CTX inner_key, outer_key;
    explicit Reducer(const std::vector<unsigned char>& key) {
        if(key.size()!=16) throw std::runtime_error("nonce length");
        unsigned char ipad[64],opad[64];
        for(int i=0;i<64;i++) {
            const unsigned char value = i<16 ? key[i] : 0;
            ipad[i]=value^0x36;
            opad[i]=value^0x5c;
        }
        SHA256_Init(&inner_key); SHA256_Update(&inner_key,ipad,64);
        SHA256_Init(&outer_key); SHA256_Update(&outer_key,opad,64);
    }
    void component(const std::string& text,unsigned char out[16]) const {
        SHA256_CTX inner=inner_key, outer=outer_key;
        unsigned char innerhash[32],hmac[32];
        SHA256_Update(&inner,text.data(),text.size());
        SHA256_Final(innerhash,&inner);
        SHA256_Update(&outer,innerhash,32);
        SHA256_Final(hmac,&outer);
        std::memcpy(out,hmac,16);
    }
};
int main(int argc, char** argv) {
    try {
        if(argc!=4)throw std::runtime_error("usage: <original-note-path> <lo> <hi>");
        const std::string sourcepath=argv[1];
        std::ifstream input(sourcepath,std::ios::binary);
        if(!input)throw std::runtime_error("failed reading original notes");
        const std::string src((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
        const auto actualsource=sha(src.data(),src.size());
        if(hex(actualsource.data(),32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")
            throw std::runtime_error("source SHA mismatch");
        const std::set<std::string> selected={"N02","N06","N10","N13","N17","N18","N20","N23"};
        std::set<std::string> seen,vocabulary;
        const std::regex header("^(N[0-9][0-9]) / Emily "), token("[A-Za-z0-9]+");
        for(size_t pos=0;pos<src.size();) {
            const size_t end=src.find('\n',pos);
            const std::string line=src.substr(pos,end==std::string::npos?std::string::npos:end-pos);
            pos=end==std::string::npos?src.size():end+1;
            std::smatch m;
            if(!std::regex_search(line,m,header)||!selected.count(m[1]))continue;
            if(!seen.insert(m[1]).second)throw std::runtime_error("duplicate Emily note");
            const size_t bodyend=src.find('\n',pos);
            const std::string body=src.substr(pos,bodyend==std::string::npos?std::string::npos:bodyend-pos);
            for(std::sregex_iterator it(body.begin(),body.end(),token),stop;it!=stop;++it){
                std::string word=it->str();
                std::transform(word.begin(),word.end(),word.begin(),[](unsigned char c){return static_cast<char>(std::tolower(c));});
                vocabulary.insert(word);
            }
        }
        if(seen!=selected||vocabulary.size()!=90)throw std::runtime_error("author notes or 90-word vocabulary failed");
        std::string list;
        for(const auto& word:vocabulary){if(!list.empty())list+='\n';list+=word;}
        const auto vocabsha=sha(list.data(),list.size());
        if(hex(vocabsha.data(),32)!="a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261")
            throw std::runtime_error("vocabulary fingerprint failed");
        const std::vector<std::string> words(vocabulary.begin(),vocabulary.end());
        const size_t lo=std::stoull(argv[2]),hi=std::stoull(argv[3]);
        if(!(lo<hi&&hi<=words.size()))throw std::runtime_error("invalid shard limits");
        Reducer reducer(unhex("5F933DA6A1BD03C32DA5CBC25344F497"));
        const auto target=unhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
        unsigned char component[16];
        reducer.component("a good watch leaves the room ready for the next pair of hands",component);
        if(hex(component,16)!="bf889359b0303f2b2b2fd96ae841210b")throw std::runtime_error("N02 genuine control failed");
        reducer.component("back before the first boat",component);
        if(hex(component,16)!="a3100ae1abb9c8d58315d9ebf326978b")throw std::runtime_error("N18 genuine fiveword control failed");
        const std::string planted=words[lo]+" night voices at table";
        reducer.component(planted,component);
        const auto synthetic=sha(component,16);
        uint64_t candidates=0, hits=0, positives=0;
        for(size_t i=lo;i<hi;i++)
        for(const auto& b:words)
        for(const auto& c:words)
        for(const auto& d:words){
            const std::string prefix=words[i]+" "+b+" "+c+" "+d+" ";
            SHA256_CTX prefix_ctx=reducer.inner_key;
            SHA256_Update(&prefix_ctx,prefix.data(),prefix.size());
            for(const auto& e:words){
                SHA256_CTX inner=prefix_ctx,outer=reducer.outer_key;
                unsigned char digest1[32],digest2[32];
                SHA256_Update(&inner,e.data(),e.size());
                SHA256_Final(digest1,&inner);
                SHA256_Update(&outer,digest1,32);
                SHA256_Final(digest2,&outer);
                const auto digest=sha(digest2,16);
                if(std::memcmp(digest.data(),target.data(),32)==0){
                    hits++;
                    std::cout<<"AUTHENTIC_K08: "<<prefix<<e<<" COMPONENT="<<hex(digest2,16)<<std::endl;
                }
                if(digest==synthetic){
                    positives++;
                    if(prefix+e!=planted)throw std::runtime_error("incorrect synthetic preimage");
                }
                candidates++;
            }
        }
        const uint64_t expected=static_cast<uint64_t>(hi-lo)*90*90*90*90;
        if(candidates!=expected||positives!=1)throw std::runtime_error("search count or planted recovery failed");
        std::cout<<"K08 FIVEWORD source_sha256="<<hex(actualsource.data(),32)
                 <<" vocab_sha256="<<hex(vocabsha.data(),32)
                 <<" shard="<<lo<<":"<<hi<<" candidates="<<candidates
                 <<" original_hits="<<hits<<" planted_hits="<<positives<<std::endl;
        return 0;
    } catch(const std::exception& ex){
        std::cerr<<"FAIL: "<<ex.what()<<std::endl;
        return 2;
    }
}
