"""
Cleans data/raw_customer_data.csv and saves data/cleaned_customer_data.csv.

Each step prints what it found so the output can be checked.

Run from the project folder:
    python src/data_cleaning.py
"""

import numpy as np
import pandas as pd

RAW_FILE = "data/raw_customer_data.csv"
CLEAN_FILE = "data/cleaned_customer_data.csv"


def section(title):
    print(f"\n=== {title} ===")


df = pd.read_csv(RAW_FILE)

section("1. Shape")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

section("2. Columns and data types")
print(df.dtypes)

section("3. Missing values")
print(df.isna().sum()[df.isna().sum() > 0])

section("4. Duplicates")
print("Exact duplicate rows:", df.duplicated().sum())

df = df.drop_duplicates().copy()
print("Rows after removing exact duplicates:", len(df))

# Text is standardized before the customer_id duplicate check, because some
# duplicate customers only differ in text case.
section("5. Standardize categorical values")
text_cols = ["customer_id", "gender", "contract_type", "payment_method", "service_type",
             "internet_service", "region", "customer_segment", "churn"]
for col in text_cols:
    df[col] = df[col].str.strip()

print("Before:")
for col in ["gender", "contract_type", "payment_method", "region", "churn"]:
    print(f"  {col}: {sorted(df[col].dropna().unique())}")

df["customer_id"] = df["customer_id"].str.upper()
df["gender"] = df["gender"].str.title().replace({"M": "Male", "F": "Female"})
df["contract_type"] = df["contract_type"].str.lower().map({
    "month-to-month": "Month-to-month", "month to month": "Month-to-month",
    "one year": "One year", "1 year": "One year",
    "two year": "Two year", "2 year": "Two year",
})
df["payment_method"] = df["payment_method"].str.lower().map({
    "auto debit": "Auto Debit", "auto-debit": "Auto Debit",
    "credit card": "Credit Card", "upi": "UPI",
    "net banking": "Net Banking", "netbanking": "Net Banking", "cash": "Cash",
})
df["region"] = df["region"].str.title()
df["churn"] = df["churn"].str.upper().map({"YES": "Yes", "Y": "Yes", "NO": "No", "N": "No"})

print("After:")
for col in ["gender", "contract_type", "payment_method", "region", "churn"]:
    print(f"  {col}: {sorted(df[col].dropna().unique())}")

section("6. Validate customer IDs")
print("Missing customer_id:", df["customer_id"].isna().sum())
df = df[df["customer_id"].notna()].copy()
valid_id = df["customer_id"].str.match(r"^CUST-\d{5}$")
print("IDs not in CUST-12345 format:", (~valid_id).sum())
df = df[valid_id].copy()

section("7. Duplicate customer records")
dup_ids = df["customer_id"].duplicated(keep=False)
print("Rows sharing a customer_id:", dup_ids.sum())
print("Of these, exact copies after standardizing text:", df.duplicated().sum())
df = df.drop_duplicates(subset="customer_id", keep="first").copy()
print("Rows after removing duplicate customers:", len(df))

section("8. Validate churn")
print("Missing churn:", df["churn"].isna().sum(), "-> removed (the target value is unknown)")
df = df[df["churn"].notna()].copy()
print(df["churn"].value_counts())

section("9. Validate tenure")
neg = df["tenure_months"] < 0
print("Negative tenure values:", neg.sum())
# total_charges / monthly_charges should be close to tenure; this confirms the sign was the only problem
check = df.loc[neg, ["customer_id", "tenure_months", "monthly_charges", "total_charges"]].copy()
check["implied_tenure"] = (check["total_charges"] / check["monthly_charges"]).round(1)
print(check.to_string(index=False))
df.loc[neg, "tenure_months"] = df.loc[neg, "tenure_months"].abs()
print("Tenure range after fix:", df["tenure_months"].min(), "to", df["tenure_months"].max())

section("10. Outliers")
for col in ["age", "tenure_months", "monthly_charges", "support_tickets", "usage_frequency"]:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    count = ((df[col] < low) | (df[col] > high)).sum()
    print(f"{col}: IQR range {low:.1f} to {high:.1f}, outside range: {count}")

# Age: customers must be adults, and ages above 100 are entry errors
bad_age = (df["age"] < 18) | (df["age"] > 100)
print("\nInvalid ages:", sorted(df.loc[bad_age, "age"].astype(int)), "-> set to missing")
df.loc[bad_age, "age"] = np.nan

# Monthly charges: the highest real plan is around Rs 2,800. Some values are
# about 10x what total_charges / tenure_months suggests (extra zero typed).
implied_monthly = df["total_charges"] / df["tenure_months"]
high_charge = (df["monthly_charges"] > 5000) | (df["monthly_charges"] / implied_monthly > 5)
check = df.loc[high_charge, ["customer_id", "monthly_charges", "total_charges", "tenure_months"]].copy()
check["total_div_tenure"] = implied_monthly[high_charge].round(0)
print("\nMonthly charges that don't match total_charges / tenure:")
print(check.to_string(index=False))
df.loc[high_charge, "monthly_charges"] = df.loc[high_charge, "monthly_charges"] / 10
print("These were divided by 10. New max:", df["monthly_charges"].max())

# Note: IQR flags every customer with 4+ tickets, which is too strict for a
# count column. Only the very high values are looked at here.
# Support tickets: 11+ tickets is unusual but possible, so these rows are kept
print("\nCustomers with more than 10 support tickets (kept):", (df["support_tickets"] > 10).sum())

section("11. Validate charges")
print("Missing total_charges:", df["total_charges"].isna().sum(),
      "-> filled with monthly_charges x tenure_months")
df["total_charges"] = df["total_charges"].fillna(df["monthly_charges"] * df["tenure_months"]).round(2)
ratio = df["total_charges"] / (df["monthly_charges"] * df["tenure_months"])
print(f"total / (monthly x tenure): min {ratio.min():.2f}, max {ratio.max():.2f}")
print("Rows where the ratio is outside 0.85-1.15:", ((ratio < 0.85) | (ratio > 1.15)).sum())
print("Non-positive charges:", ((df["monthly_charges"] <= 0) | (df["total_charges"] <= 0)).sum())

section("12. Missing value treatment")
median_age = df["age"].median()
print("Missing age (incl. invalid ages):", df["age"].isna().sum(), f"-> filled with median age {median_age:.0f}")
df["age"] = df["age"].fillna(median_age)
for col in ["gender", "payment_method", "region"]:
    print(f"Missing {col}:", df[col].isna().sum(), "-> 'Unknown'")
    df[col] = df[col].fillna("Unknown")

section("13. Data types")
for col in ["age", "tenure_months", "support_tickets", "usage_frequency"]:
    df[col] = df[col].astype(int)
print(df.dtypes)

# 14. Derived columns
df["tenure_group"] = pd.cut(df["tenure_months"], bins=[0, 6, 12, 24, 48, 72],
                            labels=["0-6 months", "7-12 months", "13-24 months",
                                    "25-48 months", "49+ months"])
# Rs 500 steps. The quartiles are about 660, 1060 and 1390, so the two middle
# bands hold most customers and 1500+ is roughly the top fifth.
df["charge_band"] = pd.cut(df["monthly_charges"], bins=[0, 499, 999, 1499, np.inf],
                           labels=["Under 500", "500-999", "1000-1499", "1500+"])
df["support_ticket_band"] = pd.cut(df["support_tickets"], bins=[-1, 0, 2, 4, np.inf],
                                   labels=["0", "1-2", "3-4", "5+"])
section("14. Derived columns")
for col in ["tenure_group", "charge_band", "support_ticket_band"]:
    print(df[col].value_counts(sort=False).to_string(), "\n")

section("15. Final checks")
checks = {
    "no missing values": df.isna().sum().sum() == 0,
    "no duplicate customer_id": df["customer_id"].is_unique,
    "all IDs valid": df["customer_id"].str.match(r"^CUST-\d{5}$").all(),
    "churn is Yes/No": df["churn"].isin(["Yes", "No"]).all(),
    "age 18-100": df["age"].between(18, 100).all(),
    "tenure 1-72": df["tenure_months"].between(1, 72).all(),
    "monthly charges under 3000": (df["monthly_charges"] < 3000).all(),
}
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {name}")
assert all(checks.values()), "A final check failed"

print(f"\nFinal shape: {df.shape}")
df.to_csv(CLEAN_FILE, index=False)
print(f"Saved {CLEAN_FILE}")
