import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h17_synthetic_ci_bundle import FILES, stage
from h17_synthetic_transfer_fixture import write_fixture, HMAC16, NONCE, PHRASE
import hashlib
import hmac

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.work = self.root / 'work'
        self.work.mkdir(parents=True)
        for name in FILES:
            (self.work / name).write_text('# invented code fixture\n')
        self.secret = self.root / 'resources' / 'invented-sentinel'
        self.secret.parent.mkdir()
        self.secret.write_text('SYNTHETIC SENTINEL; must not stage')
        (self.work / 'unlisted.py').write_text('SYNTHETIC SENTINEL; must not stage')
        self.out = self.base / 'out'

    def test_positive_allowlist(self):
        self.assertEqual(stage(self.root, self.out), len(FILES))
        self.assertEqual({p.name for p in self.out.iterdir()}, set(FILES))
        self.assertTrue(all(p.read_text() == '# invented code fixture\n' for p in self.out.iterdir()))

    def test_symlink_fails_closed(self):
        path = self.work / FILES[0]
        path.unlink()
        path.symlink_to(self.secret)
        with self.assertRaises(OSError):
            stage(self.root, self.out)
        self.assertFalse(self.out.exists())

    def test_missing_file_fails_closed(self):
        (self.work / FILES[-1]).unlink()
        with self.assertRaises(FileNotFoundError):
            stage(self.root, self.out)
        self.assertFalse(self.out.exists())

    def test_no_existing_or_in_repo_destination(self):
        self.out.mkdir()
        for out in (self.out, self.root / 'output'):
            with self.assertRaises(ValueError):
                stage(self.root, out)

    def test_synthetic_fixture(self):
        acceptance, chain = write_fixture(self.base / 'fixture')
        self.assertEqual(hmac.digest(NONCE, PHRASE.encode(), 'sha256')[:16], HMAC16)
        self.assertEqual(acceptance['slot_sha256']['K08'], hashlib.sha256(HMAC16).hexdigest())
        self.assertEqual(len(chain), 16)

if __name__ == '__main__':
    unittest.main()
