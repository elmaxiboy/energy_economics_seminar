class hydrogen:
    def __init__(self, electrolyzer_efficiency: float, h2_price: float, co2_equivalence:float ):
        """
        Initializes a hydrogen plant.
        """
        self.electrolyzer_efficiency = electrolyzer_efficiency
        self.h2_price = h2_price
        self.h2_output = None #kg of H2
        self.lower_heating_value= 33.33  # Lower Heating Value of hydrogen (kWh/kg)
        self.co2_equivalence= co2_equivalence #per kg of H2

    def __str__(self):
        """
        String representation of the hydrogen plant.
        """
        return f"Electrolyzer efficiency: {self.electrolyzer_efficiency} %, H2 price: ${self.h2_price:.2f}"
    
    def calculate_hydrogen_from_energy(self,input_mwh):
        # Constants
        # Convert MWh to kWh
        kwh = input_mwh * 1000
    
        # Calculate hydrogen production (kg)
        self.h2_output = round(kwh * (self.electrolyzer_efficiency / 100)) / self.lower_heating_value

        self.h2_output = round(self.h2_output, 2)
    
        return self.h2_output
    
    def avoided_co2_emmissions_tons(self,kg_of_h2):
        
        return round(self.co2_equivalence*kg_of_h2/1000,2)
    
    def to_dict(self):

        return {
             
                "electrolyzer_efficiency":self.electrolyzer_efficiency,
                "h2_price":self.h2_price,
                "h2_output":self.h2_output,
                "lower_heating_value":self.lower_heating_value,  
                "co2_equivalence":self.co2_equivalence
        
    }

def calculate_hydrogen_from_energy_dict(h2_dict,input_mwh):
        # Constants
        # Convert MWh to kWh
        kwh = input_mwh * 1000
    
        # Calculate hydrogen production (kg)
        h2_output = round(kwh * (h2_dict.get("electrolyzer_efficiency") / 100)) / h2_dict.get("lower_heating_value")

        h2_output = round(h2_output, 2)
    
        return h2_output
        
def avoided_co2_emmissions_tons_dict(h2_dict,kg_of_h2):
        
        return round(h2_dict.get("co2_equivalence")*kg_of_h2/1000,2)
