// H-17 K08 present-tense scene reconstruction; C++17 with OpenSSL libcrypto.
// Usage: binary resources/evidence/crew/noticeboard-and-desk-notes.txt
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
static const vector<string> sea={
"the sea is outside","the sea is still outside","the sea is beyond the window",
"the water is beyond the window","the sea stays outside","the sea keeps watch outside",
"the sea is waiting outside","the sea waits outside","the sea is outside the window",
"outside the sea is waiting","outside the sea waits","the sea goes on outside",
"the sea will still be there","the sea is at the window","the water is outside",
"the water stays outside","the sea keeps the night","the sea holds the night",
"the sea waits for daylight","the water waits for daylight","the sea is in the dark",
"the sea is on the other side of the glass","the night is out at sea",
"outside the sea keeps its watch","the sea has its own watch",
"the water holds the last of the night","outside the water keeps moving",
"the sea is still there","the water is still there","outside the sea is dark"
};
static const vector<string> night={
"the night is nearly finished","the night is almost finished",
"the night is nearly over","the night is almost over","the night is ending",
"the night is coming to an end","the long watch is almost over",
"the long watch is nearly done","the watch is nearly finished","the shift is almost over",
"the last cup is empty","the last mug is empty","the last cup is almost finished",
"the first light is coming","daylight is near","morning is nearly here",
"morning is coming","the night gives way to morning","the night has nearly gone",
"the watch is almost done","the end of the night is near",
"the end of the watch is near","the night leaves us time",
"the last cup cools on the table"
};
static const vector<string> room={
"there is room at the table","there is room at the table for one more",
"there is still room for one more","there is always room for one more",
"there is room for each other","there is room for another cup",
"there is still room for another mug","we make room for one another",
"we make room for each other","we leave room for the next watch",
"the room has space for one more","we keep a place for one more",
"we keep a place at the table","we keep a chair at the table",
"we make room at the table","we always make room for each other",
"we save a seat for the next watch","the voices are still at the table",
"voices are still at the table","the voices stay at the table",
"there are voices at the table","the voices make room for one more",
"our voices stay at the table","the mugs are still by the window",
"the mugs are still on the table","the little lamp stays on",
"the little lamp is still on","the light stays on at the table",
"the lamp stays on for the next watch","there is always another cup at the table",
"we leave the lamp on","we keep the little lamp on","someone remembers the lamp",
"someone keeps the lamp on","someone leaves a mug for the next watch",
"we count the mugs rather than the beds","the room still has voices at the table",
"the table has room for one more","the table keeps room for one more",
"there is always room for the next pair of hands"
};
static const vector<string> linkers={"and","but","while","as","when","with","even as","and still"};
static const vector<string> prefaces={"at the end of the night","at the end of a long night","after the last cup",
"after the last cup is finished","when the watch is nearly over","when the night is nearly finished",
"as the night comes to an end","after the long watch","as the last watch ends",
"with the water outside","with the sea outside","under the last of the night"};
static const array<unsigned char,16> nonce={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const array<unsigned char,32> target={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static string hex(const unsigned char* p,size_t n){const char* h="0123456789abcdef";string out;out.reserve(n*2);for(size_t i=0;i<n;++i){out+=h[p[i]>>4];out+=h[p[i]&15];}return out;}
static array<unsigned char,32> slot_digest(const string& phrase){
 unsigned char mac[EVP_MAX_MD_SIZE];unsigned int size=0;
 if(!HMAC(EVP_sha256(),nonce.data(),nonce.size(),reinterpret_cast<const unsigned char*>(phrase.data()),phrase.size(),mac,&size)||size!=32)throw runtime_error("HMAC error");
 array<unsigned char,32> digest{};SHA256(mac,16,digest.data());return digest;
}
int main(int argc,char** argv){
 if(argc!=2){cerr<<"usage: k08_present_habitual_scene_sft <original noticeboard-and-desk-notes.txt>\n";return 2;}
 ifstream in(argv[1],ios::binary);string source{istreambuf_iterator<char>(in),istreambuf_iterator<char>()};
 unsigned char hash[32];SHA256(reinterpret_cast<const unsigned char*>(source.data()),source.size(),hash);
 if(hex(hash,32)!="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb")throw runtime_error("original source SHA mismatch");
 unsigned char control[32];unsigned int ctrl_size=0;
 const string n02="a good watch leaves the room ready for the next pair of hands";
 HMAC(EVP_sha256(),nonce.data(),nonce.size(),reinterpret_cast<const unsigned char*>(n02.data()),n02.size(),control,&ctrl_size);
 if(ctrl_size!=32||hex(control,16)!="bf889359b0303f2b2b2fd96ae841210b")throw runtime_error("original N02 HMAC control mismatch");
 const string planted="the sea is outside while there is room at the table and the night is almost over";
 const auto planted_hash=slot_digest(planted);
 size_t tested=0,original_hits=0,synthetic_hits=0;
 auto check=[&](const string& candidate){const auto digest=slot_digest(candidate);++tested;if(digest==target){cout<<"K08_ORIGINAL_MATCH "<<candidate<<"\n";++original_hits;}if(digest==planted_hash)++synthetic_hits;};
 const auto start=chrono::steady_clock::now();
 array<int,3> order={0,1,2};
 do{
  for(const string& a:sea)for(const string& b:room)for(const string& c:night){
   const array<const string*,3> pieces={&a,&b,&c};
   for(const string& l1:linkers)for(const string& l2:linkers)
    check(*pieces[order[0]]+" "+l1+" "+*pieces[order[1]]+" "+l2+" "+*pieces[order[2]]);
  }
 }while(next_permutation(order.begin(),order.end()));
 const size_t triple_count=6ull*sea.size()*room.size()*night.size()*linkers.size()*linkers.size();
 for(const string& p:prefaces)for(const string& a:sea)for(const string& b:room)for(const string& l:linkers){
  check(p+" "+a+" "+l+" "+b);check(p+" "+b+" "+l+" "+a);
 }
 const size_t temporal_count=2ull*prefaces.size()*sea.size()*room.size()*linkers.size();
 if(tested!=triple_count+temporal_count||synthetic_hits!=1)throw runtime_error("enumeration or synthetic-positive control failure");
 cout<<"K08_PRESENT_SCENE_COMPLETE source_SHA_PASS original_N02_HMAC_PASS triples="<<triple_count<<" temporal="<<temporal_count<<" tested="<<tested<<" original_hits="<<original_hits<<" synthetic_hits="<<synthetic_hits<<" seconds="<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"\n";
 return original_hits?1:0;
}
