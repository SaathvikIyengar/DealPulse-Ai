"""
lbo_engine.py
Core 5-Year Leveraged Buyout (LBO) Financial Modeling & Sensitivity Engine.
Models Sources & Uses, Operating Projections, Mandatory + Cash-Sweep Debt Waterfall,
MOIC, IRR, and 2D Entry/Exit Multiple Sensitivity Matrices.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


@dataclass
class DealAssumptions:
    company_name: str
    sector: str
    ltm_revenue: float          # $M
    ltm_ebitda: float           # $M
    entry_multiple: float       # EV / EBITDA
    exit_multiple: float        # EV / EBITDA
    debt_pct: float             # % of Purchase EV funded via Debt (0.0 - 0.85)
    interest_rate: float        # Annual interest rate on debt (e.g., 0.085 for 8.5%)
    rev_growth: float           # Annual revenue growth rate
    target_ebitda_margin: float # Year 5 target EBITDA margin
    tax_rate: float = 0.25      # Corporate cash tax rate
    da_pct_rev: float = 0.03    # D&A as % of revenue
    capex_pct_rev: float = 0.035 # CapEx as % of revenue
    nwc_pct_delta_rev: float = 0.05 # Change in NWC as % of incremental revenue
    mandatory_amort_pct: float = 0.05 # 5% annual mandatory debt amortization
    cash_sweep_pct: float = 0.75 # 75% excess FCF swept to pay down debt
    tx_fee_pct: float = 0.02    # 2% advisory & financing transaction fees


PRESET_DEALS: Dict[str, Tuple[DealAssumptions, str]] = {
    "Apex Cloud Systems (B2B SaaS)": (
        DealAssumptions(
            company_name="Apex Cloud Systems",
            sector="Enterprise B2B SaaS",
            ltm_revenue=48.0,
            ltm_ebitda=12.0,
            entry_multiple=10.5,
            exit_multiple=11.5,
            debt_pct=0.50,
            interest_rate=0.085,
            rev_growth=0.14,
            target_ebitda_margin=0.29,
        ),
        (
            "Apex Cloud Systems provides mission-critical compliance workflow software "
            "with 94% gross retention and 112% net dollar retention. However, the top 3 "
            "enterprise clients represent 34% of total ARR, and one major contract renews in Q3. "
            "Gross margins remain strong at 78%, though R&D cloud compute expenses grew 18% YoY "
            "due to new AI feature rollouts. Existing senior credit facility carries a 4.5x net "
            "leverage maintenance covenant."
        ),
    ),
    "Vanguard Cold-Chain Logistics": (
        DealAssumptions(
            company_name="Vanguard Cold-Chain Logistics",
            sector="Industrial & Supply Chain",
            ltm_revenue=110.0,
            ltm_ebitda=16.5,
            entry_multiple=7.4,
            exit_multiple=8.0,
            debt_pct=0.60,
            interest_rate=0.080,
            rev_growth=0.07,
            target_ebitda_margin=0.175,
        ),
        (
            "Vanguard operates 14 temperature-controlled regional distribution hubs serving "
            "pharmaceutical and specialty food distributors. Multi-year take-or-pay contracts "
            "cover 70% of warehouse capacity with automatic inflation escalators. Key diligence "
            "items include aging refrigeration fleet capex requirements over the next 24 months, "
            "diesel fuel surcharge pass-through lags, and regional driver wage inflation."
        ),
    ),
    "MedCore Specialty Clinics": (
        DealAssumptions(
            company_name="MedCore Specialty Clinics",
            sector="Healthcare Services",
            ltm_revenue=75.0,
            ltm_ebitda=13.5,
            entry_multiple=9.0,
            exit_multiple=9.5,
            debt_pct=0.55,
            interest_rate=0.0825,
            rev_growth=0.09,
            target_ebitda_margin=0.20,
        ),
        (
            "MedCore is a 22-clinic outpatient physical therapy and diagnostics platform with "
            "strong organic patient volume growth (+8.5% YoY) and clear bolt-on M&A tuck-in "
            "opportunities. Risks include potential commercial insurer reimbursement rate pressure, "
            "clinician turnover in two metropolitan markets, and billing system integration "
            "delays following two recent acquisitions."
        ),
    ),
}


def run_lbo_model(assumptions: DealAssumptions) -> Dict:
    """
    Executes a 5-year LBO projection and returns Sources & Uses, annual schedule DataFrame,
    and exit return metrics (MOIC, IRR, Value Creation Bridge).
    """
    # 1. Entry Valuation & Sources/Uses
    entry_ev = assumptions.ltm_ebitda * assumptions.entry_multiple
    tx_fees = entry_ev * assumptions.tx_fee_pct
    total_uses = entry_ev + tx_fees

    initial_debt = entry_ev * assumptions.debt_pct
    sponsor_equity = total_uses - initial_debt

    sources_uses = pd.DataFrame({
        "Sources": ["Senior & Mezzanine Debt", "Sponsor Equity", "Total Sources"],
        "Amount ($M)": [initial_debt, sponsor_equity, total_uses],
        "% of Total": [
            (initial_debt / total_uses) * 100,
            (sponsor_equity / total_uses) * 100,
            100.0,
        ],
        "Uses": ["Purchase Enterprise Value", "Transaction & Financing Fees", "Total Uses"],
        "Uses ($M)": [entry_ev, tx_fees, total_uses],
    })

    # 2. 5-Year Operating & Debt Waterfall Schedule
    years = [1, 2, 3, 4, 5]
    ltm_margin = assumptions.ltm_ebitda / assumptions.ltm_revenue if assumptions.ltm_revenue > 0 else 0.15

    records: List[Dict] = []
    prev_rev = assumptions.ltm_revenue
    beg_debt = initial_debt

    for yr in years:
        rev = prev_rev * (1.0 + assumptions.rev_growth)
        # Linear margin progression from LTM margin to Year 5 target margin
        margin = ltm_margin + (assumptions.target_ebitda_margin - ltm_margin) * (yr / 5.0)
        ebitda = rev * margin
        da = rev * assumptions.da_pct_rev
        ebit = ebitda - da

        # Beginning debt interest avoids circularity in fast screening models
        interest = beg_debt * assumptions.interest_rate
        ebt = ebit - interest
        taxes = max(0.0, ebt * assumptions.tax_rate)

        capex = rev * assumptions.capex_pct_rev
        delta_nwc = (rev - prev_rev) * assumptions.nwc_pct_delta_rev
        fcf = ebitda - interest - taxes - capex - delta_nwc

        mandatory_amort = min(beg_debt, initial_debt * assumptions.mandatory_amort_pct)
        remaining_fcf = fcf - mandatory_amort

        if remaining_fcf >= 0:
            cash_sweep = min(beg_debt - mandatory_amort, remaining_fcf * assumptions.cash_sweep_pct)
            revolver_draw = 0.0
        else:
            cash_sweep = 0.0
            revolver_draw = abs(remaining_fcf)

        end_debt = max(0.0, beg_debt - mandatory_amort - cash_sweep + revolver_draw)
        implied_ev = ebitda * assumptions.exit_multiple
        implied_equity = max(0.0, implied_ev - end_debt)

        records.append({
            "Year": f"Year {yr}",
            "Revenue ($M)": round(rev, 2),
            "EBITDA ($M)": round(ebitda, 2),
            "EBITDA Margin (%)": round(margin * 100, 1),
            "Interest ($M)": round(interest, 2),
            "Cash Taxes ($M)": round(taxes, 2),
            "CapEx & ΔNWC ($M)": round(capex + delta_nwc, 2),
            "Free Cash Flow ($M)": round(fcf, 2),
            "Beginning Debt ($M)": round(beg_debt, 2),
            "Debt Paydown ($M)": round(beg_debt - end_debt, 2),
            "Ending Debt ($M)": round(end_debt, 2),
            "Implied Equity Value ($M)": round(implied_equity, 2),
            "Net Leverage (Debt/EBITDA)": round(end_debt / ebitda, 2) if ebitda > 0 else 0.0,
        })

        prev_rev = rev
        beg_debt = end_debt

    schedule_df = pd.DataFrame(records)

    # 3. Exit Returns & Value Creation Attribution
    exit_ebitda = schedule_df.iloc[-1]["EBITDA ($M)"]
    exit_debt = schedule_df.iloc[-1]["Ending Debt ($M)"]
    exit_ev = exit_ebitda * assumptions.exit_multiple
    exit_equity = exit_ev - exit_debt

    if sponsor_equity > 0 and exit_equity > 0:
        moic = exit_equity / sponsor_equity
        irr = (moic ** (1.0 / 5.0)) - 1.0
    else:
        moic = 0.0
        irr = -1.0

    # Value Creation Bridge ($M)
    ebitda_growth_impact = (exit_ebitda - assumptions.ltm_ebitda) * assumptions.entry_multiple
    multiple_expansion_impact = (assumptions.exit_multiple - assumptions.entry_multiple) * exit_ebitda
    debt_paydown_impact = initial_debt - exit_debt

    # Deal Verdict Logic (Standard PE Hurdle: >=20% IRR & >=2.2x MOIC)
    if irr >= 0.22 and moic >= 2.3:
        verdict = "STRONG BUY — Exceeds 20% Institutional PE Hurdle"
    elif irr >= 0.16 and moic >= 1.8:
        verdict = "WATCHLIST — Borderline Returns; Requires Operational Upside"
    else:
        verdict = "PASS — Below Target Risk-Adjusted Hurdle Rate"

    return {
        "entry_ev": round(entry_ev, 2),
        "initial_debt": round(initial_debt, 2),
        "sponsor_equity": round(sponsor_equity, 2),
        "exit_ev": round(exit_ev, 2),
        "exit_debt": round(exit_debt, 2),
        "exit_equity": round(exit_equity, 2),
        "moic": round(moic, 2),
        "irr_pct": round(irr * 100, 1),
        "verdict": verdict,
        "sources_uses": sources_uses,
        "schedule": schedule_df,
        "attribution": {
            "EBITDA Growth ($M)": round(ebitda_growth_impact, 2),
            "Multiple Expansion ($M)": round(multiple_expansion_impact, 2),
            "Debt De-leveraging ($M)": round(debt_paydown_impact, 2),
        },
    }


def generate_irr_sensitivity(
    assumptions: DealAssumptions,
    entry_steps: List[float] = None,
    exit_steps: List[float] = None,
) -> pd.DataFrame:
    """
    Computes a 5x5 Entry Multiple vs. Exit Multiple IRR (%) sensitivity table.
    """
    if entry_steps is None:
        base_in = assumptions.entry_multiple
        entry_steps = [round(base_in + d, 1) for d in [-1.0, -0.5, 0.0, 0.5, 1.0]]
    if exit_steps is None:
        base_out = assumptions.exit_multiple
        exit_steps = [round(base_out + d, 1) for d in [-1.0, -0.5, 0.0, 0.5, 1.0]]

    matrix = []
    for entry_m in entry_steps:
        row = []
        for exit_m in exit_steps:
            temp = DealAssumptions(
                company_name=assumptions.company_name,
                sector=assumptions.sector,
                ltm_revenue=assumptions.ltm_revenue,
                ltm_ebitda=assumptions.ltm_ebitda,
                entry_multiple=max(3.0, entry_m),
                exit_multiple=max(3.0, exit_m),
                debt_pct=assumptions.debt_pct,
                interest_rate=assumptions.interest_rate,
                rev_growth=assumptions.rev_growth,
                target_ebitda_margin=assumptions.target_ebitda_margin,
            )
            res = run_lbo_model(temp)
            row.append(res["irr_pct"])
        matrix.append(row)

    df = pd.DataFrame(
        matrix,
        index=[f"Entry {m:.1f}x" for m in entry_steps],
        columns=[f"Exit {m:.1f}x" for m in exit_steps],
    )
    return df
