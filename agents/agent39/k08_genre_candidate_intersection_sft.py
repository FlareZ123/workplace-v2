"""Count exact K08 phrase overlaps between prior Agent10 and Agent39 editors.
Read-only, standard library, repo-local. Does not consult the original K08 hash.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

old = load('h17_agent10_editor', ROOT / 'agents/agent10/k08_purpose_editor_sft.py')
new = load('h17_agent39_editor', ROOT / 'agents/agent39/k08_envelope_genre_editor_sft.py')

prior = set(map(old.norm, old.candidates()))
expanded = set(map(new.norm, new.phrase_pool()))
checked = {s for s in expanded if new.has_themes(s)}
assert len(prior) == 21836
assert len(expanded) == 257296
assert len(checked) == 25388
assert len(prior & expanded) == 419
assert len(prior & checked) == 0
assert len(checked - prior) == 25388
print('AGENT10_PRIOR_ALL', len(prior))
print('AGENT39_COMPLETE_ALL', len(expanded))
print('AGENT39_SCENE_CONDITIONED', len(checked))
print('COMPLETE_POOL_OVERLAP', len(prior & expanded))
print('ORIGINAL_TARGET_CHECKED_OVERLAP', len(prior & checked))
print('INCREMENTAL_UNIQUE_TARGET_CHECKS', len(checked - prior))
print('NO_ORIGINAL_K08_MATCH from Agent39 original experiment')
