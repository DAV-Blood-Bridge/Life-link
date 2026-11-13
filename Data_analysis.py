
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Clean_Dataset.xlsx"
OUTPUT_DIR = BASE_DIR / "Analysis_Results"
OUTPUT_DIR.mkdir(exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Clean_Dataset.xlsx was not found. Run data_cleaning.py first and "
        "keep this script in the same project folder."
    )

# 1. Load cleaned data
df = pd.read_excel(INPUT_FILE)

# 2. Check required columns
required_columns = [
    "Blood Group", "Age", "Gender", "Place", "Donation Status",
    "Donation Count", "Blood Bank", "Distance (km)", "Donor Availability"
]
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    raise ValueError(f"The dataset is missing these required columns: {missing_columns}")

# Convert numeric fields safely
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Donation Count"] = pd.to_numeric(df["Donation Count"], errors="coerce")
df["Distance (km)"] = pd.to_numeric(df["Distance (km)"], errors="coerce")

# 3. Generate summary tables
summaries = {
    "blood_group_summary.csv": df["Blood Group"].value_counts(dropna=False).rename_axis("Blood Group").reset_index(name="Donor Records"),
    "gender_summary.csv": df["Gender"].value_counts(dropna=False).rename_axis("Gender").reset_index(name="Donor Records"),
    "age_group_summary.csv": df["Age Group"].value_counts(dropna=False).rename_axis("Age Group").reset_index(name="Donor Records") if "Age Group" in df.columns else pd.DataFrame(),
    "donation_status_summary.csv": df["Donation Status"].value_counts(dropna=False).rename_axis("Donation Status").reset_index(name="Donor Records"),
    "donor_availability_summary.csv": df["Donor Availability"].value_counts(dropna=False).rename_axis("Donor Availability").reset_index(name="Donor Records"),
    "blood_bank_summary.csv": df["Blood Bank"].value_counts(dropna=False).rename_axis("Blood Bank").reset_index(name="Donor Records"),
    "place_summary.csv": df["Place"].value_counts(dropna=False).rename_axis("Place").reset_index(name="Donor Records"),
}

for filename, table in summaries.items():
    if not table.empty:
        table.to_csv(OUTPUT_DIR / filename, index=False)

# Cross-tabulation: blood group vs donation status
blood_group_status = pd.crosstab(df["Blood Group"], df["Donation Status"])
blood_group_status.to_csv(OUTPUT_DIR / "blood_group_by_donation_status.csv")

# 4. Calculate key descriptive statistics
record_count = len(df)
avg_age = df["Age"].mean()
median_age = df["Age"].median()
avg_donations = df["Donation Count"].mean()
avg_distance = df["Distance (km)"].mean()

blood_group_counts = df["Blood Group"].value_counts()
most_common_blood_group = blood_group_counts.index[0] if not blood_group_counts.empty else "N/A"
status_counts = df["Donation Status"].value_counts()
most_common_status = status_counts.index[0] if not status_counts.empty else "N/A"
availability_counts = df["Donor Availability"].value_counts()
most_common_availability = availability_counts.index[0] if not availability_counts.empty else "N/A"

eligible_count = int((df["Donation Status"].astype(str).str.casefold() == "eligible").sum())
eligible_percentage = (eligible_count / record_count * 100) if record_count else 0

# 5. Create a readable text report
report_lines = [
    "BLOOD BANK & DONOR DATA ANALYSIS REPORT",
    "=" * 48,
    f"Total donor records analysed: {record_count}",
    f"Average age: {avg_age:.2f} years" if pd.notna(avg_age) else "Average age: N/A",
    f"Median age: {median_age:.2f} years" if pd.notna(median_age) else "Median age: N/A",
    f"Average donation count: {avg_donations:.2f}" if pd.notna(avg_donations) else "Average donation count: N/A",
    f"Average distance (km): {avg_distance:.2f}" if pd.notna(avg_distance) else "Average distance (km): N/A",
    f"Most frequently recorded blood group: {most_common_blood_group}",
    f"Most common donation status: {most_common_status}",
    f"Most common donor availability status: {most_common_availability}",
    f"Records marked Eligible: {eligible_count} ({eligible_percentage:.1f}%)",
    "",
    "DONOR RECORDS BY BLOOD GROUP",
    "-" * 32,
]
for label, count in blood_group_counts.items():
    report_lines.append(f"{label}: {count}")

report_lines += ["", "DONATION STATUS COUNTS", "-" * 24]
for label, count in status_counts.items():
    report_lines.append(f"{label}: {count}")

report_lines += [
    "",
    "Note: This report describes the supplied dataset only. It does not determine medical eligibility or guarantee real-time blood availability.",
]

(OUTPUT_DIR / "analysis_report.txt").write_text("\n".join(report_lines), encoding="utf-8")

print("DATA ANALYSIS COMPLETED")
print("=" * 35)
print(f"Records analysed: {record_count}")
print(f"Average age: {avg_age:.2f}" if pd.notna(avg_age) else "Average age: N/A")
print(f"Most common blood group: {most_common_blood_group}")
print(f"Eligible records: {eligible_count} ({eligible_percentage:.1f}%)")
print(f"Results saved in: {OUTPUT_DIR}")
print("Open analysis_report.txt to read the summary.")
