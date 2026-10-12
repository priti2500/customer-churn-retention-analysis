"""
Generates the raw customer dataset used in this project.

The company is fictional: an Indian telecom and broadband provider.
Charges are in Indian Rupees. The data is a snapshot of customers,
where churn = "Yes" means the customer left.

Churn is built from a few business rules (contract, tenure, support
tickets, charges, payment method, usage) plus random noise, so the
patterns are there but not perfect. Some data problems are added at the
end on purpose so the cleaning step has real work to do.

Run from the project folder:
    python src/generate_data.py
"""

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 4000
OUTPUT_FILE = "data/raw_customer_data.csv"

rng = np.random.default_rng(SEED)
n = N_CUSTOMERS

# ---------- basic customer details ----------
customer_id = [f"CUST-{10001 + i}" for i in range(n)]
gender = rng.choice(["Male", "Female"], size=n, p=[0.52, 0.48])
region = rng.choice(["North", "South", "East", "West", "Central"], size=n,
                    p=[0.25, 0.23, 0.17, 0.22, 0.13])
segment = rng.choice(["Individual", "Family", "Small Business", "Student"], size=n,
                     p=[0.42, 0.28, 0.15, 0.15])

age = np.where(segment == "Student", rng.integers(18, 26, n), rng.normal(40, 12, n).round())
age = np.clip(age, 18, 79).astype(int)

# ---------- contract and tenure ----------
contract = []
for s in segment:
    if s == "Student":
        p = [0.72, 0.20, 0.08]
    elif s == "Small Business":
        p = [0.35, 0.33, 0.32]
    else:
        p = [0.52, 0.26, 0.22]
    contract.append(rng.choice(["Month-to-month", "One year", "Two year"], p=p))
contract = np.array(contract)

tenure = np.where(
    contract == "Month-to-month", rng.exponential(16, n),
    np.where(contract == "One year", rng.uniform(4, 60, n), rng.uniform(10, 72, n)),
)
tenure = np.clip(tenure.round(), 1, 72).astype(int)

# ---------- services and charges ----------
service_type = rng.choice(
    ["Mobile Only", "Broadband Only", "Broadband + TV", "Mobile + Broadband", "All-in-One"],
    size=n, p=[0.22, 0.26, 0.16, 0.22, 0.14],
)
internet = np.where(service_type == "Mobile Only", "No Internet",
                    rng.choice(["Fiber", "DSL"], size=n, p=[0.6, 0.4]))

base_price = {
    "Mobile Only": (249, 599),
    "Broadband Only": (499, 999),
    "Broadband + TV": (799, 1399),
    "Mobile + Broadband": (899, 1499),
    "All-in-One": (1299, 2199),
}
monthly = np.array([rng.uniform(*base_price[s]) for s in service_type])
monthly = monthly + np.where(internet == "Fiber", 150, 0)
monthly = monthly * np.where(segment == "Small Business", 1.2, 1.0)
monthly = monthly.round()

# total charges = monthly x tenure, with small changes for price updates and discounts
total = (monthly * tenure * rng.uniform(0.93, 1.05, n)).round(2)

payment = rng.choice(["Auto Debit", "Credit Card", "UPI", "Net Banking", "Cash"], size=n,
                     p=[0.26, 0.20, 0.27, 0.15, 0.12])

support_tickets = rng.poisson(1.3, n)
# fiber customers raise a few more tickets (installation and speed issues)
support_tickets = support_tickets + rng.binomial(1, np.where(internet == "Fiber", 0.25, 0.1))

# days the customer used the service in the last 30 days
usage = np.clip(rng.normal(19, 6, n).round(), 1, 30).astype(int)

# ---------- churn ----------
score = -1.85
score = score + np.select([contract == "Month-to-month", contract == "One year"], [0.9, -0.3], -1.1)
score = score + np.select([tenure <= 6, tenure <= 12, tenure <= 24, tenure <= 48], [0.8, 0.45, 0.1, -0.2], -0.5)
score = score + np.minimum(support_tickets, 6) * 0.22
score = score + (monthly - 1000) / 1000 * 0.45
score = score + pd.Series(payment).map(
    {"Auto Debit": -0.35, "Credit Card": -0.1, "UPI": 0.05, "Net Banking": 0.2, "Cash": 0.35}).to_numpy()
score = score + pd.Series(segment).map(
    {"Individual": 0.0, "Family": -0.15, "Small Business": -0.1, "Student": 0.3}).to_numpy()
score = score - (usage - 19) * 0.04
score = score + np.where(internet == "Fiber", 0.15, 0.0)
score = score + rng.normal(0, 0.6, n)  # behaviour not explained by the columns above

churn_prob = 1 / (1 + np.exp(-score))
churn = np.where(rng.random(n) < churn_prob, "Yes", "No")

df = pd.DataFrame({
    "customer_id": customer_id,
    "gender": gender,
    "age": age,
    "tenure_months": tenure,
    "contract_type": contract,
    "monthly_charges": monthly,
    "total_charges": total,
    "payment_method": payment,
    "service_type": service_type,
    "internet_service": internet,
    "support_tickets": support_tickets,
    "usage_frequency": usage,
    "region": region,
    "customer_segment": segment,
    "churn": churn,
}).astype(object)

# ---------- add data quality problems ----------

def pick(count):
    return rng.choice(df.index, size=count, replace=False)

# a few real high-ticket customers (outliers that are kept)
for i in pick(6):
    df.at[i, "support_tickets"] = int(rng.integers(11, 16))

# monthly charges entered with an extra zero (data entry outliers)
for i in pick(7):
    df.at[i, "monthly_charges"] = df.at[i, "monthly_charges"] * 10

# impossible ages
for i, bad_age in zip(pick(5), [5, 9, 112, 135, 150]):
    df.at[i, "age"] = bad_age

# tenure entered as a negative number
for i in pick(4):
    df.at[i, "tenure_months"] = -df.at[i, "tenure_months"]

# inconsistent text formatting
text_variants = {
    "gender": {"Male": ["male", "M", " Male"], "Female": ["female", "F", "FEMALE"]},
    "contract_type": {"Month-to-month": ["month-to-month", "Month to Month", "MONTH-TO-MONTH"],
                      "One year": ["one year", "1 Year", "One Year "],
                      "Two year": ["two year", "2 Year", "Two Year"]},
    "payment_method": {"Auto Debit": ["auto debit", "Auto-Debit"], "Credit Card": ["credit card", "CREDIT CARD"],
                       "UPI": ["upi", " UPI"], "Net Banking": ["net banking", "Netbanking"], "Cash": ["cash", "CASH "]},
    "region": {"North": ["north", "NORTH", " North "], "South": ["south", "South "],
               "East": ["east", "EAST"], "West": ["west", " West"], "Central": ["central", "CENTRAL"]},
    "churn": {"Yes": ["yes", "Y", "YES"], "No": ["no", "N", "NO "]},
}
for col, mapping in text_variants.items():
    for i in pick(60 if col != "churn" else 25):
        options = mapping.get(df.at[i, col])
        if options:
            df.at[i, col] = rng.choice(options)

# lowercase / padded customer ids
for i in pick(15):
    df.at[i, "customer_id"] = " " + df.at[i, "customer_id"].lower()

# missing values
for col, count in [("gender", 18), ("age", 22), ("total_charges", 14),
                   ("payment_method", 11), ("region", 9), ("churn", 7), ("customer_id", 3)]:
    for i in pick(count):
        df.at[i, col] = np.nan

# exact duplicate rows (same record loaded twice)
exact_dups = df.loc[pick(45)]

# same customer again, but with different text formatting
format_dups = df.loc[pick(12)].copy()
format_dups = format_dups[format_dups["customer_id"].notna()]
format_dups["customer_id"] = format_dups["customer_id"].str.strip().str.lower()
format_dups["region"] = format_dups["region"].str.upper()

df = pd.concat([df, exact_dups, format_dups], ignore_index=True)
df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
