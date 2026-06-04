# Variable Notes

## Research Question

Is the proportion of current alcohol use different between male and female students?

## Source Data

Original file: `data/raw/YRBS_2007.csv`

## Group Variable

Variable: `WhatIsYourSex`

Coding used in this project:

- `1 = Female`
- `2 = Male`

Rows with missing or invalid sex values are removed from the analysis. The analysis keeps only valid codes `1` and `2`.

## Response Variable

Variable: `CurrentAlcoholUse`

Cycle 3 required recoding rule:

- failure / no current alcohol use: code `1`
- success / yes current alcohol use: codes `2` through `7`

Binary coding used in this project:

- `0 = no current alcohol use`
- `1 = current alcohol use`

Rows with missing or invalid current alcohol use values are removed from the analysis. The analysis keeps only valid codes `1` through `7`.

Missing values are not treated as "no current alcohol use" because that would change the meaning of the response variable.

## Statistical Method

Because the response variable is binary, this project compares two proportions.

- Null hypothesis: `p_male - p_female = 0`
- Alternative hypothesis: `p_male - p_female != 0`
- Test: two-proportion z-test
- Significance level: `alpha = 0.05`
- Confidence interval: 95% CI for `p_male - p_female`
- Additional effect size measures: relative risk and odds ratio for male students compared with female students

## Assumptions Considered

- The male and female groups are treated as independent groups.
- The response is binary after recoding.
- Both groups have large enough sample sizes for the normal approximation.
- Missing values are excluded rather than treated as no responses.
- This is observational survey data, so the analysis compares association only and does not claim causation.
