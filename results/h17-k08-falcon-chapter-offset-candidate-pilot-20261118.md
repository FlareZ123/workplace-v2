# K08: Falcon 4+12-bit chapter/word packet pilot

**Agent 20 | 18 November 2026 | Independent reproduction of Agent43's bounded SFT.**  
This is a conjectural source-indexed pilot, not an authenticated recovery route. No original evidence, routing, acceptance, verifier or canonical candidate was changed.

## Hypothesis and frozen source pins

Two original ACK1/RECOVER packets, PS-261003-0320 and PS-261003-0323, may encode eight 16-bit addresses into the pinned 1889 *Falcon on the Baltic* normalized word stream. Each u16 is interpreted as a 4-bit chapter index plus 12-bit within-chapter word offset, testing both high/low nibble orientations, BE/LE byte order, and zero-/one-based chapter and word indices. Each candidate phrase is HMAC-SHA256 keyed by the original K08 desk nonce, truncated to 16 bytes, then SHA-256 checked against the original K08 commitment.

The source does **not** authenticate N23→PS-0323, the use of PS-0320 as a control, Falcon as David's physical map-back book, or this 4+12 address format.

- Pinned text: `work/h17_falcon_1889_normalized_words.txt`, 81,392 words; SHA-256 excluding trailing LF `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`.
- Pinned spool: SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- K08 key/nonce: `5F933DA6A1BD03C32DA5CBC25344F497`.
- K08 target: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- Packet payloads: PS-0320 `9B9D8D85D48AF325FF55556CE0AE7BF3`; PS-0323 `1E51EFD2E5CA8F4E1FC8B49297B3D74F`.
- Chapter boundaries in the pinned normalized stream: `[0,3278,8236,14403,20871,28053,33145,40292,44696,49818,56233,61762,67997,74086,79441,81392]`. The first segment is the unheaded opening/Chapter I, followed by explicit II–XV headings.

## Independent reproduction and controls

I independently reimplemented the committed decoder against the pinned wordstream and the exact spool payloads. The candidate family is:

`2 jobs × 3 packet transforms (raw/AES-ECB encrypt/AES-ECB decrypt) × 2 byte orders × 2 nibble orientations × 2 chapter bases × 2 word bases = 96 attempted`.

**32** produced eight in-range words; **0** matched the original K08 commitment. Controls passed:
- N02 known-answer HMAC16: `BF889359B0303F2B2B2FD96AE841210B`.
- NIST AES-128-ECB known-answer vector: `69c4e0d86a7b0430d8cdb78070b4c55a`.
- Synthetic planted 4+12-bit chapter/word addresses decoded to the expected eight words using the frozen boundary vector.

## All complete in-range candidates

| Job | Transform | Endian | 4+12 orientation | Chapter base | Word base | Eight-word phrase | HMAC16 | SHA-256 of HMAC16 |
|---|---|---|---|---:|---:|---|---|---|
| 0320 | raw | big | low | 1 | 0 | `there village of many house with aspect clock` | `0094B4DB7F99FDD6C12A49722539346B` | `bb0641b43788c4cac619bc0902b734dc8aa6cd93536edb129c0f4f65cbc8b1ff` |
| 0320 | raw | big | low | 1 | 1 | `day little end its small scratch the o` | `55E6DBA54D943A624BDCD35CEF1D1FE2` | `f7b25d09dcc62ea182765ad56ee5e6b279f86e0f3fa32888213cc96c679482eb` |
| 0320 | raw | little | high | 1 | 0 | `thousand of may jim enough willems it theatres` | `5F0E5A688F3E3DED13030BA9900F8CFC` | `df3e54994b2d9bd81eab5995de7fa29164a16557691846b0a10343aa12768dc8` |
| 0320 | raw | little | high | 1 | 1 | `a air i here t noord behind air` | `FEE4DE0C064D00078F20865E9643A055` | `b6a36f4dd2540ca75466f4acb4b749b4ca2eb96a30cf6df47185f751a071be2f` |
| 0320 | AES encrypt | little | high | 1 | 0 | `crime hill done who in this leak this` | `CE0651431461CB1D8BFD3EEAFB141CBA` | `23150d8f69326d5ab645e0c0102d57325b58f4deb760e863824ac9611c2d717a` |
| 0320 | AES encrypt | little | high | 1 | 1 | `heinous clad be all exception behind mysterious in` | `964A64633ACB0D5325CE99B716BC683C` | `6d3255f8f500752ef267960ff46a273bd2597999c6a421f22268306823957d3e` |
| 0320 | AES encrypt | little | low | 0 | 0 | `back mainland having the not lady its anchorage` | `A0EAACAC2B6E59F066EA3B0106B93BC2` | `93d3080cd161586b3c16339e6f58e7c6868b096097e1a952bf1ac147a04b32ee` |
| 0320 | AES encrypt | little | low | 0 | 1 | `and the and on did old with old` | `3BC6BFA3D60C2C0C2C7C26016E09E82D` | `10eff07a4611ee48e8d3c04dab5995ff16d83e83ffc4e644ad3aea40252a0fb2` |
| 0320 | AES decrypt | big | high | 0 | 0 | `in the to england the catch in town` | `5550DC5E5DAE81ADB9CCE69F9A1C9334` | `95c352a41b7b746c496f7be8e456e223898369d04e698761ff26de7e2ea42933` |
| 0320 | AES decrypt | big | high | 0 | 1 | `sight by had in as to invested little` | `903F2F59FF2D286F7347ADFE9F263A09` | `42057541328d286eadea5cee257205ca580079c00009827ad3d6bd02b328520c` |
| 0320 | AES decrypt | big | high | 1 | 0 | `had on who is there i eyes us` | `2667BC6805BC3DE9933FA681F1956EA7` | `c85b3d6634294a5d8dd392f5ccfdf9c2ab85bde2b72e33f8433f8667aa211458` |
| 0320 | AES decrypt | big | high | 1 | 1 | `who bird chap which and distant shy prevented` | `56A24B31EF0C310352A9FEB935468082` | `c87fc955ae7ea02f15d02d9ee489eefbd25e523a4eda532af74403e882db9ad6` |
| 0320 | AES decrypt | little | low | 0 | 0 | `up entertained hours walked a enough but drinks` | `E5AD3E93D37DD382B21810DC2F44DAE2` | `e329d20c69ba17ddc6184ae57e943d5349875a37d67e2c0d5e580bae58ca1418` |
| 0320 | AES decrypt | little | low | 0 | 1 | `bound wright four anyone tobacco high change more` | `AC70D522ADFBC83AAE93493E642DB379` | `682fee2f3b049749cd2bbe6ca221855ccb056313ca020bd49fb6b9d8f523ad4c` |
| 0320 | AES decrypt | little | low | 1 | 0 | `he yards the its that deepening the could` | `D41D9086B4331F6A397C423771E617F7` | `200e4e2c38a001e1615e9b2d76bf8faa4f9fb03f8ef5522bf7846f283ab23700` |
| 0320 | AES decrypt | little | low | 1 | 1 | `and 110 for found thought artificial down we` | `FD15754C94DACF7B7809FB2DB6A29C8C` | `09c39bdc1fc1dad53077930465780ee3becc406a7c53fa76ab5e123c454571c4` |
| 0323 | raw | little | high | 0 | 0 | `through shore unlike along be dutch conceit dared` | `1AB96E9BEDEE0509A3F0A30788738A71` | `f5d26119fcaf5b3b7e885ce3508161253e48f5a75699aca4684c60f5df665819` |
| 0323 | raw | little | high | 0 | 1 | `but the hundested staggered to the self i` | `247E642C79A01A1CAF1E0588BFF69860` | `5d536700369f7668fb0b451f95b472a19aa4dd65f598807b67e1aed5c78fa599` |
| 0323 | raw | little | high | 1 | 0 | `soul the desolate round view of side i` | `921ECD4C6BEAEC64A1BB8CB7521463BA` | `1aabd033a78db154916ecdbda799445fbaebee03e778038186dc0159dfbae05d` |
| 0323 | raw | little | high | 1 | 1 | `a across as stroll the bay by charge` | `4A79BE0E1B2E69C5CAD30F7B179BD8C7` | `0d4fe15c76d5f6f27f5028aea21defa713320376f60f6decd14af458e65f588d` |
| 0323 | AES encrypt | big | low | 0 | 0 | `a fortunate to us which ancient as times` | `66B4F6D93AE45B271DC3B91DC36B7B63` | `7b93d73a02772d36e6d0886586db0d61f201ecd3664cac181f439104b8d266de` |
| 0323 | AES encrypt | big | low | 0 | 1 | `in a stretching to other the transformation several` | `2292535D4180435C175DBB0537540771` | `17106273c256b9cbe1a77fabde2a4624bc3db4675fc2a2f178a06fe09a368489` |
| 0323 | AES encrypt | little | high | 1 | 0 | `with was replied up was to were of` | `13C7E8C828BC737B655486369FE5417E` | `37849d4dd92e2e1682405277fd55e3e510b2b6683dae78889f83aff32be195bd` |
| 0323 | AES encrypt | little | high | 1 | 1 | `provided it conscience broke times easy high that` | `9C1BCD5CE001DC35AE30E179D7C6488B` | `8f7714de448b46bc4307a2753a2a02f78cb0ec3456641c912fc39b826383a0d3` |
| 0323 | AES decrypt | big | high | 0 | 0 | `to one be wind track was o could` | `AAE32FABC4AF5216B9265B1FF757AD09` | `f762c1ebb85da00aa5f927a6198ba25804d121224b7ab0cb430c56a0093e8486` |
| 0323 | AES decrypt | big | high | 0 | 1 | `open day cannot little the and two we` | `FF06920414379293B1E51A5A342F7DA9` | `ca20eb956088f6fa76da4195c8f1e7a3fc64ec16edd788f967f98372c6be6b44` |
| 0323 | AES decrypt | big | high | 1 | 0 | `and spouse was the said where among here` | `3F3EEADB6A7F85700677638778827222` | `2897b27c7141f719da681cb5b5cc0d21b628db6cb71e743080dcbcc727a089f2` |
| 0323 | AES decrypt | big | high | 1 | 1 | `up his breeze saying i inn hills roofs` | `D4FBA56BB4B3BED239FA2F403FF792E5` | `2d991400c7cc11584efd4ae43678b62d9c1a4a72cf54c53c60fcf2a9d3bba740` |
| 0323 | AES decrypt | little | low | 0 | 0 | `far so ought having i for in we` | `0F00AF74C58158512A392D68A00C8333` | `f9a5e08adf26a90c02286c99e9146d198015c7b5eba2cf9b514b99c3ca6e8501` |
| 0323 | AES decrypt | little | low | 0 | 1 | `was bay it farm way bound put when` | `8494D9B9F23C8C43083755C64010F467` | `d5da9275289a1f62c0fbda55f229622dfc32b090b98026a74d082c2e533d304c` |
| 0323 | AES decrypt | little | low | 1 | 0 | `church by with the light to everywhere astonishment` | `23671C2D3A4CF2CC98DFB21F05ACBD54` | `69e609c464cc400cd0df08d617371d15f9d3619f1f8038f096a939a033b19617` |
| 0323 | AES decrypt | little | low | 1 | 1 | `the bordered bunk was a falcon apparent great` | `D18BC36D894ADD1B4555674D12AC4F01` | `6dbfd9ee9d7ee998af43e6e26250487cb00178e40e8730ea1b0cf2ebcedcc99a` |

## Result and boundary

**0/32 complete in-range phrases matched the original K08 SHA-256 commitment.** The independent reproduction agrees with Agent43's script-level assertions `attempts=96, valid=32`, and confirms that the successful CI run was not itself a K08 match.

This closes only the frozen raw/AES-ECB packet → 4+12 chapter/word → pinned Falcon text → original K08 HMAC/SHA family. It does not authenticate the physical book, the packet-to-caption relation, or rule out other independently sourced carriers. Do not widen the hypothesis with arbitrary chapter offsets, title skips or other books without a source/custody witness.
