// Historical H-17 K08, exactly one unobserved bigram between Emily source-word walks.
// Run: k08_author_single_bridge <original-notes> <first-word-start> <first-word-end>
// C++17, OpenSSL libcrypto. Original acceptance and sources are read only.
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <regex>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Digest=std::array<unsigned char,32>;
Digest sha(const void* p,size_t n){Digest a{};SHA256((const unsigned char*)p,n,a.data());return a;}
std::string hex(const unsigned char* p,size_t n){const char* a="0123456789abcdef";std::string s;for(size_t i=0;i<n;i++){s+=a[p[i]>>4];s+=a[p[i]&15];}return s;}
std::vector<unsigned char> unhex(const std::string& s){std::vector<unsigned char> o;for(size_t i=0;i<s.size();i+=2)o.push_back((unsigned char)std::stoi(s.substr(i,2),nullptr,16));return o;}
struct Reducer {
 SHA256_CTX inner,outer;
 explicit Reducer(const std::vector<unsigned char>& key) {
  if(key.size()!=16)throw std::runtime_error("nonce width");
  unsigned char ip[64],op[64];for(int i=0;i<64;i++){unsigned char c=i<16?key[i]:0;ip[i]=c^0x36;op[i]=c^0x5c;}
  SHA256_Init(&inner);SHA256_Update(&inner,ip,64);SHA256_Init(&outer);SHA256_Update(&outer,op,64);
 }
 Digest commit(const SHA256_CTX& c,unsigned char out16[16]) const {
  SHA256_CTX x=c,y=outer;unsigned char i[32],o[32];SHA256_Final(i,&x);SHA256_Update(&y,i,32);SHA256_Final(o,&y);std::memcpy(out16,o,16);return sha(o,16);
 }
 Digest commitText(const std::string& s,unsigned char out16[16]) const {
  SHA256_CTX x=inner;SHA256_Update(&x,s.data(),s.size());return commit(x,out16);
 }
};
struct Search {
 const Reducer& reducer;
 const std::vector<std::string>& words;
 const std::vector<std::vector<int>>& adj;
 const std::vector<std::vector<bool>>& original;
 const std::vector<int>& motif;
 const Digest& target;
 const Digest& plantedHash;
 const std::string& plantedPhrase;
 std::vector<int> stack;
 uint64_t checked=0,hits=0,planted=0;
 Search(const Reducer& r,const std::vector<std::string>&w,const std::vector<std::vector<int>>&a,const std::vector<std::vector<bool>>&o,const std::vector<int>&f,const Digest&t,const Digest&ph,const std::string&pt):reducer(r),words(w),adj(a),original(o),motif(f),target(t),plantedHash(ph),plantedPhrase(pt){}
 std::string sentence() const {std::string text;for(int w:stack){if(!text.empty())text+=' ';text+=words[w];}return text;}
 void check(const SHA256_CTX& ctx) {
  unsigned char out[16];const Digest digest=reducer.commit(ctx,out);++checked;
  if(digest==target){++hits;std::cout<<"AUTHENTIC_K08 "<<sentence()<<" component="<<hex(out,16)<<std::endl;}
  if(digest==plantedHash){++planted;if(sentence()!=plantedPhrase)throw std::runtime_error("synthetic collision / wrong preimage");}
 }
 void visit(int last,int length,int flags,bool used,const SHA256_CTX& ctx){
  if(length>=6&&flags==7&&used)check(ctx);
  if(length==14)return;
  int missing=3-__builtin_popcount((unsigned)flags);
  if(14-length<missing)return;
  if(used){
   for(int n:adj[last]){
    SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[n].data(),words[n].size());
    stack.push_back(n);visit(n,length+1,flags|motif[n],true,next);stack.pop_back();
   }
  }else{
   for(size_t n=0;n<words.size();n++){
    SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[n].data(),words[n].size());
    stack.push_back((int)n);visit((int)n,length+1,flags|motif[n],!original[last][n],next);stack.pop_back();
   }
  }
 }
};
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("usage: <original-crew-notes> <lo> <hi>");
 std::ifstream f(argv[1],std::ios::binary);if(!f)throw std::runtime_error("original file unreadable");
 const std::string src((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 const auto srcHash=sha(src.data(),src.size());
 if(hex(srcHash.data(),32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw std::runtime_error("original notes hash");
 std::set<std::string> ids,types,edges;
 const std::regex hd("^(N[0-9][0-9]) / Emily "),token("[A-Za-z0-9]+");
 const std::set<std::string> want={"N02","N06","N10","N13","N17","N18","N20","N23"};
 for(size_t pos=0;pos<src.size();){
  const size_t stop=src.find('\n',pos);const std::string line=src.substr(pos,stop==std::string::npos?std::string::npos:stop-pos);pos=stop==std::string::npos?src.size():stop+1;
  std::smatch m;if(!std::regex_search(line,m,hd)||!want.count(m[1]))continue;
  if(!ids.insert(m[1]).second)throw std::runtime_error("repeat note");
  const size_t stop2=src.find('\n',pos);const std::string body=src.substr(pos,stop2==std::string::npos?std::string::npos:stop2-pos);
  std::string prev;
  for(std::sregex_iterator it(body.begin(),body.end(),token),end;it!=end;++it){
   std::string w=it->str();std::transform(w.begin(),w.end(),w.begin(),[](unsigned char c){return (char)std::tolower(c);});
   types.insert(w);if(!prev.empty())edges.insert(prev+" "+w);prev=w;
  }
 }
 if(ids!=want||types.size()!=90||edges.size()!=130)throw std::runtime_error("source author/word/edge count");
 const std::vector<std::string> words(types.begin(),types.end());
 std::string vocab;for(const auto& word:words){if(!vocab.empty())vocab+='\n';vocab+=word;}
 const auto vocabHash=sha(vocab.data(),vocab.size());
 if(hex(vocabHash.data(),32)!="a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261")throw std::runtime_error("vocab SHA mismatch");
 const size_t lo=std::stoull(argv[2]),hi=std::stoull(argv[3]);
 if(lo>=90||hi!=lo+9||lo%9!=0)throw std::runtime_error("use exactly a nine-word matrix partition");
 std::vector<std::vector<int>> next(90);std::vector<std::vector<bool>> have(90,std::vector<bool>(90,false));
 for(int i=0;i<90;i++)for(int j=0;j<90;j++)if(edges.count(words[i]+" "+words[j])){have[i][j]=true;next[i].push_back(j);}
 std::vector<int> motifs(90);
 for(int i=0;i<90;i++)motifs[i]=((words[i]=="sea"||words[i]=="water")?1:0)|((words[i]=="night"||words[i]=="watch"||words[i]=="morning")?2:0)|((words[i]=="room"||words[i]=="voices"||words[i]=="table"||words[i]=="people")?4:0);
 const std::array<uint64_t,10> expected={96229895,16772290,61431136,29988881,58379552,74722555,50200343,109378311,116660807,77991768};
 const std::array<std::string,10> controls={
  "a good watch sea the room","board night the sea the room","draft the night the room sea","had night the sea the room","kept night the sea the room",
  "little night the sea the room","of the night the room sea","ready night the sea the room","somebody night the sea the room","us night the sea the room"
 };
 const std::array<std::string,10> controlHash={
  "e04bbb8ecd7c0c3073c6de50e1799a9ffcef1704104a47e77a266176f74fe9bd","21367c776baa229afed7a294cee8381fa0307b361beaa4aa12836f30de8fd3e4",
  "12e913efcf7d0af97358c636ec0ea9ec23dd7a68c0aa6b8d9a199c74fb9cb916","fafd044e3ac162718354343ac9a279927daaf030fc56eb46c75d0f74f9fa32be",
  "bfe12fd14b2019eac964da1019d496d5e72cd7300cd01e73b391aed78a915f3e","1d9681650c845e5e1bb30d763c00910072f8c73d00daa1eec50e6324c02d0f9f",
  "0bada22bb40d6cbf592b6ac60d352fb06db2d1bf449917b51f0e9cbe6b3e39ae","604c296061794a2d3e2225b06196691edee1e1bb13f4b72f748533125fba22ab",
  "7ce4fdcf406294a9ab9894478592db2a91bcdd9600af77d0ad6f3596dd2e2b31","1449b48eba5d6ed8375a8540d1422a76559445ef79b8a8aee4880b8e586c1871"
 };
 const int k=lo/9;Reducer reducer(unhex("5F933DA6A1BD03C32DA5CBC25344F497"));
 unsigned char out[16];reducer.commitText("a good watch leaves the room ready for the next pair of hands",out);
 if(hex(out,16)!="bf889359b0303f2b2b2fd96ae841210b")throw std::runtime_error("known N02 full HMAC control");
 const Digest plant=reducer.commitText(controls[k],out);if(hex(plant.data(),32)!=controlHash[k])throw std::runtime_error("independent planted digest mismatch");
 const auto targetv=unhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
 Digest target{};std::memcpy(target.data(),targetv.data(),32);
 Search s(reducer,words,next,have,motifs,target,plant,controls[k]);
 for(size_t ai=lo;ai<hi;ai++){
  SHA256_CTX ctx=reducer.inner;SHA256_Update(&ctx,words[ai].data(),words[ai].size());
  s.stack.push_back((int)ai);s.visit((int)ai,1,motifs[ai],false,ctx);s.stack.pop_back();
 }
 if(s.checked!=expected[k]||s.planted!=1)throw std::runtime_error("DP candidate cardinality / planted mismatch");
 std::cout<<"K08 BRIDGE original_source="<<hex(srcHash.data(),32)<<" vocabulary="<<words.size()<<" directed_edges="<<edges.size()
          <<" first_range="<<lo<<":"<<hi<<" checked="<<s.checked<<" original_hits="<<s.hits<<" planted_hits="<<s.planted<<std::endl;
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<std::endl;return 2;}}
