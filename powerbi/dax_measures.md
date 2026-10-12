# DAX Measures

These measures are written for the report described in [dashboard_design.md](dashboard_design.md). I wrote them for Power BI Desktop, but I could not run Power BI in my setup, so the expected values below come from the same data checked in Python and PostgreSQL. When you build the report, the cards should show these numbers with no slicers selected.

## Table and columns used

Import `data/cleaned_customer_data.csv` and name the table **customer_churn**.

| Column | Type in Power BI | Used in |
|---|---|---|
| customer_id | Text | Total Customers (one row = one customer) |
| churn | Text ("Yes" / "No") | Churned, Retained |
| tenure_months | Whole number | Average Tenure, High-Risk |
| monthly_charges | Decimal number | Average Monthly Charges |
| contract_type | Text | High-Risk |
| support_tickets | Whole number | High-Risk |

## Measures

### Total Customers

```DAX
Total Customers = COUNTROWS(customer_churn)
```

Counts the rows in the table. Each row is one customer, because duplicates were removed during cleaning.

Expected value: **3,990**

### Churned Customers

```DAX
Churned Customers =
CALCULATE([Total Customers], customer_churn[churn] = "Yes")
```

Counts only the customers whose churn value is "Yes".

Expected value: **1,126**

### Retained Customers

```DAX
Retained Customers =
CALCULATE([Total Customers], customer_churn[churn] = "No")
```

Counts the customers who stayed.

Expected value: **2,864**

### Churn Rate %

```DAX
Churn Rate % = DIVIDE([Churned Customers], [Total Customers])
```

Churned customers divided by all customers. `DIVIDE` returns blank instead of an error if a slicer leaves no customers. Set the format to Percentage with 1 decimal place.

Expected value: **28.2%**

### Retention Rate %

```DAX
Retention Rate % = DIVIDE([Retained Customers], [Total Customers])
```

Retained customers divided by all customers. Churn Rate % and Retention Rate % always add up to 100%.

Expected value: **71.8%**

### Average Tenure

```DAX
Average Tenure = AVERAGE(customer_churn[tenure_months])
```

Average number of months customers have been with the company.

Expected value: **25.7 months** (churned: 16.8, retained: 29.2)

### Average Monthly Charges

```DAX
Average Monthly Charges = AVERAGE(customer_churn[monthly_charges])
```

Average monthly bill in Rupees.

Expected value: **Rs 1,077.10** (churned: Rs 1,151.13, retained: Rs 1,048.00)

### High-Risk Customers

```DAX
High-Risk Customers =
CALCULATE(
    [Total Customers],
    KEEPFILTERS(customer_churn[contract_type] = "Month-to-month"),
    KEEPFILTERS(customer_churn[tenure_months] <= 12),
    KEEPFILTERS(customer_churn[support_tickets] >= 3)
)
```

Counts customers who match all three conditions: month-to-month contract, 12 months or less with the company, and 3 or more support tickets. These are the three factors with the clearest churn differences in the analysis. This is a simple rule I defined from the analysis, not a prediction model.

`KEEPFILTERS` makes the measure respect the slicers. Without it, the contract type condition would replace the Contract Type slicer, and the card would still show 225 when "Two year" is selected.

Expected value: **225** (134 of them churned, a 59.6% churn rate)

### High-Risk Active Customers

```DAX
High-Risk Active Customers =
CALCULATE([High-Risk Customers], customer_churn[churn] = "No")
```

The high-risk customers who have not left yet. These are the customers the retention team could still contact.

Expected value: **91**

## Where the expected values come from

| Measure | SQL query in `sql/churn_queries.sql` |
|---|---|
| Total / Churned / Retained Customers | 1, 2, 3 |
| Churn Rate % / Retention Rate % | 4, 5 |
| Average Monthly Charges (churned vs retained) | 15 |
| Average Tenure (churned vs retained) | 16 |
| High-Risk Customers / High-Risk Active Customers | 17b |

The overall averages (25.7 months and Rs 1,077.10) were checked with `AVG()` in PostgreSQL and `mean()` in pandas.
