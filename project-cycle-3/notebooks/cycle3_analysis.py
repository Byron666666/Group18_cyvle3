from pathlib import Path
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MPL_CACHE_DIR = PROJECT_ROOT / ".matplotlib-cache"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
XDG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
(XDG_CACHE_DIR / "fontconfig").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

RAW_DATA = PROJECT_ROOT / "data" / "raw" / "YRBS_2007.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
SUMMARY_DIR = PROJECT_ROOT / "outputs" / "summary"
REPORT_DIR = PROJECT_ROOT / "report"

for directory in [PROCESSED_DIR, FIGURES_DIR, TABLES_DIR, SUMMARY_DIR, REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

GROUP_COL = "WhatIsYourSex"
RESPONSE_COL = "CurrentAlcoholUse"
ALPHA = 0.05
Z_CRIT = norm.ppf(1 - ALPHA / 2)

sns.set_theme(style="whitegrid")


def fmt_num(value, digits=4):
    return f"{value:.{digits}f}"


def fmt_pct(value, digits=1):
    return f"{100 * value:.{digits}f}%"


def main():
    df = pd.read_csv(RAW_DATA)

    selected = df[[GROUP_COL, RESPONSE_COL]].copy()
    selected["sex"] = selected[GROUP_COL].map({1: "Female", 2: "Male"})
    selected["current_alcohol_use"] = np.select(
        [
            selected[RESPONSE_COL].eq(1),
            selected[RESPONSE_COL].between(2, 7, inclusive="both"),
        ],
        [0, 1],
        default=np.nan,
    )

    cleaned = selected.dropna(subset=["sex", "current_alcohol_use"]).copy()
    cleaned["current_alcohol_use"] = cleaned["current_alcohol_use"].astype(int)
    cleaned = cleaned.rename(
        columns={
            GROUP_COL: "sex_code",
            RESPONSE_COL: "current_alcohol_code",
        }
    )
    cleaned.to_csv(PROCESSED_DIR / "cycle3_cleaned_gender_alcohol.csv", index=False)

    group_summary = (
        cleaned.groupby("sex", observed=True)["current_alcohol_use"]
        .agg(n="count", current_alcohol_users="sum", proportion_current_alcohol_use="mean")
        .reset_index()
    )
    group_summary["current_alcohol_non_users"] = (
        group_summary["n"] - group_summary["current_alcohol_users"]
    )
    group_summary["percent_current_alcohol_use"] = (
        100 * group_summary["proportion_current_alcohol_use"]
    )
    group_summary["sex"] = pd.Categorical(
        group_summary["sex"],
        categories=["Female", "Male"],
        ordered=True,
    )
    group_summary = group_summary.sort_values("sex").reset_index(drop=True)
    group_summary.to_csv(TABLES_DIR / "group_summary.csv", index=False)

    display_summary = group_summary.copy()
    display_summary["Proportion"] = display_summary[
        "proportion_current_alcohol_use"
    ].round(4)
    display_summary["Percent"] = (
        display_summary["proportion_current_alcohol_use"] * 100
    ).round(1).astype(str) + "%"
    display_summary = display_summary.rename(
        columns={
            "sex": "Group",
            "current_alcohol_users": "Current alcohol users",
        }
    )
    display_summary = display_summary[
        ["Group", "n", "Current alcohol users", "Proportion", "Percent"]
    ]
    display_summary.to_csv(TABLES_DIR / "group_summary_display.csv", index=False)
    group_summary_md = (
        "| Group | n | Current alcohol users | Proportion | Percent |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    for _, row in display_summary.iterrows():
        group_summary_md += (
            f"| {row['Group']} | {row['n']} | {row['Current alcohol users']} | "
            f"{row['Proportion']} | {row['Percent']} |\n"
        )
    (TABLES_DIR / "group_summary.md").write_text(group_summary_md, encoding="utf-8")

    lookup = group_summary.set_index("sex")
    x_female = float(lookup.loc["Female", "current_alcohol_users"])
    n_female = float(lookup.loc["Female", "n"])
    x_male = float(lookup.loc["Male", "current_alcohol_users"])
    n_male = float(lookup.loc["Male", "n"])

    p_female = x_female / n_female
    p_male = x_male / n_male
    difference = p_male - p_female

    pooled = (x_male + x_female) / (n_male + n_female)
    se_pooled = np.sqrt(pooled * (1 - pooled) * (1 / n_male + 1 / n_female))
    z_stat = difference / se_pooled
    p_value = 2 * norm.sf(abs(z_stat))

    se_unpooled = np.sqrt(
        p_male * (1 - p_male) / n_male + p_female * (1 - p_female) / n_female
    )
    ci_low = difference - Z_CRIT * se_unpooled
    ci_high = difference + Z_CRIT * se_unpooled

    results = {
        "comparison": "Male - Female",
        "female_n": int(n_female),
        "male_n": int(n_male),
        "female_successes": int(x_female),
        "male_successes": int(x_male),
        "female_proportion": p_female,
        "male_proportion": p_male,
        "difference_male_minus_female": difference,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "z_statistic": z_stat,
        "p_value": p_value,
        "alpha": ALPHA,
        "reject_null": p_value < ALPHA,
    }
    pd.DataFrame([results]).to_csv(TABLES_DIR / "inference_results.csv", index=False)

    male_non_users = n_male - x_male
    female_non_users = n_female - x_female
    risk_ratio = p_male / p_female
    se_log_rr = np.sqrt((1 / x_male) - (1 / n_male) + (1 / x_female) - (1 / n_female))
    rr_low = np.exp(np.log(risk_ratio) - Z_CRIT * se_log_rr)
    rr_high = np.exp(np.log(risk_ratio) + Z_CRIT * se_log_rr)

    odds_male = x_male / male_non_users
    odds_female = x_female / female_non_users
    odds_ratio = odds_male / odds_female
    se_log_or = np.sqrt(1 / x_male + 1 / male_non_users + 1 / x_female + 1 / female_non_users)
    or_low = np.exp(np.log(odds_ratio) - Z_CRIT * se_log_or)
    or_high = np.exp(np.log(odds_ratio) + Z_CRIT * se_log_or)

    effect_size_results = {
        "comparison": "Male vs Female",
        "relative_risk": risk_ratio,
        "rr_ci_low": rr_low,
        "rr_ci_high": rr_high,
        "odds_ratio": odds_ratio,
        "or_ci_low": or_low,
        "or_ci_high": or_high,
    }
    pd.DataFrame([effect_size_results]).to_csv(
        TABLES_DIR / "effect_size_results.csv",
        index=False,
    )
    effect_size_md = (
        "| Measure | Estimate | 95% CI |\n"
        "| --- | --- | --- |\n"
        f"| Relative Risk | {fmt_num(risk_ratio, 4)} | [{fmt_num(rr_low, 4)}, {fmt_num(rr_high, 4)}] |\n"
        f"| Odds Ratio | {fmt_num(odds_ratio, 4)} | [{fmt_num(or_low, 4)}, {fmt_num(or_high, 4)}] |"
    )
    (TABLES_DIR / "effect_size_results.md").write_text(effect_size_md + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(group_summary))
    proportions = group_summary["proportion_current_alcohol_use"].to_numpy()
    counts = group_summary["n"].to_numpy()
    errors = Z_CRIT * np.sqrt(proportions * (1 - proportions) / counts)
    colors = ["#4C78A8", "#F58518"]
    ax.bar(x, proportions, yerr=errors, capsize=7, color=colors, width=0.62)
    ax.set_xticks(x, group_summary["sex"])
    ax.set_ylim(0, max(0.55, float((proportions + errors).max()) + 0.08))
    ax.set_ylabel("Proportion with current alcohol use")
    ax.set_title("Current Alcohol Use by Sex")
    for xpos, prop, n in zip(x, proportions, counts):
        ax.text(xpos, prop + 0.02, f"{fmt_pct(prop)}\nn={int(n)}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "current_alcohol_use_by_sex.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(
        difference,
        0,
        xerr=[[difference - ci_low], [ci_high - difference]],
        fmt="o",
        color="#2F4B7C",
        ecolor="#2F4B7C",
        capsize=8,
        markersize=8,
    )
    ax.axvline(0, color="#777777", linestyle="--", linewidth=1.2)
    ax.set_yticks([0], ["Male - Female"])
    ax.set_xlabel("Difference in current alcohol use proportions")
    ax.set_title("95% Confidence Interval for Difference")
    padding = max(0.03, (ci_high - ci_low) * 0.4)
    ax.set_xlim(ci_low - padding, ci_high + padding)
    ax.text(difference, 0.12, f"Difference = {fmt_pct(difference)}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "difference_confidence_interval.png", dpi=200)
    plt.close(fig)

    create_summary_slide(results, risk_ratio, odds_ratio)
    write_interpretation(results, risk_ratio, odds_ratio, rr_low, rr_high, or_low, or_high)

    print("Cycle 3 analysis complete.")


def create_summary_slide(results, risk_ratio, odds_ratio):
    fig = plt.figure(figsize=(13.333, 7.5), facecolor="#F7F4EF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    ax.text(0.06, 0.90, "Gender and Current Alcohol Use", fontsize=30, weight="bold", color="#1F2933")
    ax.text(
        0.06,
        0.83,
        "Two-proportion z-test using YRBS 2007",
        fontsize=15,
        color="#52606D",
    )

    ax.text(0.06, 0.71, "Research question", fontsize=14, weight="bold", color="#1F2933")
    ax.text(
        0.06,
        0.65,
        "Is the proportion of current alcohol use different between male and female students?",
        fontsize=16,
        color="#1F2933",
        wrap=True,
    )

    metric_y = 0.48
    metrics = [
        ("Female", fmt_pct(results["female_proportion"]), f"n={results['female_n']}"),
        ("Male", fmt_pct(results["male_proportion"]), f"n={results['male_n']}"),
        ("Difference", fmt_pct(results["difference_male_minus_female"]), "Male - Female"),
    ]
    for idx, (label, value, sublabel) in enumerate(metrics):
        x0 = 0.06 + idx * 0.22
        ax.add_patch(plt.Rectangle((x0, metric_y), 0.18, 0.16, color="#FFFFFF", ec="#D9E2EC"))
        ax.text(x0 + 0.02, metric_y + 0.105, value, fontsize=24, weight="bold", color="#1F2933")
        ax.text(x0 + 0.02, metric_y + 0.060, label, fontsize=13, color="#52606D")
        ax.text(x0 + 0.02, metric_y + 0.027, sublabel, fontsize=11, color="#7B8794")

    inset = fig.add_axes([0.58, 0.25, 0.34, 0.38])
    vals = [results["female_proportion"], results["male_proportion"]]
    inset.bar(["Female", "Male"], vals, color=["#4C78A8", "#F58518"], width=0.58)
    inset.set_ylim(0, 0.55)
    inset.set_ylabel("Proportion")
    inset.set_title("Current alcohol use")
    for xpos, prop in enumerate(vals):
        inset.text(xpos, prop + 0.015, fmt_pct(prop), ha="center", fontsize=12)

    ax.text(0.06, 0.31, "Key result", fontsize=14, weight="bold", color="#1F2933")
    ax.text(
        0.06,
        0.25,
        f"95% CI for difference: [{fmt_pct(results['ci_low'])}, {fmt_pct(results['ci_high'])}]",
        fontsize=16,
        color="#1F2933",
    )
    ax.text(
        0.06,
        0.20,
        f"p-value = {fmt_num(results['p_value'], 6)}; RR = {fmt_num(risk_ratio, 4)}; OR = {fmt_num(odds_ratio, 4)}",
        fontsize=14,
        color="#52606D",
    )
    ax.text(0.06, 0.12, "Conclusion", fontsize=14, weight="bold", color="#1F2933")
    ax.text(
        0.06,
        0.07,
        "At alpha = 0.05, the difference is not statistically significant.",
        fontsize=17,
        color="#1F2933",
    )

    fig.savefig(SUMMARY_DIR / "one_slide_infographic_summary.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_interpretation(results, risk_ratio, odds_ratio, rr_low, rr_high, or_low, or_high):
    direction_sentence = (
        "male students had a higher observed proportion of current alcohol use than female students"
        if results["difference_male_minus_female"] > 0
        else "male students had a lower observed proportion of current alcohol use than female students"
    )

    if results["reject_null"]:
        test_sentence = "Because the p-value is below 0.05, we reject the null hypothesis."
        conclusion_sentence = "There is statistical evidence that the proportion of current alcohol use differs between male and female students."
    else:
        test_sentence = "Because the p-value is not below 0.05, we fail to reject the null hypothesis."
        conclusion_sentence = "There is not enough statistical evidence to conclude that the proportion of current alcohol use differs between male and female students."

    report = f"""# Final Interpretation

## Research Question

Is the proportion of current alcohol use different between male and female students?

## Method

The response variable was recoded as binary:

- `1 = current alcohol use`
- `0 = no current alcohol use`

Because the response variable is binary and the group variable has two independent groups, a two-proportion z-test was used. As an additional effect size analysis, relative risk and odds ratio were also calculated for male students compared with female students.

## Results

- Female sample size: {results['female_n']}
- Male sample size: {results['male_n']}
- Female current alcohol use proportion: {fmt_num(results['female_proportion'], 4)} ({fmt_pct(results['female_proportion'])})
- Male current alcohol use proportion: {fmt_num(results['male_proportion'], 4)} ({fmt_pct(results['male_proportion'])})
- Difference, male minus female: {fmt_num(results['difference_male_minus_female'], 4)} ({fmt_pct(results['difference_male_minus_female'])})
- 95% confidence interval: [{fmt_num(results['ci_low'], 4)}, {fmt_num(results['ci_high'], 4)}]
- z statistic: {fmt_num(results['z_statistic'], 4)}
- p-value: {fmt_num(results['p_value'], 6)}
- Relative risk, male vs female: {fmt_num(risk_ratio, 4)}; 95% CI: [{fmt_num(rr_low, 4)}, {fmt_num(rr_high, 4)}]
- Odds ratio, male vs female: {fmt_num(odds_ratio, 4)}; 95% CI: [{fmt_num(or_low, 4)}, {fmt_num(or_high, 4)}]

## Conclusion at alpha = 0.05

{test_sentence}

In this sample, {direction_sentence}. {conclusion_sentence}

The relative risk was {fmt_num(risk_ratio, 4)}, meaning the male current alcohol use proportion was about {fmt_num(risk_ratio, 2)} times the female proportion. The odds ratio was {fmt_num(odds_ratio, 4)}, meaning the odds of current alcohol use were slightly higher for male students than for female students. Both effect size estimates are close to 1, which suggests that the practical difference between male and female students is small.

This result should be interpreted as an association in survey data, not as evidence that sex causes alcohol use behavior.
"""

    (REPORT_DIR / "final_interpretation.md").write_text(report, encoding="utf-8")
    (SUMMARY_DIR / "analysis_summary.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
