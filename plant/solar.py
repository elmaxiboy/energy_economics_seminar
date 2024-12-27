
import requests
import pandas as pd

class solar:
    def __init__(self, installed_cap: float, cap_factor: float):
        """
        Initializes a solar plant.
        """
        self.installed_cap = installed_cap
        self.cap_factor = cap_factor
        self.latitude= -33.459229 # Santiago de Chile
        self.longitude= -70.645348
        self.annual_production_mwh= None
        self.avg_monthly_ghi=None


    def calculate_annual_production(self, average_daily_radiation: float, efficiency: float):
        """
        Calculates the annual energy production in MWh.

        :param average_daily_radiation: Average daily radiation in kWh/m²
        :param efficiency: Efficiency of the solar panels (0-1)
        """
        # Assume 365 days in a year
        self.annual_production_kwh = (
            self.capacity_kw * average_daily_radiation * 365 * efficiency
        )
        return self.annual_production_kwh
    

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
        df= df.groupby('month')['radiation'].mean()

        # Group by the month and calculate the mean
        self.avg_monthly_ghi = df.to_json()

        # Display the results
        print("Average monthly Global Horizontal Irradiance:")
        print(self.avg_monthly_ghi)        

        if response.status_code != 200:
            raise Exception("Failed to retrieve solar radiation data.")       

        return self.avg_monthly_ghi

    
    def __str__(self):
        """
        String representation of the solar plant.
        """
        return f"Installed capacity: {self.installed_cap} W, Capacity factor: {self.cap_factor:.2f} %"
