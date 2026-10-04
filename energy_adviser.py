"""
Community Energy Saving & Carbon Advisory Engine for Mumbai Households.
Generates localized, actionable recommendations in English, Hindi, and Marathi.
"""

from typing import Dict, Any, List, Union


class EnergyAdvisor:
    """
    Analyzes household electrical appliances and consumption patterns to:
    - Compute monthly carbon footprint and ecological offset (trees required).
    - Detect energy inefficiencies specific to Mumbai's coastal humid climate.
    - Provide localized recommendations in English, Hindi, and Marathi with quantified rupee savings.
    """

    # CEA (Central Electricity Authority, India) grid emission factor for Western Region
    GRID_CARBON_INTENSITY = 0.82  # kg CO2 per kWh

    # Average annual CO2 absorption capacity of a mature native tree (e.g. Neem/Peepal)
    TREE_ANNUAL_ABSORPTION_KG = 20.0

    def __init__(self):
        pass

    def calculate_carbon_footprint(self, kwh_units: float) -> Dict[str, float]:
        """
        Calculate carbon emissions and ecological offset requirements.
        """
        kwh = max(0.0, float(kwh_units or 0.0))
        monthly_carbon = round(kwh * self.GRID_CARBON_INTENSITY, 2)
        annual_carbon = round((monthly_carbon * 12) / 1000.0, 2)  # Metric tonnes
        trees_needed = max(1, round((monthly_carbon * 12) / self.TREE_ANNUAL_ABSORPTION_KG)) if monthly_carbon > 0 else 0

        # Eco tier evaluation
        if kwh <= 100:
            tier = "Green Champion (हरित विजेता / ग्रीन चॅम्पियन)"
            tier_code = "A"
        elif kwh <= 250:
            tier = "Moderate Eco Footprint (मध्यम स्तर / मध्यम प्रभाव)"
            tier_code = "B"
        elif kwh <= 450:
            tier = "High Energy Consumer (उच्च वापरकर्ता / उच्च ऊर्जा ग्राहक)"
            tier_code = "C"
        else:
            tier = "Critical Energy Inefficiency (अत्यधिक वापर / गंभीर ऊर्जा अपव्यय)"
            tier_code = "D"

        return {
            "monthly_carbon_kg": monthly_carbon,
            "annual_carbon_tonnes": annual_carbon,
            "trees_needed": trees_needed,
            "eco_tier": tier,
            "tier_code": tier_code
        }

    def generate_advice(
        self,
        ac_usage: Union[float, int, str],
        ref_usage: str,
        fans: Union[float, int, str],
        other_appliances: Union[List[str], str],
        kwh_units: float,
        lang: str = "English"
    ) -> Dict[str, Any]:
        """
        Evaluate household appliances and output targeted recommendations in the specified language.
        """
        kwh = max(0.0, float(kwh_units or 0.0))
        carbon_info = self.calculate_carbon_footprint(kwh)

        # Normalize AC usage hours
        try:
            if isinstance(ac_usage, str):
                import re
                nums = re.findall(r"\d+\.?\d*", ac_usage)
                ac_hours = float(nums[0]) if nums else 0.0
            else:
                ac_hours = float(ac_usage or 0)
        except Exception:
            ac_hours = 0.0

        # Normalize fan count
        try:
            fan_count = float(fans or 0)
        except Exception:
            fan_count = 3.0

        # Normalize appliances list
        if isinstance(other_appliances, str):
            appliance_str = other_appliances.lower()
        elif isinstance(other_appliances, list):
            appliance_str = " ".join(other_appliances).lower()
        else:
            appliance_str = ""

        recommendations = []
        total_potential_savings_inr = 0.0

        # 1. AC Usage Inefficiency Check (> 4 hours daily or non-inverter)
        if ac_hours >= 4.0:
            saving = round(ac_hours * 30 * 1.2 * 0.20 * 10.29, 0)  # 20% savings via 24°C setting & timer
            total_potential_savings_inr += saving
            if lang == "Marathi":
                recommendations.append({
                    "category": "एअर कंडिशनर (AC)",
                    "title": "AC चे तापमान २४° से. वर ठेवा आणि टाइमर वापरा",
                    "description": f"तुमचा रोजचा AC वापर अंदाजे {ac_hours:.0f} तास आहे. AC चे तापमान १८° ऐवजी २४°C वर सेट केल्यास प्रत्येक डिग्रीमागे ६% वीज बचत होते. रात्री २ तासांचा स्लीप टाइमर वापरा.",
                    "saving_inr": f"₹ {saving:,.0f} प्रति महिना",
                    "priority": "उच्च (High)",
                    "carbon_saving": f"{saving * 0.08:.1f} kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "एयर कंडीशनर (AC)",
                    "title": "AC को 24°C पर चलाएं और स्लीप टाइमर सेट करें",
                    "description": f"आपका दैनिक AC उपयोग {ac_hours:.0f} घंटे है। AC को 18° के बजाय 24°C पर रखने से प्रति डिग्री 6% बिजली की बचत होती है। रात को सीलिंग फैन के साथ 24°C का उपयोग करें।",
                    "saving_inr": f"₹ {saving:,.0f} प्रति माह",
                    "priority": "उच्च (High)",
                    "carbon_saving": f"{saving * 0.08:.1f} kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "Air Conditioning",
                    "title": "Optimize AC to 24°C & Activate Sleep Mode",
                    "description": f"Daily AC usage is ~{ac_hours:.0f} hrs. Increasing cooling setpoint from 18°C/20°C to BEE-recommended 24°C saves up to 24% electricity. Pair with ceiling fans for Mumbai humidity.",
                    "saving_inr": f"₹ {saving:,.0f} / month",
                    "priority": "High",
                    "carbon_saving": f"{saving * 0.08:.1f} kg CO₂/mo"
                })
        elif ac_hours > 0:
            saving = 250.0
            total_potential_savings_inr += saving
            if lang == "Marathi":
                recommendations.append({
                    "category": "एअर कंडिशनर (AC)",
                    "title": "AC फिल्टर नियमित स्वच्छ करा",
                    "description": "मुंबईच्या दमट हवेमुळे AC फिल्टरवर धूळ साचते. दर १५ दिवसांनी फिल्टर धुतल्यास कॉम्प्रेसरवरील भार कमी होऊन ५-१०% वीज वाचते.",
                    "saving_inr": f"₹ {saving:,.0f} प्रति महिना",
                    "priority": "मध्यम (Medium)",
                    "carbon_saving": "20.5 kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "एयर कंडीशनर (AC)",
                    "title": "AC एयर फिल्टर की नियमित सफाई करें",
                    "description": "मुंबई की आर्द्र हवा में धूल जमने से कंप्रेसर पर लोड बढ़ता है। हर 15 दिनों में फिल्टर धोने से 5-10% बिजली की खपत घटती है।",
                    "saving_inr": f"₹ {saving:,.0f} प्रति माह",
                    "priority": "मध्यम (Medium)",
                    "carbon_saving": "20.5 kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "Air Conditioning",
                    "title": "Fortnightly Air Filter Cleaning",
                    "description": "Coastal dust clogs evaporator coils rapidly in Mumbai. Regular fortnightly filter washing prevents compressor overworking and cuts energy drain by 5-10%.",
                    "saving_inr": f"₹ {saving:,.0f} / month",
                    "priority": "Medium",
                    "carbon_saving": "20.5 kg CO₂/mo"
                })

        # 2. Ceiling Fans: BLDC Upgrade Opportunity
        if fan_count >= 2:
            saving_bldc = round(fan_count * 45 * 12 * 30 / 1000 * 8.5, 0)
            total_potential_savings_inr += saving_bldc
            if lang == "Marathi":
                recommendations.append({
                    "category": "पंखे (Ceiling Fans)",
                    "title": "पारंपारिक पंख्यांऐवजी 5-Star BLDC पंखे वापरा",
                    "description": f"घरात {fan_count:.0f} पंखे आहेत. जुने पंखे ७५W वीज वापरतात तर BLDC पंखे फक्त २८W घेतात. यामुळे ६०% विजेची थेट बचत होते आणि पेबॅक अवघ्या १२-१४ महिन्यांत मिळतो.",
                    "saving_inr": f"₹ {saving_bldc:,.0f} प्रति महिना",
                    "priority": "मध्यम (Medium)",
                    "carbon_saving": f"{saving_bldc * 0.09:.1f} kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "पंखे (Ceiling Fans)",
                    "title": "पुराने पंखों को 5-स्टार BLDC पंखों से बदलें",
                    "description": f"आपके घर में {fan_count:.0f} पंखे हैं। पारंपरिक पंखे 75W खपत करते हैं जबकि आधुनिक BLDC पंखे सिर्फ 28W लेते हैं। इससे पंखों के बिजली बिल में 60% तक कमी आएगी।",
                    "saving_inr": f"₹ {saving_bldc:,.0f} प्रति माह",
                    "priority": "मध्यम (Medium)",
                    "carbon_saving": f"{saving_bldc * 0.09:.1f} kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "Ceiling Fans",
                    "title": "Switch to 5-Star Brushless DC (BLDC) Smart Fans",
                    "description": f"With {fan_count:.0f} active fans, conventional induction fans consume ~75W each, whereas BLDC motors consume only ~28W. Offers 60%+ drop in continuous fan load.",
                    "saving_inr": f"₹ {saving_bldc:,.0f} / month",
                    "priority": "Medium",
                    "carbon_saving": f"{saving_bldc * 0.09:.1f} kg CO₂/mo"
                })

        # 3. Water Geyser / Heating Appliances Inefficiency Check
        if "geyser" in appliance_str or "heater" in appliance_str or kwh > 200:
            saving_geyser = 320.0
            total_potential_savings_inr += saving_geyser
            if lang == "Marathi":
                recommendations.append({
                    "category": "गीझर / वॉटर हीटर",
                    "title": "गीझर थर्मोस्टॅट ५०° से. वर ठेवा आणि १५ मिनिटांत बंद करा",
                    "description": "वॉटर गीझर २,००० ते ३,००० वॅट वीज खेचतो. नळ चालू ठेवण्यापूर्वी थर्मोस्टॅट ५०°C वर मर्यादित करा आणि आंघोळीनंतर ताबडतोब स्विच बंद करा.",
                    "saving_inr": f"₹ {saving_geyser:,.0f} प्रति महिना",
                    "priority": "उच्च (High)",
                    "carbon_saving": "26.2 kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "गीजर / वाटर हीटर",
                    "title": "गीजर थर्मोस्टेट को 50°C पर सेट करें और उपयोग बाद बंद करें",
                    "description": "गीजर 2000W-3000W का भारी लोड लेता है। इसे हमेशा चालू न छोड़ें और थर्मोस्टेट को 50°C पर रखें। 15-20 मिनट पहले चालू करके बंद कर दें।",
                    "saving_inr": f"₹ {saving_geyser:,.0f} प्रति माह",
                    "priority": "उच्च (High)",
                    "carbon_saving": "26.2 kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "Water Heating",
                    "title": "Calibrate Geyser Thermostat to 50°C & Avoid Idling",
                    "description": "Electric geysers draw 2,000-3,000W. Limiting thermostat cutoff to 50°C instead of 65°C and switching off right after heating stops standby thermal losses.",
                    "saving_inr": f"₹ {saving_geyser:,.0f} / month",
                    "priority": "High",
                    "carbon_saving": "26.2 kg CO₂/mo"
                })

        # 4. Refrigerator Efficiency Check
        saving_ref = 180.0
        total_potential_savings_inr += saving_ref
        if lang == "Marathi":
            recommendations.append({
                "category": "रेफ्रिजरेटर",
                "title": "फ्रिज भिंतीपासून ६ इंच दूर ठेवा आणि डीफ्रॉस्ट करा",
                "description": "कंडेन्सर कॉइलभोवती पुरेशी हवा खेळती राहण्यासाठी फ्रिज भिंतीपासून दूर ठेवा. फ्रीझरमध्ये बर्फाचा जाड थर साचू देऊ नका आणि गरम अन्न थेट ठेवू नका.",
                "saving_inr": f"₹ {saving_ref:,.0f} प्रति महिना",
                "priority": "कमी (Low)",
                "carbon_saving": "14.8 kg CO₂/महिना"
            })
        elif lang == "Hindi":
            recommendations.append({
                "category": "रेफ्रिजरेटर",
                "title": "फ्रिज को दीवार से 6 इंच दूर रखें व नियमित डीफ्रॉस्ट करें",
                "description": "फ्रिज के पीछे वेंटिलेशन के लिए जगह रखें। फ्रीजर में बर्फ की मोटी परत न जमने दें और गर्म खाना सीधे फ्रिज में न रखें।",
                "saving_inr": f"₹ {saving_ref:,.0f} प्रति माह",
                "priority": "कम (Low)",
                "carbon_saving": "14.8 kg CO₂/माह"
            })
        else:
            recommendations.append({
                "category": "Refrigeration",
                "title": "Maintain 6-inch Wall Clearance & Defrost Regularly",
                "description": "Ensure rear condenser coils have ample airflow. Do not place hot vessels directly inside; defrost coils whenever frost exceeds 5mm to cut compressor load.",
                "saving_inr": f"₹ {saving_ref:,.0f} / month",
                "priority": "Low",
                "carbon_saving": "14.8 kg CO₂/mo"
            })

        # 5. High Consumption Slab Penalty Protection (>300 kWh)
        if kwh > 300:
            saving_slab = round((kwh - 300) * (14.55 - 10.29), 0)
            total_potential_savings_inr += max(400.0, saving_slab)
            if lang == "Marathi":
                recommendations.append({
                    "category": "MERC स्लॅब दर नियंत्रण",
                    "title": "वीज वापर ३०० युनिट्सच्या खाली आणून उच्च स्लॅब टाळा",
                    "description": f"तुमचा वापर {kwh:.0f} युनिट्स असल्याने तुम्ही महावितरणच्या ₹१४.५५/युनिटच्या महागड्या स्लॅबमध्ये आहात. ३०० युनिट्सच्या आत राहिल्यास थेट उच्च स्लॅबचा भुर्दंड टळेल.",
                    "saving_inr": f"₹ {max(400.0, saving_slab):,.0f} प्रति महिना",
                    "priority": "अति उच्च (Critical)",
                    "carbon_saving": "45.0 kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "MERC स्लैब टैरिफ नियंत्रण",
                    "title": "खपत को 300 यूनिट से नीचे लाकर महंगे स्लैब से बचें",
                    "description": f"वर्तमान में आपका उपभोग {kwh:.0f} यूनिट है, जिससे आप ₹14.55/यूनिट वाले तीसरे स्लैब में आते हैं। संयमित उपयोग से 300 यूनिट के नीचे रहने पर भारी बचत होगी।",
                    "saving_inr": f"₹ {max(400.0, saving_slab):,.0f} प्रति माह",
                    "priority": "अति उच्च (Critical)",
                    "carbon_saving": "45.0 kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "MERC Tariff Protection",
                    "title": "Curtail Usage Below 300 kWh to Dodge Punitive Slabs",
                    "description": f"Current consumption of {kwh:.0f} units exposes your bill to the steep ₹14.55/unit slab (>300 kWh). Trimming just 10-15% consumption prevents falling into upper slabs.",
                    "saving_inr": f"₹ {max(400.0, saving_slab):,.0f} / month",
                    "priority": "Critical",
                    "carbon_saving": "45.0 kg CO₂/mo"
                })

        # 6. PM Surya Ghar Muft Bijli Solar Opportunity (for high consumers)
        if kwh > 250:
            solar_saving = min(2800.0, round(kwh * 7.5, 0))
            if lang == "Marathi":
                recommendations.append({
                    "category": "सौर ऊर्जा (Rooftop Solar)",
                    "title": "पीएम सूर्य घर मुफ्त बिजली योजनेचा लाभ घ्या",
                    "description": "छतावर २ kW सौर प्रकल्प बसवून केंद्र सरकारचे ₹६०,००० ते ₹७८,००० अनुदान मिळवा. यामुळे मासिक वीज बिल ८०-९०% पर्यंत शून्य होऊ शकते.",
                    "saving_inr": f"₹ {solar_saving:,.0f} प्रति महिना",
                    "priority": "दीर्घकालीन (Long Term)",
                    "carbon_saving": f"{kwh * 0.7:.0f} kg CO₂/महिना"
                })
            elif lang == "Hindi":
                recommendations.append({
                    "category": "रूफटॉप सोलर",
                    "title": "पीएम सूर्य घर मुफ्त बिजली योजना अपनाएं",
                    "description": "2 kW के रूफटॉप सोलर सिस्टम पर केंद्र सरकार की ₹60,000-₹78,000 सब्सिडी उपलब्ध है। इससे आपका मासिक बिजली बिल 80% तक शून्य हो सकता है।",
                    "saving_inr": f"₹ {solar_saving:,.0f} प्रति माह",
                    "priority": "दीर्घकालिक (Long Term)",
                    "carbon_saving": f"{kwh * 0.7:.0f} kg CO₂/माह"
                })
            else:
                recommendations.append({
                    "category": "Rooftop Solar",
                    "title": "Adopt PM Surya Ghar Muft Bijli Solar Subsidy",
                    "description": "Eligible for up to ₹78,000 Central subsidy for a 2-3 kW residential rooftop solar array, reducing grid reliance and near-zero monthly electricity bills.",
                    "saving_inr": f"₹ {solar_saving:,.0f} / month",
                    "priority": "Long Term",
                    "carbon_saving": f"{kwh * 0.7:.0f} kg CO₂/mo"
                })

        annual_savings_inr = total_potential_savings_inr * 12

        return {
            "kwh_units": kwh,
            "monthly_carbon_kg": carbon_info["monthly_carbon_kg"],
            "annual_carbon_tonnes": carbon_info["annual_carbon_tonnes"],
            "trees_needed": carbon_info["trees_needed"],
            "eco_tier": carbon_info["eco_tier"],
            "tier_code": carbon_info["tier_code"],
            "potential_savings_inr": round(total_potential_savings_inr, 2),
            "annual_savings_inr": round(annual_savings_inr, 2),
            "localized_recommendations_list": recommendations
        }
