# Code Explanation

This file explains the main steps in `notebooks/cycle3_analysis.ipynb`.

## 1. Setup

The notebook imports the required Python packages and defines the project folders:

- `data/raw/` for the original dataset
- `data/processed/` for cleaned data
- `outputs/figures/` for saved visualizations
- `outputs/tables/` for saved tables
- `outputs/summary/` for the one-slide infographic summary
- `report/` for the final interpretation

## 2. Load Data

The notebook reads `data/raw/YRBS_2007.csv` with pandas and selects two variables:

- `WhatIsYourSex`
- `CurrentAlcoholUse`

## 3. Recode Variables

The group variable is recoded as:

- `1 = Female`
- `2 = Male`

The response variable is recoded as:

- `0 = no current alcohol use`, original code `1`
- `1 = current alcohol use`, original codes `2` through `7`

Rows with missing or invalid values are removed.

## 4. Descriptive Summary

The notebook calculates the sample size, number of current alcohol users, and current alcohol use proportion for each group.

The summary is saved in:

- `outputs/tables/group_summary.csv`
- `outputs/tables/group_summary_display.csv`
- `outputs/tables/group_summary.md`

## 5. Two-Proportion Z-Test

Because the response variable is binary, the notebook compares the male and female proportions using a two-proportion z-test.

The comparison is:

`p_male - p_female`

The notebook reports:

- estimated difference
- 95% confidence interval
- z statistic
- p-value
- conclusion at `alpha = 0.05`

## 6. Effect Size

The notebook also calculates relative risk and odds ratio for male students compared with female students.

These help describe the size of the difference, not only whether the result is statistically significant.

## 7. Visualizations

The notebook saves:

- a bar chart comparing current alcohol use proportions by sex
- a confidence interval plot for `p_male - p_female`
- a one-slide infographic summary for exhibition

## 8. Final Interpretation

The notebook writes the final interpretation in context and saves it to:

- `report/final_interpretation.md`
- `outputs/summary/analysis_summary.md`
