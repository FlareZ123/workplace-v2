import unittest

from agents.agent25.k04_native_spool_commitment_bridge import self_test


class K04NativeSpoolCommitmentBridgeTests(unittest.TestCase):
    def test_job_id_paired_spl_window_recovers_synthetic_component(self):
        result = self_test()
        self.assertTrue(result["passed"])
        self.assertEqual(result["matching_pairs"], 1)
        self.assertEqual(
            result["component_hex"],
            "00112233445566778899AABBCCDDEEFF",
        )
        self.assertEqual(result["candidate_offset"], 6)


if __name__ == "__main__":
    unittest.main()
