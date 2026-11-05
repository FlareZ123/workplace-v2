#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Block=std::array<unsigned char,16>;
struct Base {std::string name;std::vector<std::string> words;};
const std::vector<std::string> lex={"a","after","almost","an","and","at","back","because","beside","copy","corridor","cup","desk","do","each","end","envelope","finally","finished","for","going","gone","good","had","hands","has","hold","i","in","is","it","just","kept","label","lamp","last","leave","leaves","like","line","little","long","making","margin","meant","mugs","my","never","next","night","not","of","official","on","only","other","outside","pair","people","photograph","put","quarterly","quiet","ready","remembered","remembers","report","room","sea","shorter","slogan","somebody","sound","standby","stays","stood","table","the","to","until","us","use","voices","wanted","was","watch","water","window","with","wording","words"};
const std::vector<Base> bases={
  {"N02",{"a","good","watch","leaves","the","room","ready","for","the","next","pair","of","hands"}},
  {"N06",{"the","little","lamp","stays","on","until","the","corridor","has","gone","quiet"}},
  {"N20-sea-time-table",{"the","sea","the","end","of","the","night","and","the","voices","at","the","table"}},
  {"MAIL11-desc",{"people","making","room","for","each","other","after","a","long","watch","with","the","water","outside","and","the","night","almost","finished"}},
  {"N13",{"at","the","end","of","the","night","the","mugs","stood","beside","the","window","and","somebody","had","remembered","to","leave","the","little","lamp","on"}},
  {"N23-UNTESTED",{"the","wording","in","my","margin","was","never","an","official","slogan","the","envelope","only","remembers","the","words","i","finally","put","on","it"}},
  {"N20-sea-table-time",{"the","sea","the","voices","at","the","table","and","the","end","of","the","night"}},
  {"N20-time-sea-table",{"the","end","of","the","night","the","sea","and","the","voices","at","the","table"}},
  {"N20-time-table-sea",{"the","end","of","the","night","the","voices","at","the","table","and","the","sea"}},
  {"N20-table-sea-time",{"the","voices","at","the","table","the","sea","and","the","end","of","the","night"}},
  {"N20-table-time-sea",{"the","voices","at","the","table","the","end","of","the","night","and","the","sea"}}
};
static unsigned char key[64],padin[64],padout[64];
static SHA256_CTX inBase,outBase;
static const unsigned char original[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static void hashSource(const std::string& path,const char* expected){
 std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("source missing "+path);
 SHA256_CTX c;SHA256_Init(&c);unsigned char buf[32768];
 while(f){f.read(reinterpret_cast<char*>(buf),sizeof(buf));auto n=f.gcount();if(n)SHA256_Update(&c,buf,size_t(n));}
 unsigned char d[32];SHA256_Final(d,&c);char hex[65];for(int i=0;i<32;i++)sprintf(hex+2*i,"%02x",d[i]);hex[64]=0;
 if(strcmp(hex,expected))throw std::runtime_error("original source digest changed "+path);
}
static void digest(const char* data,size_t len,unsigned char* out){
 SHA256_CTX c=inBase;SHA256_Update(&c,data,len);unsigned char inner[32];SHA256_Final(inner,&c);
 c=outBase;SHA256_Update(&c,inner,32);unsigned char hmac[32];SHA256_Final(hmac,&c);
 SHA256(hmac,16,out);
}
int main(int argc,char** argv){
 if(argc<3||argc>5){fprintf(stderr,"USAGE: k08_subseq_insertion /path/to/original-archive base_index [mask_start] [mask_end]\n");return 2;}
 std::string root=argv[1];int ix=atoi(argv[2]);if(ix<0||ix>=int(bases.size()))return 2;
 try{
 hashSource(root+"/evidence/crew/noticeboard-and-desk-notes.txt","13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb");
 hashSource(root+"/evidence/mail/11.eml","f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29");
 hashSource(root+"/acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
 }catch(const std::exception& e){fprintf(stderr,"SOURCE_PIN_FAILURE %s\n",e.what());return 2;}
 const char* k="5F933DA6A1BD03C32DA5CBC25344F497";
 for(int i=0;i<16;i++){unsigned x;sscanf(k+2*i,"%2x",&x);key[i]=static_cast<unsigned char>(x);}
 for(int i=0;i<64;i++){padin[i]=key[i]^0x36;padout[i]=key[i]^0x5c;}
 SHA256_Init(&inBase);SHA256_Update(&inBase,padin,64);
 SHA256_Init(&outBase);SHA256_Update(&outBase,padout,64);
 unsigned char d[32];
 const char* n02="a good watch leaves the room ready for the next pair of hands";
 digest(n02,strlen(n02),d);
 unsigned char known16[16]={0xbf,0x88,0x93,0x59,0xb0,0x30,0x3f,0x2b,0x2b,0x2f,0xd9,0x6a,0xe8,0x41,0x21,0x0b};
 unsigned char check[32];SHA256(known16,16,check);
 if(memcmp(check,d,32)){fprintf(stderr,"ORIGINAL_N02_HMAC_CONTROL_FAIL\n");return 2;}
 fprintf(stderr,"SOURCE_PIN_PASS lex=%zu N02_control=PASS\n",lex.size());
 const auto& base=bases[ix];int n=int(base.words.size());
 uint64_t total=uint64_t(1)<<n;
 uint64_t lo=argc>=4?strtoull(argv[3],nullptr,10):0,hi=argc>=5?strtoull(argv[4],nullptr,10):total;
 if(hi>total||lo>hi)return 2;
 // Freeze an in-family planted phrase separately for each actual source base.
 // Mask 0xF retains its first four original source words; the fifth is
 // exactly one inserted source-lexicon word, so every base has a real control.
 std::string planted;
 for(int i=0;i<4;i++){if(i)planted+=' ';planted+=base.words[i];}
 planted+=" sea";
 digest(planted.data(),planted.size(),d);
 unsigned char targetPlant[32];memcpy(targetPlant,d,32);
 unsigned long long checks=0,hits=0,plantedHits=0,eligible=0;
 char buff[512];
 for(uint64_t mask=lo;mask<hi;mask++){
  int count=__builtin_popcountll(mask);
  if(count<4||count>12)continue;
  std::vector<std::string> words;words.reserve(count);
  for(int k=0;k<n;k++)if(mask&(uint64_t(1)<<k))words.push_back(base.words[k]);
  eligible++;
  for(int gap=0;gap<=count;gap++){
   std::string before,after;
   for(int j=0;j<gap;j++){if(j)before+=' ';before+=words[j];}
   for(int j=gap;j<count;j++){if(j>gap)after+=' ';after+=words[j];}
   const size_t a=before.size(),b=after.size();
   if(a)memcpy(buff,before.data(),a);
   size_t at=a; if(a)buff[at++]=' ';
   for(const auto& word:lex){
    size_t used=at;
    memcpy(buff+used,word.data(),word.size());used+=word.size();
    if(b){buff[used++]=' ';memcpy(buff+used,after.data(),b);used+=b;}
    digest(buff,used,d);checks++;
    if(memcmp(d,original,32)==0){hits++;fprintf(stderr,"K08_HIT base=%s mask=%llu gap=%d caption=%.*s\n",base.name.c_str(),(unsigned long long)mask,gap,int(used),buff);}
    if(memcmp(d,targetPlant,32)==0)plantedHits++;
   }
  }
 }
 if(lo<=15&&15<hi&&plantedHits==0){fprintf(stderr,"PLANTED_COMPLETE_IN_FAMILY_CONTROL_FAIL\n");return 3;}
 fprintf(stdout,"BASE_DONE name=%s mask_range=[%llu,%llu) eligible_masks=%llu complete_checks=%llu original_hits=%llu planted_hits=%llu lex=%zu\n",base.name.c_str(),(unsigned long long)lo,(unsigned long long)hi,(unsigned long long)eligible,checks,hits,plantedHits,lex.size());
 return hits?1:0;
}
