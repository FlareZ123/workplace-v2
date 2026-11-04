// H-17 K04: exhaustive two-nibble deletion plus two independently inserted nibbles.
// Read-only diagnostic; test any full component against unchanged original SHA256.
// Build: g++ -O3 -fopenmp -std=c++17 k04_dual_nibble_reassembly_sft.cpp -lcrypto -o k04_dual_nibble
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>
#include <openssl/sha.h>

std::string read_file(const std::string& p) {
    std::ifstream f(p, std::ios::binary);
    if (!f) throw std::runtime_error("Cannot read " + p);
    return std::string(std::istreambuf_iterator<char>(f), {});
}
int hex(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    throw std::runtime_error("Invalid hex");
}
std::array<unsigned char, 32> fromhex64(const std::string& s) {
    if (s.size() != 64) throw std::runtime_error("Digest not 64 hex characters");
    std::array<unsigned char, 32> x{};
    for (int i = 0; i < 32; ++i) x[i] = (hex(s[i*2])<<4) | hex(s[i*2+1]);
    return x;
}
std::array<unsigned char,16> fromhex32(const std::string& s) {
    if (s.size() != 32) throw std::runtime_error("Payload not 32 hex characters");
    std::array<unsigned char,16> x{};
    for (int i = 0; i < 16; ++i) x[i] = (hex(s[i*2])<<4) | hex(s[i*2+1]);
    return x;
}
std::string hex16(const unsigned char* x) {
    const char* a="0123456789ABCDEF";
    std::string s(32,'0');
    for(int i=0;i<16;i++){s[i*2]=a[x[i]>>4];s[i*2+1]=a[x[i]&15];}
    return s;
}
std::string group(const std::string& x,const std::string& rx){
    std::smatch m;
    if(!std::regex_search(x,m,std::regex(rx))) throw std::runtime_error("Missing original selector " + rx);
    return m[1].str();
}
// Remove source nibble positions i,j, insert new nibble values at destination a,b.
void restore(const unsigned char* source, int i,int j,int a,int b,int va,int vb,unsigned char* out){
    unsigned char kept[30]; int k=0;
    for(int p=0;p<32;p++) if(p!=i && p!=j) kept[k++]=source[p];
    k=0;
    for(int p=0;p<32;p++) {
        unsigned char d = p==a ? (unsigned char)va : (p==b ? (unsigned char)vb : kept[k++]);
        if ((p&1)==0) out[p>>1] = d<<4;
        else out[p>>1] |= d;
    }
}
int main(int argc,char**argv){
  try {
    const std::string base = argc>1 ? argv[1] : ".";
    const auto spool=read_file(base+"/evidence/print/spool-reconstruction.log");
    unsigned char sh[SHA256_DIGEST_LENGTH]; SHA256((const unsigned char*)spool.data(),spool.size(),sh);
    if(hex16(sh)!="7D71D8BEF7F01596E705AC14E24C5C43") throw std::runtime_error("Original spool hash prefix mismatch");
    std::string payload;
    std::regex r("[^\\n]*JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32})[^\\n]*");
    for(std::sregex_iterator it(spool.begin(),spool.end(),r),end;it!=end;++it){
      if(!payload.empty()) throw std::runtime_error("Duplicate selected spool row");
      payload=(*it)[1].str();
    }
    if(payload!="A9A9DC5731A5E2AE879C47215C2559D5") throw std::runtime_error("Unexpected selected source");
    const std::string route=read_file(base+"/evidence/recovery-routing.json");
    const std::string accepts=read_file(base+"/acceptance.json");
    const auto mask=fromhex32(group(route,R"REG("masked_component"\s*:\s*"([0-9A-F]{32})")REG"));
    const auto target=fromhex64(group(accepts,R"REG("K04"\s*:\s*"([0-9a-f]{64})")REG"));
    unsigned char source[32]; for(int i=0;i<32;i++)source[i]=hex(payload[i]);
    const auto baseline=fromhex32(payload);
    unsigned char baseline_key[16]; for(int k=0;k<16;k++)baseline_key[k]=baseline[k]^mask[k];
    unsigned char dh[32];SHA256(baseline_key,16,dh);
    if(std::memcmp(dh,target.data(),32)==0)throw std::runtime_error("Original copied ACK unexpectedly passes");
    // Planted corruption test uses two deletions and two insertions, causing a long nibble shift.
    unsigned char planted[16]={};restore(source,1,25,7,28,11,4,planted);
    unsigned char pk[16];for(int k=0;k<16;k++)pk[k]=planted[k]^mask[k];
    unsigned char planted_digest[32];SHA256(pk,16,planted_digest);
    std::atomic<uint64_t> trials{0}, real_hits{0}, synthetic_hits{0};
    #pragma omp parallel for schedule(dynamic,4)
    for(int x=0;x<32;x++){
       uint64_t subtrials=0, subreal=0,subsynthetic=0;
       unsigned char restored[16], key[16], digest[32];
       for(int y=x+1;y<32;y++)for(int a=0;a<32;a++)for(int b=a+1;b<32;b++)
         for(int v=0;v<256;v++){
            restore(source,x,y,a,b,v>>4,v&15,restored);
            for(int k=0;k<16;k++)key[k]=restored[k]^mask[k];
            SHA256(key,16,digest);
            subtrials++;
            if(std::memcmp(digest,planted_digest,32)==0)subsynthetic++;
            if(std::memcmp(digest,target.data(),32)==0){
              subreal++;
              #pragma omp critical
              {std::cout<<"FOUND original K04="<<hex16(key)<<" deleted="<<x<<","<<y<<" inserted="<<a<<","<<b<<" values="<<(v>>4)<<","<<(v&15)<<"\n";}
            }
         }
        trials+=subtrials;real_hits+=subreal;synthetic_hits+=subsynthetic;
    }
    std::cout<<"source_sha256="<<hex16(sh)<<"...\n"
             <<"planted_component="<<hex16(pk)<<" planted_matches="<<synthetic_hits.load()<<"\n"
             <<"complete_assignments="<<trials.load()<<" expected=62980096 original_matches="<<real_hits.load()<<"\n";
    if(trials!=62980096 || synthetic_hits<1)return 2;
    return real_hits?3:0;
  }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
