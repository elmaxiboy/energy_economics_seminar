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

# NPV Calculation Function
def calculate_npv(project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price):
    results = []
    cash_flows = []
    energy_content_h2= 33.33 #kWh/kg 
    # Convert parameters
    discount_rate /= 100  # Convert to decimal
    total_h2_production = energy_output / (energy_content_h2/(h2_efficiency/100))  # Annual H2 production in kg
    annual_revenue = total_h2_production * h2_price
    
    # Calculate NPV
    for year in range(1, project_lifetime + 1):
        # Net cash flow for the year
        annual_cash_flow = annual_revenue - opex
        cash_flows.append(round(annual_cash_flow, 2))
        
        # Discounted cash flow
        discounted_cf = annual_cash_flow / ((1 + discount_rate) ** year)
        results.append(discounted_cf)
    
    npv = sum(results) - capex  # Subtract initial CapEx
    return round(npv, 2), round(total_h2_production, 2), round(annual_revenue, 2), cash_flows, results

# Function to Generate NPV Graph
def generate_npv_graph(project_lifetime, discounted_cash_flows_with_capex):
    # Cumulative cash flows (including initial CapEx)
    cumulative_npv = np.cumsum(discounted_cash_flows_with_capex)
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


@app.route("/", methods=["GET", "POST"])
def index():
    default_values = {
        "project_lifetime": 20,
        "discount_rate": 8,
        "capex": 15000000,
        "opex": 300000,
        "energy_output": 17520000,
        "h2_efficiency": 55,
        "h2_price": 5
    }
    
    if request.method == "POST":
        project_lifetime = int(request.form["project_lifetime"])
        discount_rate = float(request.form["discount_rate"])
        capex = float(request.form["capex"])
        opex = float(request.form["opex"])
        energy_output = float(request.form["energy_output"])
        h2_efficiency = float(request.form["h2_efficiency"])
        h2_price = float(request.form["h2_price"])
        
        npv, total_h2_production, annual_revenue, cash_flows, discounted_cash_flows = calculate_npv(
            project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price
        )
        
        # Pass the zipped data to the template
        cash_flows = [annual_revenue - opex for _ in range(1, project_lifetime + 1)]
        cash_flow_table = list(zip(range(1, project_lifetime + 1), cash_flows, discounted_cash_flows))

        total_cash_flow = sum(cash_flows) or 0
        total_discounted_cash_flow = sum(discounted_cash_flows) or 0
        
        return render_template(
            "index.html",
            npv=npv,
            total_h2_production=total_h2_production,
            annual_revenue=annual_revenue,
            cash_flow_table=cash_flow_table,
            total_cash_flow=round(total_cash_flow, 2),
            total_discounted_cash_flow=round(total_discounted_cash_flow, 2),
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
    energy_output = float(request.args.get("energy_output", 17520000))
    h2_efficiency = float(request.args.get("h2_efficiency", 55))
    h2_price = float(request.args.get("h2_price", 5))
    
    _, _, _, _, discounted_cash_flows = calculate_npv(
        project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price
    )
    discounted_cash_flows_with_capex = [-capex] + discounted_cash_flows

    img = generate_npv_graph(project_lifetime, discounted_cash_flows_with_capex)
    return send_file(img, mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
