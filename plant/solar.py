
import requests

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
        
        data_dict = self.avg_monthly_ghi
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
        
        results = list(data['ALLSKY_SFC_SW_DWN'].items())
        
        # Format dataframe
        ghi={
            "01":[],
            "02":[],
            "03":[],
            "04":[],
            "05":[],
            "06":[],
            "07":[],
            "08":[],
            "09":[],
            "10":[],
            "11":[],
            "12":[]
        }

        for value in results:
            month= str(value[0])[-2:]
            if month!="13":
                ghi[month].append(value[1])

        averages_ghi = {key: round(sum(values) / len(values),2) if values else 0 for key, values in ghi.items()}
        
        # Group by the month and calculate the mean
        
        self.avg_monthly_ghi = averages_ghi
        self.last_latitude = self.latitude
        self.last_longitude = self.longitude
        
        return self.avg_monthly_ghi
    
    def calculate_capacity_factor(self):
        theoretical_annual_production= self.installed_cap*365*24
        self.cap_factor=self.annual_production_mwh/theoretical_annual_production
        return self.cap_factor
    
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
            
                "installed_cap":self.installed_cap,
                "cap_factor" :self.cap_factor,
                "latitude":self.latitude ,
                "longitude" :self.longitude,
                "annual_production_mwh":self.annual_production_mwh,
                "avg_monthly_ghi":self.avg_monthly_ghi,
                "panel_efficiency":self.panel_efficiency,
                "production_decline":self.production_decline,
                "land_required":self.land_required,
                "last_latitude" :self.last_latitude,
                "last_longitude" :self.last_longitude
        
    }

    
    def __str__(self):
        """
        String representation of the solar plant.
        """
        return f"Installed capacity: {self.installed_cap} W, Capacity factor: {self.cap_factor:.2f} %"


def calculate_annual_production_dict(solar_dict):
        """
        Calculates the annual energy production in MWh.
        """
        
        #Initialize annual production
        annual_production_kwh=0 
        
        #Standard test conditions: Surface per 1kW ~ 1kw/m2
        stc_capacity_per_m2=1 

        #Required m2 for actual capacity
        m2_per_mw = (solar_dict.get("installed_cap")*1000)/(stc_capacity_per_m2)
        
        data_dict = solar_dict.get("avg_monthly_ghi")
        for month,ghi in data_dict.items():
            annual_production_kwh=annual_production_kwh+(ghi*30) #KWh/m2/year
 
        solar_dict["annual_production_mwh"] = (annual_production_kwh/1000)*(solar_dict.get("panel_efficiency")/100)*solar_dict.get("installed_cap")*5000
        solar_dict["land_required"]=m2_per_mw
        
        return solar_dict    

def calculate_capacity_factor_dict(solar_dict):
        theoretical_annual_production= solar_dict.get("installed_cap")*365*24
        solar_dict["cap_factor"]=solar_dict.get("annual_production_mwh")/theoretical_annual_production
        return solar_dict
    