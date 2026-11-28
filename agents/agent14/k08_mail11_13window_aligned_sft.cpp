#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Bytes32 = std::array<unsigned char,32>;

static std::string read_all(const std::string& p){
  std::ifstream f(p, std::ios::binary); if(!f) throw std::runtime_error("open "+p);
  std::ostringstream s; s<<f.rdbuf(); return s.str();
}
static std::string hex(const unsigned char* p,size_t n){
  static const char* h="0123456789abcdef"; std::string s; s.reserve(n*2);
  for(size_t i=0;i<n;i++){s.push_back(h[p[i]>>4]);s.push_back(h[p[i]&15]);} return s;
}
static Bytes32 sha256(const std::string& s){ Bytes32 d; SHA256((const unsigned char*)s.data(),s.size(),d.data()); return d; }
static std::vector<unsigned char> unhex(std::string s){
  if(s.size()%2) throw std::runtime_error("odd hex"); std::vector<unsigned char> v(s.size()/2);
  auto nib=[](char c)->int{if(c>='0'&&c<='9')return c-'0'; if(c>='a'&&c<='f')return c-'a'+10; if(c>='A'&&c<='F')return c-'A'+10; return -1;};
  for(size_t i=0;i<v.size();++i){int a=nib(s[2*i]),b=nib(s[2*i+1]); if(a<0||b<0)throw std::runtime_error("bad hex"); v[i]=(unsigned char)((a<<4)|b);} return v;
}
static std::vector<std::string> words(const std::string& s){
  std::vector<std::string> out; std::string cur;
  for(unsigned char c: s){
    if((c>='a'&&c<='z')||(c>='0'&&c<='9')) cur.push_back(c);
    else if(c>='A'&&c<='Z') cur.push_back((char)(c+32));
    else if(!cur.empty()){out.push_back(cur);cur.clear();}
  }
  if(!cur.empty())out.push_back(cur); return out;
}
static std::string join(const std::vector<std::string>& w){
  std::string s; for(size_t i=0;i<w.size();++i){if(i)s+=' ';s+=w[i];}return s;
}
static std::string note_body(const std::string& all, int n){
  char id[8]; std::snprintf(id,sizeof(id),"N%02d /",n);
  size_t p=all.find(id); if(p==std::string::npos) throw std::runtime_error("note missing");
  p=all.find('\n',p); if(p==std::string::npos) throw std::runtime_error("note body missing"); ++p;
  size_t e=all.find("\n\n",p); if(e==std::string::npos)e=all.size(); return all.substr(p,e-p);
}
static std::string post_label(std::string s){
  size_t p=s.find(": "); return p==std::string::npos?s:s.substr(p+2);
}
static std::string json_string(const std::string& s,const std::string& key){
  std::regex r("\\\""+key+"\\\"\\s*:\\s*\\\"([0-9A-Fa-f]+)\\\"");
  std::smatch m; if(!std::regex_search(s,m,r)) throw std::runtime_error("json key "+key); return m[1].str();
}
struct HmacFixed {
  SHA256_CTX inner0{}, outer0{};
  explicit HmacFixed(const std::vector<unsigned char>& key){
    unsigned char k[64]{};
    if(key.size()>64){unsigned char t[32]; SHA256(key.data(),key.size(),t); std::copy(t,t+32,k);}
    else std::copy(key.begin(),key.end(),k);
    unsigned char ip[64],op[64]; for(int i=0;i<64;i++){ip[i]=k[i]^0x36;op[i]=k[i]^0x5c;}
    SHA256_Init(&inner0); SHA256_Update(&inner0,ip,64);
    SHA256_Init(&outer0); SHA256_Update(&outer0,op,64);
  }
  void from_inner(SHA256_CTX in, unsigned char out[32]) const {
    unsigned char d[32]; SHA256_Final(d,&in);
    SHA256_CTX o=outer0; SHA256_Update(&o,d,32); SHA256_Final(out,&o);
  }
  std::array<unsigned char,16> digest16(const std::string& s) const {
    SHA256_CTX in=inner0; SHA256_Update(&in,s.data(),s.size());
    unsigned char d[32]; from_inner(in,d);
    std::array<unsigned char,16> r; std::copy(d,d+16,r.begin()); return r;
  }
};
static Bytes32 slot_hash(const unsigned char hmac[32]){
  Bytes32 d; SHA256(hmac,16,d.data()); return d;
}

int main(int argc,char**argv){
  if(argc!=3){std::cerr<<"usage: k08_mail11_13window_aligned_sft ROOT INDEX\n";return 2;}
  std::string root=argv[1]; int widx=std::stoi(argv[2]);
  std::string notes=read_all(root+"/evidence/crew/noticeboard-and-desk-notes.txt");
  auto nd=sha256(notes);
  if(hex(nd.data(),32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb") throw std::runtime_error("notes SHA");
  auto n02=words(post_label(note_body(notes,2)));
  auto n08=words(post_label(note_body(notes,8)));
  auto n09=words(post_label(note_body(notes,9)));
  if(n02.size()!=13||n08.size()!=13||n09.size()!=13) throw std::runtime_error("13-word invariant");

  std::string mail=read_all(root+"/evidence/mail/11.eml");
  auto md=sha256(mail);
  if(hex(md.data(),32)!="f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29") throw std::runtime_error("MAIL11 SHA");
  size_t a=mail.find("For this envelope"), b=mail.find("finished.",a);
  if(a==std::string::npos||b==std::string::npos) throw std::runtime_error("MAIL11 intent sentence");
  auto intent=words(mail.substr(a,b+9-a));
  if(intent.size()!=29||widx<0||widx>16) throw std::runtime_error("MAIL11 window invariant");
  std::vector<std::string> mw(intent.begin()+widx,intent.begin()+widx+13);
  std::array<std::vector<std::string>,4> rows{n02,n08,n09,mw};

  std::string route=read_all(root+"/evidence/recovery-routing.json");
  std::string acc=read_all(root+"/acceptance.json");
  auto key=unhex(json_string(route,"desk_nonce"));
  auto targetv=unhex(json_string(acc,"K08"));
  if(key.size()!=16||targetv.size()!=32) throw std::runtime_error("route/target width");
  HmacFixed hm(key);
  auto ctl=hm.digest16(join(n02));
  if(hex(ctl.data(),16)!="bf889359b0303f2b2b2fd96ae841210b") throw std::runtime_error("historical N02 HMAC control");

  auto plant16=hm.digest16(join(n02));
  unsigned char ph[32]{}; std::copy(plant16.begin(),plant16.end(),ph);
  auto plant_target=slot_hash(ph);
  unsigned long long expected_plant=1;
  for(int i=0;i<13;i++){
    int m=0; for(int r=0;r<4;r++) m += rows[r][i]==n02[i];
    expected_plant*=m;
  }

  std::array<unsigned char,32> target{};
  std::copy(targetv.begin(),targetv.end(),target.begin());
  std::atomic<unsigned long long> hits{0}, plant_hits{0}, leaves{0};
  const unsigned long long SHARDS=256;
  #pragma omp parallel for schedule(dynamic,1)
  for(unsigned long long shard=0; shard<SHARDS; ++shard){
    SHA256_CTX ctx=hm.inner0; unsigned long long x=shard;
    for(int pos=0;pos<4;pos++){
      int r=x&3; x>>=2; if(pos) SHA256_Update(&ctx," ",1);
      auto &w=rows[r][pos]; SHA256_Update(&ctx,w.data(),w.size());
    }
    struct Frame {int pos; SHA256_CTX ctx;};
    std::vector<Frame> st; st.push_back({4,ctx});
    while(!st.empty()){
      Frame f=st.back(); st.pop_back();
      if(f.pos==13){
        unsigned char h[32]; hm.from_inner(f.ctx,h); auto d=slot_hash(h);
        if(d==target) ++hits; if(d==plant_target) ++plant_hits; ++leaves; continue;
      }
      for(int r=0;r<4;r++){
        SHA256_CTX c=f.ctx; SHA256_Update(&c," ",1);
        auto &w=rows[r][f.pos]; SHA256_Update(&c,w.data(),w.size());
        st.push_back({f.pos+1,c});
      }
    }
  }
  if(leaves!=67108864ULL) throw std::runtime_error("assignment count");
  if(plant_hits!=expected_plant) throw std::runtime_error("planted enumeration control");
  std::cout<<"K08_MAIL11_WINDOW index="<<widx<<" assignments="<<leaves
           <<" original_hits="<<hits<<" planted_hits="<<plant_hits
           <<" expected_plant="<<expected_plant
           <<" historical_n02_control=PASS source13=PASS\n";
  return hits?3:0;
}
