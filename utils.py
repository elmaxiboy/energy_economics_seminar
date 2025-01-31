import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from matplotlib.ticker import FuncFormatter

default_values = {
        "project_lifetime": 20,
        "discount_rate": 8,
        "capex": 300000000,
        "opex": 30000000,
        "tax_rate":22.5,
        "electrolyzers_efficiency": 55,
        "h2_price": 5.5,
        "cap_factor":14.7,
        "installed_cap":300,
        "latitude":39.338160,
        "longitude":87.511127,
        "panel_efficiency": 22,
        "inflation_rate": 2.75,
        "prod_decline":0.5,
        "tangible_capex":0.2,
        "intangible_capex":0.8,
        "slider_input":0.2,
        "depr_periods_tangible_capex":10,
        "depr_periods_related_capex":15,
        "related_capex_factor":11,
        "opex_increase_rate":0.025,
        "co2_equivalence": 22.87,
        "carbon_credit_price":5
    }

def calculate_hydrogen_from_energy(mwh, efficiency):
    # Constants
    LHV_HYDROGEN = 33.33  # Lower Heating Value of hydrogen (kWh/kg)
    
    # Convert MWh to kWh
    kwh = mwh * 1000
    
    # Calculate hydrogen production (kg)
    hydrogen_production = (kwh * (efficiency / 100)) / LHV_HYDROGEN
    
    return round(hydrogen_production, 2)


def millions_formatter(x, pos):
        return f"${x / 1_000_000:.1f}MM"
