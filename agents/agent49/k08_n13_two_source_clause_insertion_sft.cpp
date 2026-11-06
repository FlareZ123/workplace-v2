// Original-source SFT: exact two source-literal additions to Emily's 22-word N13.
// OpenSSL >=1.1.1; read-only; no guessed original wording used in construction.
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

static string slurp(const string &p) {
    ifstream f(p, ios::binary); if (!f) throw runtime_error("Missing source: " + p);
    return string(istreambuf_iterator<char>(f), {});
}
static string normalize(const string &s) {
    string out; bool space = true;
    for (unsigned char c: s) {
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) {out += char(c); space=false;}
        else if (c >= 'A' && c <= 'Z') {out += char(c+32);space=false;}
        else if (!space) {out += ' ';space=true;}
    }
    if (!out.empty() && out.back()==' ') out.pop_back();
    return out;
}
static vector<string> split(const string &s) {
    vector<string> v; string t;
    for(char c:s) {if (c==' ') {if(!t.empty()){v.push_back(t);t.clear();}}else t+=c;}
    if(!t.empty())v.push_back(t);return v;
}
static string join(const vector<string> &v,size_t a,size_t b) {
    string o;for(size_t i=a;i<b;++i){if(i>a)o+=' ';o+=v[i];}return o;
}
static map<int,string> notes_map(const string &raw) {
    map<int,string> out;size_t at=0;
    while(at<raw.size()){
        auto end=raw.find('\n',at);if(end==string::npos)end=raw.size();
        string line=raw.substr(at,end-at);
        if(line.size()>=6 && line[0]=='N' && isdigit(static_cast<unsigned char>(line[1])) && isdigit(static_cast<unsigned char>(line[2])) && line.substr(4,2)=="/ ") {
            const int id=(line[1]-'0')*10+(line[2]-'0');
            auto start=end+1;auto nxt=raw.find('\n',start);if(nxt==string::npos)nxt=raw.size();
            out[id]=raw.substr(start,nxt-start);
        }
        at=end+1;
    }
    return out;
}
static vector<string> spans(const vector<string> &texts,const set<string> &keys) {
    set<string> uniq;
    for(const string &t:texts){const auto w=split(normalize(t));
        for(size_t a=0;a<w.size();++a){for(size_t b=a+2;b<=w.size()&&b<=a+8;++b){
            bool found=false;for(size_t k=a;k<b;++k)if(keys.count(w[k])){found=true;break;}
            if(found) uniq.insert(join(w,a,b));
        }}
    }
    return vector<string>(uniq.begin(),uniq.end());
}
static array<unsigned char,16> fromhex16(const string &s){
    array<unsigned char,16> a{};
    if(s.size()!=32) throw runtime_error("bad hex");
    for(int i=0;i<16;++i){a[i]=static_cast<unsigned char>(stoul(s.substr(i*2,2),nullptr,16));}
    return a;
}
static array<unsigned char,32> fromhex32(const string &s){
    array<unsigned char,32> a{};if(s.size()!=64)throw runtime_error("bad sha");
    for(int i=0;i<32;++i){a[i]=static_cast<unsigned char>(stoul(s.substr(i*2,2),nullptr,16));}return a;
}
static array<unsigned char,32> digest(const string &s) {
    array<unsigned char,32> out{};SHA256(reinterpret_cast<const unsigned char*>(s.data()),s.size(),out.data());return out;
}
int main(){
    const auto clock0=chrono::steady_clock::now();
    const char *env=getenv("H17_SOURCE_ROOT");const string root=env ? string(env) : ".";
    const string note=slurp(root+"/resources/evidence/crew/noticeboard-and-desk-notes.txt");
    if(digest(note)!=fromhex32("13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"))throw runtime_error("Source SHA differs");
    auto notes=notes_map(note);if(notes.size()!=24)throw runtime_error("Notes extraction differs");
    auto base=split(normalize(notes.at(13)));if(base.size()!=22||join(base,0,6)!="at the end of the night")throw runtime_error("N13 mismatch");
    const string mail11=slurp(root+"/resources/evidence/mail/11.eml");
    const string mail12=slurp(root+"/resources/evidence/mail/12.eml");
    string e11=mail11.substr(mail11.find("\n\n")+2), e12=mail12.substr(mail12.find("\n\n")+2);
    const auto sea=spans({notes.at(1),notes.at(8),notes.at(14),notes.at(20),e11}, {"sea","water","outside","horizon"});
    const auto people=spans({notes.at(2),notes.at(3),notes.at(9),notes.at(11),notes.at(19),notes.at(20),e11,e12},
                            {"voices","table","people","room","somebody","mugs","cup","hands"});
    if(sea.size()!=171||people.size()!=331)throw runtime_error("Original source span mismatch: "+to_string(sea.size())+" / "+to_string(people.size()));
    const auto nonce=fromhex16("5F933DA6A1BD03C32DA5CBC25344F497");
    const auto official=fromhex32("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
    string n02=normalize(notes.at(2));n02=n02.substr(string("first draft for the crew board ").size());
    unsigned char h[32]{};unsigned int hlen=0;
    HMAC(EVP_sha256(),nonce.data(),16,reinterpret_cast<const unsigned char*>(n02.data()),n02.size(),h,&hlen);
    if(hlen!=32 || memcmp(h,fromhex16("BF889359B0303F2B2B2FD96AE841210B").data(),16))throw runtime_error("N02 HMAC control mismatch");
    const array<int,7> positions={6,8,12,14,16,21,22};
    const array<string,3> conn={"", "and ", "with "};
    const char *shard_env=getenv("H17_SEA_POS");
    const int focus=shard_env ? stoi(shard_env) : -1;
    uint64_t checked=0, planted_hits=0, hits=0;const map<int,string> planted_by_sea_position={
        {6,"5302506441a031f3df00aad528bf76694ab987df5276dd8548e76f454aec0c17"},
        {8,"3417e7217355359491e5b46bd436ca6256a870d86d6b1cf0a80a6071ba87fbfe"},
        {12,"44ec54e066814aa72f1ee00fadb0fc655e35bdd6b2952ad7e72f19c932409efc"},
        {14,"20fc49cb5c6acc219f5583a45a17f0754f4f12d660339217f0bc80da20f1b3b2"},
        {16,"7a2a98e5f26a63f62dca589886cd7223ba31b62857b186af2484a66a77c7bb88"},
        {21,"da3dce613b95b41f6a2fbea125d5875b52b8de731a5fe7a14b468340119c5348"},
        {22,"52516200f45920cee953d237dced1af7706600dad9b396825514ffedef8845fe"}
    };
    const auto planted=fromhex32(planted_by_sea_position.at(focus<0?6:focus));bool set_planted=false;
    string planted_example;
    for(int sp:positions){if(focus!=-1 && sp!=focus)continue;
        for(int pp:positions){if(sp==pp)continue;
        const int lo=min(sp,pp),hi=max(sp,pp);
        const string first=join(base,0,lo),middle=join(base,lo,hi),last=join(base,hi,base.size());
        const string tail=last.empty()?string():" "+last;
        for(const auto &a:sea){for(const auto &b:people){for(const auto &ca:conn){for(const auto &cb:conn){
            string sea_clause=ca+a, people_clause=cb+b;
            string phrase=(sp<pp)
                ? first+" "+sea_clause+" "+middle+" "+people_clause+tail
                : first+" "+people_clause+" "+middle+" "+sea_clause+tail;
            HMAC(EVP_sha256(),nonce.data(),16,reinterpret_cast<const unsigned char*>(phrase.data()),phrase.size(),h,&hlen);
            unsigned char slot_sha[32]{};SHA256(h,16,slot_sha);
            if(!set_planted){if(memcmp(slot_sha,planted.data(),32))throw runtime_error("Independent planted target mismatch");planted_example=phrase;set_planted=true;}
            if(!memcmp(slot_sha,planted.data(),32))++planted_hits;
            if(!memcmp(slot_sha,official.data(),32)){
                ++hits;cout<<"ORIGINAL_K08_MATCH "<<phrase<<"\n";
            }
            ++checked;
        }}}}
    }}
    const uint64_t expected=uint64_t(sea.size())*people.size()*(focus<0?7:1)*6*3*3;
    if(checked!=expected||planted_hits==0)throw runtime_error("Enumeration/planted control failure");
    const double elapsed=chrono::duration<double>(chrono::steady_clock::now()-clock0).count();
    cout<<"K08_N13_TWO_INSERT completed="<<checked<<" sea_spans="<<sea.size()<<" people_spans="<<people.size()
        <<" sea_pos="<<focus<<" positions=7 connectors=3 original_hits="<<hits<<" planted_hits="<<planted_hits<<" seconds="<<elapsed<<"\n";
    cout<<"PLANTED_EXAMPLE "<<planted_example<<"\n";
    return 0;
}
