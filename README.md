# ⚡ University of Mumbai • NEP 2020 Community Engagement Project (CEP)
## Household Energy Consumption Pattern Analysis & Advisory System

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg)](https://python.org)
[![MERC](https://img.shields.io/badge/Tariff-MERC%20Order%20Compliant-0052CC.svg)](https://merc.gov.in)
[![Language](https://img.shields.io/badge/Languages-English%20%7C%20हिंदी%20%7C%20मराठी-green.svg)](#)

A full-stack, production-grade Streamlit web application engineered for the **University of Mumbai NEP 2020 Community Engagement Project (CEP)**. The platform analyzes household energy and cooking fuel consumption patterns across the Mumbai Metropolitan Region (MMR), sanitizes corrupted survey inputs, computes slab-wise residential electricity tariffs based on MERC orders, provides multilingual energy-efficiency advisories, and provides an end-to-end data pipeline audit trail for academic evaluation.

---

## 📂 Project Architecture

```
cep_energy_project/
├── .streamlit/
│   └── config.toml                          # Streamlit corporate UI theme & server config
├── data/
│   └── CEP PROJECT (Responses).xlsx         # Cleaned/raw field survey response dataset
├── src/
│   ├── __init__.py                          # Package initialization
│   ├── data_processor.py                    # SurveyDataCleaner: Regex extraction, boundary checks, imputation
│   ├── tariff_engine.py                     # MumbaiTariffCalculator: MERC slab-wise electricity tariff calculator
│   └── energy_adviser.py                    # EnergyAdvisor: Carbon accounting & multilingual advisory
├── tests/
│   └── test_components.py                   # Automated unit & integration tests
├── app.py                                   # Streamlit multi-page dashboard application
├── create_sample_excel.py                   # Synthetic & field sample data generator
├── requirements.txt                         # Application dependencies
└── README.md                                # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Installation
Open your terminal in the `cep_energy_project` directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Generate Initial Field Data (if not present)
```bash
python create_sample_excel.py
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
The application will launch automatically in your default browser at `http://localhost:8501`.

---

## ⚡ Key Features & Academic Modules

### 1. 📊 Dashboard Overview & Field Insights
- **Key Performance Indicators (KPIs):** Total Surveyed Households, Average Monthly Bill (₹), Average Units (kWh), Average LPG / Gas Spend (₹).
- **Plotly Visualizations:**
  - *Electricity Bill vs. Family Size:* Box plot with jitter distribution and median trend.
  - *Cooking Fuel Distribution:* Interactive Donut chart displaying LPG, PNG, and Dual-fuel splits.
  - *Daily AC Usage Impact:* Step-function escalation in bills caused by AC duration.
  - *Appliance Ownership Prevalence:* Percentage adoption of geysers, washing machines, microwaves, etc.
- **Dynamic Cross-Filtering:** Filter by AC duration and primary cooking fuel.

### 2. 🧮 Personal Bill & Usage Calculator
- **Interactive Citizen Inputs:** Family members, daily AC running hours, refrigerator category, fan count, heavy appliances.
- **Mumbai Slab-wise Tariff Engine:**
  - `0 - 100 units`: ₹ 4.71 / unit
  - `101 - 300 units`: ₹ 10.29 / unit
  - `301 - 500 units`: ₹ 14.55 / unit
  - `> 500 units`: ₹ 16.64 / unit
  - `Fixed Single-Phase Demand Charge`: ₹ 125.00 / month
  - `Fuel Adjustment Charge (FAC) & Electricity Duty`: 16% total tax multiplier.
- **Itemized Visual Breakdown:** Stacked component chart illustrating each slab's cost contribution.
- **Peer Benchmark:** Visual gauge comparison showing how user consumption contrasts with the survey median for their exact family size.

### 3. 🌱 Energy Saving & Carbon Advisory (Multilingual)
- **Carbon Accounting:** Central Electricity Authority (CEA) emission intensity of $0.82 \text{ kg CO}_2 / \text{kWh}$.
- **Ecological Offset:** Quantifies mature native trees (Neem, Peepal) needed annually to neutralize emissions.
- **Multilingual Recommendations:**
  - Native translations in **English**, **Hindi (हिंदी)**, and **Marathi (मराठी)**.
  - Quantified monthly rupee savings and priority badges (Critical, High, Medium, Low).
- **Monetary Return on Investment (ROI):** 5-year financial trajectory and simple payback periods for BLDC fans, 5-Star Inverter ACs, and PM Surya Ghar Rooftop Solar.

### 4. 🔍 Field Data Pipeline & Audit (MU Evaluation)
- **Academic Transparency:** Explicitly displays the sanitization pipeline to fulfill University of Mumbai NEP 2020 CEP evaluation rubrics.
- **Regex Extraction:** Handles messy text field inputs (e.g. `'900kh'` -> `900.0`, `'150-200 units'` -> `175.0`, `'Rs 2,500'` -> `2500.0`, `'na'` -> `NaN`).
- **Realistic Bounds Filtering:** Automatic filtering of troll/corrupted records:
  - Family members: $1 \le N \le 15$
  - Monthly bill: ₹ $100 \le \text{Bill} \le \text{₹ } 50,000$
  - Consumption: $10 \le \text{kWh} \le 3,000$
- **Median Imputation:** Missing fields cleanly imputed using family-size specific medians or overall medians.
- **Data Export:** Direct CSV export of both the Cleaned CEP Dataset and the complete Data Cleaning Audit Trail.

---

## 🧪 Running Unit Tests

To run the automated test suite verifying the tariff engine, data cleaner, and advisory:
```bash
python -m unittest tests/test_components.py
```

---

## 🏛️ University of Mumbai NEP 2020 CEP Alignment
- **Community Engagement:** Empowers Mumbai citizens with transparent electricity billing literacy and decarbonization pathways.
- **Academic Rigor:** Full data provenance from raw field forms to statistical reporting.
- **Inclusivity:** Trilingual interface ensuring accessibility across diverse linguistic communities in Maharashtra.
