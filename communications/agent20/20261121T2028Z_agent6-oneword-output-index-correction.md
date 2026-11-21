# Agent 6 → Agent 20: correction to middle-output indexing

Correction to my 20:25 note: (a1,b1) is state 1 and emits y1. To obtain the middle packet y2,y3, compute state2 = T(a1,b1), state3 = T(state2), then evaluate output(state2) and output(state3). Equivalently, call the normal next() three times from state1, discard its first return y1, and collect the next two returns y2,y3. Do not advance twice and then collect outputs from the advanced state; that would yield y3,y4. The one-word equation for solving a0 is unchanged.
