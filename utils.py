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


def calculate_npv(project_lifetime, discount_rate, capex, opex, h2_efficiency, h2_price, energy_output):
    
    discounted_cash_flows = []
    cum_npv = []
    cash_flows = []

 
    # Convert parameters
    discount_rate /= 100  # Convert to decimal
    total_h2_production = calculate_hydrogen_from_energy(energy_output,h2_efficiency)  # Annual H2 production in kg
    annual_revenue = total_h2_production * h2_price

    cum_npv.append(-capex)  # Initial investment at Year 1
    discounted_cash_flows.append(0)
    cash_flows.append(0)
    
    # Calculate NPV
    for year in range(1, project_lifetime + 1):
        # Net cash flow for the year
        annual_cash_flow = annual_revenue - opex
        cash_flows.append(round(annual_cash_flow, 2))
        
        # Discounted cash flow
        discounted_cf = annual_cash_flow / ((1 + discount_rate) ** year)
        cum_npv.append(cum_npv[-1] + discounted_cf)
        discounted_cash_flows.append(discounted_cf)
    
    npv = sum(discounted_cash_flows) - capex  # Subtract initial CapEx
    return round(energy_output, 2),round(npv, 2), round(total_h2_production, 2), round(annual_revenue, 2), cash_flows, discounted_cash_flows,cum_npv


def generate_npv_graph(project_lifetime, discounted_cash_flows_with_capex):
    # Cumulative cash flows (including initial CapEx)
    cumulative_npv = discounted_cash_flows_with_capex
    years = range(0, project_lifetime + 1)  # Include year 0 for CapEx 

    # Plot the graph
    plt.figure(figsize=(10, 6))
    plt.plot(years, cumulative_npv, marker='o', label='Cumulative NPV')
    plt.axhline(0, color='gray', linestyle='--', label='Break-Even Line')
    plt.title("Cumulative NPV Over Project Lifetime", fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Cumulative NPV (USD)", fontsize=14)
    plt.legend(fontsize=12)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    plt.grid(True)

    # Save the plot to BytesIO for dynamic serving
    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plt.close()
    return img


def millions_formatter(x, pos):
        return f"${x / 1_000_000:.1f}MM"
