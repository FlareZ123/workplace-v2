/* H17 K04: genuine same-job retry 4-bit-lane copy multiplexers.

   Original last ACK2 is selected; attempts 1 and 3 are REQUESTED only.
   This is a bounded reconstruction candidate class. No source asserts that
   any such copier existed, or that REQUESTED payloads were ever printed.

   Build with a C compiler and OpenSSL libcrypto, run with original resource
   root as argv[1]. Evidence, acceptance, and checker remain read-only.
*/
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { MODE_COUNT = 5, P = 16 };
static const uint64_t ASSIGNMENTS = 43046721ULL; /* 3^16 */
static const char *MODE[MODE_COUNT] = {
    "repeat16_halfbyte", "shift1_halves",
    "different_retry_plus1", "different_retry_plus2",
    "shift8_halves"
};
static const char *EXPECTED_SPOOL =
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083";
static const char *EXPECTED_ROUTE =
    "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5";
static const char *EXPECTED_ACCEPT =
    "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f";
static const char *MASK_TEXT = "8556C8CB6140A7F9A5123AC7571BEE1C";
static const char *TARGET_TEXT =
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0";
static uint8_t src[3][32], mask[16], target[32], plant[MODE_COUNT][32];

static int hexval(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}
static void decode(const char *hex, uint8_t *out, size_t n) {
    if (strlen(hex) < 2*n) {
        fputs("short hex field\n", stderr);
        exit(2);
    }
    for (size_t j=0; j<n; ++j) {
        int a=hexval(hex[2*j]), b=hexval(hex[2*j+1]);
        if (a<0 || b<0) {
            fputs("invalid hex field\n", stderr);
            exit(2);
        }
        out[j]=(uint8_t)((a<<4)|b);
    }
}
static void sha_file(const char *file, const char *expected) {
    FILE *f=fopen(file,"rb");
    if (!f) { perror(file); exit(2); }
    unsigned char buf[65536], dig[SHA256_DIGEST_LENGTH], expected_bytes[32];
    size_t n=fread(buf,1,sizeof(buf),f);
    if (n == sizeof(buf) || ferror(f)) {
        fputs("source file too large or read failed\n", stderr);
        exit(2);
    }
    fclose(f);
    SHA256(buf,n,dig);
    decode(expected,expected_bytes,32);
    if (memcmp(dig,expected_bytes,32)) {
        fprintf(stderr,"source SHA256 mismatch: %s\n",file);
        exit(2);
    }
}
static void source_read(const char *root) {
    char path[1024];
    snprintf(path,sizeof(path),"%s/evidence/print/spool-reconstruction.log",root);
    sha_file(path,EXPECTED_SPOOL);
    FILE *f=fopen(path,"rb");
    if (!f) { perror(path); exit(2); }
    char line[1024]; int seen[3]={0,0,0};
    while (fgets(line,sizeof(line),f)) {
        if (!strstr(line,"JOB=PS-261003-0417 ") ||
            !strstr(line,"CLASS=RECOVER ") ) continue;
        char *a=strstr(line,"ATTEMPT="), *p=strstr(line,"PAYLOAD=");
        if (!a || !p || a[8]<'1' || a[8]>'3') {
            fputs("wrong source RECOVER row\n",stderr); exit(2);
        }
        int index=a[8]-'1';
        const char *status = index==1 ? "STATE=ACK " : "STATE=REQUESTED ";
        if (!strstr(line,status) || seen[index]++)
        { fputs("duplicate/wrong recovery source state\n",stderr); exit(2); }
        p+=8;
        for (int j=0; j<32; ++j) {
            int nib=hexval(p[j]);
            if (nib<0) { fputs("invalid source payload\n",stderr); exit(2); }
            src[index][j]=(uint8_t)nib;
        }
        if (hexval(p[32])>=0) { fputs("overlong hex\n",stderr); exit(2); }
    }
    fclose(f);
    for(int i=0;i<3;++i)
        if(seen[i]!=1) { fputs("missing retry evidence\n",stderr); exit(2); }
    snprintf(path,sizeof(path),"%s/evidence/recovery-routing.json",root);
    sha_file(path,EXPECTED_ROUTE);
    snprintf(path,sizeof(path),"%s/acceptance.json",root);
    sha_file(path,EXPECTED_ACCEPT);
    decode(MASK_TEXT,mask,16); decode(TARGET_TEXT,target,32);
}
static void coupon_for(int mode, const uint8_t d[16], uint8_t coupon[16]) {
    for (int i=0; i<16; ++i) {
        int hi=0,lo=0;
        switch (mode) {
            case 0: hi=d[(2*i)&15]; lo=d[(2*i+1)&15]; break;
            case 1: hi=d[i]; lo=d[(i+1)&15]; break;
            case 2: hi=d[i]; lo=(d[i]+1)%3; break;
            case 3: hi=d[i]; lo=(d[i]+2)%3; break;
            case 4: hi=d[i]; lo=d[(i+8)&15]; break;
            default: exit(2);
        }
        coupon[i]=(uint8_t)((src[hi][2*i]<<4)|src[lo][2*i+1]);
    }
}
static void digest_component(const uint8_t coupon[16],uint8_t digest[32]) {
    uint8_t component[16];
    for(int i=0;i<16;++i) component[i]=coupon[i]^mask[i];
    SHA256(component,16,digest);
}
static void printhex(const uint8_t *p,int n) {
    for(int i=0;i<n;++i) printf("%02X",p[i]);
}
int main(int argc,char **argv) {
    if(argc!=2) {
        fprintf(stderr,"Usage: %s RESOURCE_ROOT\n",argv[0]); return 2;
    }
    source_read(argv[1]);
    const uint64_t plant_index=1234567ULL;
    uint8_t digits[P],coupon[16],digest[32];
    uint64_t original_hits[MODE_COUNT]={0},plant_hits[MODE_COUNT]={0};

    uint64_t v=plant_index;
    for(int i=0;i<P;++i) { digits[i]=(uint8_t)(v%3);v/=3; }
    for(int mode=0;mode<MODE_COUNT;++mode) {
        coupon_for(mode,digits,coupon);
        digest_component(coupon,plant[mode]);
    }

    for(uint64_t x=0; x<ASSIGNMENTS; ++x) {
        v=x;
        for(int i=0;i<P;++i) { digits[i]=(uint8_t)(v%3);v/=3; }
        for(int mode=0;mode<MODE_COUNT;++mode) {
            coupon_for(mode,digits,coupon);
            digest_component(coupon,digest);
            if(!memcmp(digest,plant[mode],32)) plant_hits[mode]++;
            if(!memcmp(digest,target,32)) {
                original_hits[mode]++;
                printf("ORIGINAL_HIT mode=%s selector=%llu coupon=",
                       MODE[mode],(unsigned long long)x);
                printhex(coupon,16);
                printf(" component=");
                for(int j=0;j<16;++j) printf("%02X",coupon[j]^mask[j]);
                putchar('\n');
            }
        }
    }
    uint64_t total=0;
    for(int mode=0; mode<MODE_COUNT; ++mode) {
        printf("MODEL %s assignments=%llu original_hits=%llu plant_hits=%llu\n",
               MODE[mode],(unsigned long long)ASSIGNMENTS,
               (unsigned long long)original_hits[mode],
               (unsigned long long)plant_hits[mode]);
        if(!plant_hits[mode]) {
            fputs("synthetic same-loop full-coupon control failed\n",stderr);
            return 3;
        }
        total+=original_hits[mode];
    }
    printf("TOTAL complete_candidate_assignments=%llu target_hits=%llu synthetic_positive=PASS\n",
           (unsigned long long)(ASSIGNMENTS*MODE_COUNT),
           (unsigned long long)total);
    return total ? 4 : 0;
}
