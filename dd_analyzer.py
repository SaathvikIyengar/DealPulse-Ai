"""
dd_analyzer.py
AI & NLP Private Equity Due Diligence Scanner and Investment Committee (IC) Memo Generator.
Supports live Gemini LLM synthesis (via google-genai) with a deterministic NLP fallback
for zero-dependency live demos.
"""

from typing import Dict, List, Optional
import os


RISK_TAXONOMY = {
    "Customer Concentration": {
        "keywords": ["top 3", "concentration", "single customer", "renews", "churn", "client loss"],
        "severity": "High",
        "weight": 18,
        "mitigant": "Structure earn-out tied to top-account contract renewal prior to close.",
    },
    "Margin & Cost Inflation": {
        "keywords": ["wage inflation", "compute expenses", "margin compression", "fuel", "cost grew", "reimbursement"],
        "severity": "Medium",
        "weight": 12,
        "mitigant": "Implement automated pricing escalators and vendor procurement consolidation in First 100 Days.",
    },
    "CapEx & Working Capital Drag": {
        "keywords": ["aging", "capex", "fleet", "integration delays", "infrastructure", "maintenance"],
        "severity": "Medium",
        "weight": 14,
        "mitigant": "Deduct deferred maintenance CapEx dollar-for-dollar from Purchase Enterprise Value.",
    },
    "Debt & Covenant Tightness": {
        "keywords": ["covenant", "leverage", "refinancing", "floating rate", "interest coverage"],
        "severity": "High",
        "weight": 16,
        "mitigant": "Cap senior leverage at 4.0x EBITDA and hedge 70% of floating interest rate exposure.",
    },
}

STRENGTH_SIGNALS = [
    ("Recurring / Contracted Revenue", ["retention", "take-or-pay", "multi-year", "arr", "recurring"]),
    ("Pricing Power & Escalators", ["escalators", "pass-through", "gross margins remain strong"]),
    ("Scalable M&A Platform", ["bolt-on", "tuck-in", "organic", "volume growth", "mission-critical"]),
]


def analyze_due_diligence(text: str) -> Dict:
    """
    Scans data-room commentary for PE red flags and positive thesis drivers.
    Returns structured risk metrics and recommended valuation multiple adjustment.
    """
    lower_text = text.lower()
    detected_risks: List[Dict] = []
    total_risk_score = 15  # Baseline operational risk

    for category, rule in RISK_TAXONOMY.items():
        matched = [kw for kw in rule["keywords"] if kw in lower_text]
        if matched:
            total_risk_score += rule["weight"]
            detected_risks.append({
                "Risk Pillar": category,
                "Severity": rule["severity"],
                "Triggered Signals": ", ".join(matched),
                "Recommended Deal Mitigant": rule["mitigant"],
            })

    detected_strengths: List[str] = []
    for label, keywords in STRENGTH_SIGNALS:
        if any(kw in lower_text for kw in keywords):
            detected_strengths.append(label)
            total_risk_score = max(10, total_risk_score - 4)

    total_risk_score = min(95, total_risk_score)

    # Recommend entry multiple haircut based on diligence risk score
    if total_risk_score >= 55:
        multiple_haircut = -0.75
        risk_tier = "Elevated Diligence Risk"
    elif total_risk_score >= 35:
        multiple_haircut = -0.35
        risk_tier = "Moderate / Manageable Risk"
    else:
        multiple_haircut = 0.0
        risk_tier = "Clean Diligence Profile"

    return {
        "risk_score": total_risk_score,
        "risk_tier": risk_tier,
        "recommended_multiple_adjustment": multiple_haircut,
        "risks": detected_risks,
        "strengths": detected_strengths,
    }


def generate_ic_memo(
    company_name: str,
    sector: str,
    lbo_results: Dict,
    dd_results: Dict,
    raw_notes: str,
    api_key: Optional[str] = None,
) -> str:
    """
    Generates an executive Private Equity Investment Committee (IC) Memo.
    Uses Gemini 2.5 Flash if an API key is supplied; otherwise builds a crisp
    structured memo using the quantitative & NLP outputs.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")

    if key:
        try:
            from google import genai

            client = genai.Client(api_key=key)
            prompt = f"""
            You are a Principal at a middle-market Private Equity fund writing a concise,
            executive Investment Committee (IC) Memo for {company_name} ({sector}).

            Quantitative LBO Outputs:
            - Entry EV: ${lbo_results['entry_ev']}M | Sponsor Equity: ${lbo_results['sponsor_equity']}M
            - Projected 5-Year IRR: {lbo_results['irr_pct']}% | MOIC: {lbo_results['moic']}x
            - Verdict: {lbo_results['verdict']}
            - Diligence Risk Score: {dd_results['risk_score']}/100 ({dd_results['risk_tier']})

            Data Room Notes:
            {raw_notes}

            Format the memo cleanly in Markdown with:
            1. Executive Recommendation
            2. Investment Thesis & Value Creation Drivers
            3. Key Diligence Risks & Deal Structure Mitigants
            4. First 100-Day Operational Playbook
            Keep it sharp, quantitative, and under 350 words.
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception:
            pass  # Gracefully fall back to deterministic memo generator

    # Deterministic Institutional IC Memo Fallback
    strengths_md = (
        "\n".join([f"- **{s}:** Provides cash flow visibility to support LBO debt service." for s in dd_results["strengths"]])
        if dd_results["strengths"]
        else "- **Operational Turnaround Opportunity:** Margin expansion through cost discipline."
    )

    risks_md = (
        "\n".join([
            f"- **{r['Risk Pillar']} ({r['Severity']}):** Triggered by *{r['Triggered Signals']}*. *Mitigant:* {r['Recommended Deal Mitigant']}"
            for r in dd_results["risks"]
        ])
        if dd_results["risks"]
        else "- No severe structural red flags identified in preliminary data room disclosures."
    )

    adj = dd_results["recommended_multiple_adjustment"]
    pricing_note = (
        f"Recommend bidding **{abs(adj):.2f}x EBITDA below** headline ask to offset diligence findings."
        if adj < 0
        else "Headline entry valuation is supported by clean recurring cash flow metrics."
    )

    return f"""# INVESTMENT COMMITTEE MEMORANDUM: {company_name.upper()}
**Sector:** {sector} | **Recommendation:** {lbo_results['verdict']}

### 1. Transaction & Return Summary
- **Entry Enterprise Value:** ${lbo_results['entry_ev']}M (Initial Debt: ${lbo_results['initial_debt']}M | Sponsor Equity: ${lbo_results['sponsor_equity']}M)
- **Projected 5-Year Exit:** ${lbo_results['exit_ev']}M EV | **Net IRR: {lbo_results['irr_pct']}%** | **MOIC: {lbo_results['moic']}x**
- **Diligence Risk Rating:** {dd_results['risk_score']}/100 (*{dd_results['risk_tier']}*) — {pricing_note}

### 2. Core Investment Thesis
{strengths_md}
- **Value Creation Attribution:** Driven by **${lbo_results['attribution']['EBITDA Growth ($M)']}M** in organic EBITDA expansion and **${lbo_results['attribution']['Debt De-leveraging ($M)']}M** in cumulative debt paydown.

### 3. Key Diligence Risks & Deal Mitigants
{risks_md}

### 4. First 100-Day Value Creation Plan
1. **Commercial & Pricing Audit:** Enforce annual CPI price escalators and lock in multi-year renewals for top accounts.
2. **Working Capital & Cash Conversion:** Tighten DSO collection cycles to maximize Year 1–2 mandatory and cash-sweep debt paydown.
3. **AI & Process Automation:** Deploy automated workflow tooling across back-office operations to accelerate EBITDA margin expansion.
"""
