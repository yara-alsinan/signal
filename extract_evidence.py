"""Save one known management passage as a reproducible evidence example.

This is a deliberately narrow extraction exercise, not general search or an AI agent.
Offsets refer to the saved normalized text, not page numbers in the original filing.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/nvidia-latest-10q.txt"
OUTPUT = Path(__file__).resolve().parent / "evidence/nvidia-cash-flow.json"
SOURCE_URL = (
    "https://www.sec.gov/Archives/edgar/data/1045810/"
    "000104581026000075/nvda-20260726.htm"
)
PASSAGE_START = "Cash provided by operating activities increased in the first half"


def main():
    raw = SOURCE.read_bytes()
    text = raw.decode("utf-8")
    if text.count(PASSAGE_START) != 1:
        raise ValueError("Expected exactly one matching management passage; review the source.")
    start = text.index(PASSAGE_START)
    end = text.index(". ", start) + 1
    passage = text[start:end]
    if "accounts receivable" not in passage or "payment terms" not in passage:
        raise ValueError("The extracted passage needs review.")

    record = {
        "evidence_type": "management_explanation",
        "company": "NVIDIA",
        "accession": "0001045810-26-000075",
        "filing_date": "2026-08-26",
        "source_url": SOURCE_URL,
        "source_file": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "section": "Management's Discussion and Analysis / Liquidity and Capital Resources",
        "quote": passage,
        "locator": {"kind": "normalized_text_character_offsets", "start": start, "end": end},
        "plain_language_paraphrase": (
            "Management attributes the increase in operating cash flow to higher revenue, "
            "partly offset by more customer payments remaining outstanding because certain "
            "customers received longer payment terms."
        ),
        "limitation": (
            "This is management's explanation of the cash-flow increase. This passage alone "
            "does not quantify each driver's contribution or fully explain the difference "
            "between revenue growth and operating cash-flow growth."
        ),
        "method": "Known-passage extraction; paraphrase written during the guided exercise, not AI-generated at runtime.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")
    print("MANAGEMENT EXPLANATION (not independently established causation)\n")
    print(passage)
    print("\nPlain language:", record["plain_language_paraphrase"])
    print("\nLimit:", record["limitation"])
    print("\nSource:", SOURCE_URL)
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
