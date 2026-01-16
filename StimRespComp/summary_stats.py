"""
summary_stats.py
Computes SDT metrics, RT statistics, and per-condition summaries.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm


# ---------------------------------
# SDT SUPPORT
# ---------------------------------
def corrected_rate(hits, total):
    """Prevents 0 or 1 rates (standard SDT correction)."""
    if total == 0:
        return 0.5
    rate = hits / total
    adj = 1 / np.sqrt(400)
    if rate == 0:
        return adj
    if rate == 1:
        return 1 - adj
    return rate


def compute_sdt(df):
    """
    df must contain column 'sdt_resp_cat' in {Hit, Miss, FA, CR}
    Returns dictionary of SDT metrics.
    """
    nHit = len(df[df.sdt_resp_cat == "Hit"])
    nMiss = len(df[df.sdt_resp_cat == "Miss"])
    nCR = len(df[df.sdt_resp_cat == "CR"])
    nFA = len(df[df.sdt_resp_cat == "FA"])

    hit_rate = corrected_rate(nHit, nHit + nMiss)
    fa_rate = corrected_rate(nFA, nFA + nCR)

    dprime = norm.ppf(hit_rate) - norm.ppf(fa_rate)
    c_crit = -0.5 * (norm.ppf(hit_rate) + norm.ppf(fa_rate))

    return {
        "HitRate": hit_rate,
        "FARate": fa_rate,
        "d'": dprime,
        "Criterion": c_crit,
    }


# ---------------------------------
# RT SUMMARY
# ---------------------------------
def compute_rt_stats(df):
    """Assumes df includes RT column (in seconds)."""
    rts = df["RT"].dropna().values
    if len(rts) == 0:
        return {"MeanRT": None, "MedianRT": None, "SDRT": None}

    return {
        "MeanRT": np.mean(rts),
        "MedianRT": np.median(rts),
        "SDRT": np.std(rts),
    }


# ---------------------------------
# PER-CONDITION SUMMARY
# ---------------------------------
def condition_summary(df):
    """
    Computes SDT + RT summary broken down by EXPERIMENTAL CONDITION.
    """
    result = []

    for cond, subdf in df.groupby("condition"):
        sdt = compute_sdt(subdf)
        rtstats = compute_rt_stats(subdf)
        result.append({
            "condition": cond,
            **sdt,
            **rtstats,
            "N": len(subdf)
        })

    return pd.DataFrame(result)


# ---------------------------------
# EXPORT SUMMARY TO CSV/TXT
# ---------------------------------
def export_full_summary(df, filename):
    """
    Creates three output files:
    - filename + "_overall.csv"
    - filename + "_perCondition.csv"
    - filename + "_rawResponses.csv"
    """
    overall_sdt = compute_sdt(df)
    overall_rt = compute_rt_stats(df)

    overall = {**overall_sdt, **overall_rt, "N": len(df)}

    # overall summary
    pd.DataFrame([overall]).to_csv(filename + "_overall.csv", index=False)

    # per-condition breakdown
    cond_df = condition_summary(df)
    cond_df.to_csv(filename + "_perCondition.csv", index=False)

    # raw df backup
    df.to_csv(filename + "_rawResponses.csv", index=False)

    print(f"Saved summary files:\n - {filename}_overall.csv\n - {filename}_perCondition.csv\n - {filename}_rawResponses.csv")
