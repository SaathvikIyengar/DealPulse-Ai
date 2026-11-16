# DealPulse AI — Middle-Market Private Equity LBO & AI Diligence Terminal

An end-to-end Python & AI financial modeling platform designed to automate **Leveraged Buyout (LBO) underwriting**, **debt-waterfall sensitivity analysis**, and **commercial due diligence red-flag detection** for middle-market Private Equity teams.

## Why I Built This
Middle-market Private Equity analysts spend dozens of hours manually building LBO debt schedules in spreadsheets and scanning data-room documents for hidden contract or margin risks. **DealPulse AI** bridges quantitative corporate finance with NLP/LLM risk analysis—allowing an investment team to stress-test capital structures and generate a risk-adjusted Investment Committee (IC) Memo in seconds.

## Key Capabilities
1. **5-Year Dynamic LBO Engine (`lbo_engine.py`):**
   - Models Sources & Uses, revenue/margin progression, free cash flow conversion, mandatory debt amortization, and excess cash-flow sweeps.
   - Computes **Net IRR**, **MOIC**, net leverage ratios, and an **Equity Value Creation Bridge** (separating EBITDA growth, multiple expansion, and debt paydown).
2. **2D Multiple Sensitivity Heatmap:**
   - Dynamically evaluates IRR across a 5×5 Entry vs. Exit EV/EBITDA matrix against a 20% institutional PE hurdle rate.
3. **AI & NLP Due Diligence Red-Flag Scanner (`dd_analyzer.py`):**
   - Extracts risk signals across *Customer Concentration*, *Margin Inflation*, *CapEx Drag*, and *Debt Covenants* from data-room text.
   - Calculates a quantitative **Diligence Risk Score (0–100)**, recommends a risk-adjusted EV/EBITDA bid haircut, and synthesizes a downloadable **Investment Committee Memo** (powered by Gemini 2.5 Flash or a deterministic local NLP engine).

## Quickstart
```bash
git clone [https://github.com/](https://github.com/)<your-username>/DealPulse-AI.git
cd DealPulse-AI
pip install -r requirements.txt
streamlit run app.py
