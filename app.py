# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file, url_for, session
import utils
from plant import solar as s
from plant import hydrogen as h2
from investment import project

app = Flask(__name__)
app.secret_key = "seminar"  # Required for Flask-WTF forms


# NPV Calculation Function
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        #Get params from request side
        project_lifetime = int(request.form["project_lifetime"])
        discount_rate = float(request.form["discount_rate"])
        capex = float(request.form["capex"])
        opex = float(request.form["opex"])
        inflation_rate=float(request.form["inflation_rate"])
        tax_rate=float(request.form["tax_rate"])
        electrolyzers_efficiency = float(request.form["electrolyzers_efficiency"])
        h2_price = float(request.form["h2_price"])
        production_decline = float(request.form["prod_decline"])
        installed_cap = float(request.form["installed_cap"])
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])
        panel_efficiency = float(request.form["panel_efficiency"])
        tangible_capex = float(request.form["slider_input"])
        intangible_capex = round(1- tangible_capex,2)
        capex_tangible_depreciation = int(request.form["depr_periods_tangible_capex"])
        capex_related_depreciation = int(request.form["depr_periods_related_capex"])
        related_capex_factor = float(request.form["related_capex_factor"])
        opex_increase_rate = float(request.form["opex_increase_rate"])
        co2_equivalence = float(request.form["co2_equivalence"])
        carbon_credit_price = float(request.form["carbon_credit_price"])
        

        solar_plant = s.solar(installed_cap,latitude,longitude,panel_efficiency, production_decline)
        h2_plant=h2.hydrogen(electrolyzers_efficiency,h2_price,co2_equivalence)

        global p # investment project
 
        p=project.project(project_lifetime,discount_rate,capex,opex,
                          inflation_rate,solar_plant,h2_plant,tax_rate,
                          tangible_capex, intangible_capex,
                          capex_tangible_depreciation,capex_related_depreciation,
                          related_capex_factor,opex_increase_rate,
                          carbon_credit_price)

        
        return render_template(
            "index.html",
            npv=p.npv,
            total_h2_production=round(sum(p.h2_output_flows,2)),
            energy_output=round(sum(p.annual_energy_output_flows,2)),
            annual_revenue=p.annual_revenue_flows,
            total_cash_flow=round(p.total_cash_flow, 2),
            total_discounted_cash_flow=round(p.total_discounted_cash_flow, 2),
            total_cum_npv=round(p.total_cum_npv, 2),
            cap_factor=round(p.solar_plant.cap_factor,2),
            irr= p.irr,
            avoided_co2_equivalents_tons= round(sum(p.tons_co2_equivalent_flows),2),
            breakeven_price_h2=round(p.breakeven_price_h2,2),
            breakeven_price_carbon_credit=round(p.breakeven_price_carbon_credit,2),
            land_required= p.solar_plant.land_required,
            tangible_capex=tangible_capex,
            intangible_capex=intangible_capex,
            slider_input=tangible_capex,
            inputs=request.form
        )
    #rest of allowed methods
    return render_template("index.html", inputs=utils.default_values)

@app.route("/avg-monthly-ghi-graph", methods=["GET"])
def avg_monthly_ghi_graph():  
    return p.solar_plant.avg_monthly_ghi

@app.route("/npv-graph", methods=["GET"])
def npv_graph():  
    json_cum_npv=p.cum_npv_to_json()
    return json_cum_npv

@app.route("/irr", methods=["GET"])
def irr():  
    irr=p.get_irr()
    return irr

@app.route("/cash-flows", methods=["GET"])
def cash_flows():  
    cash_flows=p.get_cash_flows()
    return cash_flows

@app.route("/depreciation-schedule", methods=["GET"])
def depreciation_schedule():  
    cash_flows=p.get_depreciation_schedule()
    return cash_flows

@app.route("/outputs", methods=["GET"])
def outputs():  
    avoided_co2_equivalent=p.get_outputs()
    return avoided_co2_equivalent


@app.route("/sensitivity-analysis", methods=["GET"])
def sensitivity_analysis():  
    sensitivity_analysis=project.get_sensitivity_analysis(p)
    return sensitivity_analysis

@app.route("/breakeven-h2-price", methods=["GET"])
def breakeven_price_h2():  
    breakeven_price=p.calculate_h2_break_even_price()
    return breakeven_price

@app.route("/breakeven-carbon-credit-price", methods=["GET"])
def breakeven_price_carbon_credit():  
    breakeven_price=p.calculate_carbon_credit_break_even_price()
    return breakeven_price

@app.template_filter("format_number")
def format_number(value):
    try:
        return "{:,.2f}".format(value)
    except (TypeError, ValueError):
        return value

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
