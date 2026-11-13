
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Load the cleaned dataset
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Clean_Dataset.xlsx"
OUTPUT_DIR = BASE_DIR / "Visualisation_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Clean_Dataset.xlsx was not found. Run data_cleaning.py first "
        "and keep this script in the same project folder."
    )

df = pd.read_excel(INPUT_FILE)

required_columns = [
    "Blood Group", "Age", "Gender", "Place", "Donation Status",
    "Donation Count", "Blood Bank", "Donor Availability"
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Convert numeric columns safely
for col in ["Age", "Donation Count", "Distance (km)"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# A consistent chart style
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "axes.titlesize": 15,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

def save_chart(filename):
    """Save the current chart and close it."""
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Created: {filename}")


# -------------------------------------------------
# 2. Donor count by blood group
# -------------------------------------------------
blood_counts = df["Blood Group"].fillna("Unknown").value_counts()
plt.figure()
blood_counts.plot(kind="bar")
plt.title("Donor Records by Blood Group")
plt.xlabel("Blood Group")
plt.ylabel("Number of Donor Records")
plt.xticks(rotation=0)
save_chart("blood_group_distribution.png")


# -------------------------------------------------
# 3. Donor distribution by gender
# -------------------------------------------------
gender_counts = df["Gender"].fillna("Unknown").value_counts()
plt.figure()
gender_counts.plot(kind="bar")
plt.title("Donor Records by Gender")
plt.xlabel("Gender")
plt.ylabel("Number of Donor Records")
plt.xticks(rotation=0)
save_chart("gender_distribution.png")


# -------------------------------------------------
# 4. Donor age distribution
# -------------------------------------------------
age_data = df["Age"].dropna()
plt.figure()
plt.hist(age_data, bins=10, edgecolor="black")
plt.title("Age Distribution of Donor Records")
plt.xlabel("Age (years)")
plt.ylabel("Number of Donor Records")
save_chart("age_distribution.png")


# -------------------------------------------------
# 5. Donation status distribution
# -------------------------------------------------
status_counts = df["Donation Status"].fillna("Unknown").value_counts()
plt.figure()
status_counts.plot(kind="bar")
plt.title("Donation Status Distribution")
plt.xlabel("Donation Status")
plt.ylabel("Number of Donor Records")
plt.xticks(rotation=20, ha="right")
save_chart("donation_status_distribution.png")


# -------------------------------------------------
# 6. Donor availability distribution
# -------------------------------------------------
availability_counts = (
    df["Donor Availability"].fillna("Unknown").value_counts()
)
plt.figure()
availability_counts.plot(kind="pie", autopct="%1.1f%%", startangle=90)
plt.title("Donor Availability Distribution")
plt.ylabel("")
save_chart("donor_availability.png")


# -------------------------------------------------
# 7. Top 10 places by donor record count
# -------------------------------------------------
place_counts = df["Place"].fillna("Unknown").value_counts().head(10)
plt.figure(figsize=(11, 6))
place_counts.sort_values().plot(kind="barh")
plt.title("Top 10 Places by Donor Records")
plt.xlabel("Number of Donor Records")
plt.ylabel("Place")
save_chart("top_10_places.png")


# -------------------------------------------------
# 8. Donor records by blood bank
# -------------------------------------------------
bank_counts = df["Blood Bank"].fillna("Unknown").value_counts().head(10)
plt.figure(figsize=(11, 6))
bank_counts.sort_values().plot(kind="barh")
plt.title("Donor Records by Blood Bank (Top 10)")
plt.xlabel("Number of Donor Records")
plt.ylabel("Blood Bank")
save_chart("blood_bank_distribution.png")


# -------------------------------------------------
# 9. Donation count distribution
# -------------------------------------------------
donation_data = df["Donation Count"].dropna()
plt.figure()
plt.hist(donation_data, bins=10, edgecolor="black")
plt.title("Distribution of Donation Counts")
plt.xlabel("Donation Count")
plt.ylabel("Number of Donor Records")
save_chart("donation_count_distribution.png")


# -------------------------------------------------
# 10. Age group distribution (if available)
# -------------------------------------------------
if "Age Group" in df.columns:
    age_group_counts = df["Age Group"].fillna("Unknown").value_counts()
    # Sort age bands in their natural order when possible
    preferred_order = ["18-25", "26-35", "36-45", "46-55", "56-60", "Above 60", "Unknown"]
    ordered_labels = [x for x in preferred_order if x in age_group_counts.index]
    remaining_labels = [x for x in age_group_counts.index if x not in ordered_labels]
    age_group_counts = age_group_counts.reindex(ordered_labels + remaining_labels)

    plt.figure()
    age_group_counts.plot(kind="bar")
    plt.title("Donor Records by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Number of Donor Records")
    plt.xticks(rotation=25, ha="right")
    save_chart("age_group_distribution.png")


# -------------------------------------------------
# 11. Save a small text summary of generated charts
# -------------------------------------------------
summary = [
    "BLOOD BANK DATA VISUALISATION SUMMARY",
    "=" * 42,
    f"Dataset records visualised: {len(df)}",
    f"Charts generated: {len(list(OUTPUT_DIR.glob('*.png')))}",
    "",
    "Charts:",
]
for chart in sorted(OUTPUT_DIR.glob("*.png")):
    summary.append(f"- {chart.name}")

summary += [
    "",
    "Note: Charts describe the supplied dataset only. Donor availability "
    "in this dataset should not be treated as real-time blood stock or "
    "confirmation of medical eligibility.",
]

(OUTPUT_DIR / "visualisation_summary.txt").write_text(
    "\n".join(summary), encoding="utf-8"
)

print("\nDATA VISUALISATION COMPLETED")
print("=" * 35)
print(f"Records visualised: {len(df)}")
print(f"Charts saved in: {OUTPUT_DIR}")
