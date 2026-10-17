import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_word_resumes", ROOT / "scripts/build_word_resumes.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ParserTests(unittest.TestCase):
    def test_full_time_source(self):
        resume = MODULE.parse_resume(ROOT / "latex/resume_full_time.tex")
        self.assertEqual(resume.name, "Your Name")
        self.assertEqual(len(resume.education), 2)
        self.assertEqual(len(resume.experience), 1)
        self.assertEqual(len(resume.projects), 2)
        self.assertEqual(len(resume.skills), 3)
        self.assertIn("full-time", resume.objective)

    def test_balanced_bold_argument(self):
        source = r"\resumeItem{Reduced latency by \textbf{38\%}.}"
        parsed = MODULE.command_args(source, "resumeItem", 1)
        self.assertEqual(parsed[0][0][0], r"Reduced latency by \textbf{38\%}.")

    def test_inline_segments_keep_spaces(self):
        self.assertEqual(MODULE.decode_segment("before "), "before ")
        self.assertEqual(MODULE.decode_segment(" after"), " after")


if __name__ == "__main__":
    unittest.main()
