# Insights and Recommendations

All numbers come from `src/analysis.py` and were checked against `sql/churn_queries.sql` (query numbers in brackets). The dataset is synthetic, so these are patterns in the generated data, not results from a real company. They show which groups churn more, not why they churn.

## Insights

**1. 28.2% of customers churned.**
1,126 of 3,990 customers left and 2,864 stayed. (Q1-Q5)

**2. Contract type shows the biggest difference.**
Month-to-month customers had a 43.5% churn rate, compared with 15.6% for one-year and 8.5% for two-year contracts. Month-to-month customers were 51.1% of all customers but 78.7% of churned customers. (Q6)

**3. Churn is highest in the first 6 months and falls with tenure.**
The churn rate was 50.4% for 0-6 months, 39.5% for 7-12 months, 29.4% for 13-24 months, 17.7% for 25-48 months and 9.9% for 49+ months. Tenure has the strongest correlation with churn of the numeric columns (-0.29). (Q7, Q16)

**4. Month-to-month churn stays high even after the first year.**
Month-to-month customers with 13-24 months of tenure still had a 43.4% churn rate, and those with 25-48 months had 31.4%. Both are higher than any one-year or two-year group with at least 50 customers (the highest of those was 22.9%). (Python section 21)

**5. More support tickets go with higher churn.**
Churn was 22.2% with no tickets, 28.0% with 1-2, 35.7% with 3-4 and 37.1% with 5+. Among month-to-month customers, 3-4 tickets meant a 54.4% churn rate vs 34.3% with no tickets. The 6 customers with 11+ tickets did not churn, but that group is too small to read anything into. (Q14, Q19)

**6. Higher bills are linked to somewhat higher churn.**
Churn rose from 21.5% (under Rs 500) to 33.8% (Rs 1,500+). The pattern is clear but the correlation is weak (0.09). Customers with 12 months or less and a bill of Rs 1,500+ had a 54.9% churn rate (237 customers), about double the 26.5% of all other customers. (Q9, Q18)

**7. Customers paying by Cash or Net Banking churned more than Auto Debit customers.**
Cash was 33.3% and Net Banking 32.4%, compared with 23.8% for Auto Debit and 25.6% for Credit Card. All payment methods have a similar share of month-to-month customers (50-52%), so contract mix doesn't explain this gap. (Q8)

**8. Students had the highest churn of any segment (39.8%).**
Individual was 28.9%, Family 24.1% and Small Business 23.1%. Part of this is because 68.3% of students are on month-to-month contracts, but within month-to-month students still churned more (50.1% vs 37.2%-44.7% for other segments). (Q13)

**9. Bundles with higher bills had higher churn.**
All-in-One (34.8%) and Mobile + Broadband (32.9%) churned more than Mobile Only (22.6%). All-in-One also has the highest average bill (about Rs 1,881), so this overlaps with insight 6. Fiber customers churned more than DSL (31.4% vs 27.6%). (Q10, Q11)

**10. Region and usage show smaller differences.**
Region churn ranged from 24.3% (East) to 31.2% (South). Customers who used the service 1-10 days in the last month churned at 34.8%, compared with 24.6% for 21-30 days. Both are weaker patterns than contract or tenure. (Q12, Python section 20b)

## Recommendations

These are suggestions for what to look into next. The data shows which groups churn more, so any change should be tested on a small group first to see if it actually reduces churn.

1. **Review the first-year experience for new customers.** Churn is 50.4% in the first 6 months and 39.5% in months 7-12. Checking in with new customers or reviewing onboarding is a reasonable place to start.

2. **Offer month-to-month customers a reason to move to a longer contract.** Month-to-month customers make up 78.7% of churned customers. A discount or benefit for switching to a one-year plan could be tested, keeping in mind that customers who choose longer contracts may already be more loyal.

3. **Look into why customers raise many support tickets.** Churn rises with ticket count, especially for month-to-month customers. The data does not include ticket reasons, so the next step is to check what these tickets are about (for example, Fiber installation or speed issues).

4. **Check pricing and value for high-bill customers, especially new ones.** Short-tenure customers paying Rs 1,500+ churned at 54.9%. Reviewing whether these plans match what customers expect could help.

5. **Encourage automatic payments.** Auto Debit customers churned at 23.8% vs 33.3% for Cash. Making auto-pay easy to set up is low cost, but the gap may partly reflect the type of customer who chooses auto-pay.

The retention team could start with the 91 customers who match the high-risk rule (month-to-month, 12 months or less, 3+ tickets) and are still active.
