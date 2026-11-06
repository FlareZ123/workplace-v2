#include <openssl/sha.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using B16 = std::array<unsigned char,16>;
using B32 = std::array<unsigned char,32>;
struct Row { std::string job, attempt, state, cls, payload; };
struct Frag { std::array<unsigned char,4> b{}; int len=0, off=0, rev=0; };

static std::string read_file(const std::string& p) {
    std::ifstream f(p,std::ios::binary); if(!f) throw std::runtime_error("cannot open "+p);
    std::ostringstream s; s<<f.rdbuf(); return s.str();
}
static std::string sha_hex(const std::string& s) {
    unsigned char d[32]; SHA256((const unsigned char*)s.data(),s.size(),d);
    static const char* h="0123456789abcdef"; std::string o; o.reserve(64);
    for(unsigned char b:d){o.push_back(h[b>>4]);o.push_back(h[b&15]);} return o;
}
static unsigned char nib(char c) {
    if(c>='0'&&c<='9')return c-'0';
    if(c>='A'&&c<='F')return c-'A'+10;
    if(c>='a'&&c<='f')return c-'a'+10;
    throw std::runtime_error("invalid hex");
}
static B16 unhex16(const std::string& s) {
    if(s.size()!=32)throw std::runtime_error("expected 16-byte hex"); B16 b{};
    for(int i=0;i<16;i++)b[i]=(nib(s[2*i])<<4)|nib(s[2*i+1]); return b;
}
static B32 unhex32(const std::string& s) {
    if(s.size()!=64)throw std::runtime_error("expected 32-byte hex"); B32 b{};
    for(int i=0;i<32;i++)b[i]=(nib(s[2*i])<<4)|nib(s[2*i+1]); return b;
}
static std::string extract_value(const std::string& s,const std::string& key) {
    auto p=s.find(key); if(p==std::string::npos)throw std::runtime_error("missing key "+key);
    p=s.find('"',p+key.size()); if(p==std::string::npos)throw std::runtime_error("missing value quote");
    auto q=s.find('"',p+1); if(q==std::string::npos)throw std::runtime_error("missing closing quote");
    return s.substr(p+1,q-p-1);
}
static std::string field(const std::string& line,const std::string& key) {
    auto p=line.find(key); if(p==std::string::npos)return ""; p+=key.size();
    auto q=line.find(' ',p); return line.substr(p,q==std::string::npos?std::string::npos:q-p);
}
static B32 digest_coupon(const B16& coupon,const B16& mask) {
    B16 c{}; for(int i=0;i<16;i++)c[i]=coupon[i]^mask[i];
    B32 d{}; SHA256(c.data(),c.size(),d.data()); return d;
}
static std::string hex16(const B16& b) {
    static const char* h="0123456789ABCDEF"; std::string s; s.reserve(32);
    for(auto x:b){s.push_back(h[x>>4]);s.push_back(h[x&15]);}return s;
}
static Frag make_frag(const B16& p,int len,int off,int rev) {
    Frag f;f.len=len;f.off=off;f.rev=rev;
    for(int i=0;i<len;i++)f.b[i]=p[off+(rev?len-1-i:i)]; return f;
}

int main(int argc,char** argv) {
 try {
    if(argc<2||argc>3)throw std::runtime_error("usage: k04_ticket_five_part_fragment_sft <extracted-zip-root> [binder|chronological]");
    std::string root=argv[1];if(!root.empty()&&root.back()!='/')root+='/';
    const std::string order_name=argc==3?argv[2]:"binder";
    const std::string spool=read_file(root+"evidence/print/spool-reconstruction.log");
    const std::string fleet=read_file(root+"evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt");
    const std::string supplier=read_file(root+"evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv");
    const std::string route=read_file(root+"evidence/recovery-routing.json");
    const std::string acceptance=read_file(root+"acceptance.json");
    if(sha_hex(spool)!="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083")throw std::runtime_error("spool SHA mismatch");
    if(sha_hex(fleet)!="10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf")throw std::runtime_error("fleet SHA mismatch");
    if(sha_hex(supplier)!="73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e")throw std::runtime_error("supplier SHA mismatch");
    if(sha_hex(route)!="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5")throw std::runtime_error("route SHA mismatch");
    if(sha_hex(acceptance)!="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")throw std::runtime_error("acceptance SHA mismatch");
    if(fleet.find("PS-261003-0417   ESC-N           L-29/N        FA-17       H17-POL-17/A3")==std::string::npos)throw std::runtime_error("selected cassette route mismatch");
    const std::array<std::string,5> ticket_lines={
      "L-29/N    01     ST-094           lid plate, return",
      "L-29/N    02     ST-081           edge guide, exchange",
      "L-29/N    03     ST-106           separator, refit",
      "L-29/N    04     ST-099           hinge, retain",
      "L-29/N    05     ST-112           catch, clean"};
    for(const auto& x:ticket_lines)if(fleet.find(x)==std::string::npos)throw std::runtime_error("binder index mismatch: "+x);
    const std::array<std::string,5> supplier_rows={
      "ST-094,L29,R3,POSTED,FA-17,H17-POL-17/A3,18.40,lid-plate labour",
      "ST-081,L29,R3,POSTED,FA-17,H17-POL-17/A3,4.20,guide rail",
      "ST-106,L29,R3,POSTED,FA-17,H17-POL-17/A3,12.50,separator fitting",
      "ST-099,L29,R3,POSTED,FA-17,H17-POL-17/A3,0.00,hinge realignment",
      "ST-112,L29,R3,POSTED,FA-17,H17-POL-17/A3,0.00,catch cleaning"};
    for(const auto& x:supplier_rows)if(supplier.find(x)==std::string::npos)throw std::runtime_error("R3 supplier row mismatch: "+x);
    if(supplier.find("ST-112,L29,R4,HELD,FA-17,H17-POL-17/A4,0.00,duplicate settlement")==std::string::npos)throw std::runtime_error("ST-112 held duplicate control missing");
    const B16 mask=unhex16(extract_value(route,"\"masked_component\":"));
    const B32 target=unhex32(extract_value(acceptance,"\"K04\":"));

    std::vector<Row> rows;std::istringstream in(spool);std::string line;
    while(std::getline(in,line)){std::string job=field(line,"JOB="),payload=field(line,"PAYLOAD=");if(job.empty())continue;
      rows.push_back({job,field(line,"ATTEMPT="),field(line,"STATE="),field(line,"CLASS="),payload});}
    if(rows.size()!=133)throw std::runtime_error("expected 133 payload records");
    // Hypothesis only: interpret each one-based N ticket suffix as a one-based
    // payload-record ordinal. The source does not explicitly document this mapping.
    const std::array<int,5> tickets={94,81,106,99,112};
    const std::array<std::string,5> expected_jobs={"PS-261003-0393","PS-261003-0380","PS-261003-0405","PS-261003-0398","PS-261003-0411"};
    std::array<B16,5> donors{};
    for(int i=0;i<5;i++){const Row& r=rows[tickets[i]-1];if(r.job!=expected_jobs[i]||r.attempt!="1"||r.state!="ACK")throw std::runtime_error("ticket-indexed spool record mismatch");donors[i]=unhex16(r.payload);}
    const Row& selected=rows[129];
    if(selected.job!="PS-261003-0417"||selected.attempt!="2"||selected.state!="ACK"||selected.cls!="RECOVER")throw std::runtime_error("selected ACK2 record mismatch");
    const B16 selected_copy=unhex16(selected.payload);

    // Each of five ticket-indexed payloads contributes one contiguous fragment.
    // The coupon is partitioned 4+3+3+3+3; the 4-byte fragment may belong to
    // any part. Fragments may be read forward or backward.
    std::array<std::vector<Frag>,5> opts3,opts4;
    for(int r=0;r<5;r++){
      for(int off=0;off<=13;off++)for(int rev=0;rev<2;rev++)opts3[r].push_back(make_frag(donors[r],3,off,rev));
      for(int off=0;off<=12;off++)for(int rev=0;rev<2;rev++)opts4[r].push_back(make_frag(donors[r],4,off,rev));
    }
    const std::array<int,5> binder={0,1,2,3,4};
    const std::array<int,5> chronological={1,0,3,2,4};
    std::array<int,5> order{};
    if(order_name=="binder")order=binder;
    else if(order_name=="chronological")order=chronological;
    else throw std::runtime_error("order must be binder or chronological");
    // Planted complete-coupon positive control using the selected order.
    const std::array<int,5> planted_lengths={4,3,3,3,3};
    const std::array<int,5> planted_options={2,5,10,15,20};
    B16 planted{};int pp=0;
    for(int k=0;k<5;k++){const Frag& f=(planted_lengths[k]==4?opts4[order[k]][planted_options[k]]:opts3[order[k]][planted_options[k]]);for(int j=0;j<f.len;j++)planted[pp++]=f.b[j];}
    if(pp!=16)throw std::runtime_error("planted coupon length mismatch");
    const B32 planted_target=digest_coupon(planted,mask);if(planted_target==target)throw std::runtime_error("planted target collision");

    uint64_t tested=0,original_hits=0,planted_hits=0,selected_copy_hits=0;
    auto scan_order=[&](const std::array<int,5>& selected_order){
      for(int long_pos=0;long_pos<5;long_pos++){
        std::array<int,5> lengths={3,3,3,3,3};lengths[long_pos]=4;
        std::array<int,5> opt{};
        auto rec=[&](auto&& self,int k)->void{
          if(k==5){
            B16 coupon{};int pos=0;
            for(int q=0;q<5;q++){const Frag& f=(lengths[q]==4?opts4[selected_order[q]][opt[q]]:opts3[selected_order[q]][opt[q]]);for(int j=0;j<f.len;j++)coupon[pos++]=f.b[j];}
            if(pos!=16)throw std::runtime_error("candidate length mismatch");
            const B32 d=digest_coupon(coupon,mask);
            if(d==target){original_hits++;std::cout<<"ORIGINAL_HIT coupon="<<hex16(coupon)<<" order=";for(int x:selected_order)std::cout<<x<<",";std::cout<<" long_pos="<<long_pos<<" opts=";for(int x:opt)std::cout<<x<<",";std::cout<<"\n";}
            if(d==planted_target)planted_hits++;
            if(coupon==selected_copy)selected_copy_hits++;
            tested++;return;
          }
          const int n=(lengths[k]==4?26:28);
          for(int v=0;v<n;v++){opt[k]=v;self(self,k+1);}
        };
        rec(rec,0);
      }
    };
    scan_order(order);
    const uint64_t expected=5ULL*26ULL*28ULL*28ULL*28ULL*28ULL;
    if(tested!=expected||original_hits!=0||planted_hits<1)throw std::runtime_error("coverage or result assertion failed");
    std::cout<<"SOURCE_PINS_PASS payload_records=133 binder_tickets=94,81,106,99,112 selected_index0=129\n";
    std::cout<<"MODEL=5_ticket_fragments_partition_4_3_3_3_3 order="<<order_name<<" orientations=forward_or_reverse\n";
    std::cout<<"ASSIGNMENTS="<<tested<<" ORIGINAL_K04_HITS="<<original_hits<<" PLANTED_HITS="<<planted_hits
             <<" SELECTED_ACK2_RECONSTRUCTIONS="<<selected_copy_hits<<"\n";
    std::cout<<"PLANTED_COUPON="<<hex16(planted)<<" PLANTED_TARGET=";
    static const char* h="0123456789abcdef";for(unsigned char b:planted_target)std::cout<<h[b>>4]<<h[b&15];std::cout<<"\n";
    return 0;
 }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
