<div align="center">

<!-- Dark-Mode Custom Background & Typography Header Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:090D16,50:111827,100:064E3B&height=230&section=header&text=DealPulse%20AI&fontSize=56&fontColor=10B981&fontAlignY=38&desc=Middle-Market%20Private%20Equity%20LBO%20%26%20AI%20Due%20Diligence%20Terminal&descSize=17&descColor=D1D5DB&descAlignY=62&animation=fadeIn" width="100%" />

<!-- Tech Stack & Domain Badges -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-0F172A?style=for-the-badge&logo=python&logoColor=10B981" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-Interactive%20UI-0F172A?style=for-the-badge&logo=streamlit&logoColor=FF4B4B" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-Financial%20Charts-0F172A?style=for-the-badge&logo=plotly&logoColor=3B82F6" alt="Plotly" />
  <img src="https://img.shields.io/badge/Gemini%202.5-AI%20Diligence-0F172A?style=for-the-badge&logo=googlegemini&logoColor=A855F7" alt="Gemini AI" />
  <img src="https://img.shields.io/badge/Private%20Equity-LBO%20Engine-064E3B?style=for-the-badge" alt="Private Equity" />
</p>

<p>
  <strong>Automated 5-Year Leveraged Buyout (LBO) Modeling • Debt Waterfall Sensitivity • NLP Risk Scoring • Investment Committee Memo Synthesis</strong>
</p>

</div>

---

> [!IMPORTANT]
> **The Problem:** Middle-market Private Equity analysts spend dozens of hours manually building LBO debt schedules in spreadsheets and scanning data-room documents for hidden contract or margin risks. **DealPulse AI** combines a quantitative Python LBO engine with an AI/NLP due diligence scanner to underwrite deals and generate a risk-adjusted **Investment Committee (IC) Memo** in seconds.

---

## 🖥️ Terminal Preview


---

## ⚙️ System Architecture

```mermaid
flowchart LR
    A[<b>Deal Inputs & CIM Notes</b><br/>Revenue, EBITDA, Leverage, Disclosures] --> B[<b>lbo_engine.py</b><br/>5-Yr Operating & Debt Waterfall]
    A --> C[<b>dd_analyzer.py</b><br/>NLP / Gemini Risk Extractor]
    B --> D[<b>Return Metrics</b><br/>Net IRR, MOIC & Value Bridge]
    B --> E[<b>Sensitivity Matrix</b><br/>5x5 Entry vs. Exit Multiple]
    C --> F[<b>Risk Haircut</b><br/>Diligence Score & Bid Adjustment]
    D & E & F --> G[<b>DealPulse Terminal</b><br/>Interactive Charts & IC Memo Export]

    style A fill:#111827,stroke:#374151,color:#F9FAFB
    style B fill:#064E3B,stroke:#10B981,color:#ECFDF5
    style C fill:#1E1B4B,stroke:#6366F1,color:#EEF2FF
    style E fill:#111827,stroke:#10B981,color:#F9FAFB
    style F fill:#111827,stroke:#6366F1,color:#F9FAFB
    style G fill:#0F172A,stroke:#3B82F6,color:#F9FAFB
