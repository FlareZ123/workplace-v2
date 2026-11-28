// Bounded complete K08 candidate test: all unique P20 13-token multiset permutations.
// Compile: g++ -O3 -std=c++17 FILE.cpp -lcrypto -o p20_wordbag
// Run: ./p20_wordbag /path/to/original/extracted/bundle
// Reads only permitted crew notes, routing and acceptance; never reads PDF.
#include <algorithm>
#include <array>
#include <cassert>
#include <cctype>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>

using Bytes32 = std::array<unsigned char, SHA256_DIGEST_LENGTH>;
std::string read(const std::string &path) {
    std::ifstream file(path, std::ios::binary);
    if (!file) throw std::runtime_error("Cannot open " + path);
    return std::string(std::istreambuf_iterator<char>(file), {});
}
std::string hex(const unsigned char *ptr, size_t n) {
    const char *base = "0123456789abcdef";
    std::string out; out.reserve(n*2);
    for (size_t i=0;i<n;i++){out+=base[ptr[i]>>4];out+=base[ptr[i]&15];}
    return out;
}
std::vector<unsigned char> dehex(const std::string &s) {
    auto nib=[](char c){if(c>='0'&&c<='9')return c-'0'; if(c>='a'&&c<='f')return 10+c-'a'; if(c>='A'&&c<='F')return 10+c-'A'; throw std::runtime_error("Bad hex");};
    if(s.size()%2) throw std::runtime_error("Odd hex");
    std::vector<unsigned char> out;
    for(size_t i=0;i<s.size();i+=2)out.push_back((nib(s[i])<<4)|nib(s[i+1]));
    return out;
}
std::string extract_field(const std::string &json,const std::string &field,size_t n) {
    auto p=json.find("\""+field+"\"");
    if(p==std::string::npos)throw std::runtime_error("Missing "+field);
    p=json.find(':',p); p=json.find('"',p)+1;
    auto q=json.find('"',p); auto s=json.substr(p,q-p);
    if(s.size()!=n)throw std::runtime_error("Unexpected length "+field);
    return s;
}
std::vector<std::string> words(std::string text) {
    std::vector<std::string> out;std::string current;
    for(unsigned char c:text){
        if((c>='a'&&c<='z')||(c>='0'&&c<='9'))current+=c;
        else if(c>='A'&&c<='Z')current+=char(c+32);
        else if(!current.empty()){out.push_back(current);current.clear();}
    }
    if(!current.empty())out.push_back(current);
    return out;
}
std::string join(const std::vector<std::string> &words) {
    std::string s;
    for(const auto &w:words){if(!s.empty())s+=' ';s+=w;}
    return s;
}
class K08 {
    SHA256_CTX inner_,outer_;
public:
    explicit K08(const std::vector<unsigned char>& key) {
        assert(key.size()==16);
        unsigned char ipad[64],opad[64];
        std::memset(ipad,0x36,64);std::memset(opad,0x5c,64);
        for(size_t i=0;i<key.size();i++){ipad[i]^=key[i];opad[i]^=key[i];}
        SHA256_Init(&inner_);SHA256_Update(&inner_,ipad,64);
        SHA256_Init(&outer_);SHA256_Update(&outer_,opad,64);
    }
    Bytes32 commitment(const std::string &caption) const {
        unsigned char inner_digest[32],outer_digest[32];
        SHA256_CTX state=inner_;
        SHA256_Update(&state,caption.data(),caption.size());
        SHA256_Final(inner_digest,&state);
        state=outer_;
        SHA256_Update(&state,inner_digest,32);
        SHA256_Final(outer_digest,&state);
        Bytes32 result;
        SHA256(outer_digest,16,result.data());
        return result;
    }
};
int main(int argc,char**argv) {
    if(argc!=2){std::cerr<<"Usage: p20_wordbag original_root\n";return 2;}
    const std::string root=argv[1];
    try {
        std::string notes=read(root+"/evidence/crew/noticeboard-and-desk-notes.txt");
        unsigned char notes_sha[32];SHA256((const unsigned char*)notes.data(),notes.size(),notes_sha);
        if(hex(notes_sha,32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw std::runtime_error("Note SHA mismatch");
        auto p=notes.find("N20 / ");if(p==std::string::npos)throw std::runtime_error("No N20");
        p=notes.find('\n',p)+1;auto end=notes.find('\n',p);
        auto body=notes.substr(p,end-p);auto nw=words(body);
        if(nw.size()!=30)throw std::runtime_error("N20 token count");
        std::vector<std::string> selected(nw.begin()+6,nw.begin()+19);
        unsigned char payload_sha[32];auto payload=join(selected);
        SHA256((const unsigned char*)payload.data(),payload.size(),payload_sha);
        if(hex(payload_sha,32)!="4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c")throw std::runtime_error("P20 fingerprint mismatch");
        auto routing=read(root+"/evidence/recovery-routing.json");
        auto acceptance=read(root+"/acceptance.json");
        K08 reducer(dehex(extract_field(routing,"desk_nonce",32)));
        auto target=dehex(extract_field(acceptance,"K08",64));
        auto known_control=reducer.commitment("a good watch leaves the room ready for the next pair of hands");
        if(hex(known_control.data(),32)!="47e787785ff25082b4b960ad415f1e030ae0edc89c38b2f61c48f9331282ea55")throw std::runtime_error("Historical N02 reducer fixture failed");
        // Every nonempty submultiset: 0..5 copies of the recurring token,
        // any subset of the eight distinct singleton tokens. Each multiset
        // permuted in full; no substitutions, additions or repetitions beyond
        // the exact source multiplicity.
        std::sort(selected.begin(),selected.end());
        const auto all_sorted=selected;
        const std::string recurring="the";
        std::vector<std::string> singles;
        for(const auto &w:all_sorted)if(w!=recurring)singles.push_back(w);
        if(singles.size()!=8 || std::count(all_sorted.begin(),all_sorted.end(),recurring)!=5)
            throw std::runtime_error("Unexpected P20 multiset");
        auto planted=reducer.commitment(join(all_sorted));
        uint64_t checked=0,original_hits=0,planted_hits=0;
        std::array<uint64_t,14> length_counts{};
        for(int mask=0;mask<256;mask++) for(int countThe=0;countThe<=5;countThe++) {
            std::vector<std::string> sub(countThe,recurring);
            for(int bit=0;bit<8;bit++)if(mask&(1<<bit))sub.push_back(singles[bit]);
            if(sub.empty())continue;
            std::sort(sub.begin(),sub.end());
            const int length=int(sub.size());
            do {
                auto text=join(sub);
                auto got=reducer.commitment(text);
                if(std::memcmp(got.data(),target.data(),32)==0){original_hits++; std::cerr<<"Original acceptance hit; preserve candidate locally and authenticate before publication\n";}
                if(got==planted)planted_hits++;
                checked++;length_counts[length]++;
            } while(std::next_permutation(sub.begin(),sub.end()));
        }
        if(checked!=152152845 || planted_hits!=1 || length_counts[13]!=51891840 || length_counts[12]!=51891840)
            throw std::runtime_error("Enumeration or planted control invalid");
        std::cout<<"K08_P20_ALL_SUBMULTISET_PERMUTATIONS checked="<<checked<<" planted_hits="<<planted_hits<<" original_hits="<<original_hits<<" source=PASS N02=PASS\n";
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
