"""Offline checks: no credentials loaded and no network requests made."""

import unittest

from agent import run_research
from parley_client import ParleyError
from research_tools import execute_tool, get_financial_comparison, get_cash_flow_evidence


def completion(content=None, names=(), finish="stop"):
    message = {"content": content}
    if names:
        message["tool_calls"] = [
            {"id": "call_%d" % i, "function": {"name": name, "arguments": "{}"}}
            for i, name in enumerate(names)
        ]
    return {"choices": [{"message": message, "finish_reason": finish}],
            "usage": {"total_tokens": 10}}


class FakeClient:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def complete(self, messages, tools, first=False):
        self.requests.append((list(messages), first))
        return next(self.replies)


class AgentTests(unittest.TestCase):
    def test_reference_figures(self):
        result = get_financial_comparison()
        self.assertEqual(result["metrics"]["Revenue"]["current"], 177837000000)
        self.assertAlmostEqual(result["metrics"]["Revenue"]["growth_percent"], 95.846, places=2)
        self.assertAlmostEqual(result["revenue_minus_cash_flow_growth_percentage_points"], 21.9, places=1)
        self.assertEqual(result["metrics"]["Diluted weighted-average shares"]["absolute_change"], -233000000)
        self.assertEqual(result["display_values"]["diluted_share_count_change"], "-233 million shares")
        self.assertEqual(result["display_values"]["operating_cash_flow_growth"], "74.0%")

    def test_evidence_matches_snapshot(self):
        result = get_cash_flow_evidence()
        self.assertEqual(result["source_id"], "E1")
        self.assertIn("extended payment terms", result["quote"])

    def test_tool_boundaries(self):
        self.assertIn("error", execute_tool("run_shell", "{}"))
        self.assertIn("error", execute_tool("get_financial_comparison", '{"company":"other"}'))
        self.assertIn("error", execute_tool("get_financial_comparison", "invalid json"))

    def test_research_with_both_tools(self):
        client = FakeClient([
            completion(names=("get_financial_comparison", "get_cash_flow_evidence")),
            completion("Revenue grew 95.8% [F1]. Management mentions extended payment terms [E1]."),
        ])
        result = run_research("Compare growth and explain it", client)
        self.assertEqual(set(result["sources"]), {"F1", "E1"})
        self.assertEqual(result["model_requests"], 2)
        self.assertEqual(result["total_tokens"], 20)
        self.assertTrue(all(item["ok"] for item in result["trace"]))
        self.assertTrue(client.requests[0][1])
        self.assertEqual(client.requests[1][0][-1]["role"], "tool")

    def test_unretrieved_citation_rejected(self):
        with self.assertRaises(ParleyError):
            run_research("Explain", FakeClient([completion("A claim [F1].")]))

    def test_request_limit(self):
        client = FakeClient([completion(names=("get_financial_comparison",)) for _ in range(4)])
        with self.assertRaisesRegex(ParleyError, "Four-request limit"):
            run_research("Compare", client)
        self.assertEqual(len(client.requests), 4)

    def test_truncated_answer_rejected(self):
        with self.assertRaises(ParleyError):
            run_research("Compare", FakeClient([completion("Partial [F1]", finish="length")]))


if __name__ == "__main__":
    unittest.main()
