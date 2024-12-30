
import requests
import pandas as pd
import json

class solar:
    def __init__(self, installed_cap: float, latitude: float,longitude: float):
        """
        Initializes a solar plant.
        """
        self.installed_cap = installed_cap
        self.cap_factor = None
        self.latitude= latitude 
        self.longitude= longitude
        self.annual_production_mwh= None
        self.avg_monthly_ghi=None


    def calculate_annual_production(self, efficiency: float):
        """
        Calculates the annual energy production in KWh.

        :param average_daily_radiation: Average daily radiation in kWh/m²
        :param efficiency: Efficiency of the solar panels (0-1)
        """
        annual_production=0
        data_dict = json.loads(self.avg_monthly_ghi)
        for month,ghi in data_dict.items():
            annual_production=annual_production+(ghi*30)*efficiency  

        self.annual_production_mwh = (annual_production/1000)*self.installed_cap*6000# 1MW requires 6000 m2

        return self.annual_production_mwh
    

    def calculate_avg_monthly_ghi(self):

        api_url = f"https://power.larc.nasa.gov/api/temporal/monthly/point?start=2000&end=2022&latitude={self.latitude}&longitude={self.longitude}&community=RE&parameters=ALLSKY_SFC_SW_DWN&format=JSON"
        response = requests.get(api_url)
        data = response.json()
        data = data['properties']['parameter']

        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(list(data['ALLSKY_SFC_SW_DWN'].items()), columns=['yearMonth', 'radiation'])

        # Format dataframe
        df['month'] = df['yearMonth'].str[-2:]
        df['year'] = df['yearMonth'].str[:4]
        df = df.drop(df[df['month'] == '13'].index)
        df=df.drop('yearMonth',axis=1)
        df= df.groupby('month')['radiation'].mean().round(2)

        # Group by the month and calculate the mean
        self.avg_monthly_ghi = df.to_json()

        if response.status_code != 200:
            raise Exception("Failed to retrieve solar radiation data.")       

        return self.avg_monthly_ghi
    
    def calculate_capacity_factor(self):
        theoretical_annual_production= self.installed_cap*365*24
        self.cap_factor=self.annual_production_mwh/theoretical_annual_production
        return self.cap_factor

    
    def __str__(self):
        """
        String representation of the solar plant.
        """
        return f"Installed capacity: {self.installed_cap} W, Capacity factor: {self.cap_factor:.2f} %"
