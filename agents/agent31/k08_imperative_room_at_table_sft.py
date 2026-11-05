"""H17 K08 original-source imperative invitation writer, exact nonce+commitment.
Run: python agents/agent31/k08_imperative_room_at_table_sft.py original.zip
Read-only original ZIP; no source asserts the final caption used this grammar.
"""
import hashlib,hmac,itertools,json,re,sys,time,zipfile
NOTES_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
FIRST_DRAFT_COMPONENT="BF889359B0303F2B2B2FD96AE841210B"
VERBS=(
    "leave","keep","save","hold","make","set",
    "always leave","always keep","remember to leave","remember to keep",
    "let us leave","let us keep","we should leave","we can leave",
)
OBJECTS=(
    "room","some room","a little room","a place","a seat",
    "one more seat","an empty chair","one more chair","a chair",
    "a cup","one more cup","the last cup","a mug","a warm mug",
    "the light on","the lamp on","the little lamp on",
    "a place at the table","one more place","space",
)
BENEFICIARIES=(
    "","for one another","for each other","for the next watch",
    "for the next crew","for the late crew","for everyone",
    "for the next pair of hands","for whoever comes next",
    "for the last one in","for those who follow","for anyone still awake",
    "for the voices at the table","for the people coming in",
)
LOCATIONS=(
    "","at the table","by the window","beside the window",
    "beside the mugs","near the little lamp","inside","in the room",
)
SCENES=(
    "","when the night is nearly over","when the night is almost over",
    "as the night comes to an end","as the last night watch ends",
    "when the night watch ends","at the end of the night",
    "after a long watch","after the last cup","when the last cup is empty",
    "before the morning comes","before the first boat comes",
    "before the dawn","before the sea turns to morning",
    "while the sea waits outside","while the water waits outside",
    "while the sea is outside","while the water is outside",
    "with the sea outside","with the water outside",
    "with the sea beyond the window","with the water beyond the window",
    "while the room grows quiet","as the corridor goes quiet",
    "until the corridor is quiet","until the lamp goes out",
    "until the little lamp goes out","while the little lamp stays on",
    "as the night gives way to morning","as the sea gives back the daylight",
    "when morning reaches the water","with the night almost finished",
)
def norm(x):
    return " ".join(re.sub(r"[^a-z0-9\s]"," ",x.lower()).split())
def run(path):
    with zipfile.ZipFile(path) as z:
        notes=z.read("evidence/crew/noticeboard-and-desk-notes.txt")
        route=json.loads(z.read("evidence/recovery-routing.json"))
        acceptance=json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(notes).hexdigest()==NOTES_SHA
    assert all(s in notes.decode().lower() for s in (
        "a good watch leaves the room ready",
        "make their first cup alone after a bad night",
        "voices at the table","leave the light on for the next watch",
        "sea looks different",
    ))
    key=bytes.fromhex(route["K08"]["desk_nonce"])
    target=bytes.fromhex(acceptance["slot_sha256"]["K08"])
    first="a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(key,first.encode(),"sha256")[:16].hex().upper()==FIRST_DRAFT_COMPONENT
    seeded="leave room for the next watch at the table while the sea waits outside"
    planted=hashlib.sha256(hmac.digest(key,seeded.encode(),"sha256")[:16]).digest()
    count=hits=positive=0
    t0=time.monotonic()
    for verb,obj,beneficiary,location in itertools.product(
            VERBS,OBJECTS,BENEFICIARIES,LOCATIONS):
        base=" ".join(s for s in (verb,obj,beneficiary,location) if s)
        for scene in SCENES:
            variants=(base,) if not scene else (
                base+" "+scene,scene+" "+base,base+" and "+scene,scene+" and "+base,
            )
            for phrase in variants:
                component=hmac.digest(key,norm(phrase).encode(),"sha256")[:16]
                digest=hashlib.sha256(component).digest()
                count+=1
                hits+=digest==target
                positive+=digest==planted
    assert count==3920000 and positive==1
    print("K08_INVITATION complete_assignments",count,"planted",positive,
          "original_hits",hits,"elapsed",round(time.monotonic()-t0,2))
    if hits:
        print("WARNING original K08 match: repeat with matched phrase logging")
if __name__=="__main__":
    run(sys.argv[1])
