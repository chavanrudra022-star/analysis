"""
Unit & Integration Tests for Mumbai University CEP Energy Analytics Components.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.tariff_engine import MumbaiTariffCalculator
from src.energy_adviser import EnergyAdvisor
from src.data_processor import SurveyDataCleaner


class TestMumbaiTariffCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = MumbaiTariffCalculator()

    def test_zero_units(self):
        res = self.calc.calculate_bill(0)
        self.assertEqual(res["base_charge"], 125.0)
        self.assertEqual(res["energy_charges"], 0.0)
        # Tax: 125 * 0.16 = 20.0
        self.assertEqual(res["tax_and_duty"], 20.0)
        self.assertEqual(res["total_estimated_bill_inr"], 145.0)

    def test_slab_1_calculation(self):
        # 80 units @ 4.71 = 376.80
        # Subtotal: 376.80 + 125.0 = 501.80
        # Tax (16%): 80.29
        # Total: 582.09
        res = self.calc.calculate_bill(80)
        self.assertAlmostEqual(res["energy_charges"], 376.80, places=2)
        self.assertAlmostEqual(res["total_estimated_bill_inr"], 582.09, places=2)
        self.assertEqual(len(res["slab_details"]), 4)
        self.assertEqual(res["slab_details"][0]["units"], 80)
        self.assertEqual(res["slab_details"][1]["units"], 0)

    def test_slab_2_progressive_calculation(self):
        # 250 units:
        # Slab 1 (100 units): 100 * 4.71 = 471.0
        # Slab 2 (150 units): 150 * 10.29 = 1543.50
        # Energy charge: 2014.50
        # Subtotal: 2014.50 + 125 = 2139.50
        # Tax: 2139.50 * 0.16 = 342.32
        # Total: 2481.82
        res = self.calc.calculate_bill(250)
        self.assertAlmostEqual(res["energy_charges"], 2014.50, places=2)
        self.assertAlmostEqual(res["total_estimated_bill_inr"], 2481.82, places=2)
        self.assertEqual(res["slab_details"][0]["units"], 100)
        self.assertEqual(res["slab_details"][1]["units"], 150)
        self.assertEqual(res["slab_details"][2]["units"], 0)

    def test_upper_slabs(self):
        # 550 units:
        # 0-100: 471.0
        # 101-300: 200 * 10.29 = 2058.0
        # 301-500: 200 * 14.55 = 2910.0
        # >500: 50 * 16.64 = 832.0
        # Energy: 6271.0
        # Subtotal: 6271 + 125 = 6396.0
        # Tax: 6396 * 0.16 = 1023.36
        # Total: 7419.36
        res = self.calc.calculate_bill(550)
        self.assertAlmostEqual(res["energy_charges"], 6271.0, places=2)
        self.assertAlmostEqual(res["total_estimated_bill_inr"], 7419.36, places=2)
        self.assertEqual(res["slab_details"][3]["units"], 50)


class TestEnergyAdvisor(unittest.TestCase):
    def setUp(self):
        self.advisor = EnergyAdvisor()

    def test_carbon_calculation(self):
        # 100 kWh * 0.82 = 82.0 kg CO2
        res = self.advisor.calculate_carbon_footprint(100)
        self.assertAlmostEqual(res["monthly_carbon_kg"], 82.0, places=2)
        self.assertAlmostEqual(res["annual_carbon_tonnes"], 0.98, places=2)
        self.assertGreater(res["trees_needed"], 0)

    def test_multilingual_advice(self):
        for lang in ["English", "Hindi", "Marathi"]:
            adv = self.advisor.generate_advice(
                ac_usage=6.0,
                ref_usage="Single Door",
                fans=4,
                other_appliances=["Geyser", "Washing Machine"],
                kwh_units=350,
                lang=lang
            )
            self.assertIn("localized_recommendations_list", adv)
            self.assertGreater(len(adv["localized_recommendations_list"]), 0)
            self.assertGreater(adv["potential_savings_inr"], 0)
            # Ensure titles and descriptions are populated
            for tip in adv["localized_recommendations_list"]:
                self.assertTrue(len(tip["title"]) > 0)
                self.assertTrue(len(tip["description"]) > 0)


class TestSurveyDataCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = SurveyDataCleaner()

    def test_regex_cleaning(self):
        # Test messy inputs from survey
        val1, _ = self.cleaner.clean_numeric_string("900kh")
        self.assertEqual(val1, 900.0)

        val2, _ = self.cleaner.clean_numeric_string("150-200 units")
        self.assertEqual(val2, 175.0)

        val3, _ = self.cleaner.clean_numeric_string("900W")
        self.assertEqual(val3, 900.0)

        val4, _ = self.cleaner.clean_numeric_string("Rs. 2,450/-")
        self.assertEqual(val4, 2450.0)

        val5, _ = self.cleaner.clean_numeric_string("na")
        self.assertIsNone(val5)

        val6, _ = self.cleaner.clean_numeric_string("4 members")
        self.assertEqual(val6, 4.0)

    def test_load_and_clean_pipeline(self):
        raw_df, clean_df, audit_log = self.cleaner.load_and_clean_data(None)
        self.assertFalse(raw_df.empty)
        self.assertFalse(clean_df.empty)
        self.assertTrue(len(audit_log) > 0)

        # Check that realistic bounds hold on cleaned data
        self.assertTrue((clean_df["family_members"] >= 1).all())
        self.assertTrue((clean_df["family_members"] <= 15).all())
        self.assertTrue((clean_df["monthly_bill_inr"] >= 100).all())
        self.assertTrue((clean_df["monthly_bill_inr"] <= 50000).all())
        self.assertTrue((clean_df["kwh_units"] >= 10).all())
        self.assertTrue((clean_df["kwh_units"] <= 3000).all())

        # Check no remaining NaNs in numeric columns
        for col in self.cleaner.NUMERIC_COLUMNS:
            self.assertFalse(clean_df[col].isna().any(), f"Column {col} has unhandled NaNs")


if __name__ == "__main__":
    unittest.main()
