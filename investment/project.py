import json
from plant import solar as s
from plant import hydrogen as h2
import copy

class project:
    def __init__(self,project_lifetime: int, interest_rate: float, 
                 capex: float, opex: float, inflation_rate: float, 
                 solar_plant: s, h2_plant: h2, tax_rate, 
                 tangible_capex: float, intangible_capex: float,
                 capex_tangible_depreciation: int, capex_related_depreciation:int,
                 related_capex_factor: float, opex_increase_rate:float,
                 carbon_credit_price:float):
        """
        Initializes an investment project.
        """
        self.interest_rate = interest_rate
        self.project_lifetime = project_lifetime
        self.capex = capex
        self.opex = opex
        self.opex_increase_rate=opex_increase_rate
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
        self.irr2=None
        self.breakeven_price_h2=None
        self.breakeven_price_carbon_credit=None
        self.tax_rate = tax_rate
        self.tangible_capex=tangible_capex
        self.intangible_capex=intangible_capex
        self.tangible_capex_depr_periods =capex_tangible_depreciation# depreciation periods as % of project lifetime
        self.related_capex_factor=related_capex_factor/100
        self.related_capex_depr_periods=capex_related_depreciation
        self.tons_co2_equivalent_flows=None
        self.h2_output_flows=None
        self.emmissions_improvement_rate= None
        self.annual_energy_output_flows=None
        self.carbon_credit_price=carbon_credit_price

        self.solar_plant.calculate_avg_monthly_ghi()
        self.solar_plant.calculate_annual_production()
        self.solar_plant.calculate_capacity_factor()
        
        self.calculate_npv()
        self.calculate_irr()
        self.calculate_h2_break_even_price()
        self.calculate_carbon_credit_break_even_price()

        self.total_cash_flow = sum(self.cash_flows)
        self.total_discounted_cash_flow = sum(self.discounted_cash_flows)
        self.total_cum_npv = self.cum_npv_flows[-1]


    def calculate_npv(self):
    
        discounted_cash_flows = []
        cum_npv_flows = []
        cash_flows = []
        income_tax_flows= []
        annual_revenue_flows=[]
        opex_flows= []
        avoided_emmisions_flows=[]
        h2_output_flows=[]
        annual_energy_output_flows=[]

        tangible_capex_depreciation_flows = self.calculate_depreciation_schedule(self.capex*self.tangible_capex,self.tangible_capex_depr_periods)
        related_capex_depreciation_flows= self.calculate_depreciation_schedule(self.capex*self.related_capex_factor,self.related_capex_depr_periods)
 
        # Calculate NPV
        for year in range(0, self.project_lifetime):

            production_decline_rate= pow(1-self.solar_plant.production_decline/100,year)
            annual_energy_output = self.solar_plant.annual_production_mwh*production_decline_rate
            #TODO: UPPER BOUND TO TONS OF H2 PRODUCED
            total_h2_production = self.hydrogen_plant.calculate_hydrogen_from_energy(annual_energy_output) # Annual H2 production in kg
            avoided_tons_co2= self.hydrogen_plant.avoided_co2_emmissions_tons(total_h2_production)
            annual_revenue = total_h2_production * self.hydrogen_plant.h2_price + avoided_tons_co2*self.carbon_credit_price

            inflation_rate_increase= (1+self.inflation_rate/100)
            opex_rate_increase=pow(1+self.opex_increase_rate/100,year)
            increased_opex = self.opex*opex_rate_increase*inflation_rate_increase

            taxable_income = annual_revenue - tangible_capex_depreciation_flows[year] - related_capex_depreciation_flows[year] - increased_opex
            annual_cash_flow = annual_revenue - increased_opex

            if year == 0:
                taxable_income= taxable_income #- self.intangible_capex*self.capex
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
            avoided_emmisions_flows.append(avoided_tons_co2)
            h2_output_flows.append(round(total_h2_production/1000,2)) #tons of h2
            annual_energy_output_flows.append(round(annual_energy_output,2))

                                           
    
        self.npv = sum(discounted_cash_flows)
        self.opex_flows=opex_flows
        self.cum_npv_flows = cum_npv_flows
        self.cash_flows = cash_flows
        self.discounted_cash_flows = discounted_cash_flows
        self.annual_revenue_flows=annual_revenue_flows
        self.income_tax_flows=income_tax_flows
        self.tangible_capex_depreciation_flows= tangible_capex_depreciation_flows
        self.related_capex_depreciation_flows = related_capex_depreciation_flows
        self.tons_co2_equivalent_flows=avoided_emmisions_flows
        self.h2_output_flows=h2_output_flows
        self.annual_energy_output_flows =annual_energy_output_flows
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
    
    def calculate_irr(self, precision=1e-6, max_iterations=1000):
        low = -1.0  # Start from -100% return
        high = 1.0  # Up to 100% return
        iteration = 0

        def npv(rate):
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(self.cash_flows))

        while iteration < max_iterations:
            mid = (low + high) / 2
            npv_mid = npv(mid)

            if abs(npv_mid) < precision:
                self.irr=round(mid,4)
                return self.irr
            elif npv_mid > 0:
                low = mid
            else:
                high = mid

            iteration += 1

        self.irr=round(((low + high) / 2),4)  # Return the best estimate
        return self.irr

    

    def get_irr(self):
        return json.dumps(self.irr)
    

    def calculate_h2_break_even_price(self):
        """
        Adjusts the hydrogen_plant.h2_price to find the break-even price where the project's NPV is approximately 0.

        Args:
            project (object): The project object with attributes `npv`, `hydrogen_plant.h2_price`, and a method `calculate_npv()`.

        Returns:
            float: The break-even H2 price.
        """
        
        test_project= copy.deepcopy(self)
        
        # Define the acceptable tolerance for NPV to be considered 0
        tolerance = 1e-3

        # Define the initial search bounds for H2 price
        low_price = 0  # Lower bound (can be adjusted if negative prices are impossible)
        high_price = test_project.hydrogen_plant.h2_price*10 # Current H2 price is the upper bound

        while high_price - low_price > tolerance:
            # Calculate the midpoint price
            mid_price = (low_price + high_price) / 2

            # Set the project's H2 price to the midpoint
            test_project.hydrogen_plant.h2_price = mid_price

            # Recalculate the project's NPV
            test_project.calculate_npv()

            # Check if the NPV is close enough to 0
            if abs(test_project.npv) <= tolerance:
                break  # Exit the loop since we've found the break-even price

            # Adjust the bounds based on the NPV value
            if test_project.npv > 0:
                # If NPV is positive, decrease the H2 price
                high_price = mid_price
            else:
                # If NPV is negative, increase the H2 price
                low_price = mid_price

        self.breakeven_price_h2=test_project.hydrogen_plant.h2_price
        
        return json.dumps(self.breakeven_price_h2)
    

    def calculate_carbon_credit_break_even_price(self):
        """
        Adjusts the price to find the break-even price where the project's NPV is approximately 0.

        Args:
            project (object): The project object with attributes `npv`, `hydrogen_plant.price`, and a method `calculate_npv()`.

        Returns:
            float: The break-even price.
        """
        
        test_project= copy.deepcopy(self)
        
        # Define the acceptable tolerance for NPV to be considered 0
        tolerance = 1e-3

        # Define the initial search bounds for H2 price
        low_price = -test_project.carbon_credit_price*10  # Lower bound (can be adjusted if negative prices are impossible)
        high_price = test_project.carbon_credit_price*10 # x10 Current price is the upper bound

        while high_price - low_price > tolerance:
            # Calculate the midpoint price
            mid_price = (low_price + high_price) / 2

            # Set the project's H2 price to the midpoint
            test_project.carbon_credit_price = mid_price

            # Recalculate the project's NPV
            test_project.calculate_npv()

            # Check if the NPV is close enough to 0
            if abs(test_project.npv) <= tolerance:
                break  # Exit the loop since we've found the break-even price

            # Adjust the bounds based on the NPV value
            if test_project.npv > 0:
                # If NPV is positive, decrease the H2 price
                high_price = mid_price
            else:
                # If NPV is negative, increase the H2 price
                low_price = mid_price

        self.breakeven_price_carbon_credit=test_project.carbon_credit_price
        
        return json.dumps(self.breakeven_price_carbon_credit)

    def to_dict(self):
        def serialize_flow(flow):
            if flow is None:
                return None
            elif hasattr(flow, "tolist"):
                return flow.tolist()  # for NumPy arrays or Pandas Series
            elif isinstance(flow, (list, dict)):
                return flow
            else:
                return str(flow)  # fallback for anything weird
    
        return {
            "interest_rate": self.interest_rate,
            "project_lifetime": self.project_lifetime,
            "capex": self.capex,
            "opex": self.opex,
            "opex_increase_rate": self.opex_increase_rate,
            "inflation_rate": self.inflation_rate,
            "tax_rate": self.tax_rate,
            "tangible_capex": self.tangible_capex,
            "intangible_capex": self.intangible_capex,
            "tangible_capex_depr_periods": self.tangible_capex_depr_periods,
            "related_capex_depr_periods": self.related_capex_depr_periods,
            "related_capex_factor": self.related_capex_factor,
            "carbon_credit_price": self.carbon_credit_price,
            "npv": self.npv,
            "irr": self.irr,
            "breakeven_price_h2": self.breakeven_price_h2,
            "breakeven_price_carbon_credit": self.breakeven_price_carbon_credit,
            "solar_plant": self.solar_plant.to_dict() if hasattr(self.solar_plant, "to_dict") else str(self.solar_plant),
            "hydrogen_plant": self.hydrogen_plant.to_dict() if hasattr(self.hydrogen_plant, "to_dict") else str(self.hydrogen_plant),
            "total_cash_flow":self.total_cash_flow,
            "total_discounted_cash_flow":self.total_discounted_cash_flow,
            "cum_npv_cash_flows":self.total_cum_npv,
            
            # Serialize all *_flows
            "opex_flows": serialize_flow(self.opex_flows),
            "cum_npv_flows": serialize_flow(self.cum_npv_flows),
            "cash_flows": serialize_flow(self.cash_flows),
            "discounted_cash_flows": serialize_flow(self.discounted_cash_flows),
            "annual_revenue_flows": serialize_flow(self.annual_revenue_flows),
            "income_tax_flows": serialize_flow(self.income_tax_flows),
            "tangible_capex_depreciation_flows": serialize_flow(self.tangible_capex_depreciation_flows),
            "related_capex_depreciation_flows": serialize_flow(self.related_capex_depreciation_flows),
            "tons_co2_equivalent_flows": serialize_flow(self.tons_co2_equivalent_flows),
            "h2_output_flows": serialize_flow(self.h2_output_flows),
            "emmissions_improvement_rate": self.emmissions_improvement_rate,
            "annual_energy_output_flows": serialize_flow(self.annual_energy_output_flows),
        
    }
 

def get_sensitivity_analysis(reference_project : dict):

    solar_keys = ["panel_efficiency","production_decline"]
    h2_keys =["electrolyzer_efficiency","h2_price"]
    economic_keys = ["opex","capex","tax_rate","inflation_rate","interest_rate","carbon_credit_price"]

    dict_shifted_npv = dict()

    reference_npv= reference_project.get("npv")

    for key in economic_keys:


        analysis_project_up = copy.deepcopy(reference_project)
        analysis_project_down = copy.deepcopy(reference_project)

        values=dict()

        analysis_project_up[key]= analysis_project_up[key]*1.1
        analysis_project_down[key]= analysis_project_down[key]*0.9
        

        shifted_npv_up=calculate_npv_dict(analysis_project_up)
        shifted_npv_down=calculate_npv_dict(analysis_project_down)

        values["value_up"]=shifted_npv_up
        values["value_down"]=shifted_npv_down

        values["percentage_up"]=round(((shifted_npv_up-reference_npv)/abs(reference_npv))*100 ,4)
        values["percentage_down"]=round(((shifted_npv_down-reference_npv)/abs(reference_npv))*100 ,4)
        
        dict_shifted_npv[key]=values  

    for key in solar_keys:
            
        analysis_project_up = copy.deepcopy(reference_project)
        analysis_project_down = copy.deepcopy(reference_project)
            
        values=dict()


        analysis_project_up["solar_plant"][key]= analysis_project_up.get("solar_plant").get(key)*1.1
        analysis_project_down["solar_plant"][key]= analysis_project_down.get("solar_plant").get(key)*0.9


        match key: 
            case "panel_efficiency":
                analysis_project_up["solar_plant"]=s.calculate_annual_production_dict(analysis_project_up.get("solar_plant"))
                analysis_project_up["solar_plant"]=s.calculate_capacity_factor_dict(analysis_project_up.get("solar_plant"))
                analysis_project_down["solar_plant"]=s.calculate_annual_production_dict(analysis_project_down.get("solar_plant"))
                analysis_project_down["solar_plant"]=s.calculate_capacity_factor_dict(analysis_project_down.get("solar_plant"))
        
        shifted_npv_up=calculate_npv_dict(analysis_project_up)
        shifted_npv_down=calculate_npv_dict(analysis_project_down)
                                            
        values["value_up"]=shifted_npv_up
        values["value_down"]=shifted_npv_down
        
        values["percentage_up"]=round(((shifted_npv_up-reference_npv)/abs(reference_npv))*100 ,4)
        values["percentage_down"]=round(((shifted_npv_down-reference_npv)/abs(reference_npv))*100 ,4)

        dict_shifted_npv[key]=values  

    for key in h2_keys:


        analysis_project_up = copy.deepcopy(reference_project)
        analysis_project_down = copy.deepcopy(reference_project)

        values=dict()

        analysis_project_up["hydrogen_plant"][key]= analysis_project_up.get("hydrogen_plant").get(key)*1.1
        analysis_project_down["hydrogen_plant"][key]= analysis_project_down.get("hydrogen_plant").get(key)*0.9

        shifted_npv_up=calculate_npv_dict(analysis_project_up)
        shifted_npv_down=calculate_npv_dict(analysis_project_down)
        
        values["value_up"]=shifted_npv_up
        values["value_down"]=shifted_npv_down
        
        values["percentage_up"]=round(((shifted_npv_up-reference_npv)/abs(reference_npv))*100 ,4)
        values["percentage_down"]=round(((shifted_npv_down-reference_npv)/abs(reference_npv))*100 ,4)

        dict_shifted_npv[key]=values         


    return dict_shifted_npv

def cum_npv_to_json(json_dict):
    dict_with_indexes = {index: value for index, value in enumerate(json_dict.get("cum_npv_flows"))}
    return dict_with_indexes

def get_cash_flows(json_dict):
    
        keys = ["year","annual_revenue","opex","income_tax", "cash_flow", "disc_cash_flow","cum_npv"]
        years=[]
        
        for i in range(0, json_dict.get("project_lifetime")+1):
            years.append(i)

        json_data = [dict(zip(keys, values)) for values in zip(years,
                                                               json_dict.get("annual_revenue_flows"),
                                                               json_dict.get("opex_flows"),
                                                               json_dict.get("income_tax_flows"),
                                                               json_dict.get("cash_flows"),
                                                               json_dict.get("discounted_cash_flows"),
                                                               json_dict.get("cum_npv_flows"))]

       
        return json_data

def get_outputs(json_dict):
    
        keys = ["year","mwh_solar_output","tons_h2_output","tons_co2_equivalent"]
        years=[]
        
        for i in range(0, json_dict.get("project_lifetime")+1):
            years.append(i)

        json_data = [dict(zip(keys, values)) for values in zip(years,
                                                               json_dict.get("annual_energy_output_flows"),
                                                               json_dict.get("h2_output_flows"),
                                                               json_dict.get("tons_co2_equivalent_flows")
                                                               )]

        
        return json_data

def get_depreciation_schedule(json_dict):
    
        keys = ["year","tangible_capex","other_capex"]
        years=[]
        
        for i in range(0, json_dict.get("project_lifetime")+1):
            years.append(i)

        json_data = [dict(zip(keys, values)) for values in zip(years,
                                                               json_dict.get("tangible_capex_depreciation_flows"),
                                                               json_dict.get("related_capex_depreciation_flows")
                                                               )]

        
        return json_data

def calculate_npv_dict(project_dict):

    discounted_cash_flows = []
    cum_npv_flows = []
    cash_flows = []
    income_tax_flows= []
    annual_revenue_flows=[]
    opex_flows= []
    avoided_emmisions_flows=[]
    h2_output_flows=[]
    annual_energy_output_flows=[]
    tangible_capex_depreciation_flows = calculate_depreciation_schedule_dict(project_dict.get("project_lifetime"),project_dict.get("capex")*project_dict.get("tangible_capex"),project_dict.get("tangible_capex_depr_periods"))
    related_capex_depreciation_flows= calculate_depreciation_schedule_dict(project_dict.get("project_lifetime"),project_dict.get("capex")*project_dict.get("related_capex_factor"),project_dict.get("related_capex_depr_periods"))

    # Calculate NPV
    for year in range(0, project_dict.get("project_lifetime")):
        production_decline_rate= pow(1-project_dict.get("solar_plant").get("production_decline")/100,year)
        annual_energy_output = project_dict["solar_plant"]["annual_production_mwh"]*production_decline_rate
        #TODO: UPPER BOUND TO TONS OF H2 PRODUCED
        total_h2_production = h2.calculate_hydrogen_from_energy_dict(project_dict.get("hydrogen_plant"),annual_energy_output) # Annual H2 production in kg
        avoided_tons_co2= h2.avoided_co2_emmissions_tons_dict(project_dict.get("hydrogen_plant"),total_h2_production)
        annual_revenue = total_h2_production * project_dict.get("hydrogen_plant").get("h2_price") + avoided_tons_co2*project_dict.get("carbon_credit_price")
        inflation_rate_increase= (1+project_dict.get("inflation_rate")/100)
        opex_rate_increase=pow(1+project_dict.get("opex_increase_rate")/100,year)
        increased_opex = project_dict.get("opex")*opex_rate_increase*inflation_rate_increase
        taxable_income = annual_revenue - tangible_capex_depreciation_flows[year] - related_capex_depreciation_flows[year] - increased_opex
        annual_cash_flow = annual_revenue - increased_opex
        if year == 0:
            taxable_income= taxable_income #- self.intangible_capex*self.capex
            annual_cash_flow= annual_cash_flow - (project_dict.get("capex")+project_dict.get("capex")*project_dict.get("related_capex_factor"))
        income_tax= taxable_income*project_dict.get("tax_rate")/100
        # Net cash flow for the year
        annual_cash_flow=annual_cash_flow-income_tax
        # Append to cash flow list
        cash_flows.append(round(annual_cash_flow, 2))
    
        # Discounted cash flow
        discounted_cf = annual_cash_flow / (pow((1 + project_dict.get("interest_rate")/100), year))
        
        if year == 0:
            cum_npv_flows.append(discounted_cf)
        
        else:
            cum_npv_flows.append(cum_npv_flows[-1] + discounted_cf)
        discounted_cash_flows.append(discounted_cf)
        annual_revenue_flows.append(annual_revenue)
        income_tax_flows.append(income_tax)
        opex_flows.append(increased_opex)
        avoided_emmisions_flows.append(avoided_tons_co2)
        h2_output_flows.append(round(total_h2_production/1000,2)) #tons of h2
        annual_energy_output_flows.append(round(annual_energy_output,2))
                                       

    npv = sum(discounted_cash_flows)
    return npv

def calculate_depreciation_schedule_dict(project_lifetime,capex_subject_to_depreciation, depreciation_periods):
    
    depreciation_flows=[]
    depreciation_quota= capex_subject_to_depreciation/depreciation_periods
    period_counter=0
    for year in range(0,project_lifetime):
        if period_counter<depreciation_periods:
            depreciation_flows.append(depreciation_quota)
            period_counter+=1
        else:
            depreciation_flows.append(0)    
    return depreciation_flows

def calculate_h2_break_even_price_dict(project_dict):
        """
        Adjusts the hydrogen_plant.h2_price to find the break-even price where the project's NPV is approximately 0.

        Args:
            project (object): The project object with attributes `npv`, `hydrogen_plant.h2_price`, and a method `calculate_npv()`.

        Returns:
            float: The break-even H2 price.
        """
        
        test_project= copy.deepcopy(project_dict)
        
        # Define the acceptable tolerance for NPV to be considered 0
        tolerance = 1e-3

        # Define the initial search bounds for H2 price
        low_price = 0  # Lower bound (can be adjusted if negative prices are impossible)
        high_price = test_project["hydrogen_plant"]["h2_price"]*10 # Current H2 price is the upper bound

        while high_price - low_price > tolerance:
            # Calculate the midpoint price
            mid_price = (low_price + high_price) / 2

            # Set the project's H2 price to the midpoint
            test_project["hydrogen_plant"]["h2_price"] = mid_price

            # Recalculate the project's NPV
            calculate_npv_dict(test_project)

            # Check if the NPV is close enough to 0
            if abs(test_project["npv"]) <= tolerance:
                break  # Exit the loop since we've found the break-even price

            # Adjust the bounds based on the NPV value
            if test_project["npv"] > 0:
                # If NPV is positive, decrease the H2 price
                high_price = mid_price
            else:
                # If NPV is negative, increase the H2 price
                low_price = mid_price

        breakeven_price_h2=test_project["hydrogen_plant"]["h2_price"]
        
        return breakeven_price_h2

def calculate_carbon_credit_break_even_price_dict(project_dict):
    """
    Adjusts the price to find the break-even price where the project's NPV is approximately 0.
    Args:
        project (object): The project object with attributes `npv`, `hydrogen_plant.price`, and a method `calculate_npv()`.
    Returns:
        float: The break-even price.
    """
    
    test_project= copy.deepcopy(project_dict)
    
    # Define the acceptable tolerance for NPV to be considered 0
    tolerance = 1e-3
    # Define the initial search bounds for H2 price
    low_price = -test_project["carbon_credit_price"]*10  # Lower bound (can be adjusted if negative prices are impossible)
    high_price = test_project["carbon_credit_price"]*10 # x10 Current price is the upper bound
    while high_price - low_price > tolerance:
        # Calculate the midpoint price
        mid_price = (low_price + high_price) / 2
        # Set the project's H2 price to the midpoint
        test_project["carbon_credit_price"] = mid_price
        # Recalculate the project's NPV
        calculate_npv_dict(test_project)
        # Check if the NPV is close enough to 0
        if abs(test_project["npv"]) <= tolerance:
            break  # Exit the loop since we've found the break-even price
        # Adjust the bounds based on the NPV value
        if test_project["npv"] > 0:
            # If NPV is positive, decrease the H2 price
            high_price = mid_price
        else:
            # If NPV is negative, increase the H2 price
            low_price = mid_price
    breakeven_price_carbon_credit=test_project["carbon_credit_price"]
    
    return breakeven_price_carbon_credit

