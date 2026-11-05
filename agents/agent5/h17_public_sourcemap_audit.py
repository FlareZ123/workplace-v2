"""Bounded public, anonymous static asset sourcemap acquisition for H-17.
Only homepage-linked JS/CSS and their standard .map companions. No private routes.
"""
import hashlib,json,re
from html.parser import HTMLParser
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlsplit
ROOT="https://noyes-energy-group.pages.dev/"
HOST=urlsplit(ROOT).hostname
WORDS=re.compile("H[- ]?17|IR[- ]?261003|ESC[- ]?N|0417|BX25|FA[- ]?17|keeper|coupon|caption|envelope|Emily|records",re.I)
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,request,fp,code,msg,headers,url):return None
OPEN=build_opener(NoRedirect)
def public(url):
 p=urlsplit(url)
 return p.scheme=="https" and p.hostname==HOST and not p.username and not p.password and p.port is None and not p.path.lower().startswith(("/admin","/api","/partner","/account","/signin","/login"))
def read(url):
 assert public(url),url
 try:
  with OPEN.open(Request(url,headers={"User-Agent":"H17-public-sourcemap-audit/1.0"}),timeout=15) as r:
   assert public(r.geturl()) and r.geturl()==url
   b=r.read(3000001)
   assert len(b)<=3000000
   print("PUBLIC",r.status,url,len(b),hashlib.sha256(b).hexdigest(),r.headers.get("Content-Type"),flush=True)
   return b,dict(r.headers)
 except (HTTPError,URLError,TimeoutError) as e:print("PUBLIC_UNAVAILABLE",url,str(e),flush=True)
class Assets(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="script" and a.get("src"):self.urls.append(a["src"])
  if tag=="link" and a.get("href") and "stylesheet" in str(a.get("rel","")):self.urls.append(a["href"])
def main():
 homepage=read(ROOT)
 if homepage is None:return
 parser=Assets();parser.feed(homepage[0].decode("utf-8","replace"))
 assets=list(dict.fromkeys(urljoin(ROOT,s) for s in parser.urls if public(urljoin(ROOT,s)) and re.search(r"\\.(js|css)(\\?.*)?$",s)))
 print("LINKED_ASSETS",assets)
 for asset in assets[:10]:
  got=read(asset)
  if got is None:continue
  b,headers=got;script=b.decode("utf-8","replace")
  marker=list(WORDS.finditer(script))
  print("ASSET_SOURCE_MARKERS",asset,len(marker),[script[max(0,m.start()-60):m.end()+95] for m in marker[:8]])
  match=re.search(r"sourceMappingURL\\s*=\\s*([^\\s*]+)",script)
  maps=[urljoin(asset,match.group(1))] if match else []
  for key in ("SourceMap","X-SourceMap"):
   if headers.get(key):maps.append(urljoin(asset,headers[key]))
  if not maps:maps=[urlsplit(asset)._replace(query="").geturl()+".map"]
  for url in dict.fromkeys(maps[:2]):
   if not public(url) or not url.startswith(ROOT+"assets/"):continue
   m=read(url)
   if m is None:continue
   try:obj=json.loads(m[0])
   except (ValueError,UnicodeDecodeError):continue
   sources=obj.get("sources",[]);content=obj.get("sourcesContent",[])
   print("PUBLIC_MAP",url,"SOURCES",sources[:40])
   if isinstance(content,list):
    for n,s in enumerate(content[:100]):
     if not isinstance(s,str):continue
     hits=list(WORDS.finditer(s))
     if hits:print("PUBLIC_MAP_SOURCE_MARKERS",sources[n] if n<len(sources) else n,[s[max(0,x.start()-80):x.end()+140] for x in hits[:10]])
 print("PUBLIC_SOURCEMAP_AUDIT_COMPLETE")
if __name__=="__main__":main()
