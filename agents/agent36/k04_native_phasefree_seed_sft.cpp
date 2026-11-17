/* Stage-free native MT19937 uint32 seed/phase source test for H-17 K04.
 * Selected row 129 withheld; normal spool packet pairs act as historical controls.
 * A genuine source match identifies a full generator that could emit K04.
 */
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <random>
#include <regex>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <openssl/sha.h>
#include <omp.h>

static constexpr char ORIGINAL_SHA[] = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
struct Record { int row = 0; std::array<uint32_t,4> words{}; };
struct Witness { int row, lane, endian; uint32_t second, third; };
static uint32_t bswap(uint32_t x){ return __builtin_bswap32(x); }

static std::vector<Record> load(const std::string& path) {
    std::ifstream f(path,std::ios::binary); assert(f.good());
    std::string raw((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
    unsigned char d[32]; SHA256((const unsigned char*)raw.data(),raw.size(),d);
    char hex[65]{};
    for(int i=0;i<32;++i) std::sprintf(hex+2*i,"%02x",d[i]);
    assert(std::strcmp(hex,ORIGINAL_SHA)==0);
    std::regex pattern("PAYLOAD=([0-9A-F]{32})");
    std::vector<Record> records;
    std::stringstream in(raw); std::string line;
    while(std::getline(in,line)) {
        if(line.rfind("2026-",0)!=0) continue;
        Record rec{}; rec.row=(int)records.size();
        if(rec.row==129) {
            assert(line.find("JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER")!=std::string::npos);
            records.push_back(rec);
            continue;
        }
        std::smatch m; assert(std::regex_search(line,m,pattern));
        for(int k=0;k<4;++k)
            rec.words[k]=bswap((uint32_t)std::stoul(m[1].str().substr(8*k,8),nullptr,16));
        records.push_back(rec);
    }
    assert(records.size()==133);
    return records;
}

static unsigned scan(uint32_t seed,int phases,
    const std::unordered_map<uint32_t,std::vector<Witness>>& by_first,
    const std::array<uint8_t,65536>& hi,bool print_found) {
    std::mt19937 rng(seed);
    uint32_t prev=rng(); unsigned hits=0;
    for(int stage=0;stage<phases;++stage) {
        const uint32_t next=rng();
        if(hi[prev>>16]) {
            auto it=by_first.find(prev);
            if(it!=by_first.end()) for(const Witness& w:it->second) {
                if(next!=w.second) continue;
                if(w.lane<=1) {
                    std::mt19937 copy=rng;
                    if(copy()!=w.third) continue;
                }
                ++hits;
                if(print_found) {
                    #pragma omp critical
                    {
                        std::printf("SOURCE_PAIR seed=%u phase=%d row=%d lane=%d endian=%d first=%08X second=%08X\n",
                            seed,stage,w.row,w.lane,w.endian,prev,next);
                        std::fflush(stdout);
                    }
                }
            }
        }
        prev=next;
    }
    return hits;
}

int main(int argc,char** argv) {
    assert(argc==5);
    const uint64_t begin=std::strtoull(argv[2],nullptr,10);
    const uint64_t end=std::strtoull(argv[3],nullptr,10);
    const int phases=std::atoi(argv[4]);
    assert(begin<end&&end<=UINT64_C(4294967296)&&phases>=1&&phases<=4096);
    auto records=load(argv[1]);
    std::unordered_map<uint32_t,std::vector<Witness>> by_first;
    std::array<uint8_t,65536> hi{};
    for(const Record& record:records) if(record.row!=129) {
        for(int lane=0;lane<=2;++lane) for(int endian=0;endian<2;++endian) {
            uint32_t one=endian?bswap(record.words[lane]):record.words[lane];
            uint32_t two=endian?bswap(record.words[lane+1]):record.words[lane+1];
            uint32_t three=lane<=1?(endian?bswap(record.words[lane+2]):record.words[lane+2]):0;
            by_first[one].push_back({record.row,lane,endian,two,three});
            hi[one>>16]=1;
        }
    }
    assert(by_first.size()==792);
    std::mt19937 ref(5489U);
    assert(ref()==3499211612U && ref()==581869302U);
    std::mt19937 planted(12345U);
    for(int i=0;i<777;++i) (void)planted();
    uint32_t a=planted(),b=planted(),c=planted();
    std::unordered_map<uint32_t,std::vector<Witness>> ctrl{{a,{{-1,1,1,b,c}}}};
    std::array<uint8_t,65536> ctrl_hi{}; ctrl_hi[a>>16]=1;
    assert(scan(12345U,1024,ctrl,ctrl_hi,false)==1);
    assert(scan(12344U,1024,ctrl,ctrl_hi,false)==0);
    std::printf("SOURCE_SHA_PASS originals=132 starts=792 seeded_positive=1/1\n");
    std::fflush(stdout);
    uint64_t examined=0,hits=0,hit_seeds=0;
    const double t0=omp_get_wtime();
    #pragma omp parallel for schedule(dynamic,256) reduction(+:examined,hits,hit_seeds)
    for(uint64_t index=begin;index<end;++index) {
        unsigned n=scan((uint32_t)index,phases,by_first,hi,true);
        hits+=n; hit_seeds+=(n!=0); ++examined;
    }
    assert(examined==end-begin);
    std::printf("ORIGINAL_SCAN begin=%llu end=%llu phases=%d seeds=%llu source_pair_hits=%llu hit_seeds=%llu seconds=%.2f\n",
        (unsigned long long)begin,(unsigned long long)end,phases,
        (unsigned long long)examined,(unsigned long long)hits,
        (unsigned long long)hit_seeds,omp_get_wtime()-t0);
    return hits?7:0;
}
