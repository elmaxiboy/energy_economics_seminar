import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from matplotlib.ticker import FuncFormatter

default_values = {
        "project_lifetime": 20,
        "discount_rate": 8,
        "capex": 15000000,
        "opex": 300000,
        "h2_efficiency": 55,
        "h2_price": 5.5,
        "cap_factor":14.7,
        "installed_cap":15,
        "latitude":-23.8634,
        "longitude":-69.1328
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
