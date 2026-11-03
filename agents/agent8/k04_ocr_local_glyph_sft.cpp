// H-17 K04: position-independent, locally ambiguous OCR hex-glyph copier model.
// Read-only reproducible search, C++17 + OpenSSL. All values source-pinned.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

using Bytes = std::array<unsigned char,16>;
using Digest = std::array<unsigned char,32>;

std::string readall(const std::string &path){
    std::ifstream f(path, std::ios::binary);
    if(!f) throw std::runtime_error("could not open: "+path);
    return std::string(std::istreambuf_iterator<char>(f),std::istreambuf_iterator<char>());
}
int nibble(char c){
    if(c>='0'&&c<='9')return c-'0';
    if(c>='A'&&c<='F')return c-'A'+10;
    throw std::runtime_error("not upper hex");
}
Bytes bytes(const std::string& hex){
    if(hex.size()!=32)throw std::runtime_error("expected 32 hex characters");
    Bytes result{};
    for(int i=0;i<16;i++) result[i]=(nibble(hex[2*i])<<4)|nibble(hex[2*i+1]);
    return result;
}
Digest hash(const Bytes &x){Digest d{}; SHA256(x.data(),16,d.data());return d;}
std::string sha256hex(const std::string &data){
    unsigned char out[32]; SHA256(reinterpret_cast<const unsigned char*>(data.data()),data.size(),out);
    const char *digits="0123456789abcdef"; std::string result;
    for(unsigned char b:out){ result+=digits[b>>4];result+=digits[b&15]; }
    return result;
}
Bytes xor_bytes(const Bytes &a,const Bytes &b){
    Bytes z{};for(size_t i=0;i<16;i++)z[i]=a[i]^b[i];return z;
}
std::vector<std::string> options(const std::string &text){
    // Independent selections, even when an ambiguous glyph recurs elsewhere.
    // Exploratory valid-hex OCR visual confusion groups, not authenticated faults.
    const std::vector<std::string> groups={"0D","17","38B","4A","69","EF"};
    std::vector<std::string> all;
    for(char c:text){
        std::string choice(1,c);
        for(const auto &group:groups){if(group.find(c)!=std::string::npos){choice=group;break;}}
        std::sort(choice.begin(),choice.end());
        all.push_back(choice);
    }
    return all;
}
uint64_t count(const std::vector<std::string> &opts){
    uint64_t n=1;for(auto &o:opts)n*=o.size();return n;
}
void update_nibble(Bytes &a,size_t index,char c){
    unsigned char &b=a[index/2];
    if(index%2==0)b=(nibble(c)<<4)|(b&15);
    else b=(b&0xF0)|nibble(c);
}
struct Outcome {uint64_t tries=0,original_hits=0,planted_hits=0;};
Outcome run(const std::string &name,const std::string &original,
            const Bytes &other,const Digest &wanted){
    const auto opt=options(original);
    const uint64_t size=count(opt);
    Bytes current=bytes(original);
    for(size_t i=0;i<32;i++)update_nibble(current,i,opt[i][0]);
    std::vector<size_t> digit(32,0);

    // A deliberately nonidentity complete coupon with a controlled exact hash.
    Bytes planted=bytes(original);
    int edits=0;
    for(size_t i=0;i<32 && edits<3;i++){
        if(opt[i].size()>1 && opt[i][0]!=original[i]) {update_nibble(planted,i,opt[i][0]);edits++;}
        else if(opt[i].size()>1 && opt[i][1]!=original[i]) {update_nibble(planted,i,opt[i][1]);edits++;}
    }
    if(edits!=3)throw std::runtime_error("failed planted nonidentity channel");
    auto produce=[&](const Bytes &b)->Bytes {
        if(name=="component")return b;
        return xor_bytes(b,other);
    };
    const Digest control=hash(produce(planted));
    Outcome result;
    while(true){
        const Bytes candidate=produce(current);
        const Digest digest=hash(candidate);
        result.original_hits += (digest==wanted);
        result.planted_hits += (digest==control);
        ++result.tries;
        size_t pos=0;
        for(;pos<32;pos++){
            if(++digit[pos] < opt[pos].size()){
                update_nibble(current,pos,opt[pos][digit[pos]]);
                break;
            }
            digit[pos]=0;
            update_nibble(current,pos,opt[pos][0]);
        }
        if(pos==32)break;
    }
    if(result.tries!=size || result.planted_hits!=1)
        throw std::runtime_error("enumeration/control mismatch in "+name);
    std::cout<<name<<" assignments="<<result.tries<<" original_hits="<<result.original_hits
             <<" planted_hits="<<result.planted_hits<<"\n";
    return result;
}
int main(int argc,char**argv){
    try{
        if(argc!=3)throw std::runtime_error("Expected repository path and stage: payload, mask or component");
        const std::string stage=argv[2],root=argv[1];
        const std::string spool=readall(root+"/resources/evidence/print/spool-reconstruction.log");
        const std::string acceptance=readall(root+"/resources/acceptance.json");
        if(sha256hex(spool)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")
            throw std::runtime_error("printer source SHA mismatch");
        if(sha256hex(acceptance)!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")
            throw std::runtime_error("commitment source SHA mismatch");
        const std::string stamp="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
        if(spool.find(stamp)==std::string::npos)throw std::runtime_error("selected ACK2 source mismatch");
        const std::string captured="A9A9DC5731A5E2AE879C47215C2559D5";
        const std::string route="8556C8CB6140A7F9A5123AC7571BEE1C";
        const Bytes payload=bytes(captured),mask=bytes(route);
        const Bytes reduced=xor_bytes(payload,mask);
        const std::string component="2CFF149C50E54557228E7DE60B3EB7C9";
        if(bytes(component)!=reduced)throw std::runtime_error("wrong original XOR reducer");
        const std::string want="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
        if(acceptance.find(want)==std::string::npos)throw std::runtime_error("original digest missing");
        Digest wanted{};
        for(int i=0;i<32;i++)
            wanted[i]=(nibble(static_cast<char>(std::toupper(want[i*2])))<<4)
                     |nibble(static_cast<char>(std::toupper(want[i*2+1])));
        if(stage=="payload")run("payload",captured,mask,wanted);
        else if(stage=="mask")run("mask",route,payload,wanted);
        else if(stage=="component")run("component",component,mask,wanted);
        else throw std::runtime_error("invalid stage");
        return 0;
    } catch(const std::exception &e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
