"""
app.py
DealPulse AI — Private Equity LBO Screener & AI Due Diligence Terminal.
Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from lbo_engine import (
    DealAssumptions,
    PRESET_DEALS,
    run_lbo_model,
    generate_irr_sensitivity,
)
from dd_analyzer import analyze_due_diligence, generate_ic_memo


st.set_page_config(
    page_title="DealPulse AI | Private Equity LBO & Diligence Terminal",
    page_icon="📈",
    layout="wide",
)

# Custom styling for crisp institutional metric cards
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        padding: 14px 18px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR: DEAL CONFIGURATION ---
with st.sidebar:
    st.title("DealPulse AI")
    st.caption("Middle-Market LBO & Diligence Screener")
    st.divider()

    deal_choice = st.selectbox(
        "Select Target Company",
        list(PRESET_DEALS.keys()) + ["Custom Deal Target"],
    )

    if deal_choice != "Custom Deal Target":
        preset_assumptions, default_notes = PRESET_DEALS[deal_choice]
        comp_name = preset_assumptions.company_name
        sector = preset_assumptions.sector
        def_rev = preset_assumptions.ltm_revenue
        def_ebitda = preset_assumptions.ltm_ebitda
        def_entry = preset_assumptions.entry_multiple
        def_exit = preset_assumptions.exit_multiple
        def_debt = int(preset_assumptions.debt_pct * 100)
        def_rate = preset_assumptions.interest_rate * 100
        def_growth = preset_assumptions.rev_growth * 100
        def_margin = preset_assumptions.target_ebitda_margin * 100
    else:
        comp_name = st.text_input("Company Name", "NovaTech Industrial")
        sector = st.text_input("Sector", "Specialty Manufacturing")
        def_rev, def_ebitda = 60.0, 12.0
        def_entry, def_exit = 8.0, 8.5
        def_debt, def_rate = 55, 8.5
        def_growth, def_margin = 8.0, 22.0
        default_notes = (
            "Target generates $60M in recurring industrial component sales with strong customer "
            "retention, though aging facility equipment requires $3M in near-term maintenance capex."
        )

    st.subheader("1. Valuation & Capital Structure")
    ltm_rev = st.number_input("LTM Revenue ($M)", min_value=5.0, max_value=2000.0, value=float(def_rev), step=5.0)
    ltm_ebitda = st.number_input("LTM EBITDA ($M)", min_value=1.0, max_value=500.0, value=float(def_ebitda), step=1.0)
    entry_mult = st.slider("Entry Multiple (EV/EBITDA)", 4.0, 18.0, float(def_entry), 0.1)
    exit_mult = st.slider("Exit Multiple (EV/EBITDA)", 4.0, 18.0, float(def_exit), 0.1)
    debt_pct = st.slider("LBO Debt Financing (% of EV)", 20, 80, int(def_debt), 5)
    interest_rate = st.slider("Cost of Debt / Interest Rate (%)", 4.0, 14.0, float(def_rate), 0.25)

    st.subheader("2. Operating Case (5-Year)")
    rev_growth = st.slider("Annual Revenue Growth (%)", 0.0, 30.0, float(def_growth), 0.5)
    target_margin = st.slider("Year 5 Target EBITDA Margin (%)", 5.0, 50.0, float(def_margin), 0.5)

    st.divider()
    api_key_input = st.text_input(
        "Gemini API Key (Optional)",
        type="password",
        help="Leave blank to run the built-in NLP Diligence & Memo Engine offline.",
    )

# --- RUN MODEL ---
assumptions = DealAssumptions(
    company_name=comp_name,
    sector=sector,
    ltm_revenue=ltm_rev,
    ltm_ebitda=ltm_ebitda,
    entry_multiple=entry_mult,
    exit_multiple=exit_mult,
    debt_pct=debt_pct / 100.0,
    interest_rate=interest_rate / 100.0,
    rev_growth=rev_growth / 100.0,
    target_ebitda_margin=target_margin / 100.0,
)
results = run_lbo_model(assumptions)
schedule_df = results["schedule"]

# --- HEADER & TOP KPI RIBBON ---
st.title(f"DealPulse AI — {comp_name}")
st.caption(f"Sector: **{sector}** | Institutional Hurdle Benchmark: **20.0% IRR / 2.2x MOIC**")

if "STRONG BUY" in results["verdict"]:
    st.success(f"**Investment Committee Signal:** {results['verdict']}")
elif "WATCHLIST" in results["verdict"]:
    st.warning(f"**Investment Committee Signal:** {results['verdict']}")
else:
    st.error(f"**Investment Committee Signal:** {results['verdict']}")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Entry Enterprise Value", f"${results['entry_ev']}M", f"{entry_mult:.1f}x EBITDA")
k2.metric("Sponsor Equity Check", f"${results['sponsor_equity']}M", f"{100 - debt_pct}% Equity")
k3.metric("Year 5 Exit EV", f"${results['exit_ev']}M", f"{exit_mult:.1f}x Exit")
k4.metric(
    "Projected Net IRR",
    f"{results['irr_pct']}%",
    f"{results['irr_pct'] - 20.0:+.1f}% vs. 20% Hurdle",
)
k5.metric(
    "Return Multiple (MOIC)",
    f"{results['moic']}x",
    f"${results['exit_equity']}M Exit Equity",
)

st.divider()

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "📊 LBO Debt Waterfall & Operating Model",
    "🎯 Return Sensitivity & Value Bridge",
    "🧠 AI Due Diligence & IC Memo",
])

with tab1:
    col_chart, col_su = st.columns([2.2, 1])

    with col_chart:
        st.subheader("5-Year Debt Paydown vs. Sponsor Equity Accretion")
        fig_waterfall = go.Figure()
        fig_waterfall.add_trace(
            go.Bar(
                x=schedule_df["Year"],
                y=schedule_df["Ending Debt ($M)"],
                name="Ending Net Debt ($M)",
                marker_color="#EF4444",
            )
        )
        fig_waterfall.add_trace(
            go.Bar(
                x=schedule_df["Year"],
                y=schedule_df["Implied Equity Value ($M)"],
                name="Sponsor Equity Value ($M)",
                marker_color="#10B981",
            )
        )
        fig_waterfall.update_layout(
            barmode="stack",
            template="plotly_dark",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="Enterprise Value Split ($M)",
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col_su:
        st.subheader("Sources & Uses")
        st.dataframe(results["sources_uses"], hide_index=True, use_container_width=True)
        st.info(
            f"**De-leveraging Summary:** Debt drops from **${results['initial_debt']}M** "
            f"at entry to **${results['exit_debt']}M** by Year 5 "
            f"({schedule_df.iloc[-1]['Net Leverage (Debt/EBITDA)']}x Net Debt/EBITDA)."
        )

    st.subheader("Projected 5-Year LBO Operating & Debt Schedule")
    st.dataframe(schedule_df, hide_index=True, use_container_width=True)

with tab2:
    c_sens, c_bridge = st.columns([1.2, 1])

    with c_sens:
        st.subheader("IRR Sensitivity Matrix (Entry vs. Exit Multiple)")
        sens_df = generate_irr_sensitivity(assumptions)
        fig_heat = px.imshow(
            sens_df.values,
            x=sens_df.columns,
            y=sens_df.index,
            text_auto=".1f",
            color_continuous_scale="RdYlGn",
            aspect="auto",
        )
        fig_heat.update_layout(
            template="plotly_dark",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            coloraxis_colorbar_title="IRR (%)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with c_bridge:
        st.subheader("Sponsor Equity Value Creation Bridge")
        attr = results["attribution"]
        fig_bridge = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=[
                    "EBITDA Growth",
                    "Multiple Expansion",
                    "Debt Paydown",
                    "Total Value Created",
                ],
                y=[
                    attr["EBITDA Growth ($M)"],
                    attr["Multiple Expansion ($M)"],
                    attr["Debt De-leveraging ($M)"],
                    sum(attr.values()),
                ],
                connector={"line": {"color": "#6B7280"}},
                increasing={"marker": {"color": "#10B981"}},
                decreasing={"marker": {"color": "#EF4444"}},
                totals={"marker": {"color": "#3B82F6"}},
            )
        )
        fig_bridge.update_layout(
            template="plotly_dark",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis_title="Equity Value Contribution ($M)",
        )
        st.plotly_chart(fig_bridge, use_container_width=True)

with tab3:
    st.subheader("Data Room Disclosure & Red-Flag Scanner")
    dd_notes = st.text_area(
        "Paste Management Commentary, CIM Excerpts, or Contract Risk Notes:",
        value=default_notes,
        height=130,
    )

    dd_res = analyze_due_diligence(dd_notes)

    d1, d2, d3 = st.columns(3)
    d1.metric("Diligence Risk Score", f"{dd_res['risk_score']} / 100", dd_res["risk_tier"])
    d2.metric(
        "Suggested Valuation Haircut",
        f"{dd_res['recommended_multiple_adjustment']:+.2f}x EBITDA",
        "Risk-adjusted entry bid",
    )
    d3.metric(
        "Risk-Adjusted Entry EV",
        f"${round(ltm_ebitda * (entry_mult + dd_res['recommended_multiple_adjustment']), 2)}M",
        "Post-diligence bid price",
    )

    if dd_res["risks"]:
        st.markdown("**Flagged Diligence Risks & Deal Mitigants:**")
        st.dataframe(dd_res["risks"], hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Automated Investment Committee (IC) Memo")
    memo_md = generate_ic_memo(
        company_name=comp_name,
        sector=sector,
        lbo_results=results,
        dd_results=dd_res,
        raw_notes=dd_notes,
        api_key=api_key_input.strip() or None,
    )
    st.markdown(memo_md)
    st.download_button(
        label="📥 Download IC Memo (.md)",
        data=memo_md,
        file_name=f"{comp_name.lower().replace(' ', '_')}_ic_memo.md",
        mime="text/markdown",
    )
