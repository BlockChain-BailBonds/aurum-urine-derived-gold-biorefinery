import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from aurum_biorefinery import ScenarioError, evaluate
from aurum_biorefinery.serialization import dumps_result, load_scenario, result_document

ROOT = Path(__file__).resolve().parents[1]


class SerializationTests(unittest.TestCase):
    def test_reference_file_loads_and_serializes_stably(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "reference_scenario.json")
        result = evaluate(scenario)
        document = result_document(result)
        self.assertEqual(document["schema_version"], "aurum.result.v1")
        self.assertEqual(document["annual_refined_gold_g"], "8.4414765600000")
        self.assertIsInstance(document["first_use_balance"]["gold_in_feed_mg"], str)
        compact = dumps_result(result)
        pretty = dumps_result(result, pretty=True)
        self.assertEqual(json.loads(compact), json.loads(pretty))
        self.assertNotIn("NaN", compact)

    def test_invalid_json_reports_a_scenario_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.json"
            source.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "invalid JSON"):
                load_scenario(source)

    def test_missing_file_reports_a_scenario_error(self) -> None:
        with self.assertRaisesRegex(ScenarioError, "unable to read"):
            load_scenario(ROOT / "examples" / "does-not-exist.json")

    def test_root_must_be_an_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "list.json"
            source.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "root"):
                load_scenario(source)

    def test_decimals_never_become_binary_floats(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "reference_scenario.json")
        self.assertIsInstance(scenario.feed.gold_concentration_mg_l, Decimal)

    def test_result_document_rejects_nonresult_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "did not serialize"):
            result_document("not a campaign result")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
