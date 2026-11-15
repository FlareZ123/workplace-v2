// Agent14: bounded original-source K08 author N20 ordered-word reconstruction.
// Input: exact H-17 noticeboard original. No original evidence is modified.
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <algorithm>
#include <array>
#include <cassert>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

static const std::string kNotesSHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb";
static const std::string kK08SHA = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747";
static const std::string kN02HMAC16 = "bf889359b0303f2b2b2fd96ae841210b";
static const std::string kNonce = "5f933da6a1bd03c32da5cbc25344f497";

static std::array<unsigned char, 32> fromHex(const std::string& h) {
  std::array<unsigned char, 32> a{};
  for (size_t i=0;i<h.size()/2;i++) a[i]=static_cast<unsigned char>(std::stoul(h.substr(i*2,2),nullptr,16));
  return a;
}
static std::string hex(const unsigned char* p, size_t n) {
  const char* digits="0123456789abcdef";
  std::string s;
  for(size_t i=0;i<n;i++){s.push_back(digits[p[i]>>4]);s.push_back(digits[p[i]&15]);}
  return s;
}
static std::vector<std::string> words(const std::string& s) {
  std::vector<std::string> out;
  std::string word;
  for(unsigned char c:s){
    if((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')) word.push_back(static_cast<char>(std::tolower(c)));
    else if(!word.empty()){out.push_back(word);word.clear();}
  }
  if(!word.empty())out.push_back(word);
  return out;
}
struct HmacSha256 {
  SHA256_CTX initialInner{}, initialOuter{};
  HmacSha256(){
    auto raw = fromHex(kNonce);
    unsigned char ipad[64],opad[64];
    for(size_t i=0;i<64;i++){
      unsigned char b = i<16 ? raw[i] : 0;
      ipad[i] = b ^ 0x36;
      opad[i] = b ^ 0x5c;
    }
    SHA256_Init(&initialInner); SHA256_Update(&initialInner,ipad,64);
    SHA256_Init(&initialOuter); SHA256_Update(&initialOuter,opad,64);
  }
  void component(const char* p,size_t n,unsigned char* out) const {
    unsigned char innerDigest[32];
    SHA256_CTX in=initialInner;SHA256_Update(&in,p,n);SHA256_Final(innerDigest,&in);
    SHA256_CTX outer=initialOuter;SHA256_Update(&outer,innerDigest,32);SHA256_Final(out,&outer);
  }
  bool check(const char* p,size_t n,const std::array<unsigned char,32>& target,const std::array<unsigned char,32>& synthetic,bool& isPlanted)const {
    unsigned char comp[32],digest[32];
    component(p,n,comp);
    SHA256(comp,16,digest);
    isPlanted=CRYPTO_memcmp(digest,synthetic.data(),32)==0;
    return CRYPTO_memcmp(digest,target.data(),32)==0;
  }
};
static std::string lineAfter(const std::string& source,const std::string& marker){
  size_t i=source.find(marker);assert(i!=std::string::npos);
  size_t start=source.find('\n',i);assert(start!=std::string::npos);
  size_t end=source.find('\n',start+1);
  return source.substr(start+1,end-start-1);
}
static size_t phraseForMask(uint32_t mask,const std::vector<std::string>& src,char* buffer) {
  size_t len=0;
  for(size_t i=0;i<src.size();i++) if(mask&(1u<<i)){
    if(len)buffer[len++]=' ';
    std::memcpy(buffer+len,src[i].data(),src[i].size());len+=src[i].size();
  }
  return len;
}
int main(int argc,char** argv){
  if(argc!=2){std::cerr<<"Expected one original notes file path\n";return 2;}
  std::ifstream f(argv[1],std::ios::binary);if(!f){std::cerr<<"Source inaccessible\n";return 2;}
  std::string source((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
  unsigned char fileSha[32]; SHA256(reinterpret_cast<const unsigned char*>(source.data()),source.size(),fileSha);
  if(hex(fileSha,32)!=kNotesSHA){std::cerr<<"Original notes SHA mismatch\n";return 2;}
  std::string n20=lineAfter(source,"N20 / ");
  auto tokens=words(n20);
  if(tokens.size()!=30){std::cerr<<"N20 unexpectedly has "<<tokens.size()<<" tokens\n";return 2;}
  std::string n02=lineAfter(source,"N02 / ");
  n02=n02.substr(n02.find(':')+1);
  auto originalDraft=words(n02);
  char phrase[512];
  auto simpleJoin=[&](const std::vector<std::string>&v){
    size_t len=0;
    for(const auto& w:v){if(len)phrase[len++]=' ';std::memcpy(phrase+len,w.data(),w.size());len+=w.size();}
    return len;
  };
  HmacSha256 engine;
  auto n02len=simpleJoin(originalDraft);
  unsigned char draftComp[32]; engine.component(phrase,n02len,draftComp);
  if(hex(draftComp,16)!=kN02HMAC16){std::cerr<<"Authentic N02 HMAC control failed\n";return 2;}
  auto target=fromHex(kK08SHA);
  uint32_t anchors=(1u<<7)|(1u<<12)|(1u<<15)|(1u<<18);
  size_t plantedLength=phraseForMask(anchors,tokens,phrase);
  unsigned char plantComp[32]; engine.component(phrase,plantedLength,plantComp);
  unsigned char plantSha[32];SHA256(plantComp,16,plantSha);
  std::array<unsigned char,32> plant{}; std::copy(plantSha,plantSha+32,plant.begin());
  std::string plantPhrase(phrase,plantedLength);
  // Search A: every nonempty subsequence of Emily's exact first sentence (19 words).
  uint64_t nFirst=0, planted=0,orig=0;
  for(uint32_t mask=1;mask<(1u<<19);mask++){
    size_t len=phraseForMask(mask,tokens,phrase);
    bool isPlanted=false;
    if(engine.check(phrase,len,target,plant,isPlanted)){
      std::cout<<"ORIGINAL_K08_HIT=1 PHRASE="<<std::string(phrase,len)<<"\n";orig++;
    }
    planted+=isPlanted;
    nFirst++;
  }
  // Search B: every complete N20 ordered subsequence retaining the exact 4 motifs
  // emphasized by Emily: sea, night, voices, table. Includes both sentences.
  std::array<int,26> free{};int j=0;
  for(int i=0;i<30;i++)if((anchors&(1u<<i))==0)free[j++]=i;
  assert(j==26);
  uint64_t nAnchored=0;
  #pragma omp parallel reduction(+:nAnchored,planted,orig)
  {
    HmacSha256 h;
    char buf[512];
    #pragma omp for schedule(static)
    for(uint64_t sub=0;sub<(1ull<<26);sub++){
      uint32_t mask=anchors;
      for(int k=0;k<26;k++) if(sub&(1ull<<k))mask|=1u<<free[k];
      size_t len=phraseForMask(mask,tokens,buf);
      bool isPlanted=false;
      if(h.check(buf,len,target,plant,isPlanted)){
        #pragma omp critical
        std::cout<<"ORIGINAL_K08_HIT=1 PHRASE="<<std::string(buf,len)<<"\n";
        orig++;
      }
      planted+=isPlanted;
      nAnchored++;
    }
  }
  std::cout<<"N20_SOURCE_SHA_OK=1 N02_HMAC_OK=1\n"
    <<"FIRST_SENTENCE_ALL_NONEMPTY="<<nFirst<<"\n"
    <<"WHOLE_N20_FOUR_MOTIF_ANCHORED="<<nAnchored<<"\n"
    <<"PLANTED_PHRASE="<<plantPhrase<<" PLANTED_HITS="<<planted<<"\n"
    <<"ORIGINAL_K08_HITS="<<orig<<"\n";
  return (nFirst==524287 && nAnchored==(1ull<<26) && planted==2)? (orig?10:0) : 3;
}