"""Read-only fingerprint of the supplied original H17 ZIP. Standard Python 3."""
import hashlib,struct,sys,zipfile,zlib

path=sys.argv[1]
source=open(path,"rb").read()
assert hashlib.sha256(source).hexdigest()=="e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
n=matched=pad_bits=0
hist=[0]*8
nonzero=[]
with zipfile.ZipFile(path) as z:
    for info in z.infolist():
        if info.is_dir():continue
        n+=1
        offset=info.header_offset
        assert source[offset:offset+4]==b"PK\x03\x04"
        namelen,extralen=struct.unpack_from("<HH",source,offset+26)
        begin=offset+30+namelen+extralen
        compressed=source[begin:begin+info.compress_size]
        decoded=z.read(info.filename)
        assert zlib.decompress(compressed,-15)==decoded
        compressor=zlib.compressobj(level=6,wbits=-15)
        matched+=compressed==compressor.compress(decoded)+compressor.flush()
        pad=0
        for bits in range(1,8):
            mask=((1<<bits)-1)<<(8-bits)
            base=compressed[-1]&~mask
            valid=True
            for value in range(1<<bits):
                variant=compressed[:-1]+bytes([base|(value<<(8-bits))])
                try: valid=zlib.decompress(variant,-15)==decoded
                except zlib.error:valid=False
                if not valid:break
            if not valid:break
            pad=bits
        value=compressed[-1]>>(8-pad) if pad else 0
        hist[pad]+=1
        pad_bits+=pad
        if value:nonzero.append((info.filename,pad,value))
print("zlib",zlib.ZLIB_VERSION,"members",n,"recompressed_match",matched)
print("unused_tail_bits",pad_bits,"hist",hist,"nonzero",nonzero)
assert n==46 and pad_bits==170 and not nonzero
if zlib.ZLIB_VERSION=="1.3.1":assert matched==46
