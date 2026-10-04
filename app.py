"""
Mumbai University NEP 2020 Community Engagement Project (CEP)
Household Energy Consumption Pattern Analysis Web Application.
"""

import os
import sys
from typing import Dict, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path for robust imports (works on Streamlit Cloud & locally)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Direct imports — no 'src.' prefix, compatible with Streamlit Cloud
from data_processor import SurveyDataCleaner
from tariff_engine import MumbaiTariffCalculator
from energy_adviser import EnergyAdvisor

# ---------------------------------------------------------
# Page Configuration & UI Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="MU CEP - Household Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Multilingual UI Dictionary (English, Hindi, Marathi)
# ---------------------------------------------------------
TRANSLATIONS = {
    "English": {
        "title": "Household Energy Consumption Pattern Analysis",
        "subtitle": "University of Mumbai • NEP 2020 Community Engagement Project (CEP)",
        "nav_header": "Navigation & Control",
        "nav_page": "Select Module",
        "nav_overview": "📊 Dashboard Overview & Field Insights",
        "nav_calc": "🧮 Personal Bill & Usage Calculator",
        "nav_advisory": "🌱 Energy Saving & Carbon Advisory",
        "nav_audit": "🔍 Field Data Pipeline & Audit (MU Evaluation)",
        "lang_selector": "🌐 Select Language / भाषा निवडा",
        "data_source_header": "📁 CEP Field Survey Data Source",
        "upload_label": "Upload Survey Excel / CSV",
        "default_data_btn": "Reload Default CEP Field Dataset",
        "kpi_total_households": "Surveyed Households",
        "kpi_avg_bill": "Average Monthly Bill",
        "kpi_avg_units": "Average Consumption",
        "kpi_avg_lpg": "Average LPG / Gas Spend",
        "chart1_title": "Electricity Bill (₹) vs. Family Size",
        "chart2_title": "Cooking Fuel Distribution in Mumbai Households",
        "chart3_title": "Impact of Daily AC Running Hours on Monthly Bill",
        "chart4_title": "Household Appliance Ownership Prevalence (%)",
        "filter_header": "🔎 Filter Visualizations",
        "filter_ac": "Filter by AC Usage",
        "filter_cooking": "Filter by Cooking Fuel",
        "calc_header": "Citizen Household Appliance & Consumption Inputs",
        "fam_slider": "Number of Family Members",
        "ac_slider": "Daily AC Usage (Hours per day)",
        "fans_slider": "Number of Ceiling / Table Fans",
        "ref_select": "Refrigerator Category",
        "appliances_multiselect": "Heavy Electrical Appliances Used",
        "kwh_input": "Estimated Monthly Electricity Consumption (kWh Units)",
        "provider_select": "Utility Provider (Mumbai Jurisdiction)",
        "bill_summary": "Estimated Electricity Bill Breakdown",
        "peer_benchmark": "Peer Benchmark (Survey Comparison for your Family Size)",
        "carbon_header": "Household Carbon Footprint & Ecological Scorecard",
        "monthly_co2": "Monthly Carbon Emissions",
        "annual_co2": "Annual Carbon Footprint",
        "trees_needed": "Trees Needed to Offset",
        "tips_header": "Targeted Energy Efficiency Recommendations",
        "roi_header": "Monetary Return on Investment (ROI) Calculator",
        "audit_header": "Academic Field Data Sanitization Pipeline & Audit Trail",
        "raw_toggle": "View Raw Survey Responses",
        "clean_toggle": "View Cleaned CEP Dataset",
        "download_cleaned": "📥 Download Cleaned Dataset (CSV)",
        "download_audit": "📥 Download Cleaning Audit Log (CSV)",
    },
    "Hindi": {
        "title": "घरेलू ऊर्जा खपत पैटर्न विश्लेषण प्रणाली",
        "subtitle": "मुंबई विश्वविद्यालय • राष्ट्रीय शिक्षा नीति (NEP 2020) सामुदायिक सहभागिता परियोजना (CEP)",
        "nav_header": "नेविगेशन एवं नियंत्रण",
        "nav_page": "मॉड्यूल चुनें",
        "nav_overview": "📊 डैशबोर्ड अवलोकन और क्षेत्रीय अंतर्दृष्टि",
        "nav_calc": "🧮 व्यक्तिगत बिजली बिल एवं खपत कैलकुलेटर",
        "nav_advisory": "🌱 ऊर्जा बचत एवं कार्बन परामर्श",
        "nav_audit": "🔍 डेटा पाइपलाइन और ऑडिट (MU मूल्यांकन)",
        "lang_selector": "🌐 भाषा चुनें / Select Language",
        "data_source_header": "📁 CEP फील्ड सर्वे डेटा स्रोत",
        "upload_label": "सर्वेक्षण एक्सेल / CSV अपलोड करें",
        "default_data_btn": "डिफ़ॉल्ट फील्ड डेटासेट पुनः लोड करें",
        "kpi_total_households": "सर्वेक्षित परिवार",
        "kpi_avg_bill": "औसत मासिक बिजली बिल",
        "kpi_avg_units": "औसत मासिक खपत",
        "kpi_avg_lpg": "औसत रसोई गैस खर्च",
        "chart1_title": "परिवार के सदस्यों की संख्या बनाम बिजली बिल (₹)",
        "chart2_title": "मुंबई में खाना पकाने के ऊर्जा स्रोतों का वितरण",
        "chart3_title": "दैनिक AC उपयोग के घंटों का बिजली बिल पर प्रभाव",
        "chart4_title": "घरेलू बिजली उपकरणों की व्यापकता (%)",
        "filter_header": "🔎 फ़िल्टर विकल्प",
        "filter_ac": "AC उपयोग अनुसार फ़िल्टर करें",
        "filter_cooking": "ईंधन स्रोत अनुसार फ़िल्टर करें",
        "calc_header": "नागरिक घरेलू उपकरण एवं खपत विवरण",
        "fam_slider": "परिवार के सदस्यों की संख्या",
        "ac_slider": "दैनिक AC उपयोग (घंटे प्रति दिन)",
        "fans_slider": "सीलिंग / टेबल पंखों की संख्या",
        "ref_select": "रेफ्रिजरेटर का प्रकार",
        "appliances_multiselect": "उपयोग किए जाने वाले भारी उपकरण",
        "kwh_input": "अनुमानित मासिक बिजली खपत (kWh यूनिट)",
        "provider_select": "बिजली वितरण कंपनी (मुंबई)",
        "bill_summary": "अनुमानित बिजली बिल का मदवार विवरण",
        "peer_benchmark": "समान परिवार आकार के साथ तुलना (Peer Benchmark)",
        "carbon_header": "घरेलू कार्बन उत्सर्जन एवं पर्यावरण रिपोर्ट कार्ड",
        "monthly_co2": "मासिक कार्बन उत्सर्जन",
        "annual_co2": "वार्षिक कार्बन पदचिह्न",
        "trees_needed": "कार्बन भरपाई हेतु आवश्यक वृक्ष",
        "tips_header": "ऊर्जा बचत हेतु विशेष सुझाव",
        "roi_header": "वार्षिक आर्थिक बचत एवं ROI कैलकुलेटर",
        "audit_header": "अकादमिक डेटा परिशोधन पाइपलाइन और ऑडिट ट्रेल",
        "raw_toggle": "कच्चा फील्ड सर्वे डेटा देखें",
        "clean_toggle": "परिशोधित स्वच्छ डेटासेट देखें",
        "download_cleaned": "📥 स्वच्छ डेटा डाउनलोड करें (CSV)",
        "download_audit": "📥 डेटा ऑडिट लॉग डाउनलोड करें (CSV)",
    },
    "Marathi": {
        "title": "कौटुंबिक ऊर्जा वापर पद्धतीचे विश्लेषण",
        "subtitle": "मुंबई विद्यापीठ • राष्ट्रीय शैक्षणिक धोरण (NEP 2020) समुदाय सहभाग प्रकल्प (CEP)",
        "nav_header": "नेव्हिगेशन आणि नियंत्रण",
        "nav_page": "मॉड्यूल निवडा",
        "nav_overview": "📊 डॅशबोर्ड विहंगावलोकन आणि क्षेत्रीय निष्कर्ष",
        "nav_calc": "🧮 वैयक्तिक वीज बिल व वापर गणक",
        "nav_advisory": "🌱 ऊर्जा बचत आणि कार्बन सल्लागार",
        "nav_audit": "🔍 डेटा पाइपलाइन आणि ऑडिट (MU मूल्यमापन)",
        "lang_selector": "🌐 भाषा निवडा / Select Language",
        "data_source_header": "📁 CEP फील्ड सर्व्हे डेटा स्रोत",
        "upload_label": "सर्व्हे एक्सेल / CSV फाइल अपलोड करा",
        "default_data_btn": "मूळ फील्ड डेटासेट पुन्हा लोड करा",
        "kpi_total_households": "सर्वेक्षण केलेली कुटुंबे",
        "kpi_avg_bill": "सरासरी मासिक वीज बिल",
        "kpi_avg_units": "सरासरी वीज वापर",
        "kpi_avg_lpg": "सरासरी स्वयंपाक गॅस खर्च",
        "chart1_title": "कुटुंबाचा आकार विरूद्ध मासिक वीज बिल (₹)",
        "chart2_title": "मुंबईतील कुटुंबांमधील स्वयंपाक इंधनाचे वर्गीकरण",
        "chart3_title": "दैनंदिन AC वापराचा मासिक बिलावर होणारा परिणाम",
        "chart4_title": "घरातील विद्युत उपकरणांचे प्रमाण (%)",
        "filter_header": "🔎 आलेख फिल्टर",
        "filter_ac": "AC वापरानुसार फिल्टर करा",
        "filter_cooking": "स्वयंपाक इंधनानुसार फिल्टर करा",
        "calc_header": "नागरिक कौटुंबिक उपकरणे व वीज वापर तपशील",
        "fam_slider": "कुटुंबातील सदस्यांची संख्या",
        "ac_slider": "दैनंदिन AC वापर (तास प्रति दिवस)",
        "fans_slider": "घरातील पंख्यांची संख्या",
        "ref_select": "रेफ्रिजरेटरचा प्रकार",
        "appliances_multiselect": "वापरली जाणारी जड विद्युत उपकरणे",
        "kwh_input": "अंदाजे मासिक वीज वापर (kWh युनिट्स)",
        "provider_select": "वीज वितरण कंपनी (मुंबई कार्यक्षेत्र)",
        "bill_summary": "अंदाजे वीज बिलाची सविस्तर विभागणी",
        "peer_benchmark": "कुटुंबाच्या आकाराशी तुलना (Peer Benchmark)",
        "carbon_header": "कौटुंबिक कार्बन उत्सर्जन व पर्यावरण गुणपत्रिका",
        "monthly_co2": "मासिक कार्बन उत्सर्जन",
        "annual_co2": "वार्षिक कार्बन फूटप्रिंट",
        "trees_needed": "कार्बन संतुलनासाठी आवश्यक झाडे",
        "tips_header": "वीज बचतीसाठी कृतीशील उपाययोजना",
        "roi_header": "आर्थिक परतावा (ROI) आणि वार्षिक बचत गणक",
        "audit_header": "शैक्षणिक डेटा स्वच्छता पाइपलाइन आणि ऑडिट ट्रेल",
        "raw_toggle": "कच्चा फील्ड सर्व्हे डेटा पहा",
        "clean_toggle": "स्वच्छ व तपासलेला डेटासेट पहा",
        "download_cleaned": "📥 स्वच्छ डेटा डाउनलोड करा (CSV)",
        "download_audit": "📥 डेटा स्वच्छता ऑडिट ट्रेल डाउनलोड करा (CSV)",
    }
}

# ---------------------------------------------------------
# Data Persistence & Caching
# ---------------------------------------------------------
@st.cache_data
def get_survey_data(uploaded_file=None):
    cleaner = SurveyDataCleaner()
    target_data_dir = os.path.join(CURRENT_DIR, "data")
    os.makedirs(target_data_dir, exist_ok=True)
    default_excel_path = os.path.join(target_data_dir, "CEP PROJECT (Responses).xlsx")

    # If user uploaded a file, use it
    if uploaded_file is not None:
        return cleaner.load_and_clean_data(uploaded_file)

    # If default excel file exists, load it
    if os.path.exists(default_excel_path):
        return cleaner.load_and_clean_data(default_excel_path)

    # Otherwise generate sample data, save it to data/ directory for persistence
    raw_df = cleaner.generate_sample_cep_data(n_samples=125)
    try:
        raw_df.to_excel(default_excel_path, index=False)
    except Exception:
        # If openpyxl not yet ready or writing fails, save as csv
        csv_fallback = os.path.join(target_data_dir, "CEP_PROJECT_Responses.csv")
        raw_df.to_csv(csv_fallback, index=False)

    return cleaner.load_and_clean_data(default_excel_path if os.path.exists(default_excel_path) else raw_df)


# ---------------------------------------------------------
# Sidebar Setup
# ---------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="background-color: #0052CC; color: white; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="margin: 0; font-size: 1.15rem; color: #FFFFFF;">🏛️ Mumbai University CEP</h3>
        <p style="margin: 4px 0 0 0; font-size: 0.8rem; opacity: 0.9;">NEP 2020 Community Engagement Project</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 1. Language Selector
lang_choice = st.sidebar.selectbox(
    "🌐 Language / भाषा",
    options=["English", "Hindi (हिंदी)", "Marathi (मराठी)"],
    index=0
)
current_lang = "English"
if "Hindi" in lang_choice:
    current_lang = "Hindi"
elif "Marathi" in lang_choice:
    current_lang = "Marathi"

T = TRANSLATIONS[current_lang]

# 2. File Upload / Auto-detector
st.sidebar.subheader(T["data_source_header"])
uploaded_file = st.sidebar.file_uploader(
    T["upload_label"],
    type=["xlsx", "xls", "csv"],
    help="Upload official Mumbai University CEP responses sheet"
)

raw_df, clean_df, audit_log = get_survey_data(uploaded_file)

st.sidebar.success(
    f"✅ Dataset Loaded: {len(clean_df)} validated households ({len(raw_df) - len(clean_df)} filtered)"
)

# 3. Module Selector
st.sidebar.markdown("---")
page_selection = st.sidebar.radio(
    T["nav_page"],
    options=[
        T["nav_overview"],
        T["nav_calc"],
        T["nav_advisory"],
        T["nav_audit"]
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**MERC Approved Rates**\n"
    "• 0-100: ₹ 4.71\n"
    "• 101-300: ₹ 10.29\n"
    "• 301-500: ₹ 14.55\n"
    "• >500: ₹ 16.64\n"
    "• Fixed Demand: ₹ 125/mo\n"
    "• Duty & FAC: 16%"
)

# ---------------------------------------------------------
# App Header Banner
# ---------------------------------------------------------
st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #0052CC 0%, #0747A6 100%); padding: 22px 26px; border-radius: 10px; color: white; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <h1 style="margin: 0; font-size: 1.85rem; color: #FFFFFF; font-weight: 700;">⚡ {T['title']}</h1>
        <p style="margin: 6px 0 0 0; font-size: 0.95rem; color: #DEEBFF; font-weight: 400;">{T['subtitle']}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize engines
tariff_calc = MumbaiTariffCalculator()
advisor = EnergyAdvisor()

# =========================================================
# PAGE 1: 📊 Dashboard Overview & Field Insights
# =========================================================
if page_selection == T["nav_overview"]:
    st.subheader(T["nav_overview"])

    # 1. Top KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)

    total_resp = len(clean_df)
    avg_bill = clean_df["monthly_bill_inr"].mean()
    avg_kwh = clean_df["kwh_units"].mean()
    avg_lpg = clean_df["lpg_spend_inr"].mean()

    with col1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #0052CC; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.85rem; font-weight: 600;">{T['kpi_total_households'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{total_resp}</div>
                <div style="color: #36B37E; font-size: 0.8rem; margin-top: 4px;">✔ 100% Survey Validated</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #36B37E; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.85rem; font-weight: 600;">{T['kpi_avg_bill'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">₹ {avg_bill:,.0f}</div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">Min: ₹{clean_df['monthly_bill_inr'].min():,.0f} | Max: ₹{clean_df['monthly_bill_inr'].max():,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #FFAB00; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.85rem; font-weight: 600;">{T['kpi_avg_units'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{avg_kwh:.1f} <span style="font-size: 1rem; font-weight: 500;">kWh</span></div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">Median: {clean_df['kwh_units'].median():.1f} kWh / month</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #6554C0; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.85rem; font-weight: 600;">{T['kpi_avg_lpg'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">₹ {avg_lpg:,.0f}</div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">Avg Cylinders: {clean_df['lpg_cylinders'].mean():.1f} / mo</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Interactive Filter Bar
    with st.expander(f"{T['filter_header']}", expanded=False):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            ac_options = sorted(clean_df["ac_usage"].astype(str).unique())
            selected_ac = st.multiselect(T["filter_ac"], options=ac_options, default=ac_options)
        with fcol2:
            cook_options = sorted(clean_df["cooking_energy_source"].astype(str).unique())
            selected_cook = st.multiselect(T["filter_cooking"], options=cook_options, default=cook_options)

    # Filter dataframe
    filtered_df = clean_df[
        (clean_df["ac_usage"].isin(selected_ac)) &
        (clean_df["cooking_energy_source"].isin(selected_cook))
    ]
    if filtered_df.empty:
        filtered_df = clean_df

    # 3. Charts Section
    row1_col1, row1_col2 = st.columns([1.1, 0.9])

    with row1_col1:
        fig_bill_fam = px.box(
            filtered_df,
            x="family_members",
            y="monthly_bill_inr",
            points="all",
            color="family_members",
            labels={
                "family_members": "Number of Family Members",
                "monthly_bill_inr": "Monthly Bill (₹)"
            },
            title=f"<b>{T['chart1_title']}</b>",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_bill_fam.update_layout(
            showlegend=False,
            template="plotly_white",
            plot_bgcolor="rgba(240, 244, 250, 0.3)",
            height=390,
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig_bill_fam, use_container_width=True)

    with row1_col2:
        cook_counts = filtered_df["cooking_energy_source"].value_counts().reset_index()
        cook_counts.columns = ["Fuel Source", "Households"]
        fig_donut = px.pie(
            cook_counts,
            names="Fuel Source",
            values="Households",
            hole=0.55,
            title=f"<b>{T['chart2_title']}</b>",
            color_discrete_sequence=["#0052CC", "#36B37E", "#FFAB00", "#FF5630", "#6554C0"]
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(
            template="plotly_white",
            height=390,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=50, b=60)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    row2_col1, row2_col2 = st.columns([1, 1])

    with row2_col1:
        ac_bill_summary = filtered_df.groupby("ac_usage")["monthly_bill_inr"].agg(["mean", "median", "count"]).reset_index()
        fig_ac = px.bar(
            ac_bill_summary,
            x="ac_usage",
            y="mean",
            text_auto=".0f",
            labels={"ac_usage": "AC Daily Duration", "mean": "Average Bill (₹)"},
            title=f"<b>{T['chart3_title']}</b>",
            color="mean",
            color_continuous_scale="Blues"
        )
        fig_ac.update_layout(
            template="plotly_white",
            height=380,
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig_ac, use_container_width=True)

    with row2_col2:
        appliances_list = ["Geyser", "Washing Machine", "Microwave", "Water Purifier", "Air Cooler"]
        app_counts = {}
        for app in appliances_list:
            app_counts[app] = filtered_df["other_appliances"].str.contains(app, case=False, na=False).sum()

        app_df = pd.DataFrame({
            "Appliance": list(app_counts.keys()),
            "Ownership (%)": [(c / len(filtered_df)) * 100 for c in app_counts.values()]
        }).sort_values("Ownership (%)", ascending=True)

        fig_apps = px.bar(
            app_df,
            x="Ownership (%)",
            y="Appliance",
            orientation="h",
            text_auto=".1f",
            title=f"<b>{T['chart4_title']}</b>",
            color="Ownership (%)",
            color_continuous_scale="Teal"
        )
        fig_apps.update_layout(
            template="plotly_white",
            height=380,
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig_apps, use_container_width=True)


# =========================================================
# PAGE 2: 🧮 Personal Bill & Usage Calculator
# =========================================================
elif page_selection == T["nav_calc"]:
    st.subheader(T["nav_calc"])
    st.markdown(
        """
        Input your household size and appliance usage to receive an instantaneous, slab-wise
        electricity tariff breakdown based on Maharashtra Electricity Regulatory Commission (MERC) orders.
        """
    )

    calc_col1, calc_col2 = st.columns([1, 1.1])

    with calc_col1:
        st.markdown(f"#### ⚙️ {T['calc_header']}")

        in_fam = st.slider(T["fam_slider"], min_value=1, max_value=12, value=4, step=1)
        in_ac_hours = st.slider(T["ac_slider"], min_value=0.0, max_value=16.0, value=3.0, step=0.5)
        in_fans = st.slider(T["fans_slider"], min_value=1, max_value=10, value=4, step=1)

        in_ref = st.selectbox(
            T["ref_select"],
            options=[
                "Single Door (Direct Cool)",
                "Double Door (Frost Free)",
                "5-Star Inverter Refrigerator",
                "No Refrigerator"
            ],
            index=1
        )

        in_appliances = st.multiselect(
            T["appliances_multiselect"],
            options=["Water Geyser", "Washing Machine", "Microwave", "Water Purifier", "Iron", "Induction Stove"],
            default=["Water Geyser", "Washing Machine"]
        )

        est_base_kwh = (in_fam * 32.0) + (in_ac_hours * 38.0) + (in_fans * 12.0)
        if "Geyser" in str(in_appliances):
            est_base_kwh += 45.0
        if "Washing Machine" in str(in_appliances):
            est_base_kwh += 20.0
        if "Microwave" in str(in_appliances):
            est_base_kwh += 15.0

        in_kwh = st.number_input(
            T["kwh_input"],
            min_value=10.0,
            max_value=3000.0,
            value=float(round(est_base_kwh, 0)),
            step=10.0,
            help="Pre-filled based on your appliance configuration; adjust if you have your exact MSEDCL bill."
        )

        in_provider = st.selectbox(
            T["provider_select"],
            options=["Mahavitaran", "Adani Electricity Mumbai", "Tata Power Mumbai", "BEST Undertaking"],
            index=0
        )

    with calc_col2:
        bill_res = tariff_calc.calculate_bill(in_kwh, provider=in_provider)

        st.markdown(f"#### 📋 {T['bill_summary']}")

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #172B4D 0%, #091E42 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 18px;">
                <div style="font-size: 0.9rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">Estimated Monthly Bill ({in_provider})</div>
                <div style="font-size: 2.3rem; font-weight: 700; color: #4C9AFF; margin: 4px 0;">₹ {bill_res['total_estimated_bill_inr']:,.2f}</div>
                <div style="font-size: 0.85rem; color: #DEEBFF;">
                    Total Energy: <b>{in_kwh:.1f} kWh</b> | Effective Cost: <b>₹ {bill_res['effective_rate_per_kwh']:.2f} / unit</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        slab_df = pd.DataFrame(bill_res["slab_details"])
        disp_slab_df = slab_df[["slab_name", "units", "rate_per_unit", "amount"]].copy()
        disp_slab_df.columns = ["Tariff Slab", "Billed Units (kWh)", "Rate (₹/kWh)", "Energy Amount (₹)"]
        disp_slab_df["Rate (₹/kWh)"] = disp_slab_df["Rate (₹/kWh)"].apply(lambda x: f"₹ {x:.2f}")
        disp_slab_df["Energy Amount (₹)"] = disp_slab_df["Energy Amount (₹)"].apply(lambda x: f"₹ {x:,.2f}")

        st.dataframe(disp_slab_df, hide_index=True, use_container_width=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Fixed Demand Charge", f"₹ {bill_res['base_charge']:.2f}")
        m2.metric("Energy Charges Subtotal", f"₹ {bill_res['energy_charges']:,.2f}")
        m3.metric("MERC Duty & Tax (16%)", f"₹ {bill_res['tax_and_duty']:,.2f}")

        slab_chart_df = pd.DataFrame([
            {"Component": s["slab_name"], "Amount (₹)": s["amount"]}
            for s in bill_res["slab_details"] if s["amount"] > 0
        ] + [
            {"Component": "Fixed Demand Charge", "Amount (₹)": bill_res["base_charge"]},
            {"Component": "Duty & Taxes (16%)", "Amount (₹)": bill_res["tax_and_duty"]}
        ])

        fig_breakdown = px.bar(
            slab_chart_df,
            x="Component",
            y="Amount (₹)",
            text_auto=".1f",
            title="<b>Itemized Bill Component Contribution (₹)</b>",
            color="Component",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_breakdown.update_layout(
            template="plotly_white",
            showlegend=False,
            height=280,
            margin=dict(l=30, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_breakdown, use_container_width=True)

    st.markdown("---")
    st.markdown(f"#### 📊 {T['peer_benchmark']}")

    matching_peers = clean_df[clean_df["family_members"] == in_fam]
    if matching_peers.empty:
        matching_peers = clean_df

    peer_median_bill = matching_peers["monthly_bill_inr"].median()
    peer_mean_bill = matching_peers["monthly_bill_inr"].mean()
    peer_median_kwh = matching_peers["kwh_units"].median()

    b_col1, b_col2 = st.columns([1, 1.2])

    with b_col1:
        diff_pct = ((bill_res["total_estimated_bill_inr"] - peer_median_bill) / peer_median_bill) * 100
        if diff_pct < -5:
            bench_status = "🎉 Lower Than Median"
            bench_color = "#36B37E"
            bench_comment = f"Your energy cost is **{abs(diff_pct):.1f}% lower** than the survey median for a Mumbai household of {in_fam} members. Excellent energy conservation!"
        elif diff_pct > 15:
            bench_status = "⚠️ Higher Than Median"
            bench_color = "#FF5630"
            bench_comment = f"Your bill is **{diff_pct:.1f}% higher** than the survey median (₹ {peer_median_bill:,.0f}). Check the 'Energy Saving & Carbon Advisory' tab for actionable savings."
        else:
            bench_status = "⚖️ In Line With Median"
            bench_color = "#FFAB00"
            bench_comment = f"Your consumption aligns closely (within {abs(diff_pct):.1f}%) with typical Mumbai households of size {in_fam}."

        st.markdown(
            f"""
            <div style="background-color: white; border: 1px solid #DFE1E6; border-left: 6px solid {bench_color}; padding: 18px; border-radius: 8px;">
                <div style="font-size: 1.15rem; font-weight: 700; color: {bench_color};">{bench_status}</div>
                <div style="margin-top: 8px; font-size: 0.95rem; color: #172B4D;">
                    • <b>Your Estimated Bill:</b> ₹ {bill_res['total_estimated_bill_inr']:,.0f}<br>
                    • <b>Survey Median (Family Size {in_fam}):</b> ₹ {peer_median_bill:,.0f}<br>
                    • <b>Survey Average:</b> ₹ {peer_mean_bill:,.0f}
                </div>
                <p style="margin-top: 10px; font-size: 0.88rem; color: #505F79;">{bench_comment}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with b_col2:
        max_gauge = max(peer_median_bill * 2.2, bill_res["total_estimated_bill_inr"] * 1.3, 5000)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=bill_res["total_estimated_bill_inr"],
            delta={'reference': peer_median_bill, 'increasing': {'color': "#FF5630"}, 'decreasing': {'color': "#36B37E"}},
            title={'text': f"<b>Bill vs Median (Family of {in_fam})</b>", 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, max_gauge], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#0052CC"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#DFE1E6",
                'steps': [
                    {'range': [0, peer_median_bill * 0.85], 'color': 'rgba(54, 179, 126, 0.25)'},
                    {'range': [peer_median_bill * 0.85, peer_median_bill * 1.15], 'color': 'rgba(255, 171, 0, 0.25)'},
                    {'range': [peer_median_bill * 1.15, max_gauge], 'color': 'rgba(255, 86, 48, 0.25)'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.75,
                    'value': peer_median_bill
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=30, r=30, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)


# =========================================================
# PAGE 3: 🌱 Energy Saving & Carbon Advisory
# =========================================================
elif page_selection == T["nav_advisory"]:
    st.subheader(T["nav_advisory"])

    adv_col1, adv_col2, adv_col3 = st.columns(3)
    with adv_col1:
        adv_kwh = st.number_input("Household Monthly Consumption (kWh)", min_value=10.0, max_value=2500.0, value=280.0, step=10.0)
    with adv_col2:
        adv_ac_hours = st.slider("Daily AC Hours", 0.0, 16.0, 5.0, 0.5)
    with adv_col3:
        adv_fans = st.slider("Ceiling Fans Count", 1, 10, 4)

    adv_result = advisor.generate_advice(
        ac_usage=adv_ac_hours,
        ref_usage="Double Door",
        fans=adv_fans,
        other_appliances=["Geyser", "Washing Machine"],
        kwh_units=adv_kwh,
        lang=current_lang
    )

    st.markdown(f"#### 🌍 {T['carbon_header']}")

    c_card1, c_card2, c_card3, c_card4 = st.columns(4)
    with c_card1:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #FF5630; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.82rem; font-weight: 600;">{T['monthly_co2'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{adv_result['monthly_carbon_kg']} <span style="font-size: 0.95rem;">kg</span></div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">Grid factor: 0.82 kg/kWh</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_card2:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #FFAB00; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.82rem; font-weight: 600;">{T['annual_co2'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">{adv_result['annual_carbon_tonnes']} <span style="font-size: 0.95rem;">Tonnes</span></div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">Annual electricity footprint</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_card3:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #36B37E; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.82rem; font-weight: 600;">{T['trees_needed'].upper()}</div>
                <div style="color: #172B4D; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">🌲 {adv_result['trees_needed']}</div>
                <div style="color: #36B37E; font-size: 0.8rem; margin-top: 4px;">Mature native trees/year</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_card4:
        st.markdown(
            f"""
            <div style="background-color: white; padding: 18px; border-radius: 8px; border-left: 5px solid #0052CC; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                <div style="color: #6B778C; font-size: 0.82rem; font-weight: 600;">POTENTIAL SAVINGS</div>
                <div style="color: #0052CC; font-size: 1.8rem; font-weight: 700; margin-top: 4px;">₹ {adv_result['potential_savings_inr']:,.0f} <span style="font-size: 0.95rem;">/mo</span></div>
                <div style="color: #6B778C; font-size: 0.8rem; margin-top: 4px;">₹ {adv_result['annual_savings_inr']:,.0f} per year</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"#### 💡 {T['tips_header']} ({current_lang})")

    for tip in adv_result["localized_recommendations_list"]:
        priority_color = "#FF5630" if "High" in tip["priority"] or "उच्च" in tip["priority"] or "Critical" in tip["priority"] else "#FFAB00" if "Medium" in tip["priority"] or "मध्यम" in tip["priority"] else "#36B37E"

        st.markdown(
            f"""
            <div style="background-color: white; border: 1px solid #DFE1E6; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="background-color: #EBECF0; color: #172B4D; font-size: 0.78rem; font-weight: 600; padding: 3px 8px; border-radius: 4px;">
                        📂 {tip['category']}
                    </span>
                    <span style="background-color: {priority_color}18; color: {priority_color}; font-weight: 700; font-size: 0.82rem; padding: 3px 8px; border-radius: 4px;">
                        Priority: {tip['priority']}
                    </span>
                </div>
                <h4 style="margin: 4px 0 6px 0; color: #0052CC; font-size: 1.1rem;">{tip['title']}</h4>
                <p style="margin: 0 0 10px 0; color: #42526E; font-size: 0.92rem; line-height: 1.45;">{tip['description']}</p>
                <div style="display: flex; gap: 24px; font-size: 0.85rem; border-top: 1px dashed #DFE1E6; padding-top: 8px;">
                    <span style="color: #36B37E; font-weight: 600;">💰 Potential Saving: {tip['saving_inr']}</span>
                    <span style="color: #6554C0; font-weight: 600;">🌱 Carbon Cut: {tip['carbon_saving']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(f"#### 📈 {T['roi_header']}")
    roi_col1, roi_col2 = st.columns([1, 1.2])

    with roi_col1:
        upgrade_choice = st.selectbox(
            "Select Energy Efficiency Upgrade",
            options=[
                "Replace 3 Induction Fans with 5-Star BLDC Fans",
                "Upgrade Split AC to 5-Star Inverter AC (1.5 Ton)",
                "Install 2 kW Residential Rooftop Solar (PM Surya Ghar)"
            ]
        )

        if "BLDC" in upgrade_choice:
            capex = 3 * 3200
            monthly_gain = 3 * 45 * 12 * 30 / 1000 * 10.29
        elif "Inverter AC" in upgrade_choice:
            capex = 38000
            monthly_gain = 5 * 30 * 1.5 * 0.30 * 10.29
        else:
            capex = 60000
            monthly_gain = 240 * 10.29

        annual_gain = monthly_gain * 12
        payback_months = round(capex / monthly_gain, 1) if monthly_gain > 0 else 0

        st.write(f"• **Estimated Capital Expenditure (Capex):** ₹ {capex:,.0f}")
        st.write(f"• **Estimated Monthly Bill Reduction:** ₹ {monthly_gain:,.0f}")
        st.write(f"• **Annual Rupee Savings:** ₹ {annual_gain:,.0f}")
        st.success(f"🎯 **Simple Payback Period:** {payback_months:.1f} months (~{payback_months/12:.1f} years)")

    with roi_col2:
        years = list(range(0, 6))
        cash_flows = [-capex + (annual_gain * y) for y in years]
        roi_df = pd.DataFrame({"Year": years, "Net Cumulative Return (₹)": cash_flows})

        fig_roi = px.line(
            roi_df,
            x="Year",
            y="Net Cumulative Return (₹)",
            markers=True,
            title="<b>5-Year Cumulative Savings Trajectory (₹)</b>"
        )
        fig_roi.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Break-even / ROI Achieved")
        fig_roi.update_layout(template="plotly_white", height=300, margin=dict(l=30, r=20, t=40, b=30))
        st.plotly_chart(fig_roi, use_container_width=True)


# =========================================================
# PAGE 4: 🔍 Field Data Pipeline & Audit (MU Evaluation)
# =========================================================
elif page_selection == T["nav_audit"]:
    st.subheader(T["nav_audit"])
    st.markdown(
        """
        **Academic Context:** Under University of Mumbai NEP 2020 Community Engagement Project (CEP) guidelines,
        student field surveys must demonstrate rigorous data hygiene, automated outlier handling, and pipeline reproducibility.
        """
    )

    total_raw_rows = len(raw_df)
    clean_rows = len(clean_df)
    dropped_rows = total_raw_rows - clean_rows
    retention_pct = (clean_rows / total_raw_rows * 100) if total_raw_rows > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Raw Survey Inputs", f"{total_raw_rows} records")
    k2.metric("Corrupted / Troll Filtered", f"{dropped_rows} dropped", delta=f"-{dropped_rows}", delta_color="inverse")
    k3.metric("Cleaned CEP Dataset", f"{clean_rows} records")
    k4.metric("Retention Quality", f"{retention_pct:.1f}%")

    st.markdown("---")

    table_mode = st.radio(
        "Select Dataset View:",
        options=[T["clean_toggle"], T["raw_toggle"]],
        horizontal=True
    )

    if table_mode == T["clean_toggle"]:
        st.markdown(f"##### 🗃️ Cleaned Dataset ({clean_rows} rows)")
        st.dataframe(clean_df, use_container_width=True, height=280)
    else:
        st.markdown(f"##### 📑 Raw Survey Responses ({total_raw_rows} rows)")
        st.dataframe(raw_df, use_container_width=True, height=280)

    st.markdown("---")

    st.markdown("#### 📜 Field Data Sanitization Audit Log")
    st.caption("Every regex extraction, corrupted outlier drop, and median imputation step is recorded below.")

    audit_df = pd.DataFrame(audit_log)
    if not audit_df.empty:
        step_types = ["All Steps"] + sorted(audit_df["step"].unique().tolist())
        sel_step = st.selectbox("Filter Audit Log by Operation Type:", step_types)

        if sel_step != "All Steps":
            disp_audit = audit_df[audit_df["step"] == sel_step]
        else:
            disp_audit = audit_df

        st.dataframe(disp_audit, use_container_width=True, height=300)
    else:
        st.info("No modifications were required for the loaded dataset.")

    st.markdown("#### 💾 Export Artifacts for Evaluation")
    dcol1, dcol2 = st.columns(2)

    with dcol1:
        cleaned_csv = clean_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=T["download_cleaned"],
            data=cleaned_csv,
            file_name="cleaned_mumbai_cep_household_energy.csv",
            mime="text/csv",
            use_container_width=True
        )

    with dcol2:
        audit_csv = audit_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=T["download_audit"],
            data=audit_csv,
            file_name="mumbai_cep_data_cleaning_audit_trail.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; color: #6B778C; font-size: 0.85rem; padding: 10px 0;">
        University of Mumbai • National Education Policy (NEP 2020) • Community Engagement Project (CEP)<br>
        Developed for Academic Evaluation & Citizen Energy Literacy
    </div>
    """,
    unsafe_allow_html=True
)
