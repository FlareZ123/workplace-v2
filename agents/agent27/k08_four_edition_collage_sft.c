/*
 * Agent27: K08 full rewrite from four dated Emily stages, with no N13 base.
 * Compile: cc -O3 -Wno-deprecated-declarations -o k08_collage \
 *     agents/agent27/k08_four_edition_collage_sft.c -lcrypto
 * Run: ./k08_collage resources/evidence/crew/noticeboard-and-desk-notes.txt
 * All candidate strings are lowercase ASCII, separated by ASCII spaces.
 */
#include <assert.h>
#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

typedef struct {char word[32];} Word;
typedef struct {Word words[64]; int n;} Note;
typedef struct {char text[160]; size_t n;} Span;
static Note notes[4];
static Span spans[4][128];
static int counts[4];
static const int ids[4]={2,6,13,20};
static const unsigned char key[16]={0x5f,0x93,0x3d,0xa6,0xa1,0xbd,0x03,0xc3,0x2d,0xa5,0xcb,0xc2,0x53,0x44,0xf4,0x97};
static const unsigned char target[32]={0x28,0x5e,0xb6,0xb4,0x19,0x6d,0x21,0xea,0xf4,0x7e,0x25,0x14,0x49,0xe6,0x1e,0x0b,0xce,0x28,0x74,0x98,0x81,0xcc,0xc5,0xa0,0x65,0xca,0x73,0x3b,0x0c,0x3f,0xd7,0x47};
static const unsigned char source_sha[32]={0x13,0xf2,0x31,0x8c,0xcc,0x54,0xf3,0x5b,0x59,0x0a,0x2d,0x76,0xb3,0xa8,0x02,0x44,0xfe,0x24,0xd7,0x0f,0x06,0x99,0xc6,0x7c,0x05,0x85,0x8e,0x8b,0x89,0x83,0xc5,0xcb};
static SHA256_CTX inner_prefix,outer_prefix;
static void prepare(void){
  unsigned char a[64],b[64];
  memset(a,0x36,64);memset(b,0x5c,64);
  for(int i=0;i<16;i++){a[i]^=key[i];b[i]^=key[i];}
  SHA256_Init(&inner_prefix);SHA256_Update(&inner_prefix,a,64);
  SHA256_Init(&outer_prefix);SHA256_Update(&outer_prefix,b,64);
}
static void slot_hash(const char *s,unsigned char *out){
  unsigned char h[32],component[32]; SHA256_CTX ci=inner_prefix,co=outer_prefix;
  SHA256_Update(&ci,s,strlen(s));SHA256_Final(h,&ci);
  SHA256_Update(&co,h,32);SHA256_Final(component,&co);
  SHA256(component,16,out);
}
static void tokenize(Note *n,const char *s){
  n->n=0;while(*s){
    while(*s&&!isalnum((unsigned char)*s))s++;
    if(!*s)break;
    assert(n->n<64);int k=0;
    while(isalnum((unsigned char)*s)){
      assert(k<31);n->words[n->n].word[k++]=(char)tolower((unsigned char)*s++);
    }
    n->words[n->n++].word[k]=0;
  }
}
static void load_notes(const char *path){
  FILE *f=fopen(path,"rb");if(!f){perror(path);exit(2);}
  fseek(f,0,SEEK_END);long len=ftell(f);rewind(f);
  unsigned char *raw=malloc((size_t)len+1);assert(raw);
  assert(fread(raw,1,(size_t)len,f)==(size_t)len);fclose(f);raw[len]=0;
  unsigned char digest[32];SHA256(raw,(size_t)len,digest);
  assert(!memcmp(digest,source_sha,32)&&"source sha mismatch");
  for(int i=0;i<4;i++){
    char mark[48];snprintf(mark,sizeof(mark),"N%02d / Emily [censored]\\n",ids[i]);
    /* Convert the two-character escape in mark to a literal line ending. */
    size_t n=strlen(mark);assert(mark[n-2]=='\\'&&mark[n-1]=='n');mark[n-2]='\n';mark[n-1]=0;
    char *p=strstr((char*)raw,mark);assert(p);p+=strlen(mark);
    char *q=strchr(p,'\n');assert(q);char tmp=*q;*q=0;
    if(i<2){p=strchr(p,':');assert(p);p++;}
    tokenize(&notes[i],p);*q=tmp;
  }
  free(raw);
  assert(notes[0].n==13 && notes[1].n==11 && notes[2].n==22 && notes[3].n==30);
  for(int i=0;i<4;i++){
    for(int length=2;length<=5;length++){
      for(int first=0;first+length<=notes[i].n;first++){
        Span *s=&spans[i][counts[i]++];s->text[0]=0;
        for(int k=first;k<first+length;k++){
          if(k>first)strcat(s->text," ");strcat(s->text,notes[i].words[k].word);
        }
        s->n=strlen(s->text);
      }
    }
  }
  assert(counts[0]==42&&counts[1]==34&&counts[2]==78&&counts[3]==110);
}
int main(int argc,char **argv){
  if(argc<2||argc>3){fprintf(stderr,"usage: %s /path/to/evidence/crew/noticeboard-and-desk-notes.txt [--with-and]\n",argv[0]);return 2;}
  int with_and=argc==3; if(with_and)assert(strcmp(argv[2],"--with-and")==0);
  load_notes(argv[1]);prepare();
  unsigned char known_digest[32];
  const unsigned char known_target[32]={0x47,0xe7,0x87,0x78,0x5f,0xf2,0x50,0x82,0xb4,0xb9,0x60,0xad,0x41,0x5f,0x1e,0x03,0x0a,0xe0,0xed,0xc8,0x9c,0x38,0xb2,0xf6,0x1c,0x48,0xf9,0x33,0x12,0x82,0xea,0x55};
  slot_hash("a good watch leaves the room ready for the next pair of hands",known_digest);
  assert(!memcmp(known_digest,known_target,32)&&"known N02 HMAC/SHA control failed");
  unsigned char planted[32];char planted_phrase[700];
  snprintf(planted_phrase,sizeof(planted_phrase),with_and?"%s and %s %s %s":"%s %s %s %s",
    spans[0][0].text,spans[1][0].text,spans[2][0].text,spans[3][0].text);
  slot_hash(planted_phrase,planted);
  unsigned long long tested=0,positives=0,hits=0;
  #pragma omp parallel for reduction(+:tested,positives,hits) schedule(static)
  for(int a=0;a<counts[0];a++)for(int b=0;b<counts[1];b++)for(int c=0;c<counts[2];c++)for(int d=0;d<counts[3];d++){
    char phrase[700],found[32];
    /* 0..7: each of the three word joins optionally inserts 'and'.
       The words added by this operator are already in N13/N20. */
    for(int op=(with_and?1:0);op<(with_and?8:1);op++){
      size_t off=0;
      const Span *q0=&spans[0][a], *q1=&spans[1][b], *q2=&spans[2][c], *q3=&spans[3][d];
      memcpy(phrase+off,q0->text,q0->n);off+=q0->n;
      const char *join1=(op&1)?" and ":" ";size_t j1=(op&1)?5:1;
      memcpy(phrase+off,join1,j1);off+=j1;
      memcpy(phrase+off,q1->text,q1->n);off+=q1->n;
      const char *join2=(op&2)?" and ":" ";size_t j2=(op&2)?5:1;
      memcpy(phrase+off,join2,j2);off+=j2;
      memcpy(phrase+off,q2->text,q2->n);off+=q2->n;
      const char *join3=(op&4)?" and ":" ";size_t j3=(op&4)?5:1;
      memcpy(phrase+off,join3,j3);off+=j3;
      memcpy(phrase+off,q3->text,q3->n);off+=q3->n;
      assert(off<sizeof(phrase));phrase[off]=0;
      slot_hash(phrase,found);tested++;
      positives+=!memcmp(found,planted,32);
      if(!memcmp(found,target,32)){
        hits++;
        #pragma omp critical
        {fprintf(stdout,"ORIGINAL_K08_HIT candidate=%s\n",phrase);fflush(stdout);}
      }
    }
  }
  assert(tested==(with_and?85765680ULL:12252240ULL));
  assert(positives>0);
  printf("source_sha256=13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb\n");
  printf("model=one 2..5-word exact span from each of Emily N02,N06,N13,N20 in that order; optional and joins if --with-and\n");
  printf("source_span_counts=%d,%d,%d,%d candidates=%llu synthetic_controls=%llu original_commitment_hits=%llu\n",counts[0],counts[1],counts[2],counts[3],tested,positives,hits);
  return 0;
}
