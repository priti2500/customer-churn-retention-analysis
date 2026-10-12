"""
Churn analysis on the cleaned data using pandas.

Run from the project folder (after data_cleaning.py):
    python src/analysis.py
"""

import pandas as pd

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 30)

df = pd.read_csv("data/cleaned_customer_data.csv")
df["churn_flag"] = (df["churn"] == "Yes").astype(int)

# keep the bins in their natural order instead of alphabetical
order = {
    "tenure_group": ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49+ months"],
    "charge_band": ["Under 500", "500-999", "1000-1499", "1500+"],
    "support_ticket_band": ["0", "1-2", "3-4", "5+"],
}
df["support_ticket_band"] = df["support_ticket_band"].astype(str)
for col, values in order.items():
    df[col] = pd.Categorical(df[col], categories=values, ordered=True)


def churn_by(col):
    table = df.groupby(col, observed=True).agg(
        customers=("customer_id", "count"),
        churned=("churn_flag", "sum"),
    )
    table["churn_rate_%"] = (table["churned"] / table["customers"] * 100).round(1)
    return table


def section(title):
    print(f"\n=== {title} ===")


section("1. Shape")
print(df.shape)

section("2. head()")
print(df.head())

section("3. info()")
df.info()

section("4. describe()")
print(df.describe().round(2))

section("5. Missing values")
print(df.isna().sum().sum(), "missing values in the cleaned data")

section("6. Duplicates")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate customer IDs:", df["customer_id"].duplicated().sum())

section("7-8. Churn and retention rate")
total = len(df)
churned = df["churn_flag"].sum()
print(f"Total customers: {total}")
print(f"Churned: {churned}, Retained: {total - churned}")
print(f"Churn rate: {churned / total * 100:.1f}%")
print(f"Retention rate: {(total - churned) / total * 100:.1f}%")

group_cols = [
    ("9", "contract_type"), ("10", "tenure_group"), ("11", "payment_method"),
    ("12", "charge_band"), ("13", "service_type"), ("14", "internet_service"),
    ("15", "region"), ("16", "customer_segment"), ("17", "support_ticket_band"),
]
for num, col in group_cols:
    section(f"{num}. Churn by {col}")
    table = churn_by(col)
    if col not in order:
        table = table.sort_values("churn_rate_%", ascending=False)
    print(table)

section("18-20. Churned vs retained averages")
compare = df.groupby("churn")[["monthly_charges", "tenure_months", "usage_frequency",
                               "support_tickets", "age", "total_charges"]].mean().round(1)
print(compare)
print("\nMedian monthly charges:")
print(df.groupby("churn")["monthly_charges"].median())

section("20b. Churn by usage frequency (days used in last 30)")
df["usage_band"] = pd.cut(df["usage_frequency"], bins=[0, 10, 20, 30],
                          labels=["1-10 days", "11-20 days", "21-30 days"])
print(churn_by("usage_band"))

section("21. Customer groups with higher churn (contract x tenure, min 50 customers)")
combo = df.groupby(["contract_type", "tenure_group"], observed=True).agg(
    customers=("customer_id", "count"), churned=("churn_flag", "sum"))
combo["churn_rate_%"] = (combo["churned"] / combo["customers"] * 100).round(1)
print(combo[combo["customers"] >= 50].sort_values("churn_rate_%", ascending=False).head(8))

section("21b. Contract x support ticket band (min 50 customers)")
combo = df.groupby(["contract_type", "support_ticket_band"], observed=True).agg(
    customers=("customer_id", "count"), churned=("churn_flag", "sum"))
combo["churn_rate_%"] = (combo["churned"] / combo["customers"] * 100).round(1)
print(combo[combo["customers"] >= 50].sort_values("churn_rate_%", ascending=False).head(8))

section("21c. Short tenure (12 months or less) and high charges (1500+)")
short_high = df[(df["tenure_months"] <= 12) & (df["monthly_charges"] >= 1500)]
print(f"Customers: {len(short_high)}, churned: {short_high['churn_flag'].sum()}, "
      f"churn rate: {short_high['churn_flag'].mean() * 100:.1f}%")

section("21d. High-risk rule: Month-to-month, tenure 12 months or less, 3+ tickets")
high_risk = (df["contract_type"] == "Month-to-month") & (df["tenure_months"] <= 12) & (df["support_tickets"] >= 3)
hr = df[high_risk]
print(f"Customers matching the rule: {len(hr)}, churned: {hr['churn_flag'].sum()}, "
      f"churn rate: {hr['churn_flag'].mean() * 100:.1f}%")
print(f"Still active (retained) customers matching the rule: {(hr['churn'] == 'No').sum()}")

section("22. Retained vs churned customer profile (% of each group)")
profile = pd.DataFrame({
    "month_to_month_%": df.groupby("churn")["contract_type"].apply(lambda s: (s == "Month-to-month").mean() * 100),
    "tenure_12_or_less_%": df.groupby("churn")["tenure_months"].apply(lambda s: (s <= 12).mean() * 100),
    "3plus_tickets_%": df.groupby("churn")["support_tickets"].apply(lambda s: (s >= 3).mean() * 100),
    "auto_debit_%": df.groupby("churn")["payment_method"].apply(lambda s: (s == "Auto Debit").mean() * 100),
    "student_%": df.groupby("churn")["customer_segment"].apply(lambda s: (s == "Student").mean() * 100),
}).round(1)
print(profile)

section("22b. Checking overlaps between groups")
share = pd.DataFrame({
    "share_of_customers_%": df["contract_type"].value_counts(normalize=True) * 100,
    "share_of_churned_%": df.loc[df["churn"] == "Yes", "contract_type"].value_counts(normalize=True) * 100,
}).round(1)
print(share)
print("\nContract mix by segment (%):")
print((pd.crosstab(df["customer_segment"], df["contract_type"], normalize="index") * 100).round(1))
print("\nChurn rate by segment, month-to-month customers only:")
m2m = df[df["contract_type"] == "Month-to-month"]
print((m2m.groupby("customer_segment")["churn_flag"].mean() * 100).round(1))
print("\nShare of month-to-month customers by payment method (%):")
print((df.groupby("payment_method")["contract_type"].apply(lambda s: (s == "Month-to-month").mean()) * 100).round(1))
print("\nAverage monthly charges by service type:")
print(df.groupby("service_type")["monthly_charges"].mean().round(0))

section("23. Correlation (numeric columns)")
num_cols = ["age", "tenure_months", "monthly_charges", "total_charges",
            "support_tickets", "usage_frequency", "churn_flag"]
corr = df[num_cols].corr().round(2)
print(corr)
print("\nCorrelation with churn_flag:")
print(corr["churn_flag"].drop("churn_flag").sort_values())
