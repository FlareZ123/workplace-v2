// Agent13: all 46,206,736 byte-position involution assignments (disjoint swaps).
// The included source-pinned library is the same SFT used by the 256-shard run.
#define main original_full_permutation_main
#include "k04_allbyte_permutation_sft.cpp"
#undef main

static constexpr uint64_t EXPECTED_BY_SWAPS[9]={1,120,5460,120120,1351350,7567560,18918900,16216200,2027025};
static uint64_t counts[9]={},hits[9]={},plants[9]={};
static B16 candidate=copied,plant_coupon=copied;
static D32 plant_digest{};
static uint32_t plant_head=0;
static SHA256_CTX ctx{};
static unsigned char block[64]={},component_bytes[16];

static void check(unsigned swaps){
  counts[swaps]++;
  reduce(candidate,component_bytes);sha16(component_bytes,ctx,block);
  if(ctx.h[0]==UINT32_C(0x930A52A1)&&matches(ctx,commitment)){
    hits[swaps]++;
    std::printf("K04_AUTHENTIC_MATCH coupon=%s component=%s swaps=%u\n",
      hex(candidate.data(),16).c_str(),hex(component_bytes,16).c_str(),swaps);
  }
  if(ctx.h[0]==plant_head&&matches(ctx,plant_digest)){
    if(candidate!=plant_coupon)throw std::logic_error("Synthetic positive collision");
    plants[swaps]++;
  }
}
static void enumerate(uint16_t unused,unsigned swaps){
  if(!unused){check(swaps);return;}
  unsigned i=(unsigned)__builtin_ctz((unsigned)unused);
  uint16_t rest=(uint16_t)(unused&~(uint16_t(1)<<i));
  candidate[i]=copied[i];enumerate(rest,swaps); // fixed point
  for(unsigned j=i+1;j<16;j++)if(rest&(uint16_t(1)<<j)){
    candidate[i]=copied[j];candidate[j]=copied[i];
    enumerate((uint16_t)(rest&~(uint16_t(1)<<j)),swaps+1);
    candidate[j]=copied[j];
  }
  candidate[i]=copied[i];
}
int main(int argc,char**argv){
  if(argc!=4){std::fprintf(stderr,"Usage: involutions_sft spool route acceptance\n");return 2;}
  try{
    pin(argv[1],argv[2],argv[3]);selftest();
    const unsigned pairs[6][2]={{0,7},{1,11},{2,9},{3,13},{4,15},{5,8}};
    for(const auto& pair:pairs)std::swap(plant_coupon[pair[0]],plant_coupon[pair[1]]);
    unsigned char sample[16],digest[32];
    reduce(plant_coupon,sample);SHA256(sample,16,digest);
    std::copy(digest,digest+32,plant_digest.begin());
    plant_head=(uint32_t(plant_digest[0])<<24)|(uint32_t(plant_digest[1])<<16)|(uint32_t(plant_digest[2])<<8)|plant_digest[3];
    block[16]=0x80;block[63]=0x80;
    enumerate(UINT16_MAX,0);
    uint64_t total=0,original_hits=0,planted_hits=0;
    for(unsigned k=0;k<=8;k++){
      std::printf("SWAPS=%u ASSIGNMENTS=%llu ORIGINAL_HITS=%llu SYNTHETIC_HITS=%llu\n",
        k,(unsigned long long)counts[k],(unsigned long long)hits[k],(unsigned long long)plants[k]);
      if(counts[k]!=EXPECTED_BY_SWAPS[k])throw std::logic_error("Swap-count census mismatch");
      total+=counts[k];original_hits+=hits[k];planted_hits+=plants[k];
    }
    std::printf("SUMMARY assignments=%llu original_hits=%llu planted_hits=%llu\n",
      (unsigned long long)total,(unsigned long long)original_hits,(unsigned long long)planted_hits);
    if(total!=UINT64_C(46206736)||planted_hits<1)throw std::logic_error("Completeness or planted control failed");
    return original_hits?10:0;
  }catch(const std::exception&e){std::fprintf(stderr,"ERROR %s\n",e.what());return 3;}
}
