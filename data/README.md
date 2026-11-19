# Public snapshot provenance

Packaged for the November 19, 2026 midpoint submission. No credentials or personal research inputs are included.

| File | Source and use |
| --- | --- |
| `nvidia-companyfacts.json` | Saved response from https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json. The code selects only accession `0001045810-26-000075`, the specified six-month dates and the appropriate unit. |
| `nvidia-latest-10q.txt` | Normalized text saved from https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm. This is a historical snapshot despite the legacy filename. |

The evidence JSON stores a SHA-256 hash of the exact text bytes and character offsets into that normalized text. Those offsets are not PDF pages or locations in the original HTML. Hash/locator checks detect a changed local snapshot; they do not independently establish the truth of management's statements.

Online company facts may update after this snapshot. Replacing the files requires reviewing selected periods, accession, amendments and evidence locators rather than silently assuming compatibility.
