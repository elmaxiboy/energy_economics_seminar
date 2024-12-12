# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file
import numpy as np
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for Flask-WTF forms

# NPV Calculation Function
def calculate_npv(project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price):
    results = []
    cash_flows = []
    
    # Convert parameters
    discount_rate /= 100  # Convert to decimal
    total_h2_production = energy_output / h2_efficiency  # Annual H2 production in kg
    annual_revenue = total_h2_production * h2_price
    
    # Calculate NPV
    for year in range(1, project_lifetime + 1):
        # Net cash flow for the year
        annual_cash_flow = annual_revenue - opex
        cash_flows.append(annual_cash_flow)
        
        # Discounted cash flow
        discounted_cf = annual_cash_flow / ((1 + discount_rate) ** year)
        results.append(discounted_cf)
    
    npv = sum(results) - capex  # Subtract initial CapEx
    return round(npv, 2), round(total_h2_production, 2), round(annual_revenue, 2), results

# Function to Generate NPV Graph
def generate_npv_graph(project_lifetime, results):
    # Cumulative NPV over time
    cumulative_npv = np.cumsum(results)
    years = range(1, project_lifetime + 1)
    
    # Plot the graph
    plt.figure(figsize=(10, 6))
    plt.plot(years, cumulative_npv, marker='o', label='Cumulative NPV')
    plt.axhline(0, color='gray', linestyle='--', label='Break-Even Line')
    plt.title("Cumulative NPV Over Project Lifetime", fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Cumulative NPV (USD)", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    return img

# Flask Routes
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
        
        npv, total_h2_production, annual_revenue, cash_flows = calculate_npv(
            project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price
        )
        
        return render_template(
            "index.html",
            npv=npv,
            total_h2_production=total_h2_production,
            annual_revenue=annual_revenue,
            inputs=request.form
        )

    return render_template("index.html", inputs=default_values)

@app.route("/npv-graph", methods=["POST"])
def npv_graph():
    project_lifetime = int(request.form["project_lifetime"])
    discount_rate = float(request.form["discount_rate"])
    capex = float(request.form["capex"])
    opex = float(request.form["opex"])
    energy_output = float(request.form["energy_output"])
    h2_efficiency = float(request.form["h2_efficiency"])
    h2_price = float(request.form["h2_price"])
    
    _, _, _, discounted_cash_flows = calculate_npv(
        project_lifetime, discount_rate, capex, opex, energy_output, h2_efficiency, h2_price
    )
    
    img = generate_npv_graph(project_lifetime, discounted_cash_flows)
    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
