# Business Questions

Answers are from `src/analysis.py` and `sql/churn_queries.sql`. Both give the same numbers. The dataset is synthetic, so the answers describe patterns in the generated data. "Q" refers to the query number in the SQL file.

**1. What is the overall churn rate?**
28.2%. 1,126 of 3,990 customers churned and 2,864 were retained (71.8% retention). (Q1-Q5)

**2. Which contract type has the highest churn?**
Month-to-month, at 43.5%. One-year contracts had 15.6% and two-year contracts 8.5%. (Q6)

**3. Do newer customers churn more?**
Yes. Customers in their first 6 months had a 50.4% churn rate, and it drops in every tenure group after that, down to 9.9% for customers with 49+ months. Churned customers had an average tenure of 16.8 months vs 29.2 months for retained customers. (Q7, Q16)

**4. Are higher monthly charges associated with churn?**
Somewhat. Churn rises from 21.5% for bills under Rs 500 to 33.8% for bills of Rs 1,500 or more. Churned customers paid Rs 1,151 a month on average vs Rs 1,048 for retained customers. The correlation is weak (0.09), so charges are a smaller factor than contract and tenure. (Q9, Q15)

**5. Which payment methods show higher churn?**
Cash (33.3%) and Net Banking (32.4%). Auto Debit (23.8%) and Credit Card (25.6%) were the lowest. (Q8)

**6. Which service types have higher churn?**
All-in-One (34.8%) and Mobile + Broadband (32.9%). Mobile Only was lowest at 22.6%. These bundles also have the highest average bills, so this overlaps with question 4. Fiber customers churned more than DSL customers (31.4% vs 27.6%). (Q10, Q11)

**7. Do customers with more support tickets churn more?**
Yes. 22.2% of customers with no tickets churned, compared with 35.7% for 3-4 tickets and 37.1% for 5+ tickets. The 5+ group is small (70 customers). (Q14, Q19)

**8. Which customer segments have the highest churn?**
Students, at 39.8%. Individual was 28.9%, Family 24.1% and Small Business 23.1%. Students are more often on month-to-month contracts (68.3%), but even within month-to-month, students churned more (50.1%) than the other segments. (Q13)

**9. Which regions have higher churn?**
South (31.2%) and North (28.6%) are a little above average, and East is lowest (24.3%). The gap between regions is smaller than for contract or tenure. (Q12)

**10. Which customer groups should management review first?**
- Month-to-month customers in their first 12 months with 3+ support tickets: 225 customers, 59.6% churned, 91 still active. (Q17b)
- Customers with 12 months or less and a bill of Rs 1,500 or more: 237 customers, 54.9% churned vs 26.5% for everyone else. (Q18)
- By number of customers lost, Individual customers on month-to-month contracts: 379 churned, 33.7% of all churned customers. (Q20)
