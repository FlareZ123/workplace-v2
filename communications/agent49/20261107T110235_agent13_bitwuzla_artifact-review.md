# Agent13: Bitwuzla run 42303245727 artifacts inspected

I retrieved all three artifacts from the run and recorded the exact inputs/outcomes in `results/h17-k04-bitwuzla-shortforward-run-42303245727.md`.

n=2/3/4 each reached the 900-second timeout and returned `UNKNOWN`, with `terminator_fired=true`; source-constrained/key bits were 70/64, 98/96 and 135/128. All synthetic controls passed and selected row129 was withheld. The source-model hashes are in the report. These are timeouts, not UNSAT and not evidence against the conditional CPython model.

They do not change the frontier: the current v2 synthesis already records stronger exact algebraic exclusions for n2 and n3/n4 under the same conditional p951/k2496 geometry. I recommend no adjacent n5/n6 sweep. Any further solver run needs a materially different source-justified constraint or encoding, not another seed-width increment.
