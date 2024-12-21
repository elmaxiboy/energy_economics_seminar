# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file
from matplotlib.ticker import FuncFormatter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
app.secret_key = "seminar"  # Required for Flask-WTF forms

#TODO intrayear, cap. factor, capture seasonality


#TODO:include capacity factor of Solar plant, CO2 prices, radiation
# NPV Calculation Function

def calculate_hydrogen_from_energy(mwh, efficiency):
    # Constants
    LHV_HYDROGEN = 33.33  # Lower Heating Value of hydrogen (kWh/kg)
    
    # Convert MWh to kWh
    kwh = mwh * 1000
    
    # Calculate hydrogen production (kg)
    hydrogen_production = (kwh * (efficiency / 100)) / LHV_HYDROGEN
    
    return round(hydrogen_production, 2)

def calculate_npv(project_lifetime, discount_rate, capex, opex, h2_efficiency, h2_price, cap_factor,installed_cap):
    
    discounted_cash_flows = []
    cum_npv = []
    cash_flows = []

    energy_output= installed_cap*(cap_factor/100)*8760 #MWh a year
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



@app.route("/", methods=["GET", "POST"])
def index():
    default_values = {
        "project_lifetime": 20,
        "discount_rate": 8,
        "capex": 15000000,
        "opex": 300000,
        "h2_efficiency": 55,
        "h2_price": 5.5,
        "cap_factor":14.7,
        "installed_cap":3500
    }
    
    if request.method == "POST":
        project_lifetime = int(request.form["project_lifetime"])
        discount_rate = float(request.form["discount_rate"])
        capex = float(request.form["capex"])
        opex = float(request.form["opex"])
        h2_efficiency = float(request.form["h2_efficiency"])
        h2_price = float(request.form["h2_price"])
        cap_factor = float(request.form["cap_factor"])
        installed_cap = float(request.form["installed_cap"])
        
        energy_output,npv, total_h2_production, annual_revenue, cash_flows, discounted_cash_flows,cum_npv = calculate_npv(
            project_lifetime, discount_rate, capex, opex, h2_efficiency, h2_price,cap_factor,installed_cap
        )
        
        # Pass the zipped data to the template
        cash_flows = [annual_revenue - opex for _ in range(0, project_lifetime + 1)]
        cash_flow_table = list(zip(range(0, project_lifetime + 1), cash_flows, discounted_cash_flows,cum_npv))

        total_cash_flow = sum(cash_flows) or 0
        total_discounted_cash_flow = sum(discounted_cash_flows) or 0
        total_cum_npv = cum_npv[-1] or 0
        
        return render_template(
            "index.html",
            npv=npv,
            total_h2_production=total_h2_production,
            energy_output=energy_output,
            annual_revenue=annual_revenue,
            cash_flow_table=cash_flow_table,
            total_cash_flow=round(total_cash_flow, 2),
            total_discounted_cash_flow=round(total_discounted_cash_flow, 2),
            total_cum_npv=round(total_cum_npv, 2),
            inputs=request.form
        )

    return render_template("index.html", inputs=default_values)

@app.template_filter("format_number")
def format_number(value):
    try:
        return "{:,.2f}".format(value)
    except (TypeError, ValueError):
        return value

@app.route("/npv-graph", methods=["GET", "POST"])
def npv_graph():
    project_lifetime = int(request.args.get("project_lifetime", 20))
    discount_rate = float(request.args.get("discount_rate", 8))
    capex = float(request.args.get("capex", 15000000))
    opex = float(request.args.get("opex", 300000))
    h2_efficiency = float(request.args.get("h2_efficiency", 55))
    h2_price = float(request.args.get("h2_price", 5))
    cap_factor = float(request.args.get("cap_factor", 5))
    installed_cap = float(request.args.get("installed_cap", 5))
    
    _,_, _, _, _, _,cum_npv = calculate_npv(
        project_lifetime, discount_rate, capex, opex, h2_efficiency, h2_price,cap_factor,installed_cap
    )
    

    img = generate_npv_graph(project_lifetime, cum_npv)
    return send_file(img, mimetype='image/png')


# Function to Generate NPV Graph
def generate_npv_graph(project_lifetime, discounted_cash_flows_with_capex):
    # Cumulative cash flows (including initial CapEx)
    cumulative_npv = discounted_cash_flows_with_capex
    years = range(0, project_lifetime + 1)  # Include year 0 for CapEx

    def millions_formatter(x, pos):
        return f"${x / 1_000_000:.1f}MM"

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


if __name__ == "__main__":
    app.run(debug=True)
