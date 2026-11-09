package main

import (
 "crypto/sha256"
 "encoding/binary"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "math/rand/v2"
 "os"
 "regexp"
 "sort"
 "strings"
)

const spoolHash = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
const samples = 20000

type block [16]byte

func decode(h string) block {
 b,e:=hex.DecodeString(h)
 if e!=nil || len(b)!=16 { panic("bad source") }
 var p block
 copy(p[:],b)
 return p
}

func packet(b block, mode int) block {
 var p block
 switch mode {
 case 0: return b
 case 1: for i:=0;i<16;i++ { p[i]=b[15-i] }
 case 2: for i:=0;i<16;i++ { p[i]=b[i/4*4+3-i%4] }
 case 3: for i:=0;i<16;i++ { p[i]=b[12-i/4*4+i%4] }
 case 4: for i:=0;i<16;i++ { p[i]=b[i/8*8+7-i%8] }
 case 5: for i:=0;i<16;i++ { p[i]=b[8-i/8*8+i%8] }
 case 6: for i:=0;i<16;i++ { p[i]=b[i%4*4+i/4] }
 case 7: for i:=0;i<16;i++ { p[i]=b[(3-i%4)*4+i/4] }
 }
 return p
}

func main() {
 root:="resources"
 if len(os.Args)>1 { root=os.Args[1] }
 spool,e:=os.ReadFile(root+"/evidence/print/spool-reconstruction.log")
 if e!=nil { panic(e) }
 hash:=sha256.Sum256(spool)
 if fmt.Sprintf("%x",hash)!=spoolHash { panic("spool SHA mismatch") }
 re:=regexp.MustCompile(`JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([A-F0-9]{32})`)
 known:=map[block]bool{}
 controls:=0
 for _,m:=range re.FindAllSubmatch(spool,-1) {
  if strings.HasSuffix(string(m[1]),"-0417") && string(m[2])=="2" { continue }
  b:=decode(string(m[5]))
  for i:=0;i<8;i++ { known[packet(b,i)]=true }
  controls++
 }
 if controls!=132 { panic("control count") }
 routeBytes,e:=os.ReadFile(root+"/evidence/recovery-routing.json")
 if e!=nil { panic(e) }
 var route struct {
  K04 struct { Mask string `json:"masked_component"` }
  K08 struct { Nonce string `json:"desk_nonce"` }
 }
 if json.Unmarshal(routeBytes,&route)!=nil { panic("route") }
 candidate,e:=os.ReadFile(root+"/candidate.json")
 if e!=nil { panic(e) }
 var accepted map[string]*string
 if json.Unmarshal(candidate,&accepted)!=nil { panic("candidate") }
 seeds:=map[string]block{}
 for _,s:=range []string{"K01","K02","K03","K05","K06","K07"} {
  if accepted[s]==nil { panic("missing accepted slot") }
  seeds[s]=decode(*accepted[s])
 }
 seeds["K04_MASK"]=decode(route.K04.Mask)
 seeds["K08_NONCE"]=decode(route.K08.Nonce)
 seeds["K02_PREHASH"]=decode("E1A5E474BAD7E853A2E8C71D3317D507")
 seeds["K03_PREHASH"]=decode("D7DAD6BC9714519B7DAD0AD4BE8E87FD")
 seeds["K07_PREHASH"]=decode("8947CEDCB9CC73BAB7E87BE63302C5C9")
 seeds["BX25_PDF_ID0"]=decode("6406e62be753c69d795993a3de03a3c3")
 seeds["BX25_PDF_ID1"]=decode("3C7688377E08C7B4482A86A17932082C")
 names:=make([]string,0,len(seeds))
 for k:=range seeds { names=append(names,k) }
 sort.Strings(names)
 streams,hits:=0,0
 scan:=func(label string,get func()block) {
  streams++
  for i:=0;i<samples;i++ {
   if x:=get();known[x] {
    fmt.Printf("historical match model=%s offset=%d packet=%X\n",label,i,x)
    hits++
   }
  }
 }
 // Independent planted positive controls at packet offset 17.
 var testSeed [32]byte
 for i:=range testSeed { testSeed[i]=byte(3*i+7) }
 g:=rand.NewChaCha8(testSeed)
 var expected block
 for i:=0;i<=17;i++ {
  _,e=g.Read(expected[:])
  if e!=nil { panic(e) }
 }
 g=rand.NewChaCha8(testSeed)
 for i:=0;i<=17;i++ {
  var got block
  _,e=g.Read(got[:])
  if e!=nil { panic(e) }
  if i==17 && got!=expected { panic("ChaCha8 positive") }
 }
 pc:=rand.NewPCG(246,987)
 var p block
 for i:=0;i<=17;i++ {
  binary.LittleEndian.PutUint64(p[:8],pc.Uint64())
  binary.LittleEndian.PutUint64(p[8:],pc.Uint64())
 }
 pc=rand.NewPCG(246,987)
 for i:=0;i<=17;i++ {
  var got block
  binary.LittleEndian.PutUint64(got[:8],pc.Uint64())
  binary.LittleEndian.PutUint64(got[8:],pc.Uint64())
  if i==17 && got!=p { panic("PCG positive") }
 }
 for _,a:=range names {
  for _,b:=range names {
   if a==b { continue }
   var key [32]byte
   aa:=seeds[a]
   bb:=seeds[b]
   copy(key[:16],aa[:])
   copy(key[16:],bb[:])
   g:=rand.NewChaCha8(key)
   scan("ChaCha8:"+a+"+"+b,func()block {
    var x block
    _,e:=g.Read(x[:])
    if e!=nil { panic(e) }
    return x
   })
  }
 }
 for _,a:=range names {
  for c:=0;c<2;c++ {
   aa:=seeds[a]
   hexStr:=hex.EncodeToString(aa[:])
   if c==0 { hexStr=strings.ToUpper(hexStr) }
   var key [32]byte
   copy(key[:],[]byte(hexStr))
   g:=rand.NewChaCha8(key)
   scan(fmt.Sprintf("ChaCha8-ASCII:%s:%d",a,c),func()block {
    var x block
    _,e:=g.Read(x[:])
    if e!=nil { panic(e) }
    return x
   })
  }
 }
 for _,a:=range names {
  for m:=0;m<4;m++ {
   b:=seeds[a]
   var p,q uint64
   if m&1==0 {
    p=binary.LittleEndian.Uint64(b[:8])
    q=binary.LittleEndian.Uint64(b[8:])
   } else {
    p=binary.BigEndian.Uint64(b[:8])
    q=binary.BigEndian.Uint64(b[8:])
   }
   if m&2!=0 { p,q=q,p }
   g:=rand.NewPCG(p,q)
   scan(fmt.Sprintf("PCG:%s:%d",a,m),func()block {
    var x block
    binary.LittleEndian.PutUint64(x[:8],g.Uint64())
    binary.LittleEndian.PutUint64(x[8:],g.Uint64())
    return x
   })
  }
 }
 perJobCheck(spool)
 fmt.Printf("source-only: seeds=%d streams=%d windows=%d controls=%d matches=%d planted_chacha=PASS planted_pcg=PASS\n",len(seeds),streams,samples,controls,hits)
}


// An independent per-job source/issuer test: the printed job's own fields,
// rather than a shared archive field, initialize a newly seeded generator.
func perJobCheck(spool []byte) {
 re:=regexp.MustCompile(`(?m)^([^ ]+) JOB=([^ ]+) ATTEMPT=([^ ]+) STATE=([^ ]+) CLASS=([^ ]+) PAYLOAD=([A-F0-9]{32}) DEST=([^\s]+)`)
 rows:=re.FindAllSubmatch(spool,-1)
 if len(rows)!=133 {panic("perjob record count")}
 prefixes:=[]string{"","H17|","PS-261003|","REC8/1|","CEG-ARCHIVE-RECOVERY/v1\n"}
 tested,hits,controls:=0,0,0
 for _,m:=range rows {
  ts,job,a,state,class,dest:=string(m[1]),string(m[2]),string(m[3]),string(m[4]),string(m[5]),string(m[7])
  if job=="PS-261003-0417" && a=="2" {continue}
  controls++
  target:=decode(string(m[6]))
  tsNorm:=strings.ReplaceAll(ts,"+00:00","Z")
  forms:=[]string{job,ts,tsNorm,job+"|"+ts,job+"|"+tsNorm,job+"|"+a,job+"|"+class,job+"|"+class+"|"+dest,job+"|"+a+"|"+class,job+"|"+a+"|"+state+"|"+class+"|"+dest,job+" "+ts,tsNorm+"|"+job,fmt.Sprintf("JOB=%s ATTEMPT=%s STATE=%s CLASS=%s DEST=%s",job,a,state,class,dest),strings.TrimPrefix(job,"PS-261003-")}
  for i,form:=range forms {for j,pre:=range prefixes{
   seed:=sha256.Sum256([]byte(pre+form))
   for typ:=0;typ<3;typ++{
    var emit func() block
    if typ==0 {g:=rand.NewChaCha8(seed);emit=func()block{var b block;_,e:=g.Read(b[:]);if e!=nil{panic(e)};return b}} else {var u,v uint64;if typ==1 {u=binary.LittleEndian.Uint64(seed[:8]);v=binary.LittleEndian.Uint64(seed[8:16])} else {u=binary.BigEndian.Uint64(seed[:8]);v=binary.BigEndian.Uint64(seed[8:16])};g:=rand.NewPCG(u,v);emit=func()block{var b block;binary.LittleEndian.PutUint64(b[:8],g.Uint64());binary.LittleEndian.PutUint64(b[8:],g.Uint64());return b}}
    for offset:=0;offset<12;offset++{p:=emit();tested++;for view:=0;view<8;view++{if packet(p,view)==target{fmt.Printf("HISTORICAL_PERJOB_WHOLE_MATCH job=%s form=%d prefix=%d type=%d offset=%d wireview=%d\n",job,i,j,typ,offset,view);hits++}}}
   }
  }}
 }
 fmt.Printf("source-only-per-job: controls=%d forms=14 prefixes=5 generator_types=3 windows=12 wireviews=8 candidate_blocks=%d whole_matches=%d\n",controls,tested,hits)
}
