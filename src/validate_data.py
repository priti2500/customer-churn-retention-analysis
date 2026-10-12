"""
Checks the cleaned file and the main KPIs used in the README and docs.

Run from the project folder (after data_cleaning.py):
    python src/validate_data.py
"""

import pandas as pd

df = pd.read_csv("data/cleaned_customer_data.csv")
raw = pd.read_csv("data/raw_customer_data.csv")

checks = {
    "raw file has 4,057 rows": len(raw) == 4057,
    "cleaned file has 3,990 rows": len(df) == 3990,
    "no missing values": df.isna().sum().sum() == 0,
    "no duplicate rows": not df.duplicated().any(),
    "customer_id is unique": df["customer_id"].is_unique,
    "customer_id format CUST-12345": df["customer_id"].str.match(r"^CUST-\d{5}$").all(),
    "churn is Yes or No": df["churn"].isin(["Yes", "No"]).all(),
    "contract types": set(df["contract_type"]) == {"Month-to-month", "One year", "Two year"},
    "age between 18 and 100": df["age"].between(18, 100).all(),
    "tenure between 1 and 72": df["tenure_months"].between(1, 72).all(),
    "monthly charges between 200 and 3000": df["monthly_charges"].between(200, 3000).all(),
    "total charges close to monthly x tenure":
        (df["total_charges"] / (df["monthly_charges"] * df["tenure_months"])).between(0.9, 1.1).all(),
}

churned = (df["churn"] == "Yes").sum()
high_risk = df[(df["contract_type"] == "Month-to-month") & (df["tenure_months"] <= 12)
               & (df["support_tickets"] >= 3)]

# values quoted in README.md, docs/ and powerbi/dax_measures.md
kpis = {
    "Total Customers": (len(df), 3990),
    "Churned Customers": (churned, 1126),
    "Retained Customers": (len(df) - churned, 2864),
    "Churn Rate %": (round(churned / len(df) * 100, 1), 28.2),
    "Retention Rate %": (round((len(df) - churned) / len(df) * 100, 1), 71.8),
    "Average Tenure": (round(df["tenure_months"].mean(), 1), 25.7),
    "Average Monthly Charges": (round(df["monthly_charges"].mean(), 2), 1077.10),
    "High-Risk Customers": (len(high_risk), 225),
    "High-Risk Active Customers": ((high_risk["churn"] == "No").sum(), 91),
}
for name, (actual, expected) in kpis.items():
    checks[f"{name} = {expected}"] = actual == expected

for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {name}")

failed = [name for name, passed in checks.items() if not passed]
print(f"\n{len(checks) - len(failed)} of {len(checks)} checks passed")
if failed:
    raise SystemExit(1)
