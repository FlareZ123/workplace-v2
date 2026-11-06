// H17 selected coupon as a 3- or 4-share XOR of original source blocks.
// Read-only original commitment test; all selected ACK2 copied bytes withheld.
#include <array>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>
#include <sstream>
#include <openssl/sha.h>
using B = std::array<unsigned char,16>;
using D = std::array<unsigned char,32>;

std::string read(const std::string& p) {
    std::ifstream f(p, std::ios::binary); if(!f) throw std::runtime_error("cannot read "+p);
    return std::string(std::istreambuf_iterator<char>(f), {});
}
unsigned int hx(char c) { if(c>='0'&&c<='9') return c-'0'; if(c>='A'&&c<='F')return c-'A'+10; if(c>='a'&&c<='f')return c-'a'+10; throw std::runtime_error("bad hex"); }
template<size_t N> std::array<unsigned char,N> hex(const std::string& x) {
    if(x.size()!=2*N)throw std::runtime_error("incorrect hex field width");
    std::array<unsigned char,N> b{}; for(size_t i=0;i<N;i++)b[i]=(hx(x[2*i])<<4)|hx(x[2*i+1]); return b;
}
std::string field(const std::string& text,const std::string& name) {
    std::smatch m; if(!std::regex_search(text,m,std::regex("\\\""+name+"\\\"\\s*:\\s*\\\"([0-9A-Fa-f]+)\\\"")))throw std::runtime_error("field not found "+name);
    return m[1];
}
D hash(const B& b) {D d{}; SHA256(b.data(),b.size(),d.data()); return d;}
B x(const B&a,const B&b){B z{};for(size_t i=0;i<16;i++)z[i]=a[i]^b[i];return z;}
void require(bool yes, const std::string &msg){if(!yes)throw std::runtime_error(msg);}

int main(int argc,char**argv){
    if(argc!=2){std::cerr<<"usage: <program> /path/to/original/export/root\n";return 2;}
    const std::string root=argv[1];
    std::string spool=read(root+"/evidence/print/spool-reconstruction.log");
    std::array<unsigned char,32> sh{}; SHA256((const unsigned char*)spool.data(),spool.size(),sh.data());
    require(sh==hex<32>("7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"),"original spool hash drift");
    const std::string c=read(root+"/candidate.json"),route=read(root+"/evidence/recovery-routing.json"),accept=read(root+"/acceptance.json");
    std::vector<B> v;
    for(auto id: {"K01","K02","K03","K05","K06","K07"})v.push_back(hex<16>(field(c,id)));
    std::istringstream input(spool); std::string line;
    size_t rows=0,withheld=0;
    while(std::getline(input,line)) {
        std::smatch m;
        if(!std::regex_search(line,m,std::regex("PAYLOAD=([0-9A-Fa-f]{32})"))) continue;
        ++rows;
        if(line.find("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER ")!=std::string::npos){++withheld;continue;}
        v.push_back(hex<16>(m[1]));
    }
    require(rows==133&&withheld==1&&v.size()==138,"source counts changed");
    const B mask=hex<16>(field(route,"masked_component"));
    const D original=hex<32>(field(accept,"K04"));
    // Synthetic exact original-format positive commitments seeded by the first triple/quad.
    const D positive3=hash(x(x(x(v[0],v[1]),v[2]),mask));
    const D positive4=hash(x(x(x(x(v[0],v[1]),v[2]),v[3]),mask));
    uint64_t checks3=0,checks4=0,hits3=0,hits4=0,planted3=0,planted4=0;
    const int n=(int)v.size();
    for(int a=0;a<n-2;a++) for(int b=a+1;b<n-1;b++){
        B pair=x(v[a],v[b]);
        for(int k=b+1;k<n;k++){
            B triple=x(pair,v[k]);
            const D d3=hash(x(triple,mask));
            checks3++; hits3+=(d3==original); planted3+=(d3==positive3);
        }
    }
    for(int a=0;a<n-3;a++) for(int b=a+1;b<n-2;b++){
        B pair=x(v[a],v[b]);
        for(int k=b+1;k<n-1;k++){
            B triple=x(pair,v[k]);
            for(int l=k+1;l<n;l++){
                const D d4=hash(x(x(triple,v[l]),mask));
                checks4++;hits4+=(d4==original);planted4+=(d4==positive4);
            }
        }
    }
    require(checks3==428536&&checks4==14463090,"combinatorial count drift");
    require(planted3==1&&planted4==1,"planted positive not uniquely recovered");
    std::cout<<"SOURCE: "<<rows<<" printer entries, "<<withheld<<" selected ACK2 omitted, "<<v.size()<<" total original and accepted source blocks\n";
    std::cout<<"ORIGINAL: three_share_checks="<<checks3<<" hits="<<hits3<<" four_share_checks="<<checks4<<" hits="<<hits4<<"\n";
    std::cout<<"PLANTED: triple="<<planted3<<" quad="<<planted4<<"\n";
    return hits3||hits4 ? 3 : 0;
}
