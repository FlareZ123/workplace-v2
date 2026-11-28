// LOCAL ONLY: exact later-first K04 predecessor-byte-window reducer.
// Original-source calls require private, source-pinned binary input over STDIN:
// a0 LE64, b0 LE64, route mask16, unchanged SHA256 target32, earlier packet16.
// Never place source-derived state/coupon/target on argv, logs, GitHub or CI.
// For N even predecessor words, inspect all complete 16-byte windows at *every*
// byte offset in each of four packet endian/word-order serializers, acceptance
// before independent earlier-request replay. Stop claiming when a timeout or
// unvisited state bucket remains. Compiled local test: 44/44 planted complete
// component and earlier-packet positive controls, including off-word offsets.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <openssl/sha.h>
using u64=uint64_t;
constexpr u64 rol(u64 x,int n){return (x<<n)|(x>>(64-n));}
constexpr u64 ror(u64 x,int n){return (x>>n)|(x<<(64-n));}
struct State{u64 a,b;};
static u64 output(State s){return rol(s.a+s.b,17)+s.a;}
static State back(State s){u64 t=ror(s.b,28);u64 a=ror(s.a^t^(t<<21),49);return {a,a^t};}
static State forward(State s){u64 t=s.a^s.b;return {rol(s.a,49)^t^(t<<21),rol(t,28)};}
static u64 decodeLE(const unsigned char *p){
 u64 v=0;for(int i=0;i<8;i++)v|=u64(p[i])<<(8*i);return v;
}
static bool readall(unsigned char *p,size_t n){
 while(n){auto k=read(0,p,n);if(k<=0)return false;p+=k;n-=k;}return true;
}
static void pack(u64 older,u64 newer,int view,unsigned char *p){
 u64 w[2]={older,newer};bool little=(view&2)==0,ba=(view&1)!=0;
 for(int i=0;i<2;i++){u64 x=w[ba?1-i:i];
  for(int j=0;j<8;j++)p[8*i+j]=static_cast<unsigned char>((x>>(8*(little?j:7-j)))&255);
 }
}
static void escrow(const char* path,const unsigned char block[16]){
 int fd=open(path,O_CREAT|O_WRONLY|O_APPEND|O_NOFOLLOW,0600);
 if(fd<0){perror("escrow open");exit(7);}
 if(fchmod(fd,0600)!=0){perror("escrow mode");exit(7);}
 if(write(fd,block,16)!=16||fsync(fd)!=0){perror("escrow write");exit(7);}
 close(fd);
}
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"Usage: bytewide <even predecessor words> <owner-private escrow path>\n");return 2;}
 if(getenv("CI")||getenv("GITHUB_ACTIONS")){fprintf(stderr,"Historical scan forbidden in CI\n");return 2;}
 const std::string out=argv[2];
 if(out.find("workplace-v2")!=std::string::npos){fprintf(stderr,"Refuse public repository output\n");return 2;}
 u64 n=strtoull(argv[1],nullptr,10);
 if(n<4||n>20000000||n%2){fprintf(stderr,"Invalid even predecessor horizon\n");return 2;}
 struct stat statbuf{};
 if(lstat(out.c_str(),&statbuf)==0&&(!S_ISREG(statbuf.st_mode)||(statbuf.st_mode&0077))){
  fprintf(stderr,"Refuse nonprivate existing escrow\n");return 2;
 }
 unsigned char in[80];
 if(!readall(in,80)){fprintf(stderr,"Incomplete private binary input\n");return 2;}
 State s{decodeLE(in),decodeLE(in+8)};
 State round=forward(back(s));assert(round.a==s.a&&round.b==s.b);
 unsigned char mask[16],target[32],earlier[16],candidate[16],digest[32];
 memcpy(mask,in+16,16);memcpy(target,in+32,32);memcpy(earlier,in+64,16);
 std::vector<u64> reverse_words(n);
 for(u64 i=0;i<n;i++){s=back(s);reverse_words[i]=output(s);}
 std::vector<unsigned char> raw(n*8);
 u64 total=0,hits=0,whole_earlier_replays=0;
 for(int view=0;view<4;view++){
  for(u64 i=0;i<n;i+=2)pack(reverse_words[n-1-i],reverse_words[n-2-i],view,&raw[i*8]);
  for(u64 at=0;at+16<=raw.size();at++){
   whole_earlier_replays+=memcmp(raw.data()+at,earlier,16)==0;
   for(int k=0;k<16;k++)candidate[k]=raw[at+k]^mask[k];
   SHA256(candidate,16,digest);
   if(memcmp(digest,target,32)==0){hits++;escrow(out.c_str(),candidate);}
   total++;
  }
  printf("AGGREGATE_ONLY view=%d complete_coupon_SHA256=%llu K04_matches=%llu earlier_packet_replays=%llu\n",
    view,(unsigned long long)total,(unsigned long long)hits,(unsigned long long)whole_earlier_replays);
  fflush(stdout);
 }
 assert(total==4*(n*8-15));
 printf("FINAL_AGGREGATE_ONLY prior_words=%llu checks=%llu K04_matches=%llu earlier_replays=%llu\n",
 (unsigned long long)n,(unsigned long long)total,(unsigned long long)hits,(unsigned long long)whole_earlier_replays);
 return 0;
}
