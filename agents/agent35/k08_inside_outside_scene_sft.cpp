// H-17 exploratory K08 inside/outside/night three-clause edit grammar.
// Use: compile against OpenSSL libcrypto; pass original crew-notes path.
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
static const vector<string> outside = {"the sea was outside","the sea was still outside","the water was outside","the sea was just beyond the window","the water was beyond the window","the sea was still beyond the window","the sea waited outside","the sea waited beyond the window","the water waited outside","outside the sea was waiting","outside there was the sea","outside the water was waiting","outside the water was still dark","outside the sea was still dark","outside the sea was turning light","the sea was dark outside","the water was dark outside","the window held the sea","the window looked out to the sea","the window kept the sea outside","the sea was at the window","the sea was on the other side of the glass","the sea was beyond the glass","the water was beyond the glass","the night and the sea were outside","the dark sea was outside","there was the sea beyond the window","the sea was beyond the window"};
static const vector<string> inside = {"there was still room at the table","there was room at the table","there was room for one more at the table","there was always room at the table","there was room for one more mug","there was room for one more cup","there was room for one more person","there was room for another cup","there was room for another mug","there was room for another chair","there was room for the next watch","there was room for each other","there was room enough for us all","we made room for one more","we made room for each other","we kept room for one more","we left room at the table","we left room for another cup","we made room at the table","we still made room for each other","the crew made room for one more","the crew left room for one more","someone made room for one more","somebody made room at the table","someone had made room at the table","the mugs waited on the table","the mugs stood beside the window","the mugs were still on the table","the mugs were beside the window","the table had room for one more","the table had room for another mug","the table had room for us","the table always had room for one more","the table was waiting for us","there was room for the next pair of hands","the little lamp was still on","the little lamp stayed on","somebody remembered the little lamp","somebody kept the lamp on","the crew kept the lamp on","we kept the little lamp on","we left the little lamp on","the voices were still at the table","there were still voices at the table","voices still gathered at the table","we were all still at the table"};
static const vector<string> night = {"the night was nearly over","the night was almost over","the night was nearly finished","the night was almost finished","the night was coming to an end","the night was at an end","the night was ending","the night came to an end","the long watch was almost over","the long watch was nearly done","the long watch had ended","the watch had almost ended","the watch had come to an end","the shift was nearly done","the last cup was finished","the last cups were finished","the last mug was empty","the last mugs were empty","the last cup was on the table","the last watch was over","the day was almost here","the morning was almost here","the first light was coming","the daylight was coming","the sun was coming up","morning was coming"};
static const vector<string> conns = {"and","but","while","as","when","with","and still","even as"};
static const array<unsigned char,16> nonce={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const array<unsigned char,32> target={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static string hex(const unsigned char* p,size_t n) {
    const char *digits="0123456789abcdef";
    string s; s.reserve(2*n);
    for(size_t j=0;j<n;j++){s+=digits[p[j]>>4];s+=digits[p[j]&15];}
    return s;
}
static array<unsigned char,32> digest(const string& str) {
    unsigned char mac[32]; unsigned int n=0;
    HMAC(EVP_sha256(),nonce.data(),16,(const unsigned char*)str.data(),str.size(),mac,&n);
    if(n!=32) throw runtime_error("HMAC failed");
    array<unsigned char,32> d{};
    SHA256(mac,16,d.data());
    return d;
}
int main(int argc,char** argv){
    if(argc!=2){cerr<<"provide original crew-notes path\n";return 2;}
    ifstream f(argv[1],ios::binary);
    string source{istreambuf_iterator<char>(f),istreambuf_iterator<char>()};
    if(source.empty()){cerr<<"source unavailable\n";return 2;}
    unsigned char sourcehash[32];SHA256((const unsigned char*)source.data(),source.size(),sourcehash);
    if(hex(sourcehash,32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb") {cerr<<"source SHA256 mismatch\n";return 2;}
    unsigned char control[32];unsigned int nn=0;
    const string n02="a good watch leaves the room ready for the next pair of hands";
    HMAC(EVP_sha256(),nonce.data(),16,(const unsigned char*)n02.data(),n02.size(),control,&nn);
    if(nn!=32 || hex(control,16)!="bf889359b0303f2b2b2fd96ae841210b"){cerr<<"N02 control fail\n";return 2;}
    const string synth="the sea was outside and there was room for one more at the table while the night was almost finished";
    auto expected=digest(synth);
    array<int,3> idx={0,1,2};
    unsigned long long done=0,syn=0,hits=0;
    do{
        for(const auto& c1:conns)for(const auto& c2:conns){
            for(const auto& x:outside)for(const auto& y:inside)for(const auto& z:night){
                const array<const string*,3> vals={&x,&y,&z};
                string phrase=*vals[idx[0]]+" "+c1+" "+*vals[idx[1]]+" "+c2+" "+*vals[idx[2]];
                auto d=digest(phrase);
                ++done;
                if(d==target){++hits;cout<<"ORIGINAL_K08_HIT "<<phrase<<"\n";}
                if(d==expected){++syn;}
            }
        }
    }while(next_permutation(idx.begin(),idx.end()));
    cout<<"K08_FROZEN_CONTRAST_ASSIGNMENTS "<<done<<" ORIGINAL_MATCHES "<<hits<<" SYNTHETIC_CONTROLS "<<syn<<"\n";
    if(done != 6ull*outside.size()*inside.size()*night.size()*conns.size()*conns.size() || syn!=1) return 3;
    return hits?1:0;
}
