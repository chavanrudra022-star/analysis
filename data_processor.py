"""
Data Processing and Sanitization Pipeline for Mumbai University CEP Survey.
Handles messy field text, regex extraction, boundary validation, and audit trail generation.
"""

import os
import re
from typing import Tuple, List, Dict, Any, Union
import numpy as np
import pandas as pd


class SurveyDataCleaner:
    """
    Cleans, validates, and imputes household energy survey datasets for Mumbai University CEP evaluation.
    Logs every transformation and filtering step in a structured audit trail.
    """

    EXPECTED_COLUMNS = [
        "timestamp",
        "family_members",
        "kwh_units",
        "monthly_bill_inr",
        "lpg_cylinders",
        "lpg_spend_inr",
        "ac_usage",
        "refrigerator_usage",
        "fans_count",
        "other_appliances",
        "cooking_energy_source",
    ]

    NUMERIC_COLUMNS = [
        "family_members",
        "kwh_units",
        "monthly_bill_inr",
        "lpg_cylinders",
        "lpg_spend_inr",
        "fans_count",
    ]

    REALISTIC_BOUNDS = {
        "family_members": (1, 15),
        "monthly_bill_inr": (100.0, 50000.0),
        "kwh_units": (10.0, 3000.0),
    }

    # Common aliases in Mumbai University student Google Form exports
    COLUMN_ALIASES = {
        "timestamp": ["timestamp", "time", "date", "submission time", "marked time"],
        "family_members": [
            "family_members", "family members", "members", "household size", "family size",
            "number of members", "how many members in your family?", "no. of family members"
        ],
        "kwh_units": [
            "kwh_units", "kwh", "units", "electricity units", "monthly units", "units consumed",
            "average monthly electricity consumption in kwh", "monthly consumption (kwh)",
            "average units", "power consumption"
        ],
        "monthly_bill_inr": [
            "monthly_bill_inr", "monthly bill", "bill", "electricity bill", "bill amount",
            "monthly electricity bill in inr", "average monthly bill (rs)", "monthly bill (inr)",
            "electricity bill (in rs)"
        ],
        "lpg_cylinders": [
            "lpg_cylinders", "cylinders", "lpg cylinders used", "cylinders per year",
            "lpg cylinder count", "number of lpg cylinders", "gas cylinders per month"
        ],
        "lpg_spend_inr": [
            "lpg_spend_inr", "lpg spend", "gas spend", "gas bill", "monthly spend on lpg",
            "lpg cost", "monthly gas expense", "spend on cooking fuel"
        ],
        "ac_usage": [
            "ac_usage", "ac usage", "ac hours", "daily ac usage", "air conditioner hours",
            "hours ac used per day", "daily ac running hours"
        ],
        "refrigerator_usage": [
            "refrigerator_usage", "refrigerator", "fridge", "fridge type", "refrigerator type",
            "refrigerator star rating"
        ],
        "fans_count": [
            "fans_count", "fans", "number of fans", "fans count", "ceiling fans", "no of fans"
        ],
        "other_appliances": [
            "other_appliances", "other appliances", "appliances", "electrical appliances",
            "appliances used", "heavy appliances"
        ],
        "cooking_energy_source": [
            "cooking_energy_source", "cooking energy", "cooking fuel", "primary cooking energy source",
            "cooking source", "cooking fuel source", "primary cooking fuel"
        ]
    }

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def clean_numeric_string(self, val: Any) -> Tuple[Union[float, None], str]:
        """
        Extract numeric values from messy survey responses using regex.
        Supports patterns like:
        - '900kh' -> 900.0
        - '150-200 units' -> 175.0 (range mean)
        - '900W' -> 900.0
        - 'Rs. 2,450/-' -> 2450.0
        - '3 to 4' -> 3.5
        - 'na', 'none', 'n/a' -> None
        """
        if pd.isna(val) or val is None:
            return None, "Missing / Null value"

        if isinstance(val, (int, float)):
            if np.isnan(val):
                return None, "NaN numeric"
            return float(val), "Direct numeric"

        s = str(val).strip().lower()

        # Handle explicit null-like answers
        if s in ["na", "n/a", "none", "nil", "null", "-", "--", "don't know", "not sure", "no idea", "zero"]:
            if s == "zero":
                return 0.0, "Word zero converted to 0.0"
            return None, f"Treated '{val}' as NaN"

        # Remove currency symbols, commas, and trailing slashes
        s_clean = s.replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "").replace("/-", "").strip()

        # Check for range: e.g. "150-200", "150 to 200", "3-4"
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", s_clean)
        if range_match:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            mean_val = (low + high) / 2.0
            return mean_val, f"Range '{val}' converted to average: {mean_val}"

        # Check for single numeric value with optional units (e.g., '900kh', '900w', '4 members', '2400 inr')
        single_num_match = re.search(r"(\d+(?:\.\d+)?)", s_clean)
        if single_num_match:
            num = float(single_num_match.group(1))
            return num, f"Extracted {num} from '{val}'"

        return None, f"Unparseable string '{val}' treated as NaN"

    def map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map varied survey column headers to standard column names.
        """
        mapped_df = df.copy()
        current_cols = [str(c).strip().lower() for c in mapped_df.columns]
        column_mapping = {}

        for standard_col, aliases in self.COLUMN_ALIASES.items():
            found = False
            for col_idx, col_name in enumerate(current_cols):
                orig_col = mapped_df.columns[col_idx]
                if col_name == standard_col or col_name in aliases:
                    column_mapping[orig_col] = standard_col
                    found = True
                    break
                # Partial fuzzy match if alias substring appears in column title
                for alias in aliases:
                    if len(alias) > 3 and alias in col_name:
                        column_mapping[orig_col] = standard_col
                        found = True
                        break
                if found:
                    break

        mapped_df.rename(columns=column_mapping, inplace=True)

        # Ensure all standard columns exist
        for col in self.EXPECTED_COLUMNS:
            if col not in mapped_df.columns:
                mapped_df[col] = np.nan

        return mapped_df[self.EXPECTED_COLUMNS]

    def load_and_clean_data(
        self,
        file_path: Union[str, Any] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
        """
        Load survey responses from Excel/CSV (or synthetic data if None), clean corrupted inputs,
        filter outliers, impute missing values, and return raw_df, cleaned_df, audit_log.
        """
        self.audit_log = []

        # 1. Load Data
        raw_df = None
        if file_path is not None:
            try:
                if hasattr(file_path, "read"):  # Streamlit UploadedFile buffer
                    if getattr(file_path, "name", "").endswith(".csv"):
                        raw_df = pd.read_csv(file_path)
                    else:
                        raw_df = pd.read_excel(file_path)
                elif isinstance(file_path, str) and os.path.exists(file_path):
                    if file_path.endswith(".csv"):
                        raw_df = pd.read_csv(file_path)
                    else:
                        raw_df = pd.read_excel(file_path)
            except Exception as e:
                self.audit_log.append({
                    "step": "File Loading Error",
                    "row_index": -1,
                    "field": "file_path",
                    "details": f"Failed reading file {file_path}: {str(e)}. Falling back to sample dataset."
                })

        if raw_df is None or raw_df.empty:
            raw_df = self.generate_sample_cep_data(n_samples=125)
            self.audit_log.append({
                "step": "Dataset Fallback",
                "row_index": -1,
                "field": "dataset",
                "details": "Auto-loaded 125 representative Mumbai CEP field survey responses."
            })

        # Save raw snapshot
        raw_snapshot = raw_df.copy()

        # 2. Standardize Column Names
        standardized_df = self.map_columns(raw_snapshot)
        cleaned_df = standardized_df.copy()

        # 3. Clean numeric fields using regex
        for col in self.NUMERIC_COLUMNS:
            for idx, raw_val in cleaned_df[col].items():
                parsed_val, note = self.clean_numeric_string(raw_val)
                # If modified or unparseable, log transformation
                if str(raw_val) != str(parsed_val):
                    self.audit_log.append({
                        "step": "Regex Extraction",
                        "row_index": int(idx),
                        "field": col,
                        "raw_value": str(raw_val),
                        "transformed_value": str(parsed_val),
                        "details": note
                    })
                cleaned_df.at[idx, col] = parsed_val

            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")

        # 4. Outlier & Corrupted/Troll Records Filtering
        # Bounds: family_members: 1-15, monthly_bill_inr: 100-50,000, kwh_units: 10-3,000
        rows_to_drop = []
        for idx, row in cleaned_df.iterrows():
            drop_reasons = []

            for field, (lower_bound, upper_bound) in self.REALISTIC_BOUNDS.items():
                val = row[field]
                if pd.notna(val):
                    if val < lower_bound or val > upper_bound:
                        drop_reasons.append(
                            f"{field} = {val} outside realistic bounds [{lower_bound}, {upper_bound}]"
                        )

            if drop_reasons:
                rows_to_drop.append(idx)
                self.audit_log.append({
                    "step": "Corrupted/Troll Record Filtered",
                    "row_index": int(idx),
                    "field": "multiple",
                    "raw_value": f"Row {idx}",
                    "transformed_value": "DROPPED",
                    "details": " | ".join(drop_reasons)
                })

        cleaned_df = cleaned_df.drop(index=rows_to_drop).reset_index(drop=True)

        # 5. Imputation of Remaining Missing Values (Grouped by family_members or overall median)
        # Ensure family_members has no missing values first
        if cleaned_df["family_members"].isna().any():
            fam_median = cleaned_df["family_members"].median()
            cleaned_df["family_members"] = cleaned_df["family_members"].fillna(max(1.0, fam_median))

        for col in ["kwh_units", "monthly_bill_inr", "lpg_cylinders", "lpg_spend_inr", "fans_count"]:
            overall_median = cleaned_df[col].median()
            if pd.isna(overall_median):
                overall_median = 100.0 if "bill" in col or "kwh" in col else 1.0

            # Calculate family-size specific medians
            family_medians = cleaned_df.groupby("family_members")[col].transform("median")

            for idx, val in cleaned_df[col].items():
                if pd.isna(val):
                    imputed_val = family_medians.iloc[idx]
                    if pd.isna(imputed_val):
                        imputed_val = overall_median
                    imputed_val = round(float(imputed_val), 1)

                    fam_size = cleaned_df.at[idx, "family_members"]
                    self.audit_log.append({
                        "step": "Missing Value Imputation",
                        "row_index": int(idx),
                        "field": col,
                        "raw_value": "NaN",
                        "transformed_value": str(imputed_val),
                        "details": f"Imputed with median for family size {fam_size} (or overall: {overall_median})"
                    })
                    cleaned_df.at[idx, col] = imputed_val

        # Fill categorical missing values
        cleaned_df["ac_usage"] = cleaned_df["ac_usage"].fillna("0 hours (No AC)")
        cleaned_df["refrigerator_usage"] = cleaned_df["refrigerator_usage"].fillna("Single Door (Standard)")
        cleaned_df["cooking_energy_source"] = cleaned_df["cooking_energy_source"].fillna("LPG Cylinder")
        cleaned_df["other_appliances"] = cleaned_df["other_appliances"].fillna("Basic (TV, Mixer)")

        # Final audit summary entry
        self.audit_log.append({
            "step": "Pipeline Summary",
            "row_index": -1,
            "field": "pipeline",
            "raw_value": f"{len(raw_snapshot)} raw rows",
            "transformed_value": f"{len(cleaned_df)} clean rows",
            "details": f"Filtered {len(rows_to_drop)} corrupted records. Total audit actions logged: {len(self.audit_log)}"
        })

        return raw_snapshot, cleaned_df, self.audit_log

    @staticmethod
    def generate_sample_cep_data(n_samples: int = 125) -> pd.DataFrame:
        """
        Generate realistic field survey dataset for University of Mumbai NEP 2020 CEP.
        Incorporates authentic Mumbai urban/suburban household variations, realistic text quirks,
        and intentional edge-case troll submissions for pipeline verification.
        """
        np.random.seed(42)

        mumbai_localities = [
            "Dadar East", "Andheri West", "Borivali West", "Ghatkopar East",
            "Chembur", "Mulund West", "Bandra East", "Kurla West", "Vashi (Navi Mumbai)", "Thane West"
        ]

        timestamps = pd.date_range(start="2024-02-01", periods=n_samples, freq="4h").strftime("%Y-%m-%d %H:%M:%S")

        # Realistic family sizes: 1 to 7 members
        family_sizes = np.random.choice([1, 2, 3, 4, 5, 6, 7], size=n_samples, p=[0.08, 0.18, 0.28, 0.30, 0.10, 0.04, 0.02])

        ac_categories = [
            ("0 hours (No AC)", 0.0),
            ("1 - 2 hours", 1.5),
            ("3 - 5 hours", 4.0),
            ("6 - 8 hours", 7.0),
            ("> 8 hours (Overnight)", 9.5)
        ]

        cooking_sources = ["LPG Cylinder", "Piped Natural Gas (PNG)", "Dual (LPG + Induction)", "Electricity / Induction"]
        cooking_p = [0.60, 0.28, 0.10, 0.02]

        ref_types = [
            "Single Door (Direct Cool)",
            "Double Door (Frost Free)",
            "5-Star Inverter Refrigerator",
            "No Refrigerator"
        ]
        ref_p = [0.45, 0.40, 0.12, 0.03]

        appliance_pool = [
            "Geyser, Washing Machine, Television",
            "Microwave, Geyser, Water Purifier, Washing Machine",
            "Basic (TV, Mixer, Iron)",
            "Geyser, Air Cooler, TV",
            "Induction Stove, Microwave, Geyser, Washing Machine",
            "Television, Ceiling Fans only"
        ]

        data = []
        for i in range(n_samples):
            fam = int(family_sizes[i])
            ac_choice = np.random.choice(len(ac_categories), p=[0.25, 0.30, 0.25, 0.15, 0.05])
            ac_label, ac_hrs = ac_categories[ac_choice]

            # Base kWh per person + AC load
            base_kwh = (fam * 32.0) + (ac_hrs * 38.0) + np.random.normal(30, 15)
            base_kwh = max(25.0, round(base_kwh, 1))

            # Approximate Mahavitaran bill
            # 0-100: 4.71, 101-300: 10.29, 301-500: 14.55
            bill = 125.0  # fixed
            if base_kwh <= 100:
                bill += base_kwh * 4.71
            elif base_kwh <= 300:
                bill += 100 * 4.71 + (base_kwh - 100) * 10.29
            else:
                bill += 100 * 4.71 + 200 * 10.29 + (base_kwh - 300) * 14.55
            bill = round(bill * 1.16 + np.random.normal(0, 40), 0)
            bill = max(180.0, bill)

            cook_source = np.random.choice(cooking_sources, p=cooking_p)
            if "PNG" in cook_source:
                cylinders = 0
                lpg_spend = round(np.random.uniform(450, 950), 0)
            elif "Electricity" in cook_source:
                cylinders = 0
                lpg_spend = 0
            else:
                cylinders = 1 if fam <= 4 else 2
                lpg_spend = round(cylinders * 910 + np.random.uniform(-50, 50), 0)

            ref = np.random.choice(ref_types, p=ref_p)
            fans = max(1, fam + np.random.randint(0, 2))
            appliances = np.random.choice(appliance_pool)

            # Insert realistic messy text quirks for students to clean!
            kwh_str: Any = base_kwh
            bill_str: Any = bill
            fam_str: Any = fam

            # Field quirk 1: '900kh' or 'units' suffix
            if i % 14 == 0:
                kwh_str = f"{int(base_kwh)}kh"
            elif i % 18 == 0:
                kwh_str = f"{int(base_kwh - 15)}-{int(base_kwh + 15)} units"
            elif i % 22 == 0:
                kwh_str = f"{int(base_kwh)}W"
            elif i % 29 == 0:
                kwh_str = "na"

            # Field quirk 2: Currency formatting
            if i % 11 == 0:
                bill_str = f"₹ {int(bill):,}"
            elif i % 17 == 0:
                bill_str = f"Rs. {int(bill)}/-"
            elif i % 31 == 0:
                bill_str = "N/A"

            # Field quirk 3: Family member text
            if i % 19 == 0:
                fam_str = f"{fam} members"
            elif i % 27 == 0:
                fam_str = f"{fam}-{fam+1}"

            row = {
                "timestamp": timestamps[i],
                "family_members": fam_str,
                "kwh_units": kwh_str,
                "monthly_bill_inr": bill_str,
                "lpg_cylinders": cylinders,
                "lpg_spend_inr": lpg_spend,
                "ac_usage": ac_label,
                "refrigerator_usage": ref,
                "fans_count": fans,
                "other_appliances": appliances,
                "cooking_energy_source": cook_source
            }
            data.append(row)

        # Inject 4 intentional troll/corrupted records to prove audit filter functionality
        # Troll 1: 99 family members
        data[7]["family_members"] = "99"
        # Troll 2: 95,000 INR bill (outside realistic bound 50,000)
        data[21]["monthly_bill_inr"] = "95000"
        # Troll 3: 50,000 kWh consumption
        data[45]["kwh_units"] = "50000"
        # Troll 4: Bill of 0 INR (below 100)
        data[80]["monthly_bill_inr"] = "0"

        return pd.DataFrame(data)
