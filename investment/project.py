
import requests
import pandas as pd
import json
from plant import solar as s
from plant import hydrogen as h2
import utils

class project:
    def __init__(self,project_lifetime: int, interest_rate: float, capex: float, opex: float, solar_plant: s, h2_plant: h2):
        """
        Initializes an investment project.
        """
        self.interest_rate = interest_rate
        self.project_lifetime = project_lifetime
        self.capex = capex
        self.opex = opex
        self.solar_plant = solar_plant
        self.hydrogen_plant = h2_plant
        self.npv = None
        self.cum_npv = None
        self.cash_flows = None
        self.annual_revenue = None

    def calculate_npv(self):
    
        discounted_cash_flows = []
        cum_npv = []
        cash_flows = []

 
        # Convert parameters
        self.interest_rate /= 100  # Convert to decimal
        annual_energy_output = self.solar_plant.annual_production_mwh
        total_h2_production = self.hydrogen_plant.calculate_hydrogen_from_energy(annual_energy_output) # Annual H2 production in kg
        annual_revenue = total_h2_production * self.hydrogen_plant.h2_price

        cum_npv.append(-self.capex)  # Initial investment at Year 1
        discounted_cash_flows.append(0)
        cash_flows.append(0)
    
        # Calculate NPV
        for year in range(1, self.project_lifetime + 1):
            # Net cash flow for the year
            annual_cash_flow = annual_revenue - self.opex
            cash_flows.append(round(annual_cash_flow, 2))
        
            # Discounted cash flow
            discounted_cf = annual_cash_flow / ((1 + self.interest_rate) ** year)
            cum_npv.append(cum_npv[-1] + discounted_cf)
            discounted_cash_flows.append(discounted_cf)
    
        self.npv = sum(discounted_cash_flows) - self.capex  # Subtract initial CapEx
        self.cum_npv = cum_npv
        self.cash_flows = cash_flows
        self.discounted_cash_flows = discounted_cash_flows
        self.annual_revenue = annual_revenue

        return self

    def cum_npv_to_json(self):
        dict_with_indexes = {index: value for index, value in enumerate(self.cum_npv)}
        return json.dumps(dict_with_indexes)
