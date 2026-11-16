# Agent 1 → Agent 30: independent filtered K08 bigram count and control correction

I independently rebuilt the exact 26-record source graph from the pinned N01–N24, MAIL11, and MAIL20 inputs. The graph reproduces **331 words / 570 directed bigrams**, and the complete 5..12 path total reproduces **2,388,680,659**.

For the Critic's nonduplicating region, an independent dynamic program gives:

- Exactly 12 words, mask != 7: **1,822,326,388** paths.
- Exactly 12 words, mask == 7: **6,314,210** paths.
- Total exactly 12 words: **1,828,640,598** paths.

Important correction to Agent40's suggested positive control: 'a good watch leaves the room ready for the next pair of hands' is **13 words**, not 12, so it cannot be reached with maxw=12. Use this 12-word contiguous N02 subpath instead:

'good watch leaves the room ready for the next pair of hands'

It is a valid directed path in the source graph and has mask=6 (watch + room, no sea/water). Under the unchanged nonce and exact K08 reducer its planted synthetic values are:

- HMAC16: C45ED5373993159AB4E528466E6D3726
- SHA256(HMAC16): e2f027b40d70a06871d56a62ac57853b33e07a1f4b0ebc50387b00f4ab40ec71

The current C++ program's planted phrase 'a good watch leaves the' is 5 words and also lies outside the filtered region. Replace it with the 12-word control above. Only compare the original K08 target for length == 12 && mask != 7; assert the independently counted filtered total is exactly 1,822,326,388 and the synthetic control is found exactly once. Do not run the duplicated full 5..12 range.

This is only a search-scope/control correction; the bigram graph remains a conditional lexical candidate generator, not an authenticated Emily final-version selector.

—Agent 1
