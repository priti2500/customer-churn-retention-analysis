# Interview Explanation

Notes for explaining this project in an interview. All numbers are from the analysis output.

## 1. 30-second explanation

I analyzed customer churn for a fictional telecom and broadband company, using a synthetic dataset of about 4,000 customers that I generated in Python. I cleaned the data in Python, analyzed churn by contract, tenure, charges, support tickets and other groups using pandas and PostgreSQL, and designed a 3-page Power BI report with DAX measures. The overall churn rate was 28.2%. The clearest patterns were month-to-month contracts and short tenure, and I used them to define a simple high-risk rule to find customers worth contacting.

## 2. 60-second explanation

The goal was to understand which customers leave and which groups the business should focus on. The dataset has 15 columns like contract type, tenure, monthly charges, payment method, support tickets and churn. I generated it with a Python script because I didn't have real company data, and I added duplicates, missing values, inconsistent text and outliers so I could practice cleaning.

After cleaning, 3,990 customers were left from 4,057 raw rows. I added tenure groups, charge bands and support-ticket bands, then calculated churn rates for each group in pandas and again in PostgreSQL to check the results matched.

Overall churn was 28.2%. Month-to-month customers churned at 43.5% vs 8.5% for two-year contracts, and customers in their first 6 months churned at 50.4%. Customers with more support tickets and higher bills also churned more, but those differences were smaller. I combined the top factors into a simple high-risk rule. 225 customers matched it, and 91 of them are still active.

## 3. 2-minute detailed explanation

**Problem.** Losing customers costs a subscription business money, and it is usually cheaper to keep a customer than find a new one. So I wanted to answer: what is the churn rate, which customer groups churn more, and who should the retention team look at first?

**Data.** I created a dataset of 4,057 rows for a fictional Indian telecom company. Each row is a customer with their contract, tenure, charges, services, payment method, region, segment, support tickets, usage and churn status. Churn was generated from business rules plus random noise, so the patterns are there but not perfect.

**Cleaning.** In `src/data_cleaning.py` I removed 45 exact duplicates and 12 duplicate customers that only differed in text case. I standardized values like "M", "male" and "Male". I removed 3 rows with no customer ID and 7 rows with no churn value, because I can't analyze churn without knowing the outcome. I fixed 4 negative tenure values and 7 monthly charges that had an extra zero, and I checked both fixes against total charges divided by tenure. Impossible ages were set to missing and filled with the median. The final data has 3,990 customers and no missing values.

**Analysis.** I calculated churn rate by every main column in pandas, compared churned and retained customers, looked at combinations like contract and tenure, and checked correlations. Then I wrote 20 SQL queries in PostgreSQL that give the same numbers, using GROUP BY, CASE WHEN, CTEs and window functions.

**Findings.** Contract and tenure had the biggest differences. Support tickets, charges, payment method and the student segment also showed higher churn. Region didn't make much difference.

**Report.** I designed a 3-page Power BI report (overview, drivers, retention) and wrote the DAX measures with the expected value for each one. I haven't built the .pbix file yet.

**Recommendations.** Focus on new and month-to-month customers, look into support issues, review pricing for high-bill new customers, and encourage auto-pay, testing each idea on a small group first.

## 4. Why I chose this project

Churn analysis is a common business problem in telecom, banking, SaaS and subscription companies, and it uses the skills I want to practice: cleaning, grouping, comparing rates, SQL and dashboard design. It also produces results that a business person can act on, which is the main job of a data analyst.

## 5. Why churn matters

- A customer who leaves stops paying every month, so churn directly reduces revenue.
- Getting a new customer usually costs more than keeping an existing one.
- Knowing which groups churn more helps the company spend its retention budget on the right customers.

## 6. Data cleaning process

1. Checked shape, column names and data types
2. Counted missing values and duplicates
3. Removed exact duplicate rows
4. Trimmed spaces and standardized text values
5. Validated customer IDs (format `CUST-12345`) and removed rows with no ID
6. Removed duplicate customers that appeared after standardizing
7. Removed rows with no churn value
8. Fixed negative tenure values
9. Checked outliers in age, charges, tickets and usage
10. Checked that total charges are close to monthly charges x tenure
11. Filled remaining missing values
12. Fixed data types
13. Added tenure_group, charge_band and support_ticket_band
14. Ran final checks (no missing values, unique IDs, valid ranges, churn only Yes/No)

## 7. Missing-value treatment

| Column | Missing | What I did | Why |
|---|---|---|---|
| customer_id | 3 | Removed the rows | Can't identify the customer |
| churn | 7 | Removed the rows | It's the outcome I'm analyzing, guessing it would be wrong |
| total_charges | 14 | monthly_charges x tenure_months | Total charges are roughly monthly x tenure for every other row (within 7%) |
| age | 22 + 5 invalid | Median (38) | Only 27 rows, and age is not a main factor |
| gender, payment_method, region | 18, 11, 9 | "Unknown" | Can't be worked out from other columns, and it's better to keep the rows than guess |

## 8. Duplicate handling

There were two kinds. 45 rows were exact copies, removed with `drop_duplicates()`. Another 12 customers appeared twice, but one copy had a lowercase ID and region in capitals. They only became exact duplicates after I standardized the text, which is why I standardized before checking customer_id duplicates. I confirmed every repeated ID was an exact copy after standardizing before dropping it.

## 9. Outlier handling

I used the IQR method to find unusual values, then decided case by case:

- **Monthly charges:** 7 values were about 10 times higher than total_charges / tenure (for example Rs 20,660 when the total suggested about Rs 2,114). These were typing errors with an extra zero, so I divided them by 10.
- **Age:** ages like 5, 9, 112, 135 and 150 are impossible for a customer, so I set them to missing and filled with the median.
- **Tenure:** 4 negative values. Total charges / monthly charges matched the positive number, so I removed the minus sign.
- **Support tickets:** 6 customers had 11-15 tickets. That is unusual but possible, so I kept them. IQR flagged everyone with 4+ tickets, which is too strict for count data.

## 10. Why segmentation was used

Overall churn (28.2%) is one number and doesn't tell the business where to act. Splitting customers into groups (contract, tenure group, charge band, segment) shows where churn is concentrated. For example, month-to-month customers in their first 6 months churned at 51.6%, almost double the overall rate. I used bins for tenure, charges and tickets because rates by group are easier to read and explain than a scatter of raw values.

## 11. Main churn patterns

- Contract: month-to-month 43.5%, one year 15.6%, two year 8.5%
- Tenure: 50.4% (0-6 months) down to 9.9% (49+ months)
- Support tickets: 22.2% (0) up to 37.1% (5+)
- Charges: 21.5% (under Rs 500) up to 33.8% (Rs 1,500+)
- Payment: Cash 33.3%, Auto Debit 23.8%
- Segment: Student 39.8%, Small Business 23.1%
- Region: small range, 24.3% to 31.2%

## 12. Main business insights

- Month-to-month customers are 51.1% of customers but 78.7% of churned customers.
- The first year is the riskiest period.
- Month-to-month churn stays high even after 1-2 years.
- Short-tenure customers with high bills churned at 54.9%.
- 225 customers match the high-risk rule (month-to-month, 12 months or less, 3+ tickets). 59.6% of them churned, and 91 are still active.

## 13. Recommendations

1. Review onboarding and the first-year experience.
2. Test offers to move month-to-month customers to longer contracts.
3. Find out what drives high support-ticket counts.
4. Review pricing and value for new high-bill customers.
5. Make auto-pay easier to set up.

## 14. Limitations

- The data is generated, not from a real company. The patterns come from rules I set, so the project shows the method, not real-world findings.
- It is a single snapshot. There are no dates, so I can't show churn over time or when customers left.
- There is no information on why customers left, ticket reasons, competitor offers or customer satisfaction.
- The analysis shows association, not cause. For example, customers who pick long contracts may already be more loyal.
- Many factors overlap (students are more often month-to-month, bundles have higher bills), so the group rates are not independent effects.
- The high-risk rule is a simple filter, not a prediction model, and it hasn't been tested on new data.
- The Power BI report is designed but not built yet.

## 15. Interview questions with simple answers

**1. What is churn rate and how did you calculate it?**
The share of customers who left. Churned customers / total customers = 1,126 / 3,990 = 28.2%.

**2. Why did you remove rows with missing churn instead of filling them?**
Churn is the outcome I'm studying. If I filled it, I would be making up the answer. It was only 7 rows, so removing them had almost no effect.

**3. How did you decide how to fill missing total_charges?**
In the rest of the data, total charges were always close to monthly charges x tenure (between 0.93 and 1.05 times). So that formula is a reasonable estimate for the 14 missing values.

**4. How did you find the wrong monthly charges?**
I compared monthly_charges with total_charges / tenure_months. For 7 rows the monthly value was about 10 times bigger, which points to an extra zero.

**5. Why didn't you remove all outliers?**
Not every outlier is an error. Customers with 11-15 support tickets are unusual but possible, so I kept them. I only fixed values that were clearly wrong, like a negative tenure or an age of 150.

**6. What is the difference between COUNT(*) and COUNT(column) in SQL?**
COUNT(*) counts all rows. COUNT(column) skips rows where that column is NULL.

**7. How did you calculate churn rate in SQL?**
`SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`. I multiply by 100.0 so PostgreSQL does decimal division instead of integer division.

**8. What is the difference between WHERE and HAVING?**
WHERE filters rows before grouping. HAVING filters groups after aggregation. I used HAVING COUNT(*) >= 30 to ignore very small groups.

**9. Where did you use a CTE and why?**
In the high-risk groups query, one CTE calculates the overall churn rate and another calculates each group's rate. Then I keep only groups above the overall rate. It's easier to read than nested subqueries.

**10. Where did you use window functions?**
RANK() to rank high-risk groups by churn rate, and SUM() OVER to calculate the cumulative share of customers by ticket count. Window functions add a calculation across rows without collapsing them like GROUP BY.

**11. What does the correlation of -0.29 between tenure and churn mean?**
Customers with longer tenure tend to churn less. It is a moderate negative relationship, not proof that tenure causes customers to stay.

**12. Correlation between monthly charges and churn is only 0.09, but churn rises across charge bands. Why?**
Correlation measures a straight-line relationship across all customers. The charge effect is real but small compared to the noise from other factors, so the correlation is weak even though the group averages show a steady increase.

**13. Does a month-to-month contract cause churn?**
I can't say that. Month-to-month customers churn more, but people who choose them may already be less committed. To prove cause, the company would need to test something, like offering contract upgrades to some customers and comparing.

**14. Why did you choose those tenure groups?**
The first 6 months and first year are common checkpoints in subscription businesses, and the churn rate changes most in that period. Wider groups after 2 years are enough because churn is lower and more stable there.

**15. How did you choose the charge bands?**
I looked at the distribution. The middle half of customers pay about Rs 660-1,390, so Rs 500 steps put most customers in two middle bands and leave about a fifth in the Rs 1,500+ band.

**16. What does DIVIDE do in DAX and why use it instead of "/"?**
DIVIDE handles division by zero and returns blank instead of an error, which happens when a slicer selection has no customers.

**17. What does CALCULATE do?**
It changes the filter context for a measure. For Churned Customers, CALCULATE counts rows only where churn = "Yes", on top of any slicers.

**18. Why did you use KEEPFILTERS in the High-Risk measure?**
Without it, the condition contract_type = "Month-to-month" would replace the Contract Type slicer. KEEPFILTERS keeps both, so the card respects the slicer.

**19. How did you make sure your numbers were correct?**
I calculated the main results in both pandas and PostgreSQL and checked they matched. I also wrote a validation script that checks the cleaned file (row count, no missing values, unique IDs, valid ranges) and the main KPIs.

**20. What would you do next with more time or real data?**
Get real data with dates to look at churn over time, add the reasons for support tickets and cancellations, and try a simple logistic regression to see which factors matter most when looked at together. I would also build the Power BI report and share it with the business team.
