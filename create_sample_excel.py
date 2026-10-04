"""
Utility script to generate sample CEP PROJECT (Responses).xlsx dataset.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from src.data_processor import SurveyDataCleaner

def main():
    data_dir = os.path.join(CURRENT_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    excel_path = os.path.join(data_dir, "CEP PROJECT (Responses).xlsx")

    cleaner = SurveyDataCleaner()
    df = cleaner.generate_sample_cep_data(n_samples=130)

    try:
        df.to_excel(excel_path, index=False)
        print(f"Successfully generated Excel sample at: {excel_path} ({len(df)} rows)")
    except Exception as e:
        print(f"Could not write Excel directly ({e}), writing CSV fallback...")
        csv_path = os.path.join(data_dir, "CEP PROJECT (Responses).csv")
        df.to_csv(csv_path, index=False)
        print(f"Successfully wrote CSV fallback at: {csv_path}")

if __name__ == "__main__":
    main()
