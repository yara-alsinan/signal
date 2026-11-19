# Signal

**The agentic research arm of Stock Sense.**

Signal helps individuals identify financial changes worth investigating and inspect the evidence behind them. This midpoint prototype researches NVIDIA using a saved SEC filing, Python calculations, and Claude Haiku 4.5 through MIT Parley.

Built by Yara Alsinan for MIT 1.125. Midpoint version: November 19, 2026.

## What works now

- Streamlit interface with financial summary cards and three research questions: cash flow versus revenue, operating profitability, and diluted EPS.
- Exact filing, period, company and unit selection from saved SEC company facts.
- Python-calculated revenue, operating cash flow, operating income, net income, operating margin, EPS and diluted-share changes.
- A bounded AI tool loop: the model selects read-only financial and evidence tools, then produces a cited explanation.
- A separate facts table, AI interpretation, and expandable source evidence.
- Validation of the saved evidence passage against its source hash and character location.

The initial live run used both tools successfully through Parley. Subsequent live review found a share-unit error and unsupported explanations; Python now supplies exact share differences, and the interface separates computed facts from AI interpretation. See [live-review.md](live-review.md).

## Install and run

Requires Python 3.11 or newer. From this repository's folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. The dashboard and calculations work without an AI key. No model request occurs when opening the page.

### Enable AI research

AI research requires an MIT Parley account with access to `claude-haiku-4-5` and available credits. This is not a universally free API.

Copy `.env.example` to `.env.local`, then edit that local plain-text file yourself:

```sh
cp .env.example .env.local
chmod 600 .env.local
```

Replace the placeholder with your own Parley key. Never commit, share or screenshot that file. It is excluded by `.gitignore`. Signal sends the key only in the authorization header to `https://parley.api.mit.edu/v1/chat/completions`; redirects are disabled. It is not placed in model prompts.

Click **Research NVIDIA** to make a live request. Each click can use credits: at most four model requests and six tool calls. Requests are not automatically retried. Results remain in the Streamlit session; no database is implemented yet.

To try the same research flow in Terminal:

```sh
python agent.py
```

## How it works

```text
Streamlit question → agent loop → Claude via MIT Parley
                          ↕ model-selected read-only tools
                  Python calculations / curated evidence
                          ↓
         Python facts + AI explanation + source inspection
```

| File | Role |
| --- | --- |
| `app.py` | Interface and session-only answer display |
| `agent.py` | Tool-calling loop, request limits and source-ID checks |
| `research_tools.py` | Financial comparison and validated evidence tools |
| `compare_nvidia.py` | Select facts by accession, dates and units; calculate changes |
| `fact_display.py` | Format financial-tool output independently of AI prose |
| `parley_client.py` | Fixed MIT endpoint and safe error handling |
| `extract_evidence.py` | Reproduce the known cash-flow passage extraction |
| `data/` | Public historical input snapshots |
| `evidence/` | Curated passage with provenance and validation metadata |

This uses an existing language model; no custom LLM is trained. The model chooses between two narrow tools. It does not autonomously browse the web or search the entire filing.

## Data and scope

The fixed historical NVIDIA 10-Q was filed August 26, 2026, accession `0001045810-26-000075`. Comparisons cover the six months ended July 27, 2025 and July 26, 2026. These are historical inputs, not a claim to use the latest filing.

- [SEC company-facts API](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json): financial facts; the online endpoint can change while the bundled snapshot stays fixed.
- [Original NVIDIA filing](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm): financial statements and management discussion.
- `data/nvidia-latest-10q.txt`: normalized saved filing text. The legacy filename means the report selected during initial exploration, not the latest available report.

API figures are in dollars, shares or dollars per share as indicated. The filing's financial statements may display millions; the code does not treat those as identical raw units. EPS growth uses reported rounded EPS. See [data/README.md](data/README.md) for provenance.

## Checks and evaluation

```sh
python -m unittest discover -s . -p 'test_*.py' -v
python compare_nvidia.py
```

Tests use public local inputs and simulated model responses; they do not load credentials or make AI requests. They cover reference figures, tool boundaries, source IDs, truncated answers, request caps and interface behavior, including older saved results. Passing tests does not establish that model interpretations are correct.

[evaluation.md](evaluation.md) contains 12 reference tasks and separate criteria for numerical accuracy, period/source accuracy, evidence support and interpretation. It is a development set, not a completed held-out benchmark. No reliability or time-saving score is claimed yet.

## Limitations and next steps

- One company, one historical filing and two six-month periods.
- One curated cash-flow passage; no relevant management evidence has yet been retrieved for EPS or margin drivers.
- Source-ID checks confirm a source was returned, not that it supports every sentence. AI can still invent explanations or misstate relationships.
- No stock prices, valuation, live refresh, scheduled checks or persistent research database yet.
- No buy/sell recommendations. Signal supports investigation; its usefulness and repeat use remain to be tested.

Before the final submission: broaden relevant evidence retrieval, evaluate the reference tasks, add persistent research history and reliable manual refresh, then polish the interface. Daily scheduling and broader company coverage are later extensions if the core works reliably.

## AI assistance

Developed interactively with Codex assistance for implementation, debugging, documentation and test design. Runtime explanations use Claude through MIT Parley. Yara selected the scope and reviewed live outputs; the repository documents remaining limitations rather than claiming full verification.
