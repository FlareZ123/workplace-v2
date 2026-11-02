/* Exact original-source two-photo-caption condensation attack, 2 Nov 2026.
   N01 (Jason) plus N09 (Zoey), each retaining an arbitrary ordered
   word subsequence of >=2 words; join the two condensed lines in either
   order, total 4..18 words. No added lexical material. Original K08
   HMAC[:16] -> SHA256 commitment, read-only. 33,189,906 assignments.
   Compile with C11 and an OpenSSL 3 libcrypto implementation.
*/
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

typedef struct { char text[160]; unsigned char len; } Segment;
static const char *a[] = {"the","sea","looks","different","when","you","have",
                           "finally","finished","your","tea"};
static const char *b[] = {"nobody","should","have","to","make","their","first",
                           "cup","alone","after","a","bad","night"};
static Segment sa[2048],sb[8192];
static SHA256_CTX ipad_ctx,opad_ctx;

static void fromhex(const char *s,unsigned char *out,int n) {
    for(int i=0;i<n;i++) {
        unsigned x;
        if(sscanf(s+2*i,"%2x",&x)!=1) abort();
        out[i]=(unsigned char)x;
    }
}
static void source_assert(const char *path,const char *hex,const char *substring) {
    FILE *f=fopen(path,"rb");if(!f) {perror(path);abort();}
    if(fseek(f,0,SEEK_END))abort();
    long n=ftell(f);if(n<0||n>2000000)abort();
    rewind(f);
    char *buf=malloc((size_t)n+1);if(!buf)abort();
    if(fread(buf,1,(size_t)n,f)!=(size_t)n)abort();
    fclose(f);buf[n]=0;
    unsigned char actual[32],expected[32];
    SHA256((unsigned char*)buf,(size_t)n,actual);
    fromhex(hex,expected,32);
    if(memcmp(actual,expected,32))abort();
    if(substring&&!strstr(buf,substring))abort();
    free(buf);
}
static int segments(const char *const *words,int n,Segment *out) {
    int count=0;
    for(unsigned mask=1;mask<(1u<<n);mask++) {
        int k=__builtin_popcount(mask);
        if(k<2)continue;
        Segment *s=&out[count++];
        s->len=(unsigned char)k;s->text[0]=0;
        for(int i=0;i<n;i++)if(mask&(1u<<i)) {
            if(*s->text)strcat(s->text," ");
            strcat(s->text,words[i]);
        }
    }
    return count;
}
static void init_hmac(const unsigned char *key) {
    unsigned char ipad[64],opad[64];
    for(int i=0;i<64;i++) {
        unsigned char x=i<16?key[i]:0;
        ipad[i]=x^0x36;opad[i]=x^0x5c;
    }
    SHA256_Init(&ipad_ctx);SHA256_Update(&ipad_ctx,ipad,64);
    SHA256_Init(&opad_ctx);SHA256_Update(&opad_ctx,opad,64);
}
static void component_and_digest(const char *words,unsigned char component[16],
                                 unsigned char out[32]) {
    unsigned char inner[32],mac[32];
    SHA256_CTX i=ipad_ctx,o=opad_ctx;
    SHA256_Update(&i,words,strlen(words));SHA256_Final(inner,&i);
    SHA256_Update(&o,inner,32);SHA256_Final(mac,&o);
    memcpy(component,mac,16);SHA256(component,16,out);
}
int main(void) {
    const char *base="resources/";
    char path[256];
    const char *names[3]={"evidence/crew/noticeboard-and-desk-notes.txt",
      "evidence/recovery-routing.json","acceptance.json"};
    const char *sha[3]={"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
      "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
      "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"};
    for(int k=0;k<3;k++) {
        snprintf(path,sizeof(path),"%s%s",base,names[k]);
        source_assert(path,sha[k],NULL);
    }
    snprintf(path,sizeof(path),"%s%s",base,names[0]);
    source_assert(path,sha[0],"For the photograph of the empty bench: The sea looks different when you have finally finished your tea.");
    source_assert(path,sha[0],"Caption for the galley board: Nobody should have to make their first cup alone after a bad night.");

    unsigned char key[16],target[32],n02[16],component[16],out[32],plant[32];
    fromhex("5F933DA6A1BD03C32DA5CBC25344F497",key,16);
    fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747",target,32);
    fromhex("BF889359B0303F2B2B2FD96AE841210B",n02,16);
    init_hmac(key);
    component_and_digest("a good watch leaves the room ready for the next pair of hands",component,out);
    if(memcmp(component,n02,16))abort();

    int na=segments(a,11,sa),nb=segments(b,13,sb);
    if(na!=2036||nb!=8178)abort();
    char phrase[320];
    snprintf(phrase,sizeof(phrase),"%s %s",sa[117].text,sb[509].text);
    component_and_digest(phrase,component,plant);
    uint64_t total=0,hits=0,positive=0;
    for(int i=0;i<na;i++)for(int j=0;j<nb;j++) {
        if(sa[i].len+sb[j].len>18)continue;
        for(int order=0;order<2;order++) {
            snprintf(phrase,sizeof(phrase),"%s %s",
                order?sb[j].text:sa[i].text,
                order?sa[i].text:sb[j].text);
            component_and_digest(phrase,component,out);
            total++;
            if(!memcmp(out,plant,32))positive++;
            if(!memcmp(out,target,32)) {
                hits++;
                printf("ORIGINAL K08 HIT %s\n",phrase);
            }
        }
    }
    printf("N01+N09 condensations: %llu complete assignments, "
           "%llu original hits, %llu planted positives\n",
        (unsigned long long)total,(unsigned long long)hits,
        (unsigned long long)positive);
    if(total!=33189906ULL||positive<1||hits)return 1;
    return 0;
}
