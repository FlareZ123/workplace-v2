/* Independent first-128-intact-packet Windows CRT rand15 source test.
 * No disputed selected ACK, route mask, or original commitment is used.
 * Builds under C17 with OpenSSL SHA256.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

static const unsigned char source_sha[32] = {
  0x7D,0x71,0xD8,0xBE,0xF7,0xF0,0x15,0x96,0xE7,0x05,0xAC,0x14,0xE2,0x4C,0x5C,0x43,
  0x52,0x04,0x25,0x12,0xB3,0x08,0x81,0x25,0xAF,0xCA,0x40,0xF3,0x84,0x1B,0x60,0x83
};
static uint32_t next_state(uint32_t s) { return s*UINT32_C(214013)+UINT32_C(2531011); }
static int emitted(uint32_t s) { return (int)((s>>16)&0x7FFFu); }
static int srcbit(const unsigned char data[16], int index, int reverse_bytes, int reverse_bits){
  int k=reverse_bytes?15-index/8:index/8;
  int bit=reverse_bits?index%8:7-index%8;
  return (data[k]>>bit)&1;
}
static void setbit(unsigned char data[16], int index, int reverse_bytes, int reverse_bits, int value){
  int k=reverse_bytes?15-index/8:index/8;
  int bit=reverse_bits?index%8:7-index%8;
  if(value)data[k]|=(unsigned char)(1<<bit);
}
static uint16_t first_word(const unsigned char data[16], int offset,int native_lsb,int rb,int rbit){
  uint16_t w=0;
  for(int i=0;i<15;i++)w|=(uint16_t)(srcbit(data,offset+i,rb,rbit)<<(native_lsb?i:14-i));
  return w;
}
static int equals_packed(const unsigned char data[16],uint32_t first_state,int native_lsb,int rb,int rbit){
  uint32_t state=first_state;
  for(int i=0;i<128;i++){
    int j=i%15;
    int value=emitted(state);
    if(((value>>(native_lsb?j:14-j))&1)!=srcbit(data,i,rb,rbit))return 0;
    if(j==14)state=next_state(state);
  }
  return 1;
}
static int matches(const unsigned char data[16],int native_lsb,int rb,int rbit){
  uint16_t r0=first_word(data,0,native_lsb,rb,rbit);
  uint16_t r1=first_word(data,15,native_lsb,rb,rbit);
  int count=0;
  for(uint32_t low=0;low<65536;low++){
    uint32_t s=((uint32_t)r0<<16)|low;
    if(emitted(next_state(s)) != r1)continue;
    if(equals_packed(data,s,native_lsb,rb,rbit))count++;
  }
  return count;
}
static void make_control(unsigned char data[16],int native_lsb,int rb,int rbit){
  uint32_t state=next_state(UINT32_C(0xA5A52137));
  memset(data,0,16);
  for(int i=0;i<128;i++){
    int j=i%15;
    int n=emitted(state);
    setbit(data,i,rb,rbit,(n>>(native_lsb?j:14-j))&1);
    if(j==14)state=next_state(state);
  }
}
static int nibble(char c){
  if(c>='0'&&c<='9')return c-'0';
  if(c>='A'&&c<='F')return c-'A'+10;
  assert(0);return -1;
}
int main(int argc,char **argv){
  assert(argc==2);
  FILE *f=fopen(argv[1],"rb");assert(f);
  assert(fseek(f,0,SEEK_END)==0);long n=ftell(f);assert(n>0 && n<150000);
  assert(fseek(f,0,SEEK_SET)==0);
  char *raw=(char*)malloc((size_t)n+1);assert(raw);
  assert(fread(raw,1,(size_t)n,f)==(size_t)n);fclose(f);raw[n]=0;
  unsigned char digest[32];SHA256((const unsigned char*)raw,(size_t)n,digest);
  assert(!memcmp(digest,source_sha,32));
  unsigned char records[128][16];int count=0,entire=0;
  for(char *line=strtok(raw,"\n");line;line=strtok(NULL,"\n")){
    const char *value=strstr(line,"PAYLOAD=");
    if(!value)continue;
    value+=8;
    if(count<128){
      assert(strlen(value)>=32);
      for(int k=0;k<16;k++)records[count][k]=(unsigned char)((nibble(value[2*k])<<4)|nibble(value[2*k+1]));
      count++;
    }
    entire++;
  }
  assert(count==128 && entire==133);
  assert(records[0][0]==0xFB && records[0][1]==0xBB);
  free(raw);
  unsigned long long intact_checked=0,positive_matches=0,original_matches=0;
  for(int native=0;native<2;native++)for(int rb=0;rb<2;rb++)for(int rbit=0;rbit<2;rbit++){
    unsigned char synthetic[16];make_control(synthetic,native,rb,rbit);
    int positive=matches(synthetic,native,rb,rbit);
    assert(positive>=1);positive_matches+=positive;
    int local=0;
    for(int row=0;row<128;row++){
      int found=matches(records[row],native,rb,rbit);
      local+=found;
      if(found)fprintf(stdout,"ORIGINAL_MODEL_FIT row=%d native_lsb=%d byte_rev=%d bit_rev=%d seeds=%d\n",row,native,rb,rbit,found);
      intact_checked++;
    }
    original_matches+=local;
    fprintf(stdout,"view native_lsb=%d byte_rev=%d bit_rev=%d: intact_packets=128 exact_matches=%d planted=%d\n",native,rb,rbit,local,positive);
  }
  assert(intact_checked==1024 && positive_matches>=8);
  printf("source_sha256=7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 original_packets=128 views=8 total_original_packet_checks=%llu planted_model_matches=%llu original_matches=%llu\n",intact_checked,positive_matches,original_matches);
  return 0;
}
