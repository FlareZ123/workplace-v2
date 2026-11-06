// Historical H-17 K08, exactly two unobserved bigrams between any original crew-note source-word walks.
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
 void visit(int last,int length,int flags,int edits,const SHA256_CTX& ctx){
  if(length>=6&&flags==7&&edits==2)check(ctx);
  if(length==9)return;
  int missing=3-__builtin_popcount((unsigned)flags);
  if(9-length<missing)return;
  if(edits==2){
   for(int n:adj[last]){
    SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[n].data(),words[n].size());
    stack.push_back(n);visit(n,length+1,flags|motif[n],edits,next);stack.pop_back();
   }
  }else{
   for(size_t n=0;n<words.size();n++){
    SHA256_CTX next=ctx;SHA256_Update(&next," ",1);SHA256_Update(&next,words[n].data(),words[n].size());
    stack.push_back((int)n);visit((int)n,length+1,flags|motif[n],edits+(!original[last][n]),next);stack.pop_back();
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
 const std::regex hd("^(N[0-9][0-9]) / "),token("[A-Za-z0-9]+");
 const std::set<std::string> want={"N01","N02","N03","N04","N05","N06","N07","N08","N09","N10","N11","N12","N13","N14","N15","N16","N17","N18","N19","N20","N21","N22","N23","N24"};
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
 if(ids!=want||types.size()!=222||edges.size()!=348)throw std::runtime_error("source author/word/edge count");
 const std::vector<std::string> words(types.begin(),types.end());
 std::string vocab;for(const auto& word:words){if(!vocab.empty())vocab+='\n';vocab+=word;}
 const auto vocabHash=sha(vocab.data(),vocab.size());
 if(hex(vocabHash.data(),32)!="e5c52e87e6011a4f6b0f3317ec243a82d24a6d2cf7f131a2f8eb9c80e58556e0")throw std::runtime_error("vocab SHA mismatch");
 const size_t lo=std::stoull(argv[2]),hi=std::stoull(argv[3]);
 const std::array<size_t,11> bounds={0,23,46,69,92,115,138,161,184,207,222};
 const auto it=std::find(bounds.begin(),bounds.end(),lo);
 if(it==bounds.end()||std::next(it)==bounds.end()||hi!=*std::next(it))throw std::runtime_error("invalid predeclared first-word shard");
 std::vector<std::vector<int>> next(222);std::vector<std::vector<bool>> have(222,std::vector<bool>(222,false));
 for(int i=0;i<222;i++)for(int j=0;j<222;j++)if(edges.count(words[i]+" "+words[j])){have[i][j]=true;next[i].push_back(j);}
 std::vector<int> motifs(222);
 for(int i=0;i<222;i++)motifs[i]=((words[i]=="sea"||words[i]=="water")?1:0)|((words[i]=="night"||words[i]=="watch"||words[i]=="morning")?2:0)|((words[i]=="room"||words[i]=="voices"||words[i]=="table"||words[i]=="people")?4:0);
 const std::array<uint64_t,10> expected={39816584,25083546,31611175,23115709,27332591,61633230,19409430,66971456,85864353,12622143};
 const std::array<std::string,10> controls={"17 17 17 night and the sea the room","bench 17 17 night and the sea the room","confesses 17 17 night and the sea the room","envelope 17 17 night and the sea the room","heads 17 17 night and the sea the room","little 17 17 night and the sea the room","on 17 17 night and the sea the room","reports 17 17 night and the sea the room","table 17 17 night and the night the sea","weather 17 17 night and the sea the room"};
 const std::array<std::string,10> controlHash={"9d0adea9d0ce3ecb3a6c47d7d58ea49dc48982b1e6012218e376ef8bbf7c8f17","7d476110aaaf2a878c9fdbd122ec6f690dbfea93305c53799f1cdd5aae021fd5","103eb46b9867a108af2dcd8e75aa3ab7a6c6c26108d1885d6e80f750fdb632ae","d1d7d9abcf3b1352b645ef98361283933723de08add028f2bb94e55fa7939ef5","519f749f801922e2a1f2695f813cbc3e5252bb49024232fa9a7c7aff88e76426","c9e829fb07ff2401290db9c2300788cd73e567b0b78ce136406888da8efef020","f40a46c1ba15bb7c78dfda815b9a5fe25b2c3999904994e45e1ad3557420b58e","155b003f1309239ba404c5ac139d58709c56d9834bfee033cdc84e1012dcd535","dadc6e85f5d0679be31425d8fe84f5f66597655c4f5cfffc76e196a899f9263e","00ca701988be70e5576420600a0007bf7d1d7bbbe903002b2c97b21199fbefe2"};
 const int k=static_cast<int>(std::distance(bounds.begin(),it));Reducer reducer(unhex("5F933DA6A1BD03C32DA5CBC25344F497"));
 unsigned char out[16];reducer.commitText("a good watch leaves the room ready for the next pair of hands",out);
 if(hex(out,16)!="bf889359b0303f2b2b2fd96ae841210b")throw std::runtime_error("known N02 full HMAC control");
 const Digest plant=reducer.commitText(controls[k],out);if(hex(plant.data(),32)!=controlHash[k])throw std::runtime_error("independent planted digest mismatch");
 const auto targetv=unhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
 Digest target{};std::memcpy(target.data(),targetv.data(),32);
 Search s(reducer,words,next,have,motifs,target,plant,controls[k]);
 for(size_t ai=lo;ai<hi;ai++){
  SHA256_CTX ctx=reducer.inner;SHA256_Update(&ctx,words[ai].data(),words[ai].size());
  s.stack.push_back((int)ai);s.visit((int)ai,1,motifs[ai],0,ctx);s.stack.pop_back();
 }
 if(s.checked!=expected[k]||s.planted!=1)throw std::runtime_error("DP candidate cardinality / planted mismatch");
 std::cout<<"K08 BRIDGE original_source="<<hex(srcHash.data(),32)<<" vocabulary="<<words.size()<<" directed_edges="<<edges.size()
          <<" first_range="<<lo<<":"<<hi<<" checked="<<s.checked<<" original_hits="<<s.hits<<" planted_hits="<<s.planted<<std::endl;
 return 0;
}catch(const std::exception&e){std::cerr<<"FAIL: "<<e.what()<<std::endl;return 2;}}
