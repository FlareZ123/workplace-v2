/* H-17 K04: copied prefix from same-job intact buffer; next three bytes free.
   Original source, mask and acceptance are read-only. C11 + OpenSSL.
*/
#define OPENSSL_API_COMPAT 0x10100000L
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static const uint8_t copied[16]={0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t mask[16]={0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint8_t donors[3][16]={
 {0xe1,0xe6,0x0d,0x5f,0x6b,0x6d,0xd2,0x22,0x5f,0xa6,0xd5,0xa2,0xa6,0x3a,0xd9,0x32},
 {0xcd,0x3e,0x4f,0x21,0x6a,0xdb,0x2f,0xb1,0x80,0xda,0x2a,0xa9,0x0b,0x33,0xf7,0xa4},
 {0x44,0xd5,0x3d,0xfc,0x29,0xd7,0x94,0x3a,0x95,0xd8,0x93,0x71,0xda,0x58,0xec,0x64}
};
static const unsigned target[8]={0x930a52a1,0xbab97ca2,0x96633213,0x7c99e992,0x98ea6182,0xfb32ab63,0xa3421dfb,0x4fd8c9e0};
static const char* spool_sha="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char* expected_row="2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench";
static void fail(const char* s){fprintf(stderr,"ERROR %s\n",s);exit(3);}
static void verify_spool(const char* path){
 FILE* f=fopen(path,"rb");if(!f)fail("cannot open original spool");
 if(fseek(f,0,SEEK_END))fail("seek");
 long size=ftell(f);
 if(size<1||size>1000000)fail("size");
 rewind(f);
 uint8_t* data=malloc((size_t)size+1);if(!data)fail("alloc");
 if(fread(data,1,(size_t)size,f)!=(size_t)size)fail("read");
 fclose(f);data[size]=0;
 uint8_t d[32];char hex[65];SHA256(data,(size_t)size,d);
 for(int i=0;i<32;i++)sprintf(hex+i*2,"%02x",d[i]);
 hex[64]=0;
 if(strcmp(hex,spool_sha))fail("original spool SHA mismatch");
 char* p=strstr((char*)data,expected_row);
 if(!p||strstr(p+strlen(expected_row),expected_row))fail("selected row mismatch");
 for(int j=0;j<3;j++){
  char donor[33];
  for(int k=0;k<16;k++)sprintf(donor+2*k,"%02X",donors[j][k]);
  donor[32]=0;
  if(!strstr((char*)data,donor))fail("donor not found in original spool");
 }
 free(data);
}
static void block_for(uint8_t block[64],const uint8_t coupon[16]){
 memset(block,0,64);
 for(int j=0;j<16;j++)block[j]=coupon[j]^mask[j];
 block[16]=0x80;block[63]=0x80;
}
static unsigned digest_word(const uint8_t* d,int i){
 return (unsigned)d[i*4]<<24|(unsigned)d[i*4+1]<<16|(unsigned)d[i*4+2]<<8|d[i*4+3];
}
int main(int argc,char** argv){
 if(argc!=3)fail("usage: SFT ORIGINAL_SPOOL --smoke|--full");
 int smoke=!strcmp(argv[2],"--smoke");
 if(!smoke&&strcmp(argv[2],"--full"))fail("mode");
 verify_spool(argv[1]);
 SHA256_CTX initial;SHA256_Init(&initial);
 uint64_t count=0,original_hits=0,planted_hits=0;
 const uint8_t plant[5]={donors[0][3],donors[0][4],0x83,0x17,0xe9};
 uint8_t synthetic[16];memcpy(synthetic,copied,16);memcpy(synthetic,plant,5);
 uint8_t synth_comp[16],synth_hash[32];
 for(int i=0;i<16;i++)synth_comp[i]=synthetic[i]^mask[i];
 SHA256(synth_comp,16,synth_hash);
 unsigned synthetic_target[8];
 for(int j=0;j<8;j++)synthetic_target[j]=digest_word(synth_hash,j);
 for(unsigned d=0;d<3;d++)for(unsigned offset=0;offset<=14;offset++)for(unsigned flip=0;flip<2;flip++){
  uint8_t candidate[16];memcpy(candidate,copied,16);
  candidate[0]=donors[d][offset+flip];candidate[1]=donors[d][offset+1-flip];
  uint8_t block[64];block_for(block,candidate);
  SHA256_CTX state=initial;SHA256_Transform(&state,block);
  uint8_t full_short[32];SHA256(block,16,full_short);
  for(int j=0;j<8;j++)if(state.h[j]!=digest_word(full_short,j))fail("SHA256_Transform differential positive");
  for(uint32_t suffix=0;suffix<(smoke?262144U:16777216U);suffix++){
   block[2]=(uint8_t)(suffix>>16)^mask[2];
   block[3]=(uint8_t)(suffix>>8)^mask[3];
   block[4]=(uint8_t)suffix^mask[4];
   state=initial;SHA256_Transform(&state,block);
   if(state.h[0]==target[0]){
    int same=1;for(int j=1;j<8;j++)same &= state.h[j]==target[j];
    if(same){
     original_hits++;
     printf("ORIGINAL_K04_MATCH donor=%u offset=%u flip=%u suffix=%06X component=",d,offset,flip,suffix);
     for(int j=0;j<16;j++)printf("%02X",block[j]);
     printf("\n");fflush(stdout);
    }
   }
   if(state.h[0]==synthetic_target[0]){
    int same=1;for(int j=1;j<8;j++)same &= state.h[j]==synthetic_target[j];
    if(same)planted_hits++;
   }
   count++;
  }
 }
 if(!smoke&&count!=90ULL*16777216ULL)fail("count discrepancy");
 if(!smoke&&planted_hits!=1)fail("synthetic five-byte target not uniquely recovered");
 printf("SUMMARY packets=3 donor_offsets=15 directions=2 unknown_bytes=3 checks=%llu original_hits=%llu planted_hits=%llu smoke=%d\n",
 (unsigned long long)count,(unsigned long long)original_hits,(unsigned long long)planted_hits,smoke);
 return original_hits?9:0;
}
