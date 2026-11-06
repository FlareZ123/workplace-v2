// Reproducible source-conditioned Go math/rand printer issuer search.
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"hash/crc32"
	"math/rand"
	"os"
	"regexp"
	"sort"
	"strings"
	"time"
)

const spoolSHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
const expectedACK = "A9A9DC5731A5E2AE879C47215C2559D5"

type route struct {
	K04 struct {
		Mask string `json:"masked_component"`
	} `json:"K04"`
}
type acceptance struct {
	Slots map[string]string `json:"slot_sha256"`
}

func mustRead(path string) []byte {
	b, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	return b
}
func mustHex(s string) []byte {
	b, err := hex.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return b
}
func payloads(b []byte) [][16]byte {
	pattern := regexp.MustCompile(`PAYLOAD=([0-9A-F]{32})`)
	matches := pattern.FindAllSubmatch(b, -1)
	if len(matches) != 133 {
		panic(fmt.Sprintf("spool records %d, expected 133", len(matches)))
	}
	out := make([][16]byte, len(matches))
	for i, m := range matches {
		copy(out[i][:], mustHex(string(m[1])))
	}
	return out
}
func next(r *rand.Rand, mode int) [16]byte {
	var out [16]byte
	switch mode {
	case 0:
		_, err := r.Read(out[:])
		if err != nil {
			panic(err)
		}
	case 1, 2, 5, 6:
		for j := 0; j < 2; j++ {
			var v uint64
			if mode >= 5 {
				v = uint64(r.Int63())
			} else {
				v = r.Uint64()
			}
			if mode%2 == 1 {
				binary.LittleEndian.PutUint64(out[8*j:], v)
			} else {
				binary.BigEndian.PutUint64(out[8*j:], v)
			}
		}
	case 3, 4:
		for j := 0; j < 4; j++ {
			v := r.Uint32()
			if mode == 3 {
				binary.LittleEndian.PutUint32(out[4*j:], v)
			} else {
				binary.BigEndian.PutUint32(out[4*j:], v)
			}
		}
	case 7:
		for j := 0; j < 16; j++ {
			out[j] = byte(r.Intn(256))
		}
	default:
		panic("invalid mode")
	}
	return out
}
func reduction(coupon [16]byte, mask []byte) [16]byte {
	var component [16]byte
	for i := 0; i < 16; i++ {
		component[i] = coupon[i] ^ mask[i]
	}
	return component
}
func seeds() []int64 {
	seen := map[int64]bool{}
	appendSeed := func(s int64) { seen[s] = true }
	event := time.Date(2026, 10, 3, 18, 2, 0, 0, time.UTC).Unix()
	for delta := int64(-43200); delta <= 43200; delta++ {
		appendSeed(event + delta)
	}
	// Directly named original dates, job numbers and microbatch counters.
	for _, v := range []int64{1, 0, 261003, 20261003, 20260924, 417, 420, 448, 300, 427, 1802, 700, 135, event * 1000, event * 1000000} {
		appendSeed(v)
	}
	for hour := 0; hour < 24; hour++ {
		t := time.Date(2026, 10, 3, hour, 0, 0, 0, time.UTC).Unix()
		appendSeed(t * 1000)
		appendSeed(t * 1000000)
	}
	for _, label := range []string{
		"IR-261003-H17", "PS-261003-0417", "PS-261003-0420", "PS-261003-0448",
		"H17-IR-261003", "ESC-N", "RECOVER", "PS-261003-0300", "2026-10-03",
	} {
		appendSeed(int64(crc32.ChecksumIEEE([]byte(label))))
		d := sha256.Sum256([]byte(label))
		appendSeed(int64(binary.LittleEndian.Uint64(d[:8])))
		appendSeed(int64(binary.BigEndian.Uint64(d[:8])))
	}
	sorted := make([]int64, 0, len(seen))
	for s := range seen {
		sorted = append(sorted, s)
	}
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
	return sorted
}
func selfTest(mask []byte) {
	for mode := 0; mode < 8; mode++ {
		seed := int64(64126)
		r := rand.New(rand.NewSource(seed))
		var target [16]byte
		for i := 0; i <= 129; i++ {
			target = next(r, mode)
		}
		r = rand.New(rand.NewSource(seed))
		var predicted [16]byte
		for i := 0; i <= 129; i++ {
			predicted = next(r, mode)
		}
		if predicted != target {
			panic("synthetic withheld coupon mismatch")
		}
		component := reduction(target, mask)
		synth := sha256.Sum256(component[:])
		if synth == ([32]byte{}) {
			panic("empty synthetic digest")
		}
	}
}
func main() {
	spoolFile := flag.String("spool", "resources/evidence/print/spool-reconstruction.log", "read-only source spool path")
	routeFile := flag.String("route", "evidence/recovery-routing.json", "read-only original route path")
	acceptFile := flag.String("accept", "acceptance.json", "read-only original acceptance path")
	flag.Parse()
	spool := mustRead(*spoolFile)
	if fmt.Sprintf("%x", sha256.Sum256(spool)) != spoolSHA {
		panic("original spool SHA mismatch")
	}
	records := payloads(spool)
	if hex.EncodeToString(records[129][:]) != strings.ToLower(expectedACK) {
		panic("selected source selector mismatch")
	}
	var rt route
	if err := json.Unmarshal(mustRead(*routeFile), &rt); err != nil {
		panic(err)
	}
	mask := mustHex(rt.K04.Mask)
	if len(mask) != 16 {
		panic("original route mask width")
	}
	var acc acceptance
	if err := json.Unmarshal(mustRead(*acceptFile), &acc); err != nil {
		panic(err)
	}
	expected := acc.Slots["K04"]
	if len(expected) != 64 {
		panic("K04 commitment unavailable")
	}
	testCoupon := records[129] // authentic copied buffer; not considered valid physical coupon
	check := reduction(testCoupon, mask)
	if fmt.Sprintf("%x", sha256.Sum256(check[:])) == expected {
		panic("known copied coupon unexpectedly passes")
	}
	selfTest(mask)
	seedList := seeds()
	controls := []int{0, 1, 14, 63, 100, 128, 130, 131, 132}
	var total, sourceFullMatches, originalHits uint64
	for mode := 0; mode < 8; mode++ {
		var modeSource, modeHits uint64
		for _, seed := range seedList {
			r := rand.New(rand.NewSource(seed))
			ci := 0
			for i := 0; i < 133; i++ {
				coupon := next(r, mode)
				if i == 129 {
					component := reduction(coupon, mask)
					sum := sha256.Sum256(component[:])
					if fmt.Sprintf("%x", sum) == expected {
						fmt.Printf("ORIGINAL_K04_PASS mode=%d seed=%d coupon=%x component=%x\n", mode, seed, coupon, component)
						modeHits++
					}
					total++
				}
				if ci < len(controls) && i == controls[ci] {
					if coupon == records[i] {
						fmt.Printf("INTACT_WHOLE_PACKET_MATCH mode=%d seed=%d row=%d\n", mode, seed, i)
						modeSource++
					}
					ci++
				}
			}
		}
		sourceFullMatches += modeSource
		originalHits += modeHits
		fmt.Printf("MODE=%d seeds=%d intact_packet_matches=%d original_target_hits=%d\n", mode, len(seedList), modeSource, modeHits)
	}
	fmt.Printf("GO_SOURCE_PINNED seeds=%d complete_K04_candidates=%d intact_packet_matches=%d original_hits=%d\n", len(seedList), total, sourceFullMatches, originalHits)
	if originalHits == 0 {
		fmt.Println("K04_NO_MATCH: this seed+serialization model only")
	}
	fmt.Println("Go source generator in math/rand, not crypto/rand; this is a conditional issuer model.")
	fmt.Println("No changes to source, acceptance, verifier or published candidate.")
}
