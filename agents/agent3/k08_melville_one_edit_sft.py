"""K08: source-cued Melville stanza one-edit candidate test. Read-only.

This Gutenberg literary antecedent is only hypothesized, never authenticated as
Emily's source. Selected K08 phrase is unknown absent full original commitment.
"""
from __future__ import annotations
import hashlib, hmac, re, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"resources"
NOTE=ROOT/"evidence/crew/noticeboard-and-desk-notes.txt"
NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
POEM="""Tonight's the night that ends the week--
Ends day and week and month and year:
A fourfold imminent flickering time,
For now the midnight draws anear:
Eight bells! and passing-bells they be--
The Old year fades, the Old Year dies at sea.

He launched them well. But shall the New
Redeem the pledge the Old Year made,
Or prove a self-asserting heir?
But healthy hearts few qualms invade:
By shot-chests grouped in bays 'tween guns
The gossips chat, the grizzled, sea-beat ones.

And boyish dreams some graybeards blab:
"To sea, my lads, we go no more
Who share the Acapulco prize;
We'll all night in, and bang the door;
Our ingots red shall yield us bliss:
Lads, golden years begin to-night with this!"

Released from deck, yet waiting call,
Glazed caps and coats baptized in storm,
A watch of Laced Sleeves round the board
Draw near in heart to keep them warm:
"Sweethearts and wives!" clink, clink, they
meet,
And, quaffing, dip in wine their beards of
sleet.
"Ay, let the star-light stay withdrawn,
So here her hearth-light memory fling,
So in this wine-light cheer be born,
And honor's fellowship weld our ring--
Honor! our Admiral's aim foretold:
"""
POEM_SHA="25d1cdf89ffe2d2ac100cd9c699018f6e5c828f837431a51989e90e1ab0d72bb"
NOTES_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

def norm(s: str) -> str:
    return " ".join(re.sub("[^a-z0-9\\s]"," ",s.lower()).split())

def check(phrase: str) -> str | None:
    raw=hmac.digest(NONCE,phrase.encode(),"sha256")[:16]
    return raw.hex().upper() if hashlib.sha256(raw).hexdigest()==TARGET else None

def main() -> None:
    assert hashlib.sha256(POEM.encode()).hexdigest()==POEM_SHA
    raw=NOTE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==NOTES_SHA
    parts=re.split(r"(?m)^N\d\d / ",raw.decode("utf-8"))
    emily=" ".join(part.split("\n",1)[1] for part in parts if part.startswith("Emily "))
    vocab=sorted(set(re.findall("[a-z0-9]+",norm(emily))))
    poem=norm(POEM).split()
    assert (len(poem),len(vocab))==(210,90)
    source="leave the light on for the next watch".split()
    assert "leave the lamp on for the next watch" in (
       " ".join(source[:j]+[w]+source[j+1:]) for j in range(len(source)) for w in vocab)
    checks=0
    for lo in range(len(poem)):
        for length in range(6,21):
            if lo+length>len(poem):break
            base=poem[lo:lo+length]
            alternatives=[]
            for i in range(length):
                alternatives.append(" ".join(base[:i]+base[i+1:]))
                for w in vocab:
                    if w!=base[i]:
                        alternatives.append(" ".join(base[:i]+[w]+base[i+1:]))
            for i in range(length+1):
                for w in vocab:
                    alternatives.append(" ".join(base[:i]+[w]+base[i:]))
            for phrase in set(alternatives):
                checks+=1
                found=check(phrase)
                if found:
                    print("ORIGINAL_K08_HIT",repr(phrase),found)
                    return
    print("SOURCE_PINNED_ONE_EDIT_PLANTED_POSITIVE=PASS")
    print("SOURCE_EDITOR_COMPLETE_CHECKS",checks,"ORIGINAL_K08_MATCHES",0)
    assert checks==7185188

if __name__=="__main__":main()
