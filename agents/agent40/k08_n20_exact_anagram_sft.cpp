// Exact N20 motif-word anagram model; read-only historical source and acceptance.
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

int main(int argc,char**argv) {
    const std::string source=(argc>1)?argv[1]:"resources/evidence/crew/noticeboard-and-desk-notes.txt";
    std::ifstream in(source,std::ios::binary);
    if(!in){fprintf(stderr,"ERROR cannot read original notes: %s\n",source.c_str());return 2;}
    const std::string notes((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
    const std::string literal="I wanted the line to hold the sea, the end of the night and the voices at the table.";
    const std::array<unsigned char,32> original_notes_sha={0x13,0xf2,0x31,0x8c,0xcc,0x54,0xf3,0x5b,0x59,0x0a,0x2d,0x76,0xb3,0xa8,0x02,0x44,0xfe,0x24,0xd7,0x0f,0x06,0x99,0xc6,0x7c,0x05,0x85,0x8e,0x8b,0x89,0x83,0xc5,0xcb};
    unsigned char source_sha[32];
    SHA256(reinterpret_cast<const unsigned char*>(notes.data()),notes.size(),source_sha);
    if(memcmp(source_sha,original_notes_sha.data(),32)!=0 || notes.find(literal)==std::string::npos){puts("ERROR input notes SHA/source phrase mismatch");return 2;}
    const std::array<unsigned char,16> nonce = {0x5F,0x93,0x3D,0xA6,0xA1,0xBD,0x03,0xC3,0x2D,0xA5,0xCB,0xC2,0x53,0x44,0xF4,0x97};
    const std::array<unsigned char,32> target = {0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
    const std::array<unsigned char,16> n02 = {0xBF,0x88,0x93,0x59,0xB0,0x30,0x3F,0x2B,0x2B,0x2F,0xD9,0x6A,0xE8,0x41,0x21,0x0B};
    const std::string historical = "a good watch leaves the room ready for the next pair of hands";
    unsigned char h[EVP_MAX_MD_SIZE], digest[SHA256_DIGEST_LENGTH]; unsigned int hlen;
    HMAC(EVP_sha256(),nonce.data(),16,reinterpret_cast<const unsigned char*>(historical.data()),historical.size(),h,&hlen);
    if(hlen!=32 || memcmp(h,n02.data(),16)!=0){puts("ERROR historical control");return 2;}
    std::vector<std::string> words = {"the","sea","the","end","of","the","night","and","the","voices","at","the","table"};
    std::sort(words.begin(),words.end());
    std::string planted="the sea the end of the night and the voices at the table";
    unsigned char planted_hash[32],plant_hmac[32];
    HMAC(EVP_sha256(),nonce.data(),16,reinterpret_cast<const unsigned char*>(planted.data()),planted.size(),plant_hmac,&hlen);
    SHA256(plant_hmac,16,planted_hash);
    std::array<unsigned char,64> ipad{},opad{};
    for(size_t i=0;i<64;i++){
        const unsigned char b=i<nonce.size()?nonce[i]:0;
        ipad[i]=b^0x36;
        opad[i]=b^0x5c;
    }
    SHA256_CTX innerbase,outerbase,inner,outer;
    SHA256_Init(&innerbase);SHA256_Update(&innerbase,ipad.data(),64);
    SHA256_Init(&outerbase);SHA256_Update(&outerbase,opad.data(),64);
    unsigned char innerhash[32];
    std::string candidate;candidate.reserve(80);
    auto start=std::chrono::steady_clock::now();
    unsigned long long count=0,found=0,planted_count=0;
    do {
        candidate.clear();
        for(size_t i=0;i<words.size();i++){
            if(i)candidate+=' ';
            candidate+=words[i];
        }
        inner=innerbase;
        SHA256_Update(&inner,candidate.data(),candidate.size());
        SHA256_Final(innerhash,&inner);
        outer=outerbase;
        SHA256_Update(&outer,innerhash,32);
        SHA256_Final(h,&outer);
        SHA256(h,16,digest);
        if(memcmp(digest,planted_hash,32)==0)planted_count++;
        if(memcmp(digest,target.data(),32)==0){found++;printf("ORIGINAL_HIT component=");for(int j=0;j<16;j++)printf("%02X",h[j]);printf(" words=%s\n",candidate.c_str());}
        count++;
    } while (std::next_permutation(words.begin(),words.end()));
    const double dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    printf("N20_TRIAD_ANAGRAM checked=%llu expected=51891840 synthetic=%llu original=%llu seconds=%.3f\n",count,planted_count,found,dt);
    return (count==51891840 && planted_count==1)?0:3;
}
