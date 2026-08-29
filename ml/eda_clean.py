import pandas as pd
import numpy as np
import os

# Get absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_dir = os.path.join(BASE_DIR, "dataset")

# Ensure dataset directory exists
os.makedirs(dataset_dir, exist_ok=True)

raw_data_path = os.path.join(dataset_dir, "D:\projects\irrigation\dataset\dataset_day1to6_completed (1).csv")
output_path = os.path.join(dataset_dir, "cleaned_dataset.csv")

# 1. Load raw dataset
df = pd.read_csv(raw_data_path)

print("=================== 1. INITIAL INSPECTION ===================")
print(f"Dataset Shape (Rows, Columns): {df.shape}")
print("\nData Types:")
print(df.dtypes)
print("\nMissing Values per Column:")
print(df.isnull().sum())
print(f"\nDuplicate Rows Count: {df.duplicated().sum()}")

print("\n=================== 2. TARGET CLASS DISTRIBUTION ===================")
counts = df["irrigation_needed"].value_counts()
percentages = df["irrigation_needed"].value_counts(normalize=True) * 100
print(f"Irrigation Not Needed (0): {counts.get(0, 0)} ({percentages.get(0, 0):.2f}%)")
print(f"Irrigation Needed     (1): {counts.get(1, 0)} ({percentages.get(1, 0):.2f}%)")

print("\n=================== 3. DATA PREPROCESSING & CLEANING ===================")
drop_cols = ['timestamp', 'timestamp_readable', 'last_irrigated', 'minutes', 'irrigation_event']
cleaned_df = df.drop(columns=[col for col in drop_cols if col in df.columns])
cleaned_df = cleaned_df.drop_duplicates()

print(f"Cleaned Dataset Shape: {cleaned_df.shape}")
print("Final Selected Features for Training:")
print(cleaned_df.columns.tolist())

print("\n=================== 4. CORRELATION MATRIX ===================")
corr = cleaned_df.corr()['irrigation_needed'].sort_values(ascending=False)
print(corr)

# Save preprocessed dataset
cleaned_df.to_csv(output_path, index=False)
print(f"\nCleaned dataset successfully saved to: {output_path}")