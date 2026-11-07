#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using B16 = std::array<unsigned char,16>;
using B4 = std::array<unsigned char,4>;

static std::string read_file(const std::string& p) {
    std::ifstream f(p,std::ios::binary);
    if (!f) throw std::runtime_error("cannot open "+p);
    std::ostringstream s; s<<f.rdbuf(); return s.str();
}
static std::string hex(const unsigned char* p,size_t n) {
    std::ostringstream s; s<<std::hex<<std::setfill('0');
    for(size_t i=0;i<n;i++) s<<std::setw(2)<<unsigned(p[i]);
    return s.str();
}
static std::array<unsigned char,32> sha(const unsigned char* p,size_t n) {
    std::array<unsigned char,32> d{}; SHA256(p,n,d.data()); return d;
}
static B16 unhex16(const std::string& s) {
    if(s.size()!=32) throw std::runtime_error("bad 16-byte hex");
    B16 b{}; for(size_t i=0;i<16;i++) b[i]=static_cast<unsigned char>(std::stoul(s.substr(2*i,2),nullptr,16)); return b;
}
static std::array<unsigned char,32> unhex32(const std::string& s) {
    if(s.size()!=64) throw std::runtime_error("bad SHA256 hex");
    std::array<unsigned char,32> b{}; for(size_t i=0;i<32;i++) b[i]=static_cast<unsigned char>(std::stoul(s.substr(2*i,2),nullptr,16)); return b;
}
static B16 reduce(const B16& p,const B16& m) {
    B16 c{}; for(size_t i=0;i<16;i++) c[i]=p[i]^m[i]; return c;
}
static bool match(const B16& p,const B16& m,const std::array<unsigned char,32>& target) {
    const B16 c=reduce(p,m); return sha(c.data(),16)==target;
}

struct Rec { std::string ts,attempt,state,cls,payload,dest; };

int main(int argc,char** argv) {
    try {
        if(argc!=4) throw std::runtime_error("usage: sft spool.log recovery-routing.json acceptance.json");
        const std::string spool=read_file(argv[1]), route=read_file(argv[2]), acceptance=read_file(argv[3]);
        const auto sh=sha(reinterpret_cast<const unsigned char*>(spool.data()),spool.size());
        const auto rh=sha(reinterpret_cast<const unsigned char*>(route.data()),route.size());
        const auto ah=sha(reinterpret_cast<const unsigned char*>(acceptance.data()),acceptance.size());
        if(hex(sh.data(),32)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083") throw std::runtime_error("spool SHA mismatch");
        if(hex(rh.data(),32)!="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5") throw std::runtime_error("route SHA mismatch");
        if(hex(ah.data(),32)!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f") throw std::runtime_error("acceptance SHA mismatch");

        const std::regex same(R"(JOB=PS-261003-0417 ATTEMPT=([0-9]+) STATE=([A-Z]+) CLASS=([A-Z]+) PAYLOAD=([0-9A-F]{32}) DEST=([a-z]+))");
        const std::array<std::string,4> times={"2026-10-03T16:45:00+00:00","2026-10-03T18:01:00Z","2026-10-03T18:02:00Z","2026-10-03T18:03:00Z"};
        const std::array<std::string,4> attempts={"1","1","2","3"}, states={"ACK","REQUESTED","ACK","REQUESTED"}, classes={"LABEL","RECOVER","RECOVER","RECOVER"};
        std::array<B16,4> same_payloads{}; size_t same_n=0;
        std::istringstream input(spool); std::string line;
        while(std::getline(input,line)) {
            if(line.find("JOB=PS-261003-0417")==std::string::npos) continue;
            std::smatch m; if(!std::regex_search(line,m,same)) throw std::runtime_error("unparsed same-job line");
            if(same_n>=4 || line.substr(0,line.find(' '))!=times[same_n] || m[1]!=attempts[same_n] || m[2]!=states[same_n] || m[3]!=classes[same_n] || m[5]!="bench")
                throw std::runtime_error("same-job chronology/state/class mismatch");
            same_payloads[same_n++]=unhex16(m[4]);
        }
        if(same_n!=4) throw std::runtime_error("expected four same-job payloads");

        const std::regex any(R"(JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+))");
        std::vector<B16> payloads; size_t target_index=static_cast<size_t>(-1);
        std::istringstream all(spool);
        while(std::getline(all,line)) {
            std::smatch m; if(!std::regex_search(line,m,any)) continue;
            if(m[1]=="PS-261003-0417" && m[2]=="2" && m[3]=="ACK" && m[4]=="RECOVER") target_index=payloads.size();
            payloads.push_back(unhex16(m[5]));
        }
        if(payloads.size()!=133 || target_index!=129 || hex(payloads[target_index].data(),16)!="a9a9dc5731a5e2ae879c47215c2559d5")
            throw std::runtime_error("original spool record count/selected ACK2 locator mismatch");

        const B16 mask=unhex16("8556C8CB6140A7F9A5123AC7571BEE1C");
        const auto target=unhex32("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
        std::cout<<"SOURCE_PINS_PASS spool="<<hex(sh.data(),32)<<" route="<<hex(rh.data(),32)<<" acceptance="<<hex(ah.data(),32)<<"\n";
        std::cout<<"SAME_JOB_RECORDS=4 indices=117,128,129,130 order=LABEL_ACK,RECOVER_REQUESTED1,RECOVER_ACK2,RECOVER_REQUESTED3\n";

        std::array<std::array<B4,26>,4> fragments{};
        for(size_t src=0;src<4;src++) for(size_t off=0;off<=12;off++) for(size_t rev=0;rev<2;rev++) {
            const size_t k=2*off+rev;
            for(size_t j=0;j<4;j++) fragments[src][k][j]=same_payloads[src][off+(rev?3-j:j)];
        }
        const std::array<int,4> plant_pick={1,7,15,24}, plant_order={2,0,3,1};
        uint64_t total=0;
        for(int mode=0;mode<2;mode++) {
            B16 planted{}; size_t pos=0;
            if(mode==0) for(int src:plant_order) for(unsigned char b:fragments[src][plant_pick[src]]) planted[pos++]=b;
            else for(size_t round=0;round<4;round++) for(int src:plant_order) planted[pos++]=fragments[src][plant_pick[src]][round];
            const auto planted_hash=sha(reduce(planted,mask).data(),16);
            std::array<int,4> order={0,1,2,3}; uint64_t checks=0,original_hits=0,planted_hits=0;
            do {
                for(int a=0;a<26;a++) for(int b=0;b<26;b++) for(int c=0;c<26;c++) for(int d=0;d<26;d++) {
                    const std::array<int,4> pick={a,b,c,d}; B16 coupon{}; pos=0;
                    if(mode==0) for(int src:order) for(unsigned char x:fragments[src][pick[src]]) coupon[pos++]=x;
                    else for(size_t round=0;round<4;round++) for(int src:order) coupon[pos++]=fragments[src][pick[src]][round];
                    const B16 component=reduce(coupon,mask); const auto digest=sha(component.data(),16);
                    if(digest==target) original_hits++;
                    if(digest==planted_hash) planted_hits++;
                    checks++;
                }
            } while(std::next_permutation(order.begin(),order.end()));
            if(checks!=10967424 || original_hits!=0 || planted_hits==0) throw std::runtime_error("fragment family control/count/hit assertion failed");
            std::cout<<(mode==0?"FOUR_SOURCE_CONCATENATED":"FOUR_SOURCE_ROUND_ROBIN")<<"_4BYTE_FRAGMENT_ASSIGNMENTS="<<checks<<" original_hits="<<original_hits<<" planted_hits="<<planted_hits<<"\n";
            total+=checks;
        }

        std::vector<unsigned char> raw; std::string hexstream;
        for(const auto& p:payloads) { raw.insert(raw.end(),p.begin(),p.end()); hexstream+=hex(p.data(),16); }
        const size_t rs=target_index*16, hs=target_index*32; uint64_t windows=0,window_hits=0;
        for(int off=-15;off<=15;off++) if(off!=0) {
            B16 c{}; std::copy_n(raw.begin()+static_cast<int64_t>(rs)+off,16,c.begin());
            if(match(c,mask,target)) window_hits++; windows++;
            std::reverse(c.begin(),c.end()); if(match(c,mask,target)) window_hits++; windows++;
        }
        for(int off=-31;off<=31;off++) if(off!=0) {
            const size_t start=static_cast<size_t>(static_cast<int64_t>(hs)+off); B16 c{};
            for(size_t j=0;j<16;j++) c[j]=static_cast<unsigned char>(std::stoul(hexstream.substr(start+2*j,2),nullptr,16));
            if(match(c,mask,target)) window_hits++; windows++;
            std::reverse(c.begin(),c.end()); if(match(c,mask,target)) window_hits++; windows++;
        }
        if(windows!=184 || window_hits!=0) throw std::runtime_error("target-including boundary-window assertion failed");

        // Positive control: a synthetic 16-byte coupon spans the byte boundary at target_start-7.
        std::vector<unsigned char> synthetic(payloads.size()*16,0); B16 plant{};
        for(size_t i=0;i<16;i++) plant[i]=static_cast<unsigned char>(0x31+i*7);
        const size_t planted_start=rs-7; std::copy(plant.begin(),plant.end(),synthetic.begin()+planted_start);
        const auto planted_hash=sha(reduce(plant,mask).data(),16); bool planted_found=false;
        for(int off=-15;off<=15;off++) if(off!=0) {
            B16 c{}; std::copy_n(synthetic.begin()+static_cast<int64_t>(rs)+off,16,c.begin());
            if(sha(reduce(c,mask).data(),16)==planted_hash) planted_found=true;
            std::reverse(c.begin(),c.end()); if(sha(reduce(c,mask).data(),16)==planted_hash) planted_found=true;
        }
        if(!planted_found) throw std::runtime_error("boundary planted positive failed");
        std::cout<<"TARGET_INCLUDING_RAW_HEX_BOUNDARY_WINDOWS="<<windows<<" original_hits="<<window_hits<<" planted_raw_boundary_control=PASS\n";
        total+=windows;
        std::cout<<"TOTAL_COMPLETE_ORIGINAL_CANDIDATE_CHECKS="<<total<<" original_hits=0\n";
        return 0;
    } catch(const std::exception& e) { std::cerr<<"ERROR: "<<e.what()<<"\n"; return 1; }
}
