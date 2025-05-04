# -*- coding: utf-8 -*-

import json
import uuid
from flask import Flask, Response, render_template, request, session, jsonify
import utils.utils as utils
from plant import solar as s
from plant import hydrogen as h2
from investment import project

app = Flask(__name__)
app.secret_key = "seminar"
app.url_map.strict_slashes = False # resolve to the canonical version of the endpoint ("endpoint/" -> "endpoint")

app.config['SESSION_COOKIE_SECURE'] = False  # only True if HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", inputs=utils.default_values)


@app.route("/results", methods=["POST"])
def calculate_results():

    if not session.get("user_uuid"):
        obj_id = str(uuid.uuid4())
        session['user_uuid'] = obj_id

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

    p=project.project(project_lifetime,discount_rate,capex,opex,
                      inflation_rate,solar_plant,h2_plant,tax_rate,
                      tangible_capex, intangible_capex,
                      capex_tangible_depreciation,capex_related_depreciation,
                      related_capex_factor,opex_increase_rate,
                      carbon_credit_price)
    
    
    p_dict=p.to_dict()
    
    session["project"]=json.dumps(p_dict)
    
    return render_template(
        "results.html",
        npv=p.npv,
        total_h2_production=round(sum(p.h2_output_flows,2)),
        energy_output=round(sum(p.annual_energy_output_flows,2)),
        annual_revenue=p.annual_revenue_flows,
        total_cash_flow=round(p.total_cash_flow, 2),
        total_discounted_cash_flow=round(p.total_discounted_cash_flow, 2),
        total_cum_npv=round(p.total_cum_npv, 2),
        cap_factor=round(p.solar_plant.cap_factor,2),
        irr= round(p.irr*100,2),
        avoided_co2_equivalents_tons= round(sum(p.tons_co2_equivalent_flows),2),
        breakeven_price_h2=round(p.breakeven_price_h2,2),
        breakeven_price_carbon_credit=round(p.breakeven_price_carbon_credit,2),
        land_required= p.solar_plant.land_required,
        tangible_capex=tangible_capex,
        intangible_capex=intangible_capex,
        slider_input=tangible_capex,
        inputs=request.form
    )


@app.route("/plot-data", methods=["GET"])
def get_plot_data():

    p= session.get("project")

    if p:
        
        p = json.loads(p)
        data_dict={}
        data_dict["avg_monthly_ghi"]=p.get("solar_plant").get("avg_monthly_ghi")
        data_dict["npv"]=project.cum_npv_to_json(p)
        data_dict["irr"]=json.dumps(p.get("irr"), indent=4)
        data_dict["cash_flows"]=project.get_cash_flows(p)
        data_dict["depreciation_schedule"]=project.get_depreciation_schedule(p)
        data_dict["avoided_co2_equivalent"]=project.get_outputs(p)
        data_dict["sensitivity_analysis"]=project.get_sensitivity_analysis(p)
        data_dict["breakeven_h2_price"]=project.calculate_h2_break_even_price_dict(p)
        data_dict["breakeneven_co2_price"]=project.calculate_carbon_credit_break_even_price_dict(p)
        
        return Response(json.dumps(data_dict, sort_keys=False), mimetype='application/json') #jsonify sorts alphabetically

    
    return jsonify({"message": "No project found in session"}), 404


@app.template_filter("format_number")
def format_number(value):
    try:
        return "{:,.2f}".format(value)
    except (TypeError, ValueError):
        return value

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

