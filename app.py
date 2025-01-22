# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file, url_for
import utils
from plant import solar as s
from plant import hydrogen as h2
from investment import project

app = Flask(__name__)
app.secret_key = "seminar"  # Required for Flask-WTF forms

#TODO: CO2 prices, capture seasonality


# NPV Calculation Function
@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":

        #Get params from request side
        project_lifetime = int(request.form["project_lifetime"])
        discount_rate = float(request.form["discount_rate"])
        capex = float(request.form["capex"])
        opex = float(request.form["opex"])
        h2_efficiency = float(request.form["h2_efficiency"])
        h2_price = float(request.form["h2_price"])
        installed_cap = float(request.form["installed_cap"])
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])


        solar_plant = s.solar(installed_cap,latitude,longitude)
        h2_plant=h2.hydrogen(h2_efficiency,h2_price)

        global p # investment project
 
        p=project.project(project_lifetime,discount_rate,capex,opex,solar_plant,h2_plant)

        p.solar_plant.calculate_avg_monthly_ghi()
        energy_output=p.solar_plant.calculate_annual_production(0.15)# 0.15% panel efficiency
        cap_factor=p.solar_plant.calculate_capacity_factor()
        
        p.calculate_npv()
        p.calculate_irr()
        
        # Pass the zipped data to the template
        cash_flow_table = list(zip(range(0, project_lifetime + 1), p.cash_flows, p.discounted_cash_flows,p.cum_npv))

        total_cash_flow = sum(p.cash_flows) or 0
        total_discounted_cash_flow = sum(p.discounted_cash_flows) or 0
        total_cum_npv = p.cum_npv[-1] or 0
        
        return render_template(
            "index.html",
            npv=p.npv,
            total_h2_production=p.hydrogen_plant.h2_output,
            energy_output=energy_output,
            annual_revenue=p.annual_revenue,
            cash_flow_table=cash_flow_table,
            total_cash_flow=round(total_cash_flow, 2),
            total_discounted_cash_flow=round(total_discounted_cash_flow, 2),
            total_cum_npv=round(total_cum_npv, 2),
            cap_factor=round(cap_factor,2),
            irr= p.irr,
            inputs=request.form
        )
    #rest of allowed methods
    return render_template("index.html", inputs=utils.default_values)
    
#TODO: Avoid calling twice npv_calculation for plotting

@app.route("/avg-monthly-ghi-graph", methods=["GET", "POST"])
def avg_monthly_ghi_graph():  
    return p.solar_plant.avg_monthly_ghi

@app.route("/npv-graph", methods=["GET", "POST"])
def npv_graph():  
    json_cum_npv=p.cum_npv_to_json()
    return json_cum_npv

@app.route("/irr", methods=["GET", "POST"])
def irr():  
    irr=p.get_irr()
    return irr

@app.route("/cash-flows", methods=["GET", "POST"])
def cash_flows():  
    cash_flows=p.get_cash_flows()
    return cash_flows



@app.template_filter("format_number")
def format_number(value):
    try:
        return "{:,.2f}".format(value)
    except (TypeError, ValueError):
        return value

if __name__ == "__main__":
    app.run(debug=True)
