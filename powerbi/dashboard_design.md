# Power BI Report Design

This is the planned structure for a 3-page Power BI report. I have not built the `.pbix` file yet, so this is a design, not a finished dashboard. The measures are in [dax_measures.md](dax_measures.md).

## Data setup

1. Get Data > Text/CSV > `data/cleaned_customer_data.csv`. Name the table `customer_churn`.
2. Check the column types: `tenure_months`, `age`, `support_tickets`, `usage_frequency` as Whole number, `monthly_charges` and `total_charges` as Decimal number, everything else as Text.
3. Add sort columns so the bins show in the right order instead of alphabetically (Power Query > Add Column > Conditional Column, or a DAX calculated column):

```DAX
tenure_group_order =
SWITCH(customer_churn[tenure_group],
    "0-6 months", 1, "7-12 months", 2, "13-24 months", 3,
    "25-48 months", 4, "49+ months", 5)

charge_band_order =
SWITCH(customer_churn[charge_band],
    "Under 500", 1, "500-999", 2, "1000-1499", 3, "1500+", 4)
```

Then select `tenure_group` > Column tools > Sort by column > `tenure_group_order`. Do the same for `charge_band`. `support_ticket_band` ("0", "1-2", "3-4", "5+") already sorts correctly as text.

## Page 1: Churn Overview

**Slicers (top of the page):** region, contract_type, customer_segment

**KPI cards:**

| Card | Measure | Expected value (no slicers) |
|---|---|---|
| Total Customers | Total Customers | 3,990 |
| Churned Customers | Churned Customers | 1,126 |
| Retained Customers | Retained Customers | 2,864 |
| Churn Rate % | Churn Rate % | 28.2% |
| Retention Rate % | Retention Rate % | 71.8% |
| Average Tenure | Average Tenure | 25.7 months |
| Average Monthly Charges | Average Monthly Charges | Rs 1,077.10 |

**Visuals:**

| Visual | Type | Fields | What it should show |
|---|---|---|---|
| Churn distribution | Donut or column chart | churn, Total Customers | 2,864 retained, 1,126 churned |
| Churn by contract type | Clustered column | contract_type, Churn Rate % | Month-to-month 43.5%, One year 15.6%, Two year 8.5% |
| Churn by tenure group | Clustered column | tenure_group, Churn Rate % | 50.4% for 0-6 months down to 9.9% for 49+ months |
| Churn by payment method | Clustered bar | payment_method, Churn Rate % | Cash 33.3% highest, Auto Debit 23.8% lowest |

## Page 2: Churn Drivers

Same slicers as Page 1 (use View > Sync slicers).

| Visual | Type | Fields | What it should show |
|---|---|---|---|
| Churn by monthly charge band | Clustered column | charge_band, Churn Rate % | 21.5% (Under 500) up to 33.8% (1500+) |
| Churn by service type | Clustered bar | service_type, Churn Rate % | All-in-One 34.8% highest, Mobile Only 22.6% lowest |
| Churn by support-ticket band | Clustered column | support_ticket_band, Churn Rate % | 22.2% (0 tickets) up to 37.1% (5+) |
| Churn by customer segment | Clustered bar | customer_segment, Churn Rate % | Student 39.8% highest, Small Business 23.1% lowest |
| Churn by region | Clustered bar | region, Churn Rate % | South 31.2% highest, East 24.3% lowest |
| Avg monthly charges: churned vs retained | Clustered column | churn, Average Monthly Charges | Rs 1,151.13 vs Rs 1,048.00 |

The payment method and region visuals also show an "Unknown" bar (11 and 9 customers). Filter it out on the visual or keep it and mention that it is too small to compare.

## Page 3: Retention Analysis

| Visual | Type | Fields | What it should show |
|---|---|---|---|
| High-risk customers | Two cards | High-Risk Customers, High-Risk Active Customers | 225 and 91 |
| High-risk customer groups | Matrix | Rows: contract_type, tenure_group. Columns: support_ticket_band. Values: Churn Rate % (conditional formatting on the background) | Month-to-month + 0-6 months + 3-4 tickets is the highest (61.5%, 130 customers) |
| Retention by tenure | Line or column chart | tenure_group, Retention Rate % | 49.6% for 0-6 months up to 90.1% for 49+ months |
| Retention by contract | Clustered column | contract_type, Retention Rate % | Month-to-month 56.5%, One year 84.4%, Two year 91.5% |
| Customer segments needing attention | Table | customer_segment, contract_type, Total Customers, Churned Customers, Churn Rate %, sorted by Churned Customers | Individual + Month-to-month lost the most customers (379) |
| Short tenure and high charges | Scatter chart | X: tenure_months, Y: monthly_charges, Legend: churn (or a table filtered to tenure_months <= 12 and monthly_charges >= 1500) | 237 customers in this group, 54.9% churned |
| Support-ticket churn pattern | Column chart | support_tickets (or support_ticket_band), Churn Rate % and Total Customers in the tooltip | Churn goes up from 22.2% (0 tickets) to 35.8% (3 tickets) |

## Design notes

- Use one color for all churn-rate bars, and only two colors where churned and retained are shown together.
- Show data labels on bar charts so people do not have to read the axis.
- Keep slicers in the same place on every page.
- Add a small text box on Page 3 that explains the high-risk rule, so nobody reads it as a model prediction.
