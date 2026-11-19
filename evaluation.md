# Signal evaluation set v1

Defined before adding or tuning an AI model. Fixed historical source, not current market analysis.
These reference answers were checked against the saved SEC figures and relevant filing text
during the guided development session. User review remains pending. No model has been scored.

## Fixed source

- Company: NVIDIA, CIK 1045810
- Filing: 10-Q, accession 0001045810-26-000075, filed August 26, 2026
- Current period: January 26–July 26, 2026
- Prior period: January 27–July 27, 2025
- Both periods: 182 days
- [Original filing](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm)
- Figures: Condensed Consolidated Statements of Income (printed page 3) and
  Condensed Consolidated Statements of Cash Flows (printed page 8).
- Explanation: Management's Discussion and Analysis, Liquidity and Capital Resources.

## Questions and reference behavior

| ID | Question | Reference answer or required behavior |
|---|---|---|
| Q01 | How did six-month revenue change year over year? | $90.805B to $177.837B; growth 95.8%. |
| Q02 | How did six-month operating cash flow change? | $42.779B to $74.421B; growth 74.0%. |
| Q03 | Did cash-flow growth keep pace with revenue growth? | No. Both increased; revenue growth exceeded cash-flow growth by 21.9 percentage points using unrounded calculations. |
| Q04 | How did six-month operating income change? | $50.078B to $117.270B; calculate growth from these values. |
| Q05 | Did operating margin improve? | 55.1489% to 65.9424%; increase 10.7935 percentage points. Distinguish margin from income growth. |
| Q06 | How did reported GAAP diluted EPS change? | $1.84 to $4.85; growth 163.6%. Select six-month diluted EPS, not quarterly or basic EPS. |
| Q07 | Did EPS grow faster than net income? | Yes: approximately 163.6% versus 161.1%. Net income $45.197B to $118.010B. |
| Q08 | What happened to the diluted share count alongside EPS? | Weighted-average diluted shares fell from 24.571B to 24.338B. Explain the denominator effect and reported EPS rounding; do not infer the reason for the decline without evidence. |
| Q09 | What explanation does management give for the operating cash-flow increase? | Attribute to management: higher revenue, partially offset by increased receivables associated with extended payment terms. Cite the stored passage. |
| Q10 | Exactly how much of the growth-rate gap did longer payment terms cause? | The identified passage does not quantify this contribution or establish a complete causal explanation. Do not invent an amount. |
| Q11 | Can we compare $96.221B revenue with $74.421B cash flow for the same period? | Reject that pairing: the revenue value covers three months, cash flow six months. Use $177.837B revenue for the six-month comparison. |
| Q12 | The filing reports revenue of 177,837 while the API says 177,837,000,000. Is one wrong? | No. The filing table uses millions of USD; the API observation is in USD. Normalize before comparing. |

## Scoring

Score each applicable dimension separately, never hide one behind an overall pass:

- Numeric correctness: correct figure, formula, unit, and rounding (0/1).
- Period/source selection: correct date range, metric definition, and filing version (0/1).
- Evidence support: cited source exists and supports the particular claim (0/1).
- Interpretation: attributes management statements and admits missing evidence (0/1).

Use N/A when a dimension does not apply. Growth tolerance: 0.1 percentage point;
reported EPS tolerance: $0.005; dollar figures must match the source's precision.
This set is development evidence, not an untouched held-out test set.

## Separate system tests, still to implement

- Reprocess the same filing: no duplicate research record.
- Add a clearly labeled synthetic amendment: preserve the original, version the revised
  figure and recalculate. Do not claim NVIDIA filed a real amendment without verification.
- Split-adjustment check before comparing EPS across a split; not yet validated generally.
- Compare time to a checked answer with the same source material, including verification time.

## Later expansion

Four-quarter revenue trends and acceleration require additional filings and period checks.
They are deferred from this first fixed comparison, not assumed to work.
