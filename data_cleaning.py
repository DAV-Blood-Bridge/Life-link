
from pathlib import Path
import pandas as pd

# -------------------------------------------------
# 1. Locate and load the raw dataset
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "BloodBankDetails_Raw.xlsx"
OUTPUT_EXCEL = BASE_DIR / "Clean_Dataset.xlsx"
OUTPUT_CSV = BASE_DIR / "Clean_Dataset.csv"

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE.name}. "
        "Place the raw dataset in the same folder as this Python file."
    )

df = pd.read_excel(INPUT_FILE)

print("----- BEFORE CLEANING -----")
print("Rows and columns:", df.shape)
print("\nMissing values in each column:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# Keep a copy for reporting
original_rows = len(df)
original_duplicates = int(df.duplicated().sum())
original_missing = int(df.isnull().sum().sum())

# -------------------------------------------------
# 2. Remove leading/trailing spaces from text values
# -------------------------------------------------
text_columns = df.select_dtypes(include=["object"]).columns

for column in text_columns:
    df[column] = df[column].apply(
        lambda value: value.strip() if isinstance(value, str) else value
    )

# -------------------------------------------------
# 3. Standardize text formatting
# -------------------------------------------------
# Names and place/organization labels use consistent title case.
columns_to_title_case = [
    "Name",
    "Gender",
    "Place",
    "Donation Status",
    "Eligibility Reason",
    "Blood Bank",
    "Donor Availability",
    "Preferred Donation Center",
    "Nearby Hospital",
]

for column in columns_to_title_case:
    if column in df.columns:
        df[column] = df[column].apply(
            lambda value: value.title() if isinstance(value, str) else value
        )

# Standardize blood group spellings
if "Blood Group" in df.columns:
    blood_group_map = {
        "A+ VE": "A+ve",
        "A+VE": "A+ve",
        "A-VE": "A-ve",
        "B+VE": "B+ve",
        "B-VE": "B-ve",
        "O+VE": "O+ve",
        "O-VE": "O-ve",
        "AB+": "AB+ve",
        "AB+VE": "AB+ve",
        "AB-": "AB-ve",
        "AB-VE": "AB-ve",
    }
    df["Blood Group"] = (
        df["Blood Group"]
        .astype("string")
        .str.upper()
        .str.replace(" ", "", regex=False)
        .replace(blood_group_map)
    )

# -------------------------------------------------
# 4. Remove duplicate records
# -------------------------------------------------
before_duplicates = len(df)
df = df.drop_duplicates()
duplicates_removed = before_duplicates - len(df)

# -------------------------------------------------
# 5. Handle missing values
# -------------------------------------------------
# A row without a donor name cannot be reliably identified,
# so remove that row rather than inventing a donor name.
if "Name" in df.columns:
    before_missing_name = len(df)
    df = df.dropna(subset=["Name"])
    rows_without_name_removed = before_missing_name - len(df)
else:
    rows_without_name_removed = 0

# Fill missing categorical values with "Unknown" or "Not specified".
unknown_columns = ["Donation Status", "Eligibility Reason"]
for column in unknown_columns:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown")

if "Preferred Donation Center" in df.columns:
    df["Preferred Donation Center"] = df["Preferred Donation Center"].fillna(
        "Not Specified"
    )

# Convert numeric columns and fill missing values with their median.
numeric_columns = ["Age", "Donation Count", "Distance (km)"]
for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].notna().any():
            df[column] = df[column].fillna(df[column].median())

# Recalculate Age Group from Age so that the two columns agree.
if "Age" in df.columns and "Age Group" in df.columns:
    bins = [0, 25, 35, 45, 55, 60, float("inf")]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-60", "Above 60"]
    df["Age Group"] = pd.cut(
        df["Age"], bins=bins, labels=labels, include_lowest=True
    ).astype("string")

# -------------------------------------------------
# 6. Reset row numbering and save cleaned dataset
# -------------------------------------------------
df = df.reset_index(drop=True)

df.to_excel(OUTPUT_EXCEL, index=False)
df.to_csv(OUTPUT_CSV, index=False)

# -------------------------------------------------
# 7. Display cleaning summary
# -------------------------------------------------
print("\n----- CLEANING SUMMARY -----")
print("Original rows:", original_rows)
print("Exact duplicate rows originally found:", original_duplicates)
print("Duplicate rows removed after standardization:", duplicates_removed)
print("Rows removed because donor name was missing:", rows_without_name_removed)
print("Missing values before cleaning:", original_missing)
print("Missing values after cleaning:", int(df.isnull().sum().sum()))
print("Final rows and columns:", df.shape)

print("\nRemaining missing values:\n", df.isnull().sum())
print("\nCleaned dataset saved as:")
print(OUTPUT_EXCEL)
print(OUTPUT_CSV)
