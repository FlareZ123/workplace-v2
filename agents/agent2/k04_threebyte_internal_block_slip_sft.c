/* Agent 2: exact three-byte internal block-loss/reinsertion K04 copier
 * distinct from Agent36's k1..2 slip and old arbitrary 3-byte replacement.
 * 182 nontrivial delete/insert positions x all 2^24 inserted byte triples.
 * Distributed 32 shards; disputed original copied row is treated as noisy input.
 * Source and acceptance SHA pins ensure unchanged original records.
 * Run: cc -O3 -Wno-deprecated-declarations -Wall -Wextra -Werror -std=c11 file.c -lcrypto -o slip3
 *      ./slip3 resources 0 32
 */
#include <openssl/sha.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t source[16]={
 0xa9,0xa9,0xdc,0x57,0x31,0xa5,0xe2,0xae,
 0x87,0x9c,0x47,0x21,0x5c,0x25,0x59,0xd5};
static const uint8_t route[16]={
 0x85,0x56,0xc8,0xcb,0x61,0x40,0xa7,0xf9,
 0xa5,0x12,0x3a,0xc7,0x57,0x1b,0xee,0x1c};
static const uint8_t target[32]={
 0x93,0x0a,0x52,0xa1,0xba,0xb9,0x7c,0xa2,
 0x96,0x63,0x32,0x13,0x7c,0x99,0xe9,0x92,
 0x98,0xea,0x61,0x82,0xfb,0x32,0xab,0x63,
 0xa3,0x42,0x1d,0xfb,0x4f,0xd8,0xc9,0xe0};
static const char *pinned[][2]={
 {"evidence/print/spool-reconstruction.log","7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"},
 {"evidence/recovery-routing.json","f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"},
 {"acceptance.json","681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"}
};
static void pin(const char*root,const char*name,const char*expected){
 char path[1024],hex[65];
 if(snprintf(path,sizeof path,"%s/%s",root,name)>=(int)sizeof path)exit(2);
 FILE*f=fopen(path,"rb");if(!f){perror(path);exit(2);}
 SHA256_CTX ctx;SHA256_Init(&ctx);
 unsigned char buffer[32768],digest[32];size_t n;
 while((n=fread(buffer,1,sizeof buffer,f))!=0) SHA256_Update(&ctx,buffer,n);
 if(ferror(f)){perror(path);exit(2);}fclose(f);
 SHA256_Final(digest,&ctx);
 for(int i=0;i<32;i++)snprintf(hex+2*i,3,"%02x",digest[i]);
 if(strcmp(hex,expected)){fprintf(stderr,"INPUT_PIN_FAIL %s\n",name);exit(2);}
}
static void make(int deletion,int insertion,uint32_t replacement,uint8_t component[16]){
 uint8_t preserved[13];int retained=0,used=0;
 for(int i=0;i<16;i++)if(i<deletion||i>=deletion+3) preserved[retained++]=source[i];
 if(retained!=13)abort();
 for(int i=0;i<16;i++){
   uint8_t value;
   if(i>=insertion&&i<insertion+3)
     value=(uint8_t)(replacement>>(8*(i-insertion)));
   else
     value=preserved[used++];
   component[i]=value^route[i];
 }
 if(used!=13)abort();
}
int main(int argc,char**argv){
 if(argc!=4){fprintf(stderr,"usage: %s resources shard shards\n",argv[0]);return 2;}
 int shard=atoi(argv[2]),shards=atoi(argv[3]);
 if(shard<0||shards<=0||shards>196||shard>=shards)return 2;
 for(int i=0;i<3;i++)pin(argv[1],pinned[i][0],pinned[i][1]);
 uint64_t tested=0, positives=0,hits=0;
 int firstpair=-1,positions=0;
 for(int pair=shard;pair<196;pair+=shards){
   int del=pair/14,ins=pair%14;
   if(del!=ins){firstpair=pair;break;}
 }
 if(firstpair<0)return 2;
 uint8_t control[16],control_digest[32];
 make(firstpair/14,firstpair%14,0xd35ea9u,control);
 SHA256(control,16,control_digest);
 for(int pair=shard;pair<196;pair+=shards){
   int del=pair/14,ins=pair%14;
   if(del==ins)continue;
   uint8_t component[16],hash[32];
   make(del,ins,0,component);
   positions++;
   for(uint32_t v=0;v<(1u<<24);v++){
     component[ins+0]=(uint8_t)(v^route[ins+0]);
     component[ins+1]=(uint8_t)((v>>8)^route[ins+1]);
     component[ins+2]=(uint8_t)((v>>16)^route[ins+2]);
     SHA256(component,16,hash);
     tested++;
     if(pair==firstpair&&v==0xd35ea9u&&memcmp(hash,control_digest,32)==0
        &&memcmp(component,control,16)==0) positives++;
     if(memcmp(hash,target,32)==0){
       fprintf(stderr,"K04_ORIGINAL_FULL_SHA256_HIT del=%d ins=%d value=%06X component=",del,ins,v);
       for(int i=0;i<16;i++)fprintf(stderr,"%02X",component[i]);
       fprintf(stderr," coupon=");
       for(int i=0;i<16;i++)fprintf(stderr,"%02X",component[i]^route[i]);
       fputc('\n',stderr);hits++;
     }
   }
 }
 uint64_t expected=(uint64_t)positions*(1u<<24);
 printf("SLIP3_COMPLETE shard=%d of=%d pair_positions=%d tested=%" PRIu64 " expected=%" PRIu64 " synthetic_positives=%" PRIu64 " original_matches=%" PRIu64 "\n",
        shard,shards,positions,tested,expected,positives,hits);
 if(positives!=1||tested!=expected)return 2;
 return hits?10:0;
}
