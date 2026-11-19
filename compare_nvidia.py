"""First Signal exercise: compare two six-month periods in one saved SEC filing.

Run from any directory with Python 3. No external packages or AI calls required.
This deliberately uses a fixed historical snapshot, not the latest available data.
"""

import json
from datetime import date
from pathlib import Path

from learning_notes import REVENUE_VS_CASH_FLOW


DATA_FILE = Path(__file__).resolve().parent / "data/nvidia-companyfacts.json"
ACCESSION = "0001045810-26-000075"
PERIODS = {
    "prior": ("2025-01-27", "2025-07-27"),
    "current": ("2026-01-26", "2026-07-26"),
}
METRICS = {
    "Revenue": "Revenues",
    "Operating cash flow": "NetCashProvidedByUsedInOperatingActivities",
    "Operating income": "OperatingIncomeLoss",
    "Net income": "NetIncomeLoss",
}


def select_fact(company_facts, tag, start, end, unit="USD"):
    """Require one observation in the specified unit, filing, and date range."""
    observations = company_facts["facts"]["us-gaap"][tag]["units"][unit]
    matches = [
        row for row in observations
        if row.get("accn") == ACCESSION
        and row.get("start") == start
        and row.get("end") == end
        and row.get("form") == "10-Q"
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {tag} observation for {start} to {end}; got {len(matches)}")
    return matches[0]


def growth_percent(prior, current):
    """The first exercise supports positive prior values only."""
    if prior <= 0:
        raise ValueError("A zero or negative baseline needs a different interpretation.")
    return (current - prior) / prior * 100


def main():
    company_facts = json.loads(DATA_FILE.read_text())
    if int(company_facts["cik"]) != 1045810:
        raise ValueError("The snapshot is not NVIDIA's company data.")

    # Check that both selected periods cover the same number of days.
    durations = [
        (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
        for start, end in PERIODS.values()
    ]
    if durations[0] != durations[1]:
        raise ValueError("The periods have different durations; review before comparing.")

    print("SIGNAL: NVIDIA historical comparison")
    print(f"Fixed filing: {ACCESSION}, filed August 26, 2026")
    print("Prior:   January 27 to July 27, 2025")
    print("Current: January 26 to July 26, 2026")
    print(f"Both periods: {durations[0]} days. Values below are USD billions.\n")

    results = {}
    print(f"{'Metric':<25} {'Prior':>10} {'Current':>10} {'Growth':>10}")
    for label, tag in METRICS.items():
        prior = select_fact(company_facts, tag, *PERIODS["prior"])["val"]
        current = select_fact(company_facts, tag, *PERIODS["current"])["val"]
        growth = growth_percent(prior, current)
        results[label] = {"prior": prior, "current": current, "growth": growth}
        print(f"{label:<25} {prior / 1e9:>10.3f} {current / 1e9:>10.3f} {growth:>9.1f}%")

    revenue = results["Revenue"]
    cash_flow = results["Operating cash flow"]
    gap = revenue["growth"] - cash_flow["growth"]
    print(f"\nRevenue growth exceeded operating cash-flow growth by {gap:.1f} percentage points.")
    print("Both increased, but operating cash flow grew more slowly.")
    print("These calculations do not establish why their growth rates differed.")

    margins = {
        period: results["Operating income"][period] / revenue[period] * 100
        for period in PERIODS
    }
    print(f"\nOperating margin: {margins['prior']:.1f}% -> {margins['current']:.1f}%")
    print(f"Change: {margins['current'] - margins['prior']:.1f} percentage points")

    eps = {
        period: select_fact(company_facts, "EarningsPerShareDiluted", *dates, unit="USD/shares")["val"]
        for period, dates in PERIODS.items()
    }
    shares = {
        period: select_fact(company_facts, "WeightedAverageNumberOfDilutedSharesOutstanding", *dates, unit="shares")["val"]
        for period, dates in PERIODS.items()
    }
    print(f"\nReported GAAP diluted EPS: ${eps['prior']:.2f} -> ${eps['current']:.2f}")
    print(f"EPS growth: {growth_percent(eps['prior'], eps['current']):.1f}%")
    print(f"Net income growth: {results['Net income']['growth']:.1f}%")
    print(f"Weighted-average diluted shares (billions): {shares['prior']/1e9:.3f} -> {shares['current']/1e9:.3f}")
    print("EPS grew slightly faster than net income while the diluted share count declined.")
    print("EPS uses reported rounded values; it does not by itself explain changes in profitability.")
    print("Operating margin = operating income / revenue. Diluted EPS = earnings per share allowing for potential dilution.")
    print(f"\nLearning note: {REVENUE_VS_CASH_FLOW}")
    print("\nSource: https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm")


if __name__ == "__main__":
    main()
