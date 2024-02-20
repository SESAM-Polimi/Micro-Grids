"""
MicroGridsPy - Multi-year capacity-expansion (MYCE)

Linear Programming framework for microgrids least-cost sizing,
able to account for time-variable load demand evolution and capacity expansion.

Authors: 
    Giulia Guidicini   - Department of Energy, Politecnico di Milano 
    Lorenzo Rinaldi    - Department of Energy, Politecnico di Milano
    Nicolò Stevanato   - Department of Energy, Politecnico di Milano / Fondazione Eni Enrico Mattei
    Francesco Lombardi - Department of Energy, Politecnico di Milano
    Emanuela Colombo   - Department of Energy, Politecnico di Milano
Based on the original model by:
    Sergio Balderrama  - Department of Mechanical and Aerospace Engineering, University of Liège / San Simon University, Centro Universitario de Investigacion en Energia
    Sylvain Quoilin    - Department of Mechanical Engineering Technology, KU Leuven
"""


import pandas as pd, numpy as np
import re
import os
from RE_calculation import RE_supply
from Demand import demand_generation
from Grid_Availability import grid_availability as grid_avail


#%% This section extracts the values of Scenarios, Periods, Years from data.dat and creates ranges for them

current_directory = os.getcwd()
inputs_directory = os.path.join(current_directory, '..', 'Inputs')
data_file_path = os.path.join(inputs_directory, 'Parameters.dat')
demand_file_path = os.path.join(inputs_directory, 'Demand.xlsx')
tamb_file_path = os.path.join(inputs_directory, 'Tamb.xlsx')
res_file_path = os.path.join(inputs_directory, 'RES_Time_Series.csv')
fuel_file_path = os.path.join(inputs_directory, 'Fuel Specific Cost.csv')
grid_file_path = os.path.join(inputs_directory, 'Grid Availability.csv')

"Extract relevant inputs parameters from Parameters.dat file"
Data_import = open(data_file_path).readlines()

Fuel_Specific_Start_Cost = []
Fuel_Specific_Cost_Rate = []

for i in range(len(Data_import)):
    if "param: Scenarios" in Data_import[i]:
        n_scenarios = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Years" in Data_import[i]:
        n_years = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Periods" in Data_import[i]:
        n_periods = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Generator_Types" in Data_import[i]:      
        n_generators = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Step_Duration" in Data_import[i]:
        step_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Min_Last_Step_Duration" in Data_import[i]:
        min_last_step_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Battery_Independence" in Data_import[i]:      
        Battery_Independence = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Renewable_Penetration" in Data_import[i]:      
        Renewable_Penetration = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: Greenfield_Investment" in Data_import[i]:      
        Greenfield_Investment = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Multiobjective_Optimization" in Data_import[i]:      
        Multiobjective_Optimization = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Optimization_Goal" in Data_import[i]:      
        Optimization_Goal = int((re.findall('\d+',Data_import[i])[0]))
    if "param: MILP_Formulation" in Data_import[i]:      
        MILP_Formulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: MultiGood_Ice" in Data_import[i]:      
        MultiGood_Ice = int((re.findall('\d+',Data_import[i])[0]))
    if "param: COP_n" in Data_import[i]:
        COP_n = float((re.findall('\d+\.*\d+',Data_import[i])[0]))
    if "param: eta_ice_tank_nom" in Data_import[i]:
        eta_ice_tank_nom = float((re.findall('\d+\.*\d+',Data_import[i])[0]))
    if "param: Generator_Partial_Load" in Data_import[i]:      
        Generator_Partial_Load = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Plot_Max_Cost" in Data_import[i]:      
        Plot_Max_Cost = int((re.findall('\d+',Data_import[i])[0]))
    if "param: RE_Supply_Calculation" in Data_import[i]:      
        RE_Supply_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Demand_Profile_Generation" in Data_import[i]:      
        Demand_Profile_Generation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Fuel_Specific_Cost_Calculation" in Data_import[i]:      
        Fuel_Specific_Cost_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Fuel_Specific_Cost_Import" in Data_import[i]:      
        Fuel_Specific_Cost_Import = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Average_Number_Outages" in Data_import[i]:      
        average_n_outages = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Average_Outage_Duration" in Data_import[i]:       
        average_outage_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Connection " in Data_import[i]:      
        Grid_Connection = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Availability_Simulation" in Data_import[i]:      
        Grid_Availability_Simulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Year_Grid_Connection " in Data_import[i]:      
        year_grid_connection = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Model_Components " in Data_import[i]:      
        Model_Components = int((re.findall('\d+',Data_import[i])[0]))
    if "param: WACC_Calculation " in Data_import[i]:      
        WACC_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: cost_of_equity" in Data_import[i]:      
        cost_of_equity = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: cost_of_debt" in Data_import[i]:      
        cost_of_debt = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: tax" in Data_import[i]:      
        tax = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: equity_share" in Data_import[i]:      
        equity_share = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: debt_share" in Data_import[i]:      
        debt_share = float((re.findall("\d+\.\d+|\d+",Data_import[i])[0]))
    if "param: Real_Discount_Rate" in Data_import[i]:      
        Discount_Rate_default = float((re.findall("\d+\.\d+|\d+|\d+",Data_import[i])[0]))
    if "param: Fuel_Specific_Start_Cost" in Data_import[i]:
        for j in range(n_generators):
            Fuel_Specific_Start_Cost.append(float((re.findall("\d+\s+(\d+\.\d+|\d+)",Data_import[i+1+j])[0])))
    if "param: Fuel_Specific_Cost_Rate" in Data_import[i]:      
        for j in range(n_generators):
            Fuel_Specific_Cost_Rate.append(float((re.findall("\d+\s+(\d+\.\d+|\d+)",Data_import[i+1+j])[0])))


scenario = [i for i in range(1,n_scenarios+1)]
year = [i for i in range(1,n_years+1)]
period = [i for i in range(1,n_periods+1)]
generator = [i for i in range(1,n_generators+1)]

#%% This section is useful to define the number of investment steps as well as to assign each year to its corresponding step
def Initialize_Upgrades_Number(model):
    if n_years % step_duration == 0:
        n_upgrades = n_years/step_duration
        return n_upgrades
    
    else:
        n_upgrades = 1
        for y in  range(1, n_years + 1):
            if y % step_duration == 0 and n_years - y > min_last_step_duration:
                n_upgrades += 1
        return int(n_upgrades)

def Initialize_YearUpgrade_Tuples(model):
    upgrade_years_list = [1 for i in range(len(model.steps))]
    s_dur = model.Step_Duration   
    for i in range(1, len(model.steps)): 
        upgrade_years_list[i] = upgrade_years_list[i-1] + s_dur    
    yu_tuples_list = [0 for i in model.years]    
    if model.Steps_Number == 1:    
        for y in model.years:            
            yu_tuples_list[y-1] = (y, 1)    
    else:        
        for y in model.years:            
            for i in range(len(upgrade_years_list)-1):
                if y >= upgrade_years_list[i] and y < upgrade_years_list[i+1]:
                    yu_tuples_list[y-1] = (y, model.steps[i+1])                
                elif y >= upgrade_years_list[-1]:
                    yu_tuples_list[y-1] = (y, len(model.steps))   
    print('\nTime horizon (year,investment-step): ' + str(yu_tuples_list))
    return yu_tuples_list

def Initialize_Discount_Rate(model):
    if WACC_Calculation:
        if equity_share == 0:
            WACC = cost_of_debt*(1-tax)
        else:
           # Definition of Leverage (L): risk perceived by investors, or viceversa as the attractiveness of the investment to external debtors.
           L = debt_share/equity_share 
           WACC = cost_of_debt*(1-tax)*L/(1+L) + cost_of_equity*1/(1+L)
    else:
        WACC = Discount_Rate_default
    return WACC

"Electric Demand"
def Initialize_Electric_Demand(model, s, y, t):
    """Initializes electric demand based on the scenario, year, and period."""
    if Demand_Profile_Generation: Demand = demand_generation()
    else: Demand = (pd.read_excel("Demand.xlsx", sheet_name = "Electric")).dropna(how='all', axis=1)
    # Multi-indexed Data Frame for Electric Demand
    Demand_Series = pd.Series()
    # Adjust the loop to iterate over the actual column names of the DataFrame
    for col in Demand.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
        dum = Demand[col].reset_index(drop=True)
        Demand_Series = pd.concat([Demand_Series, dum])
    frame = [scenario, year, period]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
    Electric_Energy_Demand = pd.DataFrame(Demand_Series)
    Electric_Energy_Demand.index = index
    return float(Electric_Energy_Demand[0][(s, y, t)])

"Ice Demand"
def Initialize_Ice_Demand(model, s, y, t):
    if MultiGood_Ice:
        """Initializes ice demand based on the scenario, year, and period."""
        Demand = (pd.read_excel("Demand.xlsx", sheet_name = "Ice")).dropna(how='all', axis=1)
        # Multi-indexed Data Frame for Ice Demand
        Demand_Series = pd.Series()
        # Adjust the loop to iterate over the actual column names of the DataFrame
        for col in Demand.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
            dum = Demand[col].reset_index(drop=True)
            Demand_Series = pd.concat([Demand_Series, dum])
        frame = [scenario, year, period]
        index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
        Ice_Demand = pd.DataFrame(Demand_Series)
        Ice_Demand.index = index
        return float(Ice_Demand[0][(s, y, t)])
    else: return None

def Initialize_RES_Energy(model, s, r, t):
    """Initializes renewable energy supply based on scenario, source, and period."""
    if RE_Supply_Calculation:
        Renewable_Energy = RE_supply().set_index(pd.Index(range(1, n_periods+1)), inplace=False)
    else:
        Renewable_Energy = pd.read_csv(res_file_path, delimiter=';', decimal=',', header=0)
    column = (s - 1) * model.RES_Sources + r
    return float(Renewable_Energy.iloc[t - 1, column]) 


 