"""Source-only p951 WN14 and full-target quotient, with negative donor rank.

Run: python agents/agent8/k04_p951_witness_target_projection_sft.py resources
Works on original 46-member case ZIP extracted to resources. Selected print
ACK, K04 mask, K04/K08 digest, key candidate and verifier are excluded.
"""
import hashlib
import importlib.util
import re
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
DEP = HERE / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("h17_p951", DEP)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ORIGIN = -1100
U = 0xffffffff
M = 0x9908b0df
WN = ("049AAB2E","1CDE7A82","CD7C6023","4303C91A")
SENSITIVE = (-1089,-1088,-1087,-1086,-1085,-1084,-919,-918,-917,-916,-915,
             -861,-860,-859,-858,-857,-692,-523,-465,-464,-463,-462,-461,
             -296,-295,-294,-293,-292,-69,-68,-67,-66,-65)
WINDOWS = (-1089,-1088,-1087,-919,-918,-861,-860,-465,-464,-296,-295,-69,-68)


def states(last=2067):
    out = [[1 << (32*i+b) for b in range(32)] for i in range(624)]
    for i in range(624,last+1):
        p,n,m = out[i-624],out[i-623],out[i-227]
        out.append([m[b] ^ (p[31] if b==30 else n[b+1] if b<30 else 0)
                    ^ (n[0] if (M>>b)&1 else 0) for b in range(32)])
    return out


def temper_expr(raw):
    v=list(raw)
    for direction,shift,mask in ((-1,11,U),(1,7,0x9d2c5680),
                                 (1,15,0xefc60000),(-1,18,U)):
        z=list(v)
        for b in range(32):
            index = b-shift if direction==1 else b+shift
            if 0<=index<32 and (mask>>b)&1:
                z[b]^=v[index]
        v=z
    return v


def reduce_affine(expr, bit, basis):
    row=(expr<<1)|(bit&1)
    while row:
        known=basis.get(row.bit_length()-1)
        if known is None:
            return row
        row^=known
    return 0


def source_basis(expr, rows):
    basis={}
    for i,position in enumerate(s.STARTS):
        if i==129:continue
        payload=rows[i]
        for j in range(4):
            native=s.untemper(int.from_bytes(payload[j*4:j*4+4],"little"))
            for bit,term in enumerate(expr[1100+position+j]):
                result=reduce_affine(term,(native>>bit)&1,basis)
                assert result!=1, "original model source contradiction"
                if result>1:basis[result.bit_length()-1]=result
    return basis


def inject_words(basis, expr, first, values):
    b=basis.copy()
    for j,native in enumerate(values):
        for bit,term in enumerate(expr[1100+first+j]):
            result=reduce_affine(term,(native>>bit)&1,b)
            if result==1:return None
            if result>1:b[result.bit_length()-1]=result
    return b


def add_linear(b,expr):
    while expr:
        pivot=expr.bit_length()-1
        known=b.get(pivot)
        if known is None:
            b[pivot]=expr
            return 1
        expr^=known
    return 0


def quotient(b, targets):
    joint=b.copy()
    return sum(add_linear(joint,e) for e in targets)


def check_synthetic(expr, targets):
    rng=random.Random(20261102)
    native=[s.untemper(rng.getrandbits(32)) for _ in range(len(expr))]
    for t in range(len(expr)-624):
        packed=(native[t]&0x80000000)|(native[t+1]&0x7fffffff)
        assert native[t+624] == (native[t+397]^s.twist(packed))
    for word_index in (0,1,327,623,624,1100,1623,1951,2067):
        for bit,component in enumerate(expr[word_index]):
            # a set bit in a symbolic expression identifies a base-state bit
            v=component
            output=0
            while v:
                low=v&-v
                k=low.bit_length()-1
                output^=(native[k//32]>>(k%32))&1
                v^=low
            assert output == ((native[word_index]>>bit)&1)
    for j in range(4):
        for bit,component in enumerate(targets[j*32:(j+1)*32]):
            v=component
            output=0
            while v:
                low=v&-v
                k=low.bit_length()-1
                output^=(native[k//32]>>(k%32))&1
                v^=low
            assert output == ((s.temper(native[1100+951+j])>>bit)&1)
    print("Genuine seeded MT symbolic forward/tempered expression: PASS")


def main(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==s.SPOOL_SHA
    rows=[bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([A-F0-9]{32})",raw)]
    assert len(rows)==133 and len(s.STARTS)==133 and s.STARTS[129]==951
    rows[129]=b"" # selected ACK explicitly unavailable to calculations
    expr=states()
    targets=[e for j in range(4) for e in temper_expr(expr[1100+951+j])]
    check_synthetic(expr,targets)
    b=source_basis(expr,rows)
    assert len(b)==15365
    linear={pivot-1:row>>1 for pivot,row in b.items()}
    assert quotient(linear,targets)==128
    print("Original source basis rank:",len(linear),"selected quotient:",128)

    tests=0
    for order in ("little","big"):
        raw_w=[s.untemper(int.from_bytes(bytes.fromhex(v),order)) for v in WN]
        for pos in WINDOWS:
            z=inject_words(b,expr,pos,raw_w)
            assert z is not None
            assert len(z)-len(b)==128
            after={p-1:row>>1 for p,row in z.items()}
            rank=quotient(after,targets)
            assert rank==128, (order,pos,rank)
            tests+=1
    assert tests==26
    print("Source-hypothesized WN14 native quartets: 26 consistent,",
          "26 with full 128-bit selected quotient.")

    single=[]
    for pos in range(-1100,0):
        v=linear.copy()
        for term in expr[1100+pos]:add_linear(v,term)
        if quotient(v,targets)!=128:
            single.append((pos,quotient(v,targets)))
    assert single == [(-523,127)],single
    print("Unique full-word negative donor reducing target rank:",single)

    btags={p-1:(row>>1,(row&1)<<128) for p,row in b.items()}
    def tagged_reduce(expression,tag):
        while expression:
            key=expression.bit_length()-1
            if key not in btags:break
            other,other_tag=btags[key]
            expression^=other
            tag^=other_tag
        return expression,tag
    for j,e in enumerate(targets):
        remainder,label=tagged_reduce(e,1<<j)
        if remainder:btags[remainder.bit_length()-1]=(remainder,label)
    for bit,expected_const in ((0,1),(1,0)):
        rem,tag=tagged_reduce(expr[1100-523][bit],0)
        assert rem==0
        assert (tag&((1<<128)-1))==0x40008000
        assert tag>>128==expected_const
    print("Original conditional source relation: X[-523].bit0 =",
          "parity(printed_selected_word0 bits 15,30) XOR 1;",
          "X[-523].bit1 = same parity.")
    oracle=linear.copy()
    for pos in SENSITIVE:
        for term in expr[1100+pos]:add_linear(oracle,term)
    assert quotient(oracle,targets)==1
    oracle_all=linear.copy()
    for pos in range(-1100,-499):
        for term in expr[1100+pos]:add_linear(oracle_all,term)
    assert quotient(oracle_all,targets)==0
    print("All 33 previously named sensitive full words together",
          "leave 1 target degree; all -1100..-500 words remove all.",
          "Sensitivity of a particular basis is insufficient alone",
          "to prove complete target observability.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else HERE/"resources")
