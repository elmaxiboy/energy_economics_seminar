# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, send_file, url_for
import utils
from plant import solar,hydrogen

app = Flask(__name__)
app.secret_key = "seminar"  # Required for Flask-WTF forms

#TODO: CO2 prices, radiation,intrayear, capture seasonality



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
        #cap_factor = float(request.form["cap_factor"])
        installed_cap = float(request.form["installed_cap"])
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])

        global solar_plant
        solar_plant = solar.solar(installed_cap,latitude,longitude)
        h2_plant=hydrogen.hydrogen(h2_efficiency,h2_price)

        solar_plant.calculate_avg_monthly_ghi()
        energy_output2=solar_plant.calculate_annual_production(0.15)# 20% panel efficiency
        cap_factor=solar_plant.calculate_capacity_factor()

        
        (energy_output,
        npv,
        total_h2_production,
        annual_revenue,
        cash_flows,
        discounted_cash_flows,
        cum_npv) = utils.calculate_npv(
            project_lifetime,
            discount_rate,
            capex,
            opex,
            h2_efficiency,
            h2_price,
            energy_output2)
        
        # Pass the zipped data to the template
        cash_flow_table = list(zip(range(0, project_lifetime + 1), cash_flows, discounted_cash_flows,cum_npv))

        total_cash_flow = sum(cash_flows) or 0
        total_discounted_cash_flow = sum(discounted_cash_flows) or 0
        total_cum_npv = cum_npv[-1] or 0
        
        return render_template(
            "index.html",
            npv=npv,
            total_h2_production=total_h2_production,
            energy_output=energy_output,
            energy_output2=energy_output2,
            annual_revenue=annual_revenue,
            cash_flow_table=cash_flow_table,
            total_cash_flow=round(total_cash_flow, 2),
            total_discounted_cash_flow=round(total_discounted_cash_flow, 2),
            total_cum_npv=round(total_cum_npv, 2),
            cap_factor=round(cap_factor,2),
            inputs=request.form
        )
    #rest of allowed methods
    return render_template("index.html", inputs=utils.default_values)
    
#TODO: Avoid calling twice npv_calculation for plotting

@app.route("/avg-monthly-ghi-graph", methods=["GET", "POST"])
def avg_monthly_ghi_graph():  
    return solar_plant.avg_monthly_ghi

@app.route("/npv-graph", methods=["GET", "POST"])
def npv_graph():  
    return solar_plant.avg_monthly_ghi


@app.route("/npv-graph", methods=["GET", "POST"])
def npv_graph():
    project_lifetime = int(request.args.get("project_lifetime", 20))
    discount_rate = float(request.args.get("discount_rate", 8))
    capex = float(request.args.get("capex", 15000000))
    opex = float(request.args.get("opex", 300000))
    h2_efficiency = float(request.args.get("h2_efficiency", 55))
    h2_price = float(request.args.get("h2_price", 5))
    cap_factor = solar_plant.cap_factor
    installed_cap = float(request.args.get("installed_cap", 5))
    
    _,_, _, _, _, _,cum_npv = utils.calculate_npv(
        project_lifetime, discount_rate, capex, opex, h2_efficiency, h2_price,solar_plant.annual_production_mwh)

    img = utils.generate_npv_graph(project_lifetime, cum_npv)

    return send_file(img, mimetype='image/png') #Multipurpose Internet Mail Extensions

@app.template_filter("format_number")
def format_number(value):
    try:
        return "{:,.2f}".format(value)
    except (TypeError, ValueError):
        return value

if __name__ == "__main__":
    app.run(debug=True)
