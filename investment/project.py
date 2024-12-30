
import requests
import pandas as pd
import json
import plant
import plant.hydrogen
import plant.solar

class project:
    def __init__(self, interest_rate: float, capex: float, opex: float, solar_plant: plant.solar, h2_plant:plant.hydrogen):
        """
        Initializes an investment project.
        """
        self.insterest_rate = interest_rate
        self.capex = capex
        self.opex = opex
        self.solar_plant = solar_plant
        self.hydrogen_plant = h2_plant
