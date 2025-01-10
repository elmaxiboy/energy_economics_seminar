class hydrogen:
    def __init__(self, electrolyzer_efficiency: float, h2_price: float ):
        """
        Initializes a hydrogen plant.
        """
        self.electrolyzer_efficiency = electrolyzer_efficiency
        self.h2_price = h2_price
        self.h2_output = None


    def __str__(self):
        """
        String representation of the hydrogen plant.
        """
        return f"Electrolyzer efficiency: {self.electrolyzer_efficiency} %, H2 price: ${self.h2_price:.2f}"
    
    def calculate_hydrogen_from_energy(self,input_mwh):
        # Constants
        LHV_HYDROGEN = 33.33  # Lower Heating Value of hydrogen (kWh/kg)
    
        # Convert MWh to kWh
        kwh = input_mwh * 1000
    
        # Calculate hydrogen production (kg)
        self.h2_output = round(kwh * (self.electrolyzer_efficiency / 100)) / LHV_HYDROGEN

        self.h2_output = round(self.h2_output, 2)
    
        return self.h2_output