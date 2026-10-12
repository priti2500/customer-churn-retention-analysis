"""
Creates the charts used in the README and saves them to images/.

Run from the project folder (after data_cleaning.py):
    python src/visualization.py
"""

import matplotlib
matplotlib.use("Agg")  # save files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

BLUE = "#2a78d6"     # retained / single-series bars
ORANGE = "#eb6834"   # churned
GRAY = "#52514e"

sns.set_theme(style="white", font_scale=0.95)
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

df = pd.read_csv("data/cleaned_customer_data.csv")
df["churn_flag"] = (df["churn"] == "Yes").astype(int)
overall_rate = df["churn_flag"].mean() * 100


def churn_rate_chart(col, title, filename, order=None):
    rates = df.groupby(col)["churn_flag"].mean().mul(100)
    rates = rates.reindex(order) if order else rates.sort_values(ascending=False)
    rates = rates.drop("Unknown", errors="ignore")  # too few rows to compare

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(rates.index.astype(str), rates.values, color=BLUE, width=0.6)
    ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    ax.axhline(overall_rate, color=GRAY, linestyle="--", linewidth=1,
               label=f"Overall churn rate ({overall_rate:.1f}%)")
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_title(title, loc="left", fontsize=12)
    ax.set_xlabel("")
    ax.set_ylabel("Churn rate (%)")
    ax.set_ylim(0, rates.max() * 1.25)
    plt.xticks(rotation=0 if len(rates) <= 5 else 15)
    fig.tight_layout()
    fig.savefig(f"images/{filename}", dpi=120)
    plt.close(fig)


# 1. churn distribution
counts = df["churn"].value_counts().reindex(["No", "Yes"])
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.bar(["Retained", "Churned"], counts.values, color=[BLUE, ORANGE], width=0.5)
labels = [f"{v:,} ({v / len(df) * 100:.1f}%)" for v in counts.values]
ax.bar_label(bars, labels=labels, padding=3, fontsize=9)
ax.set_title("Churn distribution", loc="left", fontsize=12)
ax.set_ylabel("Customers")
ax.set_ylim(0, counts.max() * 1.15)
fig.tight_layout()
fig.savefig("images/01_churn_distribution.png", dpi=120)
plt.close(fig)

# 2-9. churn rate by category
churn_rate_chart("contract_type", "Churn rate by contract type", "02_churn_by_contract.png",
                 ["Month-to-month", "One year", "Two year"])
churn_rate_chart("tenure_group", "Churn rate by tenure group", "03_churn_by_tenure.png",
                 ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49+ months"])
churn_rate_chart("payment_method", "Churn rate by payment method", "04_churn_by_payment.png")
churn_rate_chart("charge_band", "Churn rate by monthly charge band (Rs)", "05_churn_by_charge_band.png",
                 ["Under 500", "500-999", "1000-1499", "1500+"])
churn_rate_chart("service_type", "Churn rate by service type", "06_churn_by_service.png")
churn_rate_chart("region", "Churn rate by region", "07_churn_by_region.png")
churn_rate_chart("customer_segment", "Churn rate by customer segment", "08_churn_by_segment.png")
df["support_ticket_band"] = df["support_ticket_band"].astype(str)
churn_rate_chart("support_ticket_band", "Churn rate by number of support tickets",
                 "09_churn_by_support_tickets.png", ["0", "1-2", "3-4", "5+"])

# 10-11. distributions, split by churn
for col, title, filename, binwidth in [
    ("monthly_charges", "Monthly charges by churn status", "10_monthly_charges_distribution.png", 100),
    ("tenure_months", "Tenure by churn status", "11_tenure_distribution.png", 3),
]:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(data=df, x=col, hue="churn", hue_order=["No", "Yes"], binwidth=binwidth,
                 palette={"No": BLUE, "Yes": ORANGE}, multiple="stack", alpha=0.85, ax=ax)
    ax.get_legend().set_title("Churned")
    ax.set_title(title, loc="left", fontsize=12)
    ax.set_xlabel("Monthly charges (Rs)" if col == "monthly_charges" else "Tenure (months)")
    ax.set_ylabel("Customers")
    fig.tight_layout()
    fig.savefig(f"images/{filename}", dpi=120)
    plt.close(fig)

# 12. correlation heatmap
num_cols = ["age", "tenure_months", "monthly_charges", "total_charges",
            "support_tickets", "usage_frequency", "churn_flag"]
cmap = LinearSegmentedColormap.from_list("blue_orange", [BLUE, "#f0efec", ORANGE])
fig, ax = plt.subplots(figsize=(7.5, 6))
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)  # hide the repeated upper half
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=cmap, vmin=-1, vmax=1,
            linewidths=2, linecolor="white", ax=ax)
ax.set_title("Correlation between numeric columns", loc="left", fontsize=12)
fig.tight_layout()
fig.savefig("images/12_correlation_heatmap.png", dpi=120)
plt.close(fig)

print("Saved 12 charts to images/")
