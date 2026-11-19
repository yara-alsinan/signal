"""Read-only tools for the first fixed NVIDIA research example."""

import hashlib
import json

from compare_nvidia import ACCESSION, DATA_FILE, METRICS, PERIODS, growth_percent, select_fact
from extract_evidence import OUTPUT as EVIDENCE_FILE, SOURCE, SOURCE_URL
from learning_notes import REVENUE_VS_CASH_FLOW


def get_financial_comparison():
    data = json.loads(DATA_FILE.read_text())
    if int(data["cik"]) != 1045810:
        raise ValueError("Unexpected company in snapshot.")
    metrics = {}
    for label, tag in METRICS.items():
        pair = {
            period: select_fact(data, tag, *dates)["val"]
            for period, dates in PERIODS.items()
        }
        metrics[label] = dict(pair, unit="USD", growth_percent=growth_percent(pair["prior"], pair["current"]))
    for label, tag, unit in (
        ("Diluted EPS", "EarningsPerShareDiluted", "USD/shares"),
        ("Diluted weighted-average shares", "WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
    ):
        pair = {period: select_fact(data, tag, *dates, unit=unit)["val"] for period, dates in PERIODS.items()}
        metrics[label] = dict(pair, unit=unit, growth_percent=growth_percent(pair["prior"], pair["current"]),
                             absolute_change=pair["current"] - pair["prior"])
        if unit == "shares":
            metrics[label]["change_in_millions_of_shares"] = (pair["current"] - pair["prior"]) / 1e6
    margins = {
        period: metrics["Operating income"][period] / metrics["Revenue"][period] * 100
        for period in PERIODS
    }
    return {
        "source_id": "F1", "source_url": SOURCE_URL, "accession": ACCESSION,
        "scope": "Fixed historical filing dated 2026-08-26; not a live refresh.",
        "periods": PERIODS, "metrics": metrics,
        "revenue_minus_cash_flow_growth_percentage_points": (
            metrics["Revenue"]["growth_percent"] - metrics["Operating cash flow"]["growth_percent"]
        ),
        "operating_margin_percent": margins,
        "operating_margin_change_percentage_points": margins["current"] - margins["prior"],
        "display_values": {
            "revenue_growth": "%.1f%%" % metrics["Revenue"]["growth_percent"],
            "operating_cash_flow_growth": "%.1f%%" % metrics["Operating cash flow"]["growth_percent"],
            "diluted_share_count_change": "%+.0f million shares" % metrics["Diluted weighted-average shares"]["change_in_millions_of_shares"],
        },
        "learning_note": REVENUE_VS_CASH_FLOW,
        "limitation": "Figures show changes, not their causes. EPS uses reported rounded values."
    }


def get_cash_flow_evidence():
    record = json.loads(EVIDENCE_FILE.read_text())
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["source_sha256"]:
        raise ValueError("Evidence snapshot changed; review the passage again.")
    locator = record["locator"]
    if raw.decode("utf-8")[locator["start"]:locator["end"]] != record["quote"]:
        raise ValueError("Evidence passage does not match its saved location.")
    return {
        "source_id": "E1", "source_url": record["source_url"],
        "section": record["section"], "quote": record["quote"],
        "evidence_type": "management_explanation", "limitation": record["limitation"],
        "retrieval_method": "One curated, previously identified passage; not full-document search."
    }


FUNCTIONS = {
    "get_financial_comparison": get_financial_comparison,
    "get_cash_flow_evidence": get_cash_flow_evidence,
}
TOOLS = [
    {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    }}
    for name, description in (
        ("get_financial_comparison", "Get verified six-month NVIDIA financial figures, EPS, margins, and calculated changes for 2025 versus 2026. Source F1."),
        ("get_cash_flow_evidence", "Get a curated management explanation of the six-month cash-flow increase and its limits. Source E1; not a full-document search."),
    )
]


def execute_tool(name, arguments):
    if name not in FUNCTIONS:
        return {"error": "Unsupported tool. Only the listed research tools are permitted."}
    try:
        if json.loads(arguments) != {}:
            return {"error": "This fixed-snapshot tool accepts an empty object only."}
        return FUNCTIONS[name]()
    except (ValueError, KeyError, OSError, TypeError):
        return {"error": "The local source could not be validated. Do not invent an answer."}
