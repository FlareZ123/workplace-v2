/* H-17: source-pinned K04 five-ticket numeric value transfer.
 * Actual source provides repair IDs, not authenticated coupon bytes.
 * Any placement of five original ticket values is an explicit hypothesis.
 * Compile with C++17 + OpenSSL; supply original resources root to run.
 */
#include <openssl/sha.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
using namespace std;
using B16=array<uint8_t,16>;
using B32=array<uint8_t,32>;

string readfile(const string &p){
    ifstream in(p,ios::binary);
    if(!in){fprintf(stderr,"MISSING %s\n",p.c_str());exit(2);}
    return string((istreambuf_iterator<char>(in)),{});
}
string shahex(const string &s){
    uint8_t h[32];
    SHA256((const uint8_t*)s.data(),s.size(),h);
    char out[65];
    for(int i=0;i<32;i++)sprintf(out+2*i,"%02x",h[i]);
    return string(out,64);
}
void pin(const string &root,const string &p,const string &sha){
    if(shahex(readfile(root+"/"+p))!=sha){
        fprintf(stderr,"SOURCE PIN FAILED %s\n",p.c_str());exit(2);
    }
}
B32 hash16(const B16 &x){B32 h{};SHA256(x.data(),x.size(),h.data());return h;}
B16 parse16(const char *s){
    B16 b{};
    for(int i=0;i<16;i++){unsigned x;if(sscanf(s+i*2,"%02x",&x)!=1)exit(2);b[i]=uint8_t(x);}
    return b;
}
B16 bytexor(const B16 &a,const B16 &b){
    B16 out{};for(int i=0;i<16;i++)out[i]=a[i]^b[i];return out;
}
string hex16(const B16 &x){
    char out[33];for(int i=0;i<16;i++)sprintf(out+i*2,"%02X",x[i]);return string(out,32);
}
int main(int argc,char **argv){
    if(argc!=2){fprintf(stderr,"Usage: %s ORIGINAL_RESOURCES_DIR\n",argv[0]);return 2;}
    string root=argv[1];
    const string fleet="evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt";
    const string spool="evidence/print/spool-reconstruction.log";
    pin(root,fleet,"10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf");
    pin(root,spool,"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083");
    pin(root,"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f");
    pin(root,"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5");
    string txt=readfile(root+"/"+fleet);
    const char* tickets[]={"L-29/N    01     ST-094","L-29/N    02     ST-081",
        "L-29/N    03     ST-106","L-29/N    04     ST-099","L-29/N    05     ST-112"};
    for(const auto x:tickets)if(txt.find(x)==string::npos){
        fprintf(stderr,"ORIGINAL TICKET MISMATCH\n");return 2;
    }
    txt=readfile(root+"/"+spool);
    const string row="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
    size_t index=txt.find(row);
    if(index==string::npos||txt.find(row,index+1)!=string::npos){
        fprintf(stderr,"SELECTED ACK SOURCE MISMATCH\n");return 2;
    }
    B16 copied=parse16("A9A9DC5731A5E2AE879C47215C2559D5");
    B16 mask=parse16("8556C8CB6140A7F9A5123AC7571BEE1C");
    const char* target="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
    B32 want{};
    for(int k=0;k<32;k++){unsigned x;sscanf(target+2*k,"%02x",&x);want[k]=uint8_t(x);}
    vector<array<int,5>> supports;
    for(int a=0;a<12;a++)for(int b=a+1;b<13;b++)
    for(int c=b+1;c<14;c++)for(int d=c+1;d<15;d++)
    for(int e=d+1;e<16;e++)supports.push_back({a,b,c,d,e});
    if(supports.size()!=4368)return 3;
    // In order: native integers; one-based adjustment; units; last two digits;
    // lower two-digit BCD; decimal digit sum; service-tab ordinal.
    int variants[7][5]={{94,81,106,99,112},{93,80,105,98,111},
        {4,1,6,9,2},{94,81,6,99,12},{0x94,0x81,0x06,0x99,0x12},
        {13,9,7,18,4},{1,2,3,4,5}};
    B16 synthetic=copied;
    const int loc[]={0,2,5,10,15};
    for(int i=0;i<5;i++)synthetic[loc[i]]=variants[0][i];
    B32 planted=hash16(bytexor(synthetic,mask));
    if(planted==want)return 3;
    uint64_t checks=0,positive=0,hits=0;
    for(const auto &variant:variants){
        array<int,5> vals;copy_n(variant,5,vals.begin());
        sort(vals.begin(),vals.end());
        do{
            for(const auto &pos:supports){
                for(int operation=0;operation<4;operation++){
                    B16 coupon=copied;
                    for(int j=0;j<5;j++){
                        uint8_t value=uint8_t(vals[j]);int k=pos[j];
                        if(operation==0)coupon[k]=value;
                        else if(operation==1)coupon[k]^=value;
                        else if(operation==2)coupon[k]=uint8_t(coupon[k]+value);
                        else coupon[k]=uint8_t(coupon[k]-value);
                    }
                    for(int stage=0;stage<2;stage++){
                        B16 candidate=stage==0?bytexor(coupon,mask):coupon;
                        B32 digest=hash16(candidate);checks++;
                        if(digest==planted)positive++;
                        if(digest==want){
                            hits++;
                            printf("K04 MATCH %s\n",hex16(candidate).c_str());
                        }
                    }
                }
            }
        }while(next_permutation(vals.begin(),vals.end()));
    }
    printf("RESULT source_pin=PASS checks=%llu original_hits=%llu synthetic_hits=%llu\n",
      (unsigned long long)checks,(unsigned long long)hits,(unsigned long long)positive);
    if(checks!=29352960ULL||positive<1)return 3;
    return hits?10:0;
}
