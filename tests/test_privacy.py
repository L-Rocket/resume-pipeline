import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_privacy", ROOT / "scripts/check_privacy.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PrivacyTests(unittest.TestCase):
    def test_examples_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.txt").write_text(
                "you@example.com git@github.com +1 (555) 010-1234", encoding="utf-8"
            )
            self.assertEqual(MODULE.scan(root), [])

    def test_personal_contact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_email = "person" + "@university.edu"
            private_phone = "+1 (" + "212" + ") 010" + "-1234"
            (root / "sample.txt").write_text(private_email + " " + private_phone, encoding="utf-8")
            findings = MODULE.scan(root)
            self.assertTrue(any("non-example email" in item for item in findings))
            self.assertTrue(any("non-example phone" in item for item in findings))

    def test_sensitive_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "transcript.pdf").write_bytes(b"not a real PDF")
            self.assertTrue(MODULE.scan(root))


if __name__ == "__main__":
    unittest.main()
