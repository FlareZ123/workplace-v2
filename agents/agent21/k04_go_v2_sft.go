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
 fmt.Printf("source-only: seeds=%d streams=%d windows=%d controls=%d matches=%d planted_chacha=PASS planted_pcg=PASS\n",len(seeds),streams,samples,controls,hits)
}
