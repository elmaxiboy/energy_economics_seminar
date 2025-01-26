
import requests
import pandas as pd
import json
from plant import solar as s
from plant import hydrogen as h2
import utils
import numpy_financial as npf
import math 
import copy

class project:
    def __init__(self,project_lifetime: int, interest_rate: float, capex: float, opex: float, inflation_rate: float, solar_plant: s, h2_plant: h2, tax_rate):
        """
        Initializes an investment project.
        """
        self.interest_rate = interest_rate
        self.project_lifetime = project_lifetime
        self.capex = capex
        self.opex = opex
        self.opex_increase_rate=0.025 
        self.inflation_rate = inflation_rate
        self.solar_plant = solar_plant
        self.hydrogen_plant = h2_plant
        self.npv = None
        self.opex_flows=None
        self.cum_npv_flows = None
        self.cash_flows = None
        self.discounted_cash_flows=None
        self.annual_revenue_flows=None
        self.income_tax_flows=None
        self.tangible_capex_depreciation_flows=None
        self.related_capex_depreciation_flows= None
        self.irr = None
        self.tax_rate = tax_rate
        self.tangible_capex=0.2
        self.intangible_capex=0.8
        self.tangible_capex_depr_schedule =0.55 # depreciation periods as % of project lifetime
        self.related_capex_factor=0.11
        self.related_capex_depr_schedule=0.7


    def calculate_npv(self):
    
        discounted_cash_flows = []
        cum_npv_flows = []
        cash_flows = []
        income_tax_flows= []
        annual_revenue_flows=[]
        opex_flows= []

        tangible_depreciation_periods= int(math.ceil(self.project_lifetime*self.tangible_capex_depr_schedule))
        related_capex_depreciation_periods = int(math.ceil(self.project_lifetime*self.related_capex_depr_schedule))


        tangible_capex_depreciation_flows = self.calculate_depreciation_schedule(self.capex*self.tangible_capex,tangible_depreciation_periods)
        related_capex_depreciation_flows= self.calculate_depreciation_schedule(self.capex*self.related_capex_factor,related_capex_depreciation_periods)
 
        # Calculate NPV
        for year in range(0, self.project_lifetime):


            production_decline_rate= pow(1-self.solar_plant.production_decline/100,year)
            annual_energy_output = self.solar_plant.annual_production_mwh*production_decline_rate
            total_h2_production = self.hydrogen_plant.calculate_hydrogen_from_energy(annual_energy_output) # Annual H2 production in kg
            annual_revenue = total_h2_production * self.hydrogen_plant.h2_price

            inflation_rate_increase= (1+self.inflation_rate/100)
            opex_rate_increase=pow(1+self.opex_increase_rate,year)
            increased_opex = self.opex*opex_rate_increase*inflation_rate_increase

            taxable_income = annual_revenue - tangible_capex_depreciation_flows[year] - related_capex_depreciation_flows[year] - increased_opex
            annual_cash_flow = annual_revenue - increased_opex

            if year == 0:
                taxable_income= taxable_income - self.intangible_capex*self.capex
                annual_cash_flow= annual_cash_flow - (self.capex+self.capex*self.related_capex_factor)



            income_tax= taxable_income*self.tax_rate/100

            # Net cash flow for the year

            annual_cash_flow=annual_cash_flow-income_tax


            
            # Append to cash flow list

            cash_flows.append(round(annual_cash_flow, 2))
        
            # Discounted cash flow
            discounted_cf = annual_cash_flow / (pow((1 + self.interest_rate/100), year))
            
            if year == 0:
                cum_npv_flows.append(discounted_cf)
            
            else:
                cum_npv_flows.append(cum_npv_flows[-1] + discounted_cf)

            discounted_cash_flows.append(discounted_cf)
            annual_revenue_flows.append(annual_revenue)
            income_tax_flows.append(income_tax)
            opex_flows.append(increased_opex)
    
        self.npv = sum(discounted_cash_flows)
        self.opex_flows=opex_flows
        self.cum_npv_flows = cum_npv_flows
        self.cash_flows = cash_flows
        self.discounted_cash_flows = discounted_cash_flows
        self.annual_revenue_flows=annual_revenue_flows
        self.income_tax_flows=income_tax_flows
        self.tangible_capex_depreciation_flows= tangible_capex_depreciation_flows
        self.related_capex_depreciation_flows = related_capex_depreciation_flows
        
        return self
    
    def calculate_depreciation_schedule(self,capex_subject_to_depreciation, depreciation_periods):
        
        depreciation_flows=[]
        depreciation_quota= capex_subject_to_depreciation/depreciation_periods
        period_counter=0

        for year in range(0,self.project_lifetime):

            if period_counter<depreciation_periods:
                depreciation_flows.append(depreciation_quota)
                period_counter+=1
            else:
                depreciation_flows.append(0)    

        return depreciation_flows


    def cum_npv_to_json(self):
        dict_with_indexes = {index: value for index, value in enumerate(self.cum_npv_flows)}
        return json.dumps(dict_with_indexes)
    
    def calculate_irr(self):
        self.irr= npf.irr(self.cash_flows)*100
        return json.dumps(self.irr)
    
    def get_irr(self):
        return json.dumps(self.irr)
    
    def get_cash_flows(self):
    
        keys = ["year","annual_revenue","opex","income_tax", "cash_flow", "disc_cash_flow","cum_npv"]
        years=[]
        
        for i in range(0, self.project_lifetime+1):
            years.append(i)

        json_data = [dict(zip(keys, values)) for values in zip(years,
                                                               self.annual_revenue_flows,
                                                               self.opex_flows,
                                                               self.income_tax_flows,
                                                               self.cash_flows,
                                                               self.discounted_cash_flows,
                                                               self.cum_npv_flows)]

        json_output = json.dumps(json_data, indent=4)
        return json_output    
    

    def get_depreciation_schedule(self):
    
        keys = ["year","tangible_capex","other_capex"]
        years=[]
        
        for i in range(0, self.project_lifetime+1):
            years.append(i)

        json_data = [dict(zip(keys, values)) for values in zip(years,
                                                               self.tangible_capex_depreciation_flows,
                                                               self.related_capex_depreciation_flows
                                                               )]

        json_output = json.dumps(json_data, indent=4)
        return json_output


def get_sensitivity_analysis(reference_project : project):

    keys = ["panel_efficiency","production_decline"]
    dict_shifted_npv = dict()

    

    for key in keys:
            
            analysis_project_up = copy.deepcopy(reference_project)
            analysis_project_down = copy.deepcopy(reference_project)
            
            values=dict()

            setattr(analysis_project_up.solar_plant,
                key,
                getattr(analysis_project_up.solar_plant,key)*1.1)
            
            setattr(analysis_project_down.solar_plant,
                key,
                getattr(analysis_project_down.solar_plant,key)*0.9)

            match key: 
                case "panel_efficiency":

                    analysis_project_up.solar_plant.calculate_annual_production()
                    analysis_project_up.solar_plant.calculate_capacity_factor()

                    analysis_project_down.solar_plant.calculate_annual_production()
                    analysis_project_down.solar_plant.calculate_capacity_factor()

            shifted_npv_up=analysis_project_up.calculate_npv().npv
            shifted_npv_down=analysis_project_down.calculate_npv().npv

            values["up"]=shifted_npv_up
            values["down"]=shifted_npv_down

            dict_shifted_npv[key]=values     


    return json.dumps(dict_shifted_npv)    
    