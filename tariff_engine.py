"""
Mumbai Utility Tariff Engine for Residential Electricity Billing.
Implements slab-wise tariff calculations in compliance with Maharashtra Electricity Regulatory Commission (MERC) orders.
"""

from typing import Dict, Any, List


class MumbaiTariffCalculator:
    """
    Calculates residential electricity bills for Mumbai utility providers (Mahavitaran / MSEDCL, etc.)
    using slab-wise progressive tariff rates.
    """

    # MERC approved residential slab structure for Mahavitaran (MSEDCL)
    MAHAVITARAN_SLABS = [
        {"slab": "0 - 100 units", "min_kwh": 0, "max_kwh": 100, "rate": 4.71, "desc": "Lifeline / Low Consumption"},
        {"slab": "101 - 300 units", "min_kwh": 100, "max_kwh": 300, "rate": 10.29, "desc": "Moderate Consumption"},
        {"slab": "301 - 500 units", "min_kwh": 300, "max_kwh": 500, "rate": 14.55, "desc": "High Consumption"},
        {"slab": "> 500 units", "min_kwh": 500, "max_kwh": float("inf"), "rate": 16.64, "desc": "Very High / Heavy Consumption"},
    ]

    # Fixed single-phase residential demand charge per month in INR
    FIXED_DEMAND_CHARGE = 125.0

    # Fuel Adjustment Charge (FAC) and Maharashtra Electricity Duty combined multiplier
    TAX_AND_DUTY_MULTIPLIER = 0.16  # 16%

    # Indicative alternative utility benchmarks for Mumbai comparisons
    BENCHMARK_PROVIDERS = {
        "Mahavitaran": {
            "fixed_charge": 125.0,
            "tax_rate": 0.16,
            "slabs": [
                (0, 100, 4.71),
                (100, 300, 10.29),
                (300, 500, 14.55),
                (500, float("inf"), 16.64)
            ]
        },
        "Adani Electricity Mumbai": {
            "fixed_charge": 130.0,
            "tax_rate": 0.16,
            "slabs": [
                (0, 100, 4.25),
                (100, 300, 8.85),
                (300, 500, 11.20),
                (500, float("inf"), 13.50)
            ]
        },
        "Tata Power Mumbai": {
            "fixed_charge": 120.0,
            "tax_rate": 0.16,
            "slabs": [
                (0, 100, 4.50),
                (100, 300, 9.10),
                (300, 500, 12.30),
                (500, float("inf"), 14.20)
            ]
        },
        "BEST Undertaking": {
            "fixed_charge": 115.0,
            "tax_rate": 0.16,
            "slabs": [
                (0, 100, 3.80),
                (100, 300, 7.95),
                (300, 500, 11.05),
                (500, float("inf"), 12.90)
            ]
        }
    }

    def __init__(self, provider: str = "Mahavitaran"):
        self.provider = provider

    def calculate_bill(self, kwh_units: float, provider: str = "Mahavitaran") -> Dict[str, Any]:
        """
        Calculate the residential electricity bill for a given consumption in kWh units.

        Parameters:
            kwh_units (float): Total energy consumed in kWh (units) in a billing cycle.
            provider (str): Utility provider name (defaults to 'Mahavitaran').

        Returns:
            dict with:
                - base_charge (float): Fixed monthly demand charge
                - energy_charges (float): Total slab-wise energy charge
                - slab_details (list): Breakdown of units and charge in each slab
                - tax_and_duty (float): Total 16% tax and duty component
                - total_estimated_bill_inr (float): Final calculated monthly bill in INR
                - effective_rate_per_kwh (float): Average effective cost per unit
        """
        if kwh_units is None or kwh_units < 0:
            kwh_units = 0.0
        else:
            kwh_units = float(kwh_units)

        slabs_info = self.MAHAVITARAN_SLABS
        fixed_charge = self.FIXED_DEMAND_CHARGE
        tax_rate = self.TAX_AND_DUTY_MULTIPLIER

        # Custom provider selection if alternative provider requested
        if provider in self.BENCHMARK_PROVIDERS and provider != "Mahavitaran":
            p_config = self.BENCHMARK_PROVIDERS[provider]
            fixed_charge = p_config["fixed_charge"]
            tax_rate = p_config["tax_rate"]
            slabs_info = [
                {"slab": f"{s[0]}-{s[1] if s[1] != float('inf') else '>500'} units",
                 "min_kwh": s[0], "max_kwh": s[1], "rate": s[2], "desc": "Benchmark Slab"}
                for s in p_config["slabs"]
            ]

        slab_details: List[Dict[str, Any]] = []
        total_energy_charge = 0.0
        remaining_units = kwh_units

        for slab_def in slabs_info:
            slab_min = slab_def["min_kwh"]
            slab_max = slab_def["max_kwh"]
            rate = slab_def["rate"]
            slab_capacity = slab_max - slab_min

            if kwh_units > slab_min:
                # Calculate units falling strictly inside this slab
                units_in_slab = min(remaining_units, slab_capacity)
                amount = round(units_in_slab * rate, 2)
                total_energy_charge += amount
                remaining_units -= units_in_slab

                slab_details.append({
                    "slab_name": slab_def["slab"],
                    "description": slab_def["desc"],
                    "units": round(units_in_slab, 2),
                    "rate_per_unit": rate,
                    "amount": amount,
                    "active": units_in_slab > 0
                })
            else:
                slab_details.append({
                    "slab_name": slab_def["slab"],
                    "description": slab_def["desc"],
                    "units": 0.0,
                    "rate_per_unit": rate,
                    "amount": 0.0,
                    "active": False
                })

        subtotal = total_energy_charge + fixed_charge
        tax_and_duty = round(subtotal * tax_rate, 2)
        total_bill = round(subtotal + tax_and_duty, 2)
        effective_rate = round(total_bill / kwh_units, 2) if kwh_units > 0 else 0.0

        return {
            "kwh_units": kwh_units,
            "provider": provider,
            "base_charge": fixed_charge,
            "energy_charges": round(total_energy_charge, 2),
            "slab_details": slab_details,
            "tax_and_duty": tax_and_duty,
            "total_estimated_bill_inr": total_bill,
            "effective_rate_per_kwh": effective_rate
        }

    def compare_all_providers(self, kwh_units: float) -> List[Dict[str, Any]]:
        """
        Compare bill calculations across Mumbai electricity providers for academic benchmark.
        """
        results = []
        for prov in self.BENCHMARK_PROVIDERS.keys():
            res = self.calculate_bill(kwh_units, provider=prov)
            results.append({
                "Provider": prov,
                "Estimated Bill (₹)": res["total_estimated_bill_inr"],
                "Energy Charges (₹)": res["energy_charges"],
                "Effective Rate (₹/unit)": res["effective_rate_per_kwh"]
            })
        return results
