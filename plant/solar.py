
import requests
import pandas as pd
import json

class solar:
    def __init__(self, installed_cap: float, latitude: float,longitude: float, panel_efficiency: float, production_decline:float):
        """
        Initializes a solar plant.
        """
        self.installed_cap = installed_cap
        self.cap_factor = None
        self.latitude= latitude 
        self.longitude= longitude
        self.annual_production_mwh= None
        self.avg_monthly_ghi=None
        self.panel_efficiency= panel_efficiency
        self.production_decline= production_decline
        self.land_required=None
        self.last_latitude = None
        self.last_longitude = None


    def calculate_annual_production(self):
        """
        Calculates the annual energy production in MWh.
        """
        
        #Initialize annual production
        annual_production_kwh=0 
        
        #Standard test conditions: Surface per 1kW ~ 1kw/m2
        stc_capacity_per_m2=1 

        #Required m2 for actual capacity
        m2_per_mw = (self.installed_cap*1000)/(stc_capacity_per_m2)
        
        data_dict = json.loads(self.avg_monthly_ghi)
        for month,ghi in data_dict.items():
            annual_production_kwh=annual_production_kwh+(ghi*30) #KWh/m2/year
 
        self.annual_production_mwh = (annual_production_kwh/1000)*(self.panel_efficiency/100)*self.installed_cap*5000
        self.land_required=m2_per_mw
        
        return self.annual_production_mwh
    

    def calculate_avg_monthly_ghi(self):

        api_url = f"https://power.larc.nasa.gov/api/temporal/monthly/point?start=2000&end=2022&latitude={self.latitude}&longitude={self.longitude}&community=RE&parameters=ALLSKY_SFC_SW_DWN&format=JSON"  
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve solar radiation data.") 
    
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
        self.last_latitude = self.latitude
        self.last_longitude = self.longitude
        
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
