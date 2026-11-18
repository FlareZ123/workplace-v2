// Independent source-order MT19937 recurrence reproduction for H-17 K04.
// Usage: g++ -O3 -std=c++17 -Wall -Wextra -o h17_k04_agent9_mt_reproduction h17_k04_agent9_mt_reproduction.cpp
//        ./h17_k04_agent9_mt_reproduction path/to/spool-reconstruction.log
// The selected source payload row 129 (PS-261003-0417, ATTEMPT=2, ACK, RECOVER)
// is metadata-checked and skipped before its PAYLOAD hex is read or decoded.
// This is a source-signal analysis only; it does not construct a K04 candidate.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

struct Row { int source_index=-1, attempt=-1; std::string ts,job,state,klass,dest; std::array<uint32_t,4>w{}; std::string payload; };
struct PairRef { int k,l,i,j; };
uint32_t undo_right(uint32_t y,unsigned s){uint32_t x=y;for(int n=0;n<8;n++)x=y^(x>>s);return x;}
uint32_t undo_left(uint32_t y,unsigned s,uint32_t m){uint32_t x=y;for(int n=0;n<8;n++)x=y^((x<<s)&m);return x;}
uint32_t untemper(uint32_t y){y=undo_right(y,18);y=undo_left(y,15,0xefc60000u);y=undo_left(y,7,0x9d2c5680u);y=undo_right(y,11);return y;}
uint32_t twist(uint32_t a,uint32_t b){uint32_t y=(a&0x80000000u)|(b&0x7fffffffu);return (y>>1)^((b&1u)?0x9908b0dfu:0u);}
std::map<std::string,std::string> fields(const std::string&s){std::map<std::string,std::string>m;std::istringstream ss(s);std::string t;while(ss>>t){auto e=t.find('=');if(e!=std::string::npos)m[t.substr(0,e)]=t.substr(e+1);}return m;}
std::vector<Row> parse(const std::string&path,bool ack_only=false){
 std::ifstream f(path);if(!f)throw std::runtime_error("cannot open source");std::vector<Row> rows;std::string line;int payload_index=0;
 while(std::getline(f,line)){auto p=line.find("PAYLOAD=");if(p==std::string::npos)continue;
   // Parse only the metadata prefix first. The selected index 129 is skipped before PAYLOAD is read or decoded.
   Row r;r.source_index=payload_index;std::string prefix=line.substr(0,p);auto m=fields(prefix);r.ts=prefix.substr(0,prefix.find(' '));
   r.job=m["JOB"];r.attempt=m.count("ATTEMPT")?std::stoi(m["ATTEMPT"]):-1;r.state=m["STATE"];r.klass=m["CLASS"]; auto tail=line.substr(p+40); auto mt=fields(tail); r.dest=mt["DEST"];
   if(payload_index==129){if(r.job!="PS-261003-0417"||r.attempt!=2||r.state!="ACK"||r.klass!="RECOVER")throw std::runtime_error("selected row metadata mismatch");payload_index++;continue;}
   if(ack_only && r.state!="ACK"){payload_index++;continue;}
   // Only nonselected retained rows reach this point and have their payload decoded.
   std::string payload=line.substr(p+8,32);if(payload.size()!=32)throw std::runtime_error("bad payload length");r.payload=payload;
   std::array<uint8_t,16>b{};for(int i=0;i<16;i++)b[i]=(uint8_t)std::stoul(payload.substr(2*i,2),nullptr,16);
   for(int i=0;i<4;i++){uint32_t le=(uint32_t)b[4*i]|((uint32_t)b[4*i+1]<<8)|((uint32_t)b[4*i+2]<<16)|((uint32_t)b[4*i+3]<<24);r.w[i]=untemper(le);}
   rows.push_back(r);payload_index++;
 }
 if(payload_index!=133) throw std::runtime_error("expected 133 source payload rows");
 return rows;
}
struct Stats{long long count=0;std::vector<std::array<int,7>>hits;};
Stats count_witnesses(const std::vector<Row>&rows,bool keep=false){int n=(int)rows.size();std::unordered_map<uint32_t,std::vector<PairRef>>xors;xors.reserve((size_t)n*n*8);for(int k=0;k<n-1;k++)for(int l=k+1;l<n;l++)for(int i=0;i<4;i++)for(int j=0;j<4;j++)xors[rows[k].w[i]^rows[l].w[j]].push_back({k,l,i,j});Stats s;for(int r=0;r<n-2;r++)for(int j=1;j<4;j++){uint32_t d=twist(rows[r].w[j-1],rows[r].w[j]);auto it=xors.find(d);if(it==xors.end())continue;for(auto&p:it->second)if(p.k>r&&p.l>p.k){s.count++;if(keep)s.hits.push_back({r,j-1,j,p.k,p.i,p.l,p.j});}}return s;}

struct PotentialDSU {
 std::vector<int> parent,rank; std::vector<long long> pot; int conflicts=0;
 explicit PotentialDSU(int n):parent(n),rank(n,0),pot(n,0){std::iota(parent.begin(),parent.end(),0);}
 std::pair<int,long long> find(int x){if(parent[x]==x)return {x,0};int p=parent[x];auto q=find(p);pot[x]+=q.second;parent[x]=q.first;return {parent[x],pot[x]};}
 void unite(int a,int b,long long d){auto A=find(a),B=find(b);int ra=A.first,rb=B.first;long long pa=A.second,pb=B.second;if(ra==rb){if(pb-pa!=d)conflicts++;return;}long long rel=d+pa-pb;if(rank[ra]<rank[rb]){parent[ra]=rb;pot[ra]=-rel;}else{parent[rb]=ra;pot[rb]=rel;if(rank[ra]==rank[rb])rank[ra]++;}}
};
void alignment_checks(const std::vector<Row>&rows,const std::vector<std::array<int,7>>&hits){
 PotentialDSU dsu((int)rows.size());long double sumxx=0,sumxy=0,sumabs=0;int edges=0;
 for(auto h:hits){int r=h[0],p=h[1],k=h[3],i=h[4],l=h[5],j=h[6];long long d1=397+p-i,d2=624+p-j;dsu.unite(r,k,d1);dsu.unite(r,l,d2);sumxx+=(k-r)*(k-r)+(l-r)*(l-r);sumxy+=(k-r)*d1+(l-r)*d2;sumabs+=std::abs((long double)d1/(k-r)-(long double)d2/(l-r));edges+=2;}
 std::map<int,int>sizes;for(int i=0;i<(int)rows.size();i++)sizes[dsu.find(i).first]++;int nonsingle=0,largest=0;for(auto&x:sizes){if(x.second>1)nonsingle++;largest=std::max(largest,x.second);}std::cout<<"POSITION_CONSTRAINTS="<<edges<<" conflicts="<<dsu.conflicts<<" components="<<sizes.size()<<" nonsingleton_components="<<nonsingle<<" largest_component="<<largest<<" fitted_constant_stride="<<(double)(sumxy/sumxx)<<" mean_within_witness_stride_disagreement="<<(double)(sumabs/hits.size())<<"\n";
 std::vector<std::pair<std::string,std::string>>cats;for(auto&r:rows){std::pair<std::string,std::string>c{r.klass,r.dest};if(std::find(cats.begin(),cats.end(),c)==cats.end())cats.push_back(c);}std::sort(cats.begin(),cats.end());long long best_full=-1,best_halves=-1;int best_first=0,best_second=0;
 for(int mask=0;mask<(1<<cats.size());mask++){std::map<std::pair<std::string,std::string>,int>gap;for(size_t q=0;q<cats.size();q++)gap[cats[q]]=3+((mask>>q)&1);std::vector<long long>S(rows.size()+1,0);for(size_t q=0;q<rows.size();q++)S[q+1]=S[q]+4+gap[{rows[q].klass,rows[q].dest}];int full=0,first=0,second=0;for(auto h:hits){int r=h[0],p=h[1],k=h[3],i=h[4],l=h[5],j=h[6];bool a=(S[k]+i-(S[r]+p)==397);bool b=(S[l]+j-(S[r]+p)==624);first+=a;second+=b;full+=a&&b;}if(full>best_full||(full==best_full&&first+second>best_halves)){best_full=full;best_halves=first+second;best_first=first;best_second=second;}}
 std::cout<<"CLASS_DEST_GAP_MODEL assignments="<<(1<<cats.size())<<" gaps={3,4} best_full_witnesses="<<best_full<<" best_first_lag_matches="<<best_first<<" best_second_lag_matches="<<best_second<<"\n";
}

void summarize(const std::string&name,std::vector<long long>v){std::sort(v.begin(),v.end());double mean=std::accumulate(v.begin(),v.end(),0.0)/v.size();std::cout<<name<<" n="<<v.size()<<" mean="<<mean<<" median="<<(v[(v.size()-1)/2]+v[v.size()/2])/2.0<<" min="<<v.front()<<" max="<<v.back()<<" ge25="<<std::count_if(v.begin(),v.end(),[](long long x){return x>=25;})<<"\n";}
void analyse(const std::vector<Row>&rows,const std::string&label){auto s=count_witnesses(rows,true);int n=rows.size();long long cand=48LL*n*(n-1)*(n-2)/6;std::cout<<"\n== "<<label<<" ==\nrows="<<n<<" tested="<<cand<<" iid32_E="<<std::setprecision(12)<<(double)cand/4294967296.0<<" hits="<<s.count<<"\n";std::map<std::pair<int,int>,int>offs;std::map<std::pair<int,int>,int>pairs;std::set<std::tuple<int,int,int,int,int,int,int>>uniq;std::set<int>hit_rows;std::set<std::string>hit_jobs,hit_states,hit_classes,hit_dests;for(auto h:s.hits){int r=h[0],k=h[3],l=h[5];offs[{k-r,l-r}]++;pairs[{h[1],h[2]}]++;uniq.insert({h[0],h[1],h[2],h[3],h[4],h[5],h[6]});for(int q:{r,k,l}){hit_rows.insert(q);hit_jobs.insert(rows[q].job);hit_states.insert(rows[q].state);hit_classes.insert(rows[q].klass);hit_dests.insert(rows[q].dest);}}std::cout<<"unique_hit_tuples="<<uniq.size()<<" participating_rows="<<hit_rows.size()<<" unique_jobs="<<hit_jobs.size()<<" states=";for(auto&x:hit_states)std::cout<<x<<",";std::cout<<" classes=";for(auto&x:hit_classes)std::cout<<x<<",";std::cout<<" dests=";for(auto&x:hit_dests)std::cout<<x<<",";std::cout<<"\noffsets:";for(auto&x:offs)std::cout<<" ("<<x.first.first<<","<<x.first.second<<")="<<x.second;std::cout<<"\npair_positions:";for(auto&x:pairs)std::cout<<" ("<<x.first.first<<","<<x.first.second<<")="<<x.second;std::cout<<"\n";for(auto h:s.hits)std::cout<<"WITNESS r="<<h[0]<<" pair="<<h[1]<<","<<h[2]<<" k="<<h[3]<<" word="<<h[4]<<" l="<<h[5]<<" word="<<h[6]<<"\n";}
int main(int argc,char**argv){std::string path=argc>1?argv[1]:"spool-reconstruction.log";auto rows=parse(path,false);auto ack=parse(path,true);std::cout<<"SOURCE_PAYLOAD_ROWS=133; selected index 129 metadata-checked and skipped before payload decode\n";std::cout<<"all-retained rows="<<rows.size()<<" ack-only rows="<<ack.size()<<"\n";std::map<std::pair<std::string,std::string>,std::vector<int>>strata;std::map<std::tuple<std::string,std::string,std::string>,std::vector<int>>strata3;for(int i=0;i<(int)rows.size();i++){strata[{rows[i].klass,rows[i].dest}].push_back(i);strata3[{rows[i].klass,rows[i].dest,rows[i].state}].push_back(i);}std::cout<<"class-dest stratum sizes:";for(auto&x:strata)std::cout<<" "<<x.first.first<<"/"<<x.first.second<<"="<<x.second.size();std::cout<<"\nclass-dest-state stratum sizes:";for(auto&x:strata3)std::cout<<" "<<std::get<0>(x.first)<<"/"<<std::get<1>(x.first)<<"/"<<std::get<2>(x.first)<<"="<<x.second.size();std::cout<<"\n";std::set<std::string>payloads;std::set<uint32_t>words;for(auto&r:rows){payloads.insert(r.payload);for(auto w:r.w)words.insert(w);}std::cout<<"unique_payloads="<<payloads.size()<<"/"<<rows.size()<<" unique_untempered_words="<<words.size()<<"/"<<(rows.size()*4)<<"\n";analyse(rows,"all 132 except selected ACK2");auto actual=count_witnesses(rows,true);alignment_checks(rows,actual.hits);analyse(ack,"ACK-only 130 except selected ACK2");auto rev=rows;std::reverse(rev.begin(),rev.end());std::cout<<"REVERSE_ORDER_HITS="<<count_witnesses(rev).count<<"\n";
 std::mt19937_64 rng(20261118);
 std::vector<long long> row_shuffle, strat_shuffle;
 for(int t=0;t<96;t++){auto v=rows;std::shuffle(v.begin(),v.end(),rng);row_shuffle.push_back(count_witnesses(v).count);}
 summarize("ROW_UNIT_SHUFFLE_ALL132",row_shuffle);
 for(int t=0;t<96;t++){auto v=rows;for(auto&kv:strata){std::vector<Row>tmp;for(int ix:kv.second)tmp.push_back(rows[ix]);std::shuffle(tmp.begin(),tmp.end(),rng);for(size_t j=0;j<kv.second.size();j++)v[kv.second[j]]=tmp[j];}strat_shuffle.push_back(count_witnesses(v).count);}
 summarize("CLASS_DEST_STRATIFIED_ROW_SHUFFLE_ALL132",strat_shuffle);
 std::vector<long long> strat3_shuffle;for(int t=0;t<96;t++){auto v=rows;for(auto&kv:strata3){std::vector<Row>tmp;for(int ix:kv.second)tmp.push_back(rows[ix]);std::shuffle(tmp.begin(),tmp.end(),rng);for(size_t j=0;j<kv.second.size();j++)v[kv.second[j]]=tmp[j];}strat3_shuffle.push_back(count_witnesses(v).count);}summarize("CLASS_DEST_STATE_STRATIFIED_ROW_SHUFFLE_ALL132",strat3_shuffle);
 std::vector<long long> ack_shuffle;for(int t=0;t<96;t++){auto v=ack;std::shuffle(v.begin(),v.end(),rng);ack_shuffle.push_back(count_witnesses(v).count);}summarize("ROW_UNIT_SHUFFLE_ACK130",ack_shuffle);
 std::map<std::pair<std::string,std::string>,std::vector<int>>ack_strata;for(int i=0;i<(int)ack.size();i++)ack_strata[{ack[i].klass,ack[i].dest}].push_back(i);std::vector<long long> ack_strat_shuffle;for(int t=0;t<96;t++){auto v=ack;for(auto&kv:ack_strata){std::vector<Row>tmp;for(int ix:kv.second)tmp.push_back(ack[ix]);std::shuffle(tmp.begin(),tmp.end(),rng);for(size_t j=0;j<kv.second.size();j++)v[kv.second[j]]=tmp[j];}ack_strat_shuffle.push_back(count_witnesses(v).count);}summarize("CLASS_DEST_STRATIFIED_ROW_SHUFFLE_ACK130",ack_strat_shuffle);
}
