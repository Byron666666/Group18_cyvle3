# Project Cycle 3

Two-sample inference project using `YRBS_2007.csv`.

## Group Information

- Group number: TODO
- Member names: TODO, TODO

## Selected Research Question

Question 2: Gender and Current Alcohol Use

Research question: Is the proportion of current alcohol use different between male and female students?

## Vedio
- ## Presentation Video
https://ntutcc-my.sharepoint.com/personal/109370231_cc_ntut_edu_tw/_layouts/15/stream.aspx?id=%2Fpersonal%2F109370231%5Fcc%5Fntut%5Fedu%5Ftw%2FDocuments%2F%E9%8C%84%E8%A3%BD%2F%E8%88%87%E3%80%8C%E8%AC%9D%E5%AE%87%E5%AE%B6%E3%80%8D%E7%9A%84%E6%9C%83%E8%AD%B0%2D20260601%5F201945%2D%E6%9C%83%E8%AD%B0%E9%8C%84%E8%A3%BD%2Emp4&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0&ga=1&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2Ee911dc59%2D0363%2D427c%2Da34f%2D2745f4171998


## Variables

- Group variable: `WhatIsYourSex`
- Response variable: `CurrentAlcoholUse`

## Method

The response variable is binary after recoding, so this project uses a two-proportion z-test.
The confidence interval is for the difference in proportions:

`p_male - p_female`

As an additional effect size analysis, the project also reports:

- relative risk, comparing male and female current alcohol use proportions;
- odds ratio, comparing male and female odds of current alcohol use.

## How To Run

The main analysis is in:

- `notebooks/cycle3_analysis.ipynb`

Open and run the notebook from the project folder. The notebook displays the figures inline and also saves all outputs to the required output folders.

For a beginner-friendly line-by-line explanation of the notebook code, see:

- `references/code_explanation.md`

An optional script version is also available:

```bash
python notebooks/cycle3_analysis.py
```

The script saves:

- cleaned data to `data/processed/`
- figures to `outputs/figures/`
- summary tables to `outputs/tables/`
- one-slide infographic summary to `outputs/summary/`
- final interpretation to `report/`

## Required Components Checklist

- README: this file
- Variable notes: `references/variable_notes.md`
- Code explanation: `references/code_explanation.md`
- Notebook: `notebooks/cycle3_analysis.ipynb`
- Optional script: `notebooks/cycle3_analysis.py`
- Saved figures: `outputs/figures/`
- Saved summary tables: `outputs/tables/`
- One-slide infographic summary: `outputs/summary/one_slide_infographic_summary.png`
- Final interpretation: `report/final_interpretation.md`

## Short Conclusion

In this sample, male students had a slightly higher observed current alcohol use proportion than female students.

- Female proportion: 44.6%
- Male proportion: 45.8%
- Difference, male minus female: 1.2 percentage points
- 95% confidence interval: [-0.5%, 2.9%]
- p-value: 0.178869
- Relative risk, male vs female: 1.0267
- Odds ratio, male vs female: 1.0492

At `alpha = 0.05`, this difference is not statistically significant.
