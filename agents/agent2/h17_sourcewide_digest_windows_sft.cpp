// H-17 K04/K08: bounded source-substring digest reconstruction, read-only SFT.
// C++17, OpenSSL libcrypto. The PDF is deliberately excluded; it is encrypted.
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
namespace fs=filesystem;
using Block=array<unsigned char,16>;
using Hash=array<unsigned char,32>;
static Block block(string s){
 Block b{};
 if(s.size()!=32)throw runtime_error("hex length");
 for(int i=0;i<16;++i)b[i]=static_cast<unsigned char>(stoul(s.substr(i*2,2),nullptr,16));
 return b;
}
static Hash hashHex(string s){
 Hash b{};
 if(s.size()!=64)throw runtime_error("sha length");
 for(int i=0;i<32;++i)b[i]=static_cast<unsigned char>(stoul(s.substr(i*2,2),nullptr,16));
 return b;
}
static Hash sha(const Block& p){
 Hash out{};
 SHA256(p.data(),p.size(),out.data());
 return out;
}
static Hash k04ComponentHash(const Block& coupon,const Block& mask){
 Block c{};
 for(int i=0;i<16;++i)c[i]=coupon[i]^mask[i];
 return sha(c);
}
int main(int argc,char**argv){
 if(argc!=4){
  cerr<<"usage: sft evidence-directory start-index end-index\n";
  return 2;
 }
 const fs::path root=argv[1];
 const Hash target4=hashHex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0");
 const Hash target8=hashHex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747");
 const Block mask=block("8556C8CB6140A7F9A5123AC7571BEE1C");
 const EVP_MD* funcs[]={EVP_md5(),EVP_sha256()};
 vector<fs::path> paths;
 for(const auto& e:fs::recursive_directory_iterator(root))
  if(e.is_regular_file())paths.push_back(e.path());
 sort(paths.begin(),paths.end());
 const size_t first=stoul(argv[2]),last=stoul(argv[3]);
 if(first>last||last>paths.size())throw runtime_error("invalid shard range");
 unsigned long long files=0,windows=0,checks=0,hits=0;
 for(size_t i=first;i<last;++i){
  const auto& p=paths[i];
  if(p.extension()==".pdf"||p.extension()==".raw")continue;
  ifstream in(p,ios::binary);
  string text((istreambuf_iterator<char>(in)),istreambuf_iterator<char>());
  if(p.filename()=="spool-reconstruction.log"){
   const size_t start=text.find("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK");
   if(start==string::npos)throw runtime_error("selected source row missing");
   const size_t stop=text.find('\n',start);
   text.erase(start,(stop==string::npos?text.size():stop+1)-start);
  }
  ++files;
  for(size_t start=0;start<text.size();++start){
   const size_t bound=min<size_t>(256,text.size()-start);
   for(size_t len=1;len<=bound;++len){
    const auto* source=(const unsigned char*)text.data()+start;
    for(int algorithm=0;algorithm<2;++algorithm){
     unsigned char digest[32]{};
     unsigned digestLength=0;
     if(EVP_Digest(source,len,digest,&digestLength,funcs[algorithm],nullptr)!=1)
      throw runtime_error("source digest failure");
     for(int layout=0;layout<(algorithm==0?1:2);++layout){
      Block coupon{};
      memcpy(coupon.data(),digest+(layout==0?0:16),16);
      if(k04ComponentHash(coupon,mask)==target4 || sha(coupon)==target8){
       ++hits;
       cerr<<"ORIGINAL_HIT file="<<p<<" offset="<<start<<" len="<<len
           <<" algorithm="<<algorithm<<" layout="<<layout<<"\n";
      }
      ++checks;
     }
    }
    ++windows;
   }
  }
 }
 // Planted complete-component controls: digest an independently indexed
 // substring, then require both exact full K04/K08 terminal reductions.
 const string payload="abc|the sea and the table|xyz",phrase="the sea and the table";
 const size_t position=payload.find(phrase);
 if(position==string::npos)throw runtime_error("control source missing");
 unsigned char a[32]{},b[32]{};
 unsigned sa=0,sb=0;
 if(EVP_Digest(phrase.data(),phrase.size(),a,&sa,EVP_md5(),nullptr)!=1 ||
    EVP_Digest(payload.data()+position,phrase.size(),b,&sb,EVP_md5(),nullptr)!=1)
  throw runtime_error("control producer");
 Block expected{},observed{};
 memcpy(expected.data(),a,16);
 memcpy(observed.data(),b,16);
 if(expected!=observed||
    k04ComponentHash(expected,mask)!=k04ComponentHash(observed,mask)||
    sha(expected)!=sha(observed))
  throw runtime_error("full-component positive failed");
 cout<<"SHARD="<<first<<".."<<last<<" FILES="<<files<<" WINDOWS="<<windows
     <<" CANDIDATES="<<checks<<" ORIGINAL_HITS="<<hits<<" PLANTED=PASS\n";
 return hits?1:0;
}
