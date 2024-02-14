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
res_file_path = os.path.join(inputs_directory, 'RES_Time_Series.csv')
fuel_file_path = os.path.join(inputs_directory, 'Fuel Specific Cost.csv')
grid_file_path = os.path.join(inputs_directory, 'Grid Availability.csv')
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
    if "param: MultiGood_Formulation" in Data_import[i]:      
        MultiGood_Formulation = int((re.findall('\d+',Data_import[i])[0]))
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

#%% Initializes discount rate if WACC Calculation is chosen by the user

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

#%% This section imports the multi-year Demands and Renewable-Energy output and creates a Multi-indexed DataFrame for it

if RE_Supply_Calculation:
    Renewable_Energy = RE_supply().set_index(pd.Index(range(1, n_periods+1)), inplace=False)
else:
    Renewable_Energy = pd.read_csv(res_file_path, delimiter=';', decimal=',', header=0)

if Demand_Profile_Generation:
    Demand = demand_generation()
else:
    Demand = pd.read_excel("Demand.xlsx", sheet_name = "Electric")
    # Drop columns where all values are NaN, as they don't contain any useful data
    Demand = Demand.dropna(how='all', axis=1)

#%% Reads the demands; returns Null and 0 if the MultiGood_Formulation is switched to 0
    
if MultiGood_Formulation:
    Thermal = pd.read_excel("Demand.xlsx", sheet_name="Thermal")
    Ice = pd.read_excel("Demand.xlsx", sheet_name="Ice")
    
    # Multi-indexed Data Frame for Electric, Thermal and Ice Demand
    Electric_Energy_Demand_Series = pd.Series()
    Thermal_Energy_Demand_Series = pd.Series()
    Ice_Demand_Series = pd.Series()

    # Adjust the loop to iterate over the actual column names of the DataFrame
    for col in Demand.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
        dum = Demand[col].reset_index(drop=True)
        Electric_Energy_Demand_Series = pd.concat([Electric_Energy_Demand_Series, dum])
    for col in Thermal.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
        dum = Thermal[col].reset_index(drop=True)
        Thermal_Energy_Demand_Series = pd.concat([Thermal_Energy_Demand_Series, dum])
    for col in Ice.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
        dum = Ice[col].reset_index(drop=True)
        Ice_Demand_Series = pd.concat([Ice_Demand_Series, dum])    

    frame = [scenario, year, period]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])

    Electric_Energy_Demand = pd.DataFrame(Electric_Energy_Demand_Series)
    Electric_Energy_Demand.index = index
    Thermal_Energy_Demand = pd.DataFrame(Thermal_Energy_Demand_Series) 
    Thermal_Energy_Demand.index = index
    Ice_Demand = pd.DataFrame(Ice_Demand_Series) 
    Ice_Demand.index = index

    Electric_Energy_Demand_2 = pd.DataFrame()
    Thermal_Energy_Demand_2 = pd.DataFrame()
    Ice_Demand_2 = pd.DataFrame()

    for s in scenario:
        Electric_Energy_Demand_Series_2 = pd.Series()
        Thermal_Energy_Demand_Series_2 = pd.Series()
        Ice_Demand_Series_2 = pd.Series()
        for y in year:
            dum_2 = Demand[(s-1) * n_years + y][:]
            Electric_Energy_Demand_Series_2 = pd.concat([Electric_Energy_Demand_Series_2, dum_2])
            dum_2 = Thermal[(s-1) * n_years + y][:]
            Thermal_Energy_Demand_Series_2 = pd.concat([Thermal_Energy_Demand_Series_2, dum_2])
            dum_2 = Ice[(s-1) * n_years + y][:]
            Ice_Demand_Series_2 = pd.concat([Ice_Demand_Series_2, dum_2])      
        Electric_Energy_Demand_2[s] = Electric_Energy_Demand_Series_2
        Thermal_Energy_Demand_2[s] = Thermal_Energy_Demand_Series_2
        Ice_Demand_2[s] = Ice_Demand_Series_2

    # Create a RangeIndex
    index_2 = pd.RangeIndex(1, n_years * n_periods + 1)

    Electric_Energy_Demand_2.index = index_2
    Thermal_Energy_Demand_2.index = index_2
    Ice_Demand_2.index = index_2

else:
    # Define default values if MultiGood_Formulation switch is zero
    Thermal = None
    Ice = None
    Thermal_Energy_Demand = None
    Ice_Demand = None
    Thermal_Energy_Demand_2 = None
    Ice_Demand_2 = None

#%%
# Functions to initialize the different demands

def Initialize_Demand(model, s, y, t):
    return float(Electric_Energy_Demand[0][(s, y, t)])

def Initialize_Thermal_Demand(model, s, y, t):
    if MultiGood_Formulation:
        return float(Thermal_Energy_Demand[0][(s, y, t)])
    else:
        return 0
    
def Initialize_Ice_Demand(model, s, y, t):
    if MultiGood_Formulation:
        return float(Ice_Demand[0][(s, y, t)])
    else:
        return 0

#%%

def Initialize_RES_Energy(model, s, r, t):
    column = (s - 1) * model.RES_Sources + r
    return float(Renewable_Energy.iloc[t - 1, column])   


def Initialize_Battery_Unit_Repl_Cost(model):
    Unitary_Battery_Cost = model.Battery_Specific_Investment_Cost - model.Battery_Specific_Electronic_Investment_Cost
    return Unitary_Battery_Cost/(model.Battery_Cycles*2*(model.Battery_Depth_of_Discharge))
      

def Initialize_Battery_Minimum_Capacity(model,ut): 
    if model.Battery_Independence == 0: 
        return 0
    else:
        Periods = model.Battery_Independence*24
        Len =  int(model.Periods*model.Years/Periods)
        Grouper = 1
        index = 1
        for i in range(1, Len+1):
            for j in range(1,Periods+1):      
                Electric_Energy_Demand_2.loc[index, 'Grouper'] = Grouper
                index += 1      
            Grouper += 1
    
        upgrade_years_list = [1 for i in range(len(model.steps))]
        
        for u in range(1, len(model.steps)):
            upgrade_years_list[u] =upgrade_years_list[u-1] + model.Step_Duration
        if model.Steps_Number ==1:
            Electric_Energy_Demand_Upgrade = Electric_Energy_Demand_2    
        else:
            if ut==1:
                start = 0
                Electric_Energy_Demand_Upgrade = Electric_Energy_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]       
            elif ut == len(model.steps):
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Electric_Energy_Demand_Upgrade = Electric_Energy_Demand_2.loc[start :, :]       
            else:
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Electric_Energy_Demand_Upgrade = Electric_Energy_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]
        
        Period_Energy = Electric_Energy_Demand_Upgrade.groupby(['Grouper']).sum()        
        Period_Average_Energy = Period_Energy.mean()
        Available_Energy = sum(Period_Average_Energy[s]*model.Scenario_Weight[s] for s in model.scenarios) 
        
        return  Available_Energy/(model.Battery_Depth_of_Discharge)

#%% Initialization of ambient temperature, computation of average temp and number of the day when minimum temperature occurs; if RE calculation is enabled the code reads the ambient temperature from NASA Power

if RE_Supply_Calculation == 0:
    Tamb = pd.read_excel(os.path.join(inputs_directory, 'Tamb.xlsx'))  # Read from inputs if RE calculation is not enabled
    Tamb_Series = Tamb.stack()  # Stack the DataFrame to create a series
  
    frame = [scenario, year, period]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
    Tamb = pd.DataFrame(Tamb_Series, index=index, columns=['Tamb'])
    Tav = Tamb.mean()
    min_index = Tamb['Tamb'].idxmin()
    nmin = min_index[2] 
    
    # Tamb_2 = pd.DataFrame(index=pd.RangeIndex(1, n_years * n_periods + 1))

    # for s in scenario:
    #     for y in year:
    #         for t in period:
    #             Tamb_2.loc[(s - 1) * n_years * n_periods + (y - 1) * n_periods + t, s] = Tamb.loc[(s, y, t), 'Tamb']

def Initialize_Tamb(model, s, y, t):
    if RE_Supply_Calculation == 0:
        return float(Tamb.loc[(s, y, t), 'Tamb'])
    else:
        return 0        #in this case if Initialize_Tamb = 0 I will use NASA Power

#%% Initialization of ice tank parameters; the ice tank efficiency empirically decreases with the increase of the ambient temperature

def Initialize_Eta_Ice_Tank(model, s, y, t):
    if MultiGood_Formulation:
        
        eta_ice_tank = np.empty([n_periods])
        
        for i in range(n_periods):
             eta_ice_tank = eta_ice_tank_nom-0.0004*(Tamb-25)     
        eta_ice_tank = pd.DataFrame(eta_ice_tank)
        eta_Series = eta_ice_tank.stack().reset_index(drop=True)

        # eta_2 = pd.DataFrame()  
        
        # for s in scenario:
        #     eta_Series_2 = pd.Series()
        #     for y in year:
        #         dum_2 = eta_ice_tank[(s-1)*n_years + y][:]
        #         eta_Series_2 = pd.concat([eta_Series_2,dum_2])
        #     eta_2.loc[:,s] = eta_Series_2
        # index_2 = pd.RangeIndex(1,n_years*n_periods+1)
        # eta_2.index = index_2
        
        return float(eta_ice_tank[0][(s,y,t)])
    
    else:
        return 0
    

def Initialize_Ice_Tank_Minimum_Capacity(model,ut):
    if model.Ice_Tank_Independence == 0:
        return 0
    else: 
        Periods = model.Ice_Tank_Independence*24
        Len =  int(model.Periods*model.Years/Periods)
        Grouper = 1
        index = 1
        for i in range(1, Len+1):
            for j in range(1,Periods+1):      
                Ice_Demand_2.loc[index, 'Grouper'] = Grouper
                index += 1      
            Grouper += 1
    
        upgrade_years_list = [1 for i in range(len(model.steps))]
        
        for u in range(1, len(model.steps)):
            upgrade_years_list[u] =upgrade_years_list[u-1] + model.Step_Duration
        if model.Steps_Number ==1:
            Ice_Demand_Upgrade = Ice_Demand_2    
        else:
            if ut==1:
                start = 0
                Ice_Demand_Upgrade = Ice_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]       
            elif ut == len(model.steps):
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Ice_Demand_Upgrade = Ice_Demand_2.loc[start :, :]       
            else:
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Ice_Demand_Upgrade = Ice_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]
        
        Period_Ice = Ice_Demand_Upgrade.groupby(['Grouper']).sum()        
        Period_Average_Ice= Period_Ice.mean()
        Available_Ice = sum(Period_Average_Ice[s]*model.Scenario_Weight[s] for s in model.scenarios) 
        
        return  Available_Ice/(1-model.Ice_Tank_Depth_of_Discharge)

#%%

def Initialize_Fuel_Specific_Cost(model, g, y):
    if Fuel_Specific_Cost_Calculation == 1 and Fuel_Specific_Cost_Import == 1:
        fuel_cost_data = pd.read_csv(fuel_file_path, delimiter=';', decimal=',',index_col=0)

        # Create a dictionary for fuel costs
        fuel_cost_dict = {(int(gen_type), int(year)): fuel_cost_data.at[year, gen_type]
                      for gen_type in fuel_cost_data.columns
                      for year in fuel_cost_data.index}
        return fuel_cost_dict[(g, y)]
    elif Fuel_Specific_Cost_Calculation == 1 and Fuel_Specific_Cost_Import == 0:
        years = range(1, n_years+1)
        fuel_cost_dict = {}
        for gen_type in range(n_generators):
            previous_cost = Fuel_Specific_Start_Cost[gen_type]
            for year in years:
                if year == 1: 
                    cost = previous_cost
                else: cost = previous_cost * (1 + Fuel_Specific_Cost_Rate[gen_type])
                fuel_cost_dict[(gen_type + 1, year)] = cost
                previous_cost = cost
        return fuel_cost_dict[(g, y)]
        
def Initialize_Fuel_Specific_Cost_1(model, g):
    return model.Fuel_Specific_Start_Cost[g] 



#%% 
def Initialize_Generator_Marginal_Cost(model,g,y):
    if Fuel_Specific_Cost_Calculation == 1: return model.Fuel_Specific_Cost[g,y]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])

def Initialize_Generator_Marginal_Cost_1(model,g):
    if Fuel_Specific_Cost_Calculation == 0: return model.Fuel_Specific_Cost_1[g]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])

"Partial Load Effect"
def Initialize_Generator_Start_Cost(model,g,y):
    if Fuel_Specific_Cost_Calculation == 1 and MILP_Formulation == 1: return model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g]*model.Generator_pgen[g]

def Initialize_Generator_Start_Cost_1(model,g):
    if Fuel_Specific_Cost_Calculation == 0 and MILP_Formulation == 1 and Generator_Partial_Load == 1: return model.Generator_Marginal_Cost_1[g]*model.Generator_Nominal_Capacity_milp[g]*model.Generator_pgen[g]

def Initialize_Generator_Marginal_Cost_milp(model,g,y):
    if Fuel_Specific_Cost_Calculation == 1 and MILP_Formulation == 1: return ((model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g])-model.Generator_Start_Cost[g,y])/model.Generator_Nominal_Capacity_milp[g] 

def Initialize_Generator_Marginal_Cost_milp_1(model,g):
    if Fuel_Specific_Cost_Calculation == 0 and MILP_Formulation == 1 and Generator_Partial_Load == 1: return ((model.Generator_Marginal_Cost_1[g]*model.Generator_Nominal_Capacity_milp[g])-model.Generator_Start_Cost_1[g])/model.Generator_Nominal_Capacity_milp[g] 

"Grid Connection"
if Grid_Availability_Simulation:
    grid_avail(average_n_outages, average_outage_duration, n_years, year_grid_connection,n_scenarios, n_periods)

if Grid_Connection:
    availability = pd.read_csv(grid_file_path, delimiter=';', header=0)
    # availability_excel = pd.read_excel('Inputs/Generation.xlsx', sheet_name = "Grid Availability")
else:
    # Create an empty DataFrame for non-grid connection case, same as before
    availability = pd.concat([pd.DataFrame(np.zeros(n_years * n_scenarios)).T for _ in range(n_periods)])
    availability.index = pd.Index(range(n_periods))
    availability.columns = range(1, (n_years* n_scenarios) + 1)

# Create grid_availability Series
grid_availability_Series = pd.Series()
for i in range(1, n_years * n_scenarios + 1):
    if Grid_Connection and Grid_Availability_Simulation: dum = availability[str(i)]
    elif Grid_Connection and Grid_Availability_Simulation == 0: dum = availability[str(i)]
    else: dum = availability[i]
    grid_availability_Series = pd.concat([grid_availability_Series, dum])

grid_availability = pd.DataFrame(grid_availability_Series)

# Create a MultiIndex
frame = [scenario, year, period]
index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
grid_availability.index = index


# Create grid_availability_2 DataFrame
grid_availability_2 = pd.DataFrame()
for s in scenario:
    grid_availability_Series_2 = pd.Series()
    for y in year:
        if Grid_Connection: dum_2 = availability[str((s - 1) * n_years + y)]
        else: dum_2 = availability[(s - 1) * n_years + y]
        grid_availability_Series_2 = pd.concat([grid_availability_Series_2, dum_2])
    grid_availability_2[s] = grid_availability_Series_2

# Create a RangeIndex
index_2 = pd.RangeIndex(1, n_years * n_periods + 1)
grid_availability_2.index = index_2

def Initialize_Grid_Availability(model, s, y, t): 
    return float(grid_availability[0][(s,y,t)])


def Initialize_National_Grid_Inv_Cost(model):
    Grid_Connection_Specific_Cost = model.Grid_Connection_Cost  
    Grid_Distance = model.Grid_Distance  
    return Grid_Distance[None]*Grid_Connection_Specific_Cost[None]* model.Grid_Connection[None]/((1+model.Discount_Rate)**(model.Year_Grid_Connection-1))
    
def Initialize_National_Grid_OM_Cost(model):
    Grid_Connection_Specific_Cost = model.Grid_Connection_Cost
    Grid_Distance = model.Grid_Distance
    Grid_Maintenance_Cost = model.Grid_Maintenance_Cost
    Grid_OM_Cost = (Grid_Connection_Specific_Cost * model.Grid_Connection * Grid_Distance) * Grid_Maintenance_Cost
    Grid_Fixed_Cost = pd.DataFrame()
    g_fc = 0

    for y in model.year:  # Assuming 'year' is a member of 'model'
        if y < model.Year_Grid_Connection[None]:
            g_fc += (0) / ((1 + model.Discount_Rate) ** (y))
        else:
            g_fc += (Grid_OM_Cost) / ((1 + model.Discount_Rate) ** (y))

    grid_fc = pd.DataFrame({'Total': g_fc}, index=pd.MultiIndex.from_tuples([("Fixed cost", "National Grid", "-", "kUSD")]))
    grid_fc.index.names = ['Cost item', 'Component', 'Scenario', 'Unit']

    Grid_Fixed_Cost = pd.concat([Grid_Fixed_Cost, grid_fc], axis=1).fillna(0)
    Grid_Fixed_Cost = Grid_Fixed_Cost.groupby(level=[0], axis=1, sort=False).sum()

    return Grid_Fixed_Cost.iloc[0]['Total']


#%% Initialization of COP; it varies according to Tamb and the COP_n (empirical result by Khalaf et al.)

if MultiGood_Formulation:

    for i in range(n_periods):
        COP=COP_n-0.03*(Tamb.values-25)   
    COP = pd.DataFrame(COP)
    
    COP_Series = COP.stack()
    COP = pd.DataFrame(COP_Series)
    frame = [scenario,year,period]
    index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
    COP.index = index
       
    # COP_2 = pd.DataFrame()    
    # for s in scenario:
    #     COP_Series_2 = pd.Series()
    #     for y in year:
    #         dum_2 = COP[(s-1)*n_years + y][:]
    #         COP_Series_2 = pd.concat([COP_Series_2,dum_2])
    #     COP_2.loc[:,s] = COP_Series_2
    # index_2 = pd.RangeIndex(1,n_years*n_periods+1)
    # COP_2.index = index_2


def Initialize_COP(model, s, y, t):
    if MultiGood_Formulation:
        return float(COP[0][(s,y,t)])
    else:
        return 0

#%% Initialization of groundwater temperature

if MultiGood_Formulation:

    for i_day in range(n_periods):
        Tgw = Tav - 3 * np.cos(((2 * np.pi) / 365) * (i_day - nmin))  
    Tgw = pd.DataFrame(Tgw)
    
    Tgw_Series = Tgw.stack()
    Tgw = pd.DataFrame(Tgw_Series)
    frame = [scenario,year,period]
    index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
    Tgw.index = index
    
def Initialize_Tgw(model, s, y, t):
    if MultiGood_Formulation:
        return float(Tgw[0][(s,y,t)])
    else:
        return 0

 