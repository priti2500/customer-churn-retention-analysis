-- Customer churn analysis queries (PostgreSQL)
-- Table: customer_churn (see create_table.sql)
-- Run: psql -d churn_db -f sql/churn_queries.sql


-- 1. Total customers
SELECT COUNT(*) AS total_customers
FROM customer_churn;


-- 2. Churned customers
SELECT COUNT(*) AS churned_customers
FROM customer_churn
WHERE churn = 'Yes';


-- 3. Retained customers
SELECT COUNT(*) AS retained_customers
FROM customer_churn
WHERE churn = 'No';


-- 4. Overall churn rate
SELECT ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn;


-- 5. Retention rate
SELECT ROUND(100.0 * SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) / COUNT(*), 1) AS retention_rate_pct
FROM customer_churn;


-- 6. Churn by contract type (with retention rate for the Power BI retention page)
SELECT contract_type,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct,
       ROUND(100.0 * SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) / COUNT(*), 1) AS retention_rate_pct
FROM customer_churn
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;


-- 7. Churn by tenure group (ordered from newest to oldest customers)
SELECT tenure_group,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct,
       ROUND(100.0 * SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) / COUNT(*), 1) AS retention_rate_pct
FROM customer_churn
GROUP BY tenure_group
ORDER BY MIN(tenure_months);


-- 8. Churn by payment method
SELECT payment_method,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;


-- 9. Churn by monthly charge band (Rs)
SELECT charge_band,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY charge_band
ORDER BY MIN(monthly_charges);


-- 10. Churn by service type
SELECT service_type,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY service_type
ORDER BY churn_rate_pct DESC;


-- 11. Churn by internet service
SELECT internet_service,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;


-- 12. Churn by region
SELECT region,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY region
ORDER BY churn_rate_pct DESC;


-- 13. Churn by customer segment
SELECT customer_segment,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY customer_segment
ORDER BY churn_rate_pct DESC;


-- 14. Churn by support ticket band
SELECT support_ticket_band,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY support_ticket_band
ORDER BY MIN(support_tickets);


-- 15. Average monthly charges: churned vs retained
SELECT churn,
       COUNT(*) AS customers,
       ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM customer_churn
GROUP BY churn;


-- 16. Average tenure: churned vs retained
SELECT churn,
       ROUND(AVG(tenure_months), 1) AS avg_tenure_months
FROM customer_churn
GROUP BY churn;


-- 17a. High-risk customer groups
-- Contract + tenure + ticket combinations with at least 30 customers
-- and a churn rate above the overall rate.
WITH overall AS (
    SELECT AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0 END) AS rate
    FROM customer_churn
),
groups AS (
    SELECT contract_type,
           tenure_group,
           support_ticket_band,
           COUNT(*) AS customers,
           SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
           AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0 END) AS rate
    FROM customer_churn
    GROUP BY contract_type, tenure_group, support_ticket_band
    HAVING COUNT(*) >= 30
)
SELECT RANK() OVER (ORDER BY g.rate DESC) AS risk_rank,
       g.contract_type,
       g.tenure_group,
       g.support_ticket_band,
       g.customers,
       g.churned,
       ROUND(100 * g.rate, 1) AS churn_rate_pct
FROM groups g, overall o
WHERE g.rate > o.rate
ORDER BY risk_rank
LIMIT 10;


-- 17b. Customers matching the high-risk rule used in Power BI
-- Rule: Month-to-month contract, tenure 12 months or less, 3+ support tickets
SELECT COUNT(*) AS high_risk_customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       SUM(CASE WHEN churn = 'No' THEN 1 ELSE 0 END) AS still_active,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
WHERE contract_type = 'Month-to-month'
  AND tenure_months <= 12
  AND support_tickets >= 3;


-- 18. Short-tenure + high-charge customers
-- Tenure 12 months or less and monthly charges of Rs 1,500 or more,
-- compared with everyone else
SELECT CASE WHEN tenure_months <= 12 AND monthly_charges >= 1500
            THEN 'Short tenure + high charges'
            ELSE 'All other customers' END AS customer_group,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM customer_churn
GROUP BY 1
ORDER BY churn_rate_pct DESC;


-- 19. Customers with high support-ticket counts
-- Churn by exact ticket count, plus the running share of customers
SELECT support_tickets,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct,
       ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY support_tickets) / SUM(COUNT(*)) OVER (), 1) AS cumulative_customers_pct
FROM customer_churn
GROUP BY support_tickets
ORDER BY support_tickets;


-- 20. Top churn segments management should review
-- Segment + contract groups ranked by how many customers were lost,
-- with each group's share of all churned customers
WITH seg AS (
    SELECT customer_segment,
           contract_type,
           COUNT(*) AS customers,
           SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned
    FROM customer_churn
    GROUP BY customer_segment, contract_type
    HAVING COUNT(*) >= 50
)
SELECT customer_segment,
       contract_type,
       customers,
       churned,
       ROUND(100.0 * churned / customers, 1) AS churn_rate_pct,
       ROUND(100.0 * churned / (SELECT COUNT(*) FROM customer_churn WHERE churn = 'Yes'), 1) AS share_of_all_churned_pct
FROM seg
ORDER BY churned DESC
LIMIT 5;
