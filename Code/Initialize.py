"Module for initialization of specific parameters (e.g. RES time series, Demand, Grid availability)"

import pandas as pd, numpy as np
import re
from RES_calculation import RE_supply
from Demand import demand_generation
from Grid_Availability import grid_availability as grid_avail

#%% This section extracts the values of Scenarios, Periods, Years from data.dat and creates ranges for them
Data_file = "Inputs/Model_data.dat"
Data_import = open(Data_file).readlines()

for i in range(len(Data_import)):
    if "param: Scenarios" in Data_import[i]:
        n_scenarios = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Years" in Data_import[i]:
        n_years = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Generator_Types" in Data_import[i]:      
        n_generators = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Step_Duration" in Data_import[i]:
        step_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Min_Last_Step_Duration" in Data_import[i]:
        min_last_step_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Battery_Independence" in Data_import[i]:      
        Battery_Independence = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Renewable_Penetration" in Data_import[i]:      
        Renewable_Penetration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Greenfield_Investment" in Data_import[i]:      
        Greenfield_Investment = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Multiobjective_Optimization" in Data_import[i]:      
        Multiobjective_Optimization = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Optimization_Goal" in Data_import[i]:      
        Optimization_Goal = int((re.findall('\d+',Data_import[i])[0]))
    if "param: MILP_Formulation" in Data_import[i]:      
        MILP_Formulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: MES_Formulation" in Data_import[i]:      
        MES_Formulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Minute_Resolution" in Data_import[i]:
        Minute_Resolution = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Plot_Max_Cost" in Data_import[i]:      
        Plot_Max_Cost = int((re.findall('\d+',Data_import[i])[0]))
    if "param: RE_Supply_Calculation" in Data_import[i]:      
        RE_Supply_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Demand_Profile_Generation" in Data_import[i]:      
        Demand_Profile_Generation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Average_Number_Outages " in Data_import[i]:      
        average_n_outages = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Average_Outage_Duration" in Data_import[i]:       
        average_outage_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Connection " in Data_import[i]:      
        Grid_Connection = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Availability_Simulation" in Data_import[i]:      
        Grid_Availability_Simulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Year_Grid_Connection " in Data_import[i]:      
        year_grid_connection = int((re.findall('\d+',Data_import[i])[0]))

if Minute_Resolution:
    N_Time_Steps = 60
else:
    N_Time_Steps = 1
    
N_Periods = 8760*N_Time_Steps
Delta_Time = 1/N_Time_Steps
        
scenario = [i for i in range(1,n_scenarios+1)]
year = [i for i in range(1,n_years+1)]
period = [i for i in range(1,N_Periods+1)]
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

def Initialize_Renewable_Penetration(model):
    return Renewable_Penetration

#%% This section imports the multi-year Demand and Renewable-Energy output and creates a Multi-indexed DataFrame for it


if RE_Supply_Calculation:
   Renewable_Energy = RE_supply().drop([None], axis=1).set_index([pd.Index([ii for ii in range(1,8761)])], inplace = False)
else:
   Renewable_Energy = pd.read_excel('Inputs/Generation.xlsx', sheetname = "Renewable Energy", nrows = N_Periods) 
if Demand_Profile_Generation:     #so far works only with 1 hour resolution
   Demand = demand_generation() 
else:
   Demand = pd.read_excel('Inputs/Demand.xlsx', sheetname = "Electric", nrows = N_Periods)
   
if MES_Formulation:
   SC_Energy_Production = pd.read_excel('Inputs/Generation.xlsx', sheetname = "Solar_Collectors", nrows = N_Periods) 
   Thermal_Energy_Demand = pd.read_excel('Inputs/Demand.xlsx', sheetname = "Thermal", nrows = N_Periods)

Electric_Energy_Demand_Series = pd.Series()
for i in range(1,n_years*n_scenarios+1):
    dum = Demand[i][:]
    Electric_Energy_Demand_Series = pd.concat([Electric_Energy_Demand_Series,dum])
Electric_Energy_Demand = pd.DataFrame(Electric_Energy_Demand_Series) 
frame = [scenario,year,period]
index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
Electric_Energy_Demand.index = index
Electric_Energy_Demand_2 = pd.DataFrame()    
for s in scenario:
    Electric_Energy_Demand_Series_2 = pd.Series()
    for y in year:
        dum_2 = Demand[(s-1)*n_years + y][:]
        Electric_Energy_Demand_Series_2 = pd.concat([Electric_Energy_Demand_Series_2,dum_2])
    Electric_Energy_Demand_2.loc[:,s] = Electric_Energy_Demand_Series_2
index_2 = pd.RangeIndex(1,n_years*N_Periods+1)
Electric_Energy_Demand_2.index = index_2

def Initialize_Periods(model):
    return N_Periods

def Initialize_Delta_Time(model):
    return Delta_Time

def Initialize_Electric_Demand(model, s, y, t):
    return float(Electric_Energy_Demand[0][(s,y,t)])

def Initialize_Thermal_Demand(model, s, y, ct, t):
    if MES_Formulation == 0:
        return 0    
    else:
        return float(Thermal_Energy_Demand[0][(s,y,t)])

def Initialize_RES_Energy(model,s,r,t):
    column = (s-1)*model.RES_Sources + r 
    return float(Renewable_Energy[column][t])   

def Initialize_SC_Energy(model,s,r,t):
    column = (s-1)*model.Classes + r
    if MES_Formulation==0:
        return 0
    else:
        return float(SC_Energy_Production[column][t])
    
def Initialize_Battery_Unit_Repl_Cost(model):
    Unitary_Battery_Cost = model.Battery_Specific_Investment_Cost - model.Battery_Specific_Electronic_Investment_Cost
    return Unitary_Battery_Cost/(model.Battery_Cycles*2*(1-model.Battery_Depth_of_Discharge))
      

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
                Energy_Demand_2.loc[index, 'Grouper'] = Grouper
                index += 1      
            Grouper += 1
    
        upgrade_years_list = [1 for i in range(len(model.steps))]
        
        for u in range(1, len(model.steps)):
            upgrade_years_list[u] =upgrade_years_list[u-1] + model.Step_Duration
        if model.Steps_Number ==1:
            Energy_Demand_Upgrade = Energy_Demand_2    
        else:
            if ut==1:
                start = 0
                Energy_Demand_Upgrade = Energy_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]       
            elif ut == len(model.steps):
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Energy_Demand_Upgrade = Energy_Demand_2.loc[start :, :]       
            else:
                start = model.Periods*(upgrade_years_list[ut-1] -1)+1
                Energy_Demand_Upgrade = Energy_Demand_2.loc[start : model.Periods*(upgrade_years_list[ut]-1), :]
        
        Period_Energy = Energy_Demand_Upgrade.groupby(['Grouper']).sum()        
        Period_Average_Energy = Period_Energy.mean()
        Available_Energy = sum(Period_Average_Energy[s]*model.Scenario_Weight[s] for s in model.scenarios) 
        
        return  Available_Energy/(1-model.Battery_Depth_of_Discharge)

#%% 
def Initialize_Generator_Marginal_Cost(model,s,y,g):
    return model.Fuel_Specific_Cost[g]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])


if Grid_Availability_Simulation:
    grid_avail(average_n_outages, average_outage_duration, n_years, year_grid_connection, N_Time_Steps)
if Grid_Connection:  
    availability = pd.read_excel('Inputs/Generation.xlsx', sheetname = "Grid Availability", nrows = N_Periods) 
else:
    availability = pd.concat([pd.DataFrame(np.zeros(n_years)).T for ii in range(8760* N_Time_Steps)])
    availability.set_axis([ii for ii in range(8760* N_Time_Steps)], axis='index', inplace = True)
    availability.set_axis([ii for ii in range(1,n_years+1)], axis='columns', inplace = True)

grid_availability_Series = pd.Series()
for i in range(1,n_years*n_scenarios+1):
    dum = availability[i][:]
    grid_availability_Series = pd.concat([grid_availability_Series,dum])
grid_availability = pd.DataFrame(grid_availability_Series) 
frame = [scenario,year,period]
index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
grid_availability.index = index
grid_availability_2 = pd.DataFrame()    
for s in scenario:
   grid_availability_Series_2 = pd.Series()
   for y in year:
      dum_2 = availability[(s-1)*n_years + y][:]
      grid_availability_Series_2 = pd.concat([grid_availability_Series_2,dum_2])
   grid_availability_2.loc[:,s] = grid_availability_Series_2
index_2 = pd.RangeIndex(1,n_years*N_Periods+1)
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
    Grid_OM_Cost=(Grid_Connection_Specific_Cost * model.Grid_Connection * Grid_Distance)* Grid_Maintenance_Cost
    Grid_Fixed_Cost = pd.DataFrame()
    g_fc = 0
    for y in year:
        if y < model.Year_Grid_Connection[None]:
            g_fc += (0)/((1+model.Discount_Rate)**(y))
        else:
            g_fc += (Grid_OM_Cost)/((1+model.Discount_Rate)**(y))
    grid_fc = pd.DataFrame(['Fixed cost', 'National Grid', '-', 'kUSD', g_fc]).T.set_index([0,1,2,3]) 
    grid_fc.columns = ['Total']
    grid_fc.index.names = ['Cost item', 'Component', 'Scenario', 'Unit']
    Grid_Fixed_Cost = pd.concat([Grid_Fixed_Cost, grid_fc], axis=1).fillna(0) 
    Grid_Fixed_Cost = Grid_Fixed_Cost.groupby(level=[0], axis=1, sort=False).sum()
    return Grid_Fixed_Cost.iloc[0]['Total']

def Initialize_Battery_Independence(model):
    return Battery_Independence

def Initialize_MES_Formulation(model):
    return MES_Formulation

def Initialize_Optimization_Goal(model):
    return Optimization_Goal

def Initialize_Multiobjective_Optimization(model):
    return Multiobjective_Optimization

def Initialize_MILP_Formulation(model):
    return MILP_Formulation

def Initialize_Renewable_Penetration(model):
    return Renewable_Penetration

def Initialize_Greenfield_Investment(model):
    return Greenfield_Investment

def Initialize_Plot_Max_Cost(model):
    return Plot_Max_Cost