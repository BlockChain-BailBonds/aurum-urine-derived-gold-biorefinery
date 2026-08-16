import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from aurum_biorefinery.cli import main

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "examples" / "reference_scenario.json"


class CliTests(unittest.TestCase):
    def test_validate(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["validate", str(SCENARIO)])
        self.assertEqual(code, 0)
        self.assertIn("valid:", output.getvalue())

    def test_run_to_stdout(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["run", str(SCENARIO), "--pretty"])
        self.assertEqual(code, 0)
        document = json.loads(output.getvalue())
        self.assertEqual(document["schema_version"], "aurum.result.v1")

    def test_run_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "result.json"
            code = main(["run", str(SCENARIO), "--output", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(target.read_text())["evidence_status"], "hypothesis")

    def test_sensitivity_output(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "sensitivity",
                    str(SCENARIO),
                    "--concentration-mg-l",
                    "0.01",
                    "0.1",
                    "--affinity",
                    "0.5",
                    "0.9",
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(output.getvalue())["results"]), 4)

    def test_invalid_scenario_returns_two(self) -> None:
        error = StringIO()
        with redirect_stderr(error):
            code = main(["validate", str(ROOT / "missing.json")])
        self.assertEqual(code, 2)
        self.assertIn("error:", error.getvalue())


if __name__ == "__main__":
    unittest.main()
