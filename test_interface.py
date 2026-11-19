"""Interface smoke checks with credential loading explicitly blocked."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from research_tools import get_financial_comparison


class InterfaceTests(unittest.TestCase):
    def test_saved_answer_from_before_derived_fields_still_displays(self):
        source = get_financial_comparison()
        shares = source["metrics"]["Diluted weighted-average shares"]
        shares.pop("change_in_millions_of_shares")
        shares.pop("absolute_change")
        with patch("parley_client.load_local_key", side_effect=AssertionError("Credential access forbidden")) as key:
            app = AppTest.from_file(str(Path(__file__).with_name("app.py")))
            app.session_state["research_result"] = {
                "answer": "Saved answer [F1]", "sources": {"F1": source},
                "model_requests": 2, "total_tokens": 100}
            app.session_state["research_question"] = "Earlier EPS question"
            app.run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("-233 million shares" in item.value for item in app.caption))
            key.assert_not_called()

    def test_opening_and_selecting_do_not_load_key(self):
        with patch("parley_client.load_local_key", side_effect=AssertionError("Credential access forbidden")) as key:
            app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.metric), 3)
            self.assertEqual(app.metric[0].value, "$177.8B")
            app.selectbox[0].select("Earnings per share").run()
            self.assertEqual(len(app.exception), 0)
            key.assert_not_called()

    def test_research_displays_mock_answer_and_sources(self):
        result = {"answer": "Revenue grew 95.8% [F1].", "sources": {
            "F1": get_financial_comparison()},
            "model_requests": 2, "total_tokens": 100}
        with patch("parley_client.load_local_key", side_effect=AssertionError("Credential access forbidden")) as key, \
                patch("parley_client.ParleyClient.__init__", return_value=None), \
                patch("agent.run_research", return_value=result):
            app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run(timeout=20)
            app.button[0].click().run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("Revenue grew 95.8%" in item.value for item in app.markdown))
            self.assertEqual(len(app.table), 1)
            table = app.table[0].value
            self.assertEqual(table.loc[table["Measure"] == "Diluted weighted-average shares", "Change"].iloc[0], "-0.9%")
            self.assertTrue(any("-233 million shares" in item.value for item in app.caption))
            self.assertTrue(any(item.value == "AI interpretation and evidence limits" for item in app.subheader))
            key.assert_not_called()


if __name__ == "__main__":
    unittest.main()
