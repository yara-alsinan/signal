"""Signal's local web interface. Credentials load only on Research clicks."""

import streamlit as st

from agent import run_research, DEFAULT_QUESTION
from parley_client import ParleyClient, ParleyError
from research_tools import get_financial_comparison
from fact_display import comparison_rows

st.set_page_config(page_title="Signal | Company research", page_icon="◈", layout="wide")
st.markdown("""<style>
.stApp {background:#f5f7fb;color:#17253c;}
.block-container {max-width:1160px;padding-top:2.5rem;}
[data-testid="stMetric"] {background:white;border:1px solid #e2e8f0;border-radius:16px;padding:20px;}
[data-testid="stMetricLabel"] {color:#52617a;}
.eyebrow {color:#26756c;font-size:12px;font-weight:700;letter-spacing:2px;}
.hero {font-size:46px;font-weight:750;letter-spacing:-2px;margin-bottom:0;}
.subtitle {color:#52617a;font-size:18px;margin-bottom:28px;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ Signal")
    st.caption("The agentic research arm of Stock Sense")
    st.divider()
    st.markdown("**Company**\n\nNVIDIA · NVDA")
    st.markdown("**Coverage**\n\nSix months ended July 26, 2026 versus July 27, 2025")
    st.caption("Historical snapshot · filed August 26, 2026. No live refresh yet.")
    st.divider()
    st.markdown("**How research works**\n\n1. Choose a question\n2. The agent selects tools\n3. Inspect the answer and evidence")
    st.caption("AI: Claude Haiku 4.5 via MIT Parley. Each Research click uses API credits. No requests occur just from opening this page.")

st.markdown('<div class="eyebrow">COMPANY RESEARCH, WITH EVIDENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Follow the changes.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Understand what changed at NVIDIA—and inspect the evidence behind it.</div>', unsafe_allow_html=True)

try:
    figures = get_financial_comparison()
except (ValueError, KeyError, OSError, TypeError):
    st.error("The local financial snapshot could not be validated. Check the project data files.")
    st.stop()

metrics = figures["metrics"]
cols = st.columns(3)
cols[0].metric("Revenue · six months", "$%.1fB" % (metrics["Revenue"]["current"] / 1e9),
               "%.1f%% year over year" % metrics["Revenue"]["growth_percent"], delta_color="off")
cols[1].metric("Operating cash flow · six months", "$%.1fB" % (metrics["Operating cash flow"]["current"] / 1e9),
               "%.1f%% year over year" % metrics["Operating cash flow"]["growth_percent"], delta_color="off")
cols[2].metric("Operating margin", "%.1f%%" % figures["operating_margin_percent"]["current"],
               "%+.1f percentage points" % figures["operating_margin_change_percentage_points"], delta_color="off")
st.caption("Calculated in Python from the saved SEC company-facts snapshot. Percentage changes use unrounded figures.")

st.markdown("### What would you like to investigate?")
questions = {
    "Cash flow versus revenue": DEFAULT_QUESTION,
    "Operating profitability": "Did operating profitability improve? Compare operating income growth and operating margins for the supported six-month periods. State what the evidence cannot explain.",
    "Earnings per share": "How did diluted GAAP earnings per share change? Compare EPS growth, net income growth and weighted-average diluted shares for the supported six-month periods. Note rounded EPS and limits on causal attribution.",
}
with st.form("research"):
    selected = st.selectbox("Research focus", list(questions))
    st.write(questions[selected])
    submitted = st.form_submit_button("Research NVIDIA", type="primary")

if submitted:
    st.session_state.pop("research_result", None)
    st.session_state.pop("research_question", None)
    with st.status("Researching the filing…", expanded=True) as status:
        try:
            labels = {"get_financial_comparison": "Checking financial figures and calculated changes",
                      "get_cash_flow_evidence": "Retrieving the curated management passage"}
            result = run_research(questions[selected], ParleyClient(),
                                  lambda name: st.write(labels.get(name, "Unsupported tool requested")))
        except (ParleyError, ValueError, OSError):
            status.update(label="Research could not be completed", state="error")
            st.error("Check local Parley access and retry when ready. No automatic retry was made; incomplete requests may still use credits. Credentials and raw errors are hidden.")
        else:
            st.session_state["research_result"] = result
            st.session_state["research_question"] = questions[selected]
            status.update(label="Research ready · inspect the evidence below", state="complete", expanded=False)

if "research_result" in st.session_state:
    result = st.session_state["research_result"]
    st.divider()
    st.caption("ANSWER TO: " + st.session_state["research_question"])
    with st.container(border=True):
        st.subheader("Python-calculated facts")
        st.caption("These values are formatted directly from the financial tool's output, independently of the AI explanation.")
        financial_source = result["sources"].get("F1")
        if financial_source:
            st.table(comparison_rows(financial_source), alt="NVIDIA six-month financial comparison calculated in Python")
            shares = financial_source["metrics"]["Diluted weighted-average shares"]
            # Older session results contain the original values but not newer derived fields.
            share_change_millions = (shares["current"] - shares["prior"]) / 1e6
            st.caption("Weighted-average diluted share change: %+.0f million shares. EPS growth uses reported rounded EPS." % share_change_millions)
            st.markdown("[F1 · Open the SEC filing](%s)" % financial_source["source_url"])
        else:
            st.info("The agent did not retrieve the financial tool for this answer.")
    st.subheader("AI interpretation and evidence limits")
    st.caption("Generated by Claude from the retrieved tool results. Interpretations may contain unsupported claims; check the evidence below.")
    st.markdown(result["answer"])
    st.markdown("### Inspect the sources")
    for source_id, source in result["sources"].items():
        with st.expander("[%s] %s" % (source_id, "Financial figures and calculations" if source_id == "F1" else "Management explanation")):
            st.markdown("[Open SEC filing](%s)" % source["source_url"])
            if source.get("quote"):
                st.write(source["quote"])
                st.caption(source["retrieval_method"])
            else:
                st.json({"periods": source["periods"], "metrics": source["metrics"],
                         "operating_margin_percent": source["operating_margin_percent"]})
            st.caption(source["limitation"])
    st.caption("%d model requests · %d tokens reported · Source IDs checked; claim accuracy still requires review." % (result["model_requests"], result["total_tokens"]))

with st.expander("Understand the measures and current coverage"):
    st.write(figures["learning_note"])
    st.write("This prototype covers one company and two six-month periods. The evidence tool retrieves one curated cash-flow passage; it does not search the entire filing. No stock prices, live updates, or buy/sell recommendations are included. Results remain in this browser session; persistent research history is a later step.")
    st.markdown("[Financial source: NVIDIA SEC filing](%s)" % figures["source_url"])
