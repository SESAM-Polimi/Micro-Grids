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
from RE_calculation import RE_supply
from Demand import demand_generation
from Grid_Availability import grid_availability as grid_avail
import csv
from itertools import chain


#%% This section extracts the values of Scenarios, Periods, Years from data.dat and creates ranges for them
Data_file = "Inputs/Parameters.dat"
Data_import = open(Data_file).readlines()

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
    if "param: Plot_Max_Cost" in Data_import[i]:      
        Plot_Max_Cost = int((re.findall('\d+',Data_import[i])[0]))
    if "param: RE_Supply_Calculation" in Data_import[i]:      
        RE_Supply_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Demand_Profile_Generation" in Data_import[i]:      
        Demand_Profile_Generation = int((re.findall('\d+',Data_import[i])[0]))
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

    if "param: Battery_Degradation" in Data_import[i]:      
        Battery_Degradation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Battery_Technology " in Data_import[i]:      
        Battery_Type = int((re.findall('\d+',Data_import[i])[0])) 
    if "param: Battery_Depth_of_Discharge " in Data_import[i]:      
        Battery_DoD = float((re.findall('\d+.\d+',Data_import[i])[0]))
    if "param: Battery_Cycles " in Data_import[i]:      
        Battery_Cycles = int((re.findall('\d+',Data_import[i])[0])) 
        

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

#%% This section imports the multi-year Demand and Renewable-Energy output and creates a Multi-indexed DataFrame for it

if RE_Supply_Calculation:
    Renewable_Energy = RE_supply().set_index(pd.Index(range(1, 8761)), inplace=False)
    T_amb = list(Renewable_Energy.loc[:, "Ambient Temperature"])
else:
    Renewable_Energy = pd.read_csv('Inputs/RES_Time_Series.csv', delimiter=';', decimal=',', header=0)
    T_amb = list(Renewable_Energy.loc[:, "Ambient Temperature"])
    
if Demand_Profile_Generation:
    Demand = demand_generation()

Demand = pd.read_csv('Inputs/Demand.csv', delimiter=';', decimal=',', header=0)
    
# Drop columns where all values are NaN, as they don't contain any useful data
Demand = Demand.dropna(how='all', axis=1)
    
Energy_Demand_Series = pd.Series()
# Adjust the loop to iterate over the actual column names of the DataFrame
for col in Demand.columns[1:]:  # Skip the first column if it's an index, otherwise adjust as needed
    dum = Demand[col].reset_index(drop=True)
    Energy_Demand_Series = pd.concat([Energy_Demand_Series, dum])


Energy_Demand = pd.DataFrame(Energy_Demand_Series) 
frame = [scenario,year,period]
index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
Energy_Demand.index = index

Energy_Demand_2 = pd.DataFrame()
# Iterate over scenarios and years, assuming scenario and year are defined and match the CSV structure
for s in scenario:
    Energy_Demand_Series_2 = pd.Series()
    for y in year:
        # Construct the column name as it appears in the CSV headers
        column_name = f'{(s-1)*len(year) + y}'
        if column_name in Demand.columns:
            dum_2 = Demand[column_name].dropna().reset_index(drop=True)
            Energy_Demand_Series_2 = pd.concat([Energy_Demand_Series_2, dum_2])
        else:
            print(f"Warning: Column '{column_name}' does not exist in the Demand DataFrame")
    Energy_Demand_2[s] = Energy_Demand_Series_2

# Create a RangeIndex for Energy_Demand_2
index_2 = pd.RangeIndex(1, n_years * n_periods + 1)
Energy_Demand_2.index = index_2


def Initialize_Demand(model, s, y, t):
    return float(Energy_Demand[0][(s,y,t)])

def Initialize_RES_Energy(model, s, r, t):
    column = (s - 1) * model.RES_Sources + r
    return float(Renewable_Energy.iloc[t - 1, column])   

if MILP_Formulation == 1 and Battery_Degradation == 1: #initialize coefficients for battery degradation model
    T_amb = [T_amb for ii in range(1,n_years+1)]
    T_amb_ = list(chain(*T_amb))
    Tamb = [y/10 for y in T_amb_]
    z = (Battery_DoD*10)-2
    Alpha = []; Beta = []
    for x in Tamb:
        if Battery_Type==1: # 1=LFP
            cycle_coefficient = 6400/Battery_Cycles
            if Battery_DoD==0.8:
                Alpha.append(3.446908*10**(-10)*(x**3)+1.240398*10**(-9)*(x**2)+1.053498*10**(-8)*(x)+1.970248*10**(-8))
                Beta.append((6.337047*10**(-7)*(x**3)-2.869914*10**(-6)*(x**2)+9.192472*10**(-6)*(x)+3.861381*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.9:
                Alpha.append(3.446908*10**(-10)*(x**3)+1.240398*10**(-9)*(x**2)+1.053498*10**(-8)*(x)+1.970248*10**(-8))
                Beta.append((6.070837*10**(-7)*(x**3)-2.769339*10**(-6)*(x**2)+8.701044*10**(-6)*(x)+3.423667*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.7:
                Alpha.append(4.485623*10**(-10)*(x**3)+1.614189*10**(-9)*(x**2)+1.370967*10**(-8)*(x)+2.563976*10**(-8))
                Beta.append((7.549737*10**(-7)*(x**3)-3.721425*10**(-6)*(x**2)+1.167026*10**(-5)*(x)+3.269498*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.6:
                Alpha.append(4.485623*10**(-10)*(x**3)+1.614189*10**(-9)*(x**2)+1.370967*10**(-8)*(x)+2.563976*10**(-8))
                Beta.append((8.528446*10**(-7)*(x**3)-4.189309*10**(-6)*(x**2)+1.323273*10**(-5)*(x)+3.85312*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.5:
                Alpha.append(4.485623*10**(-10)*(x**3)+1.614189*10**(-9)*(x**2)+1.370967*10**(-8)*(x)+2.563976*10**(-8))
                Beta.append((9.085917*10**(-7)*(x**3)-4.051845*10**(-6)*(x**2)+1.32569*10**(-5)*(x)+6.130398*10**(-6))*cycle_coefficient)
        elif Battery_Type==2: # 2=NMC
            cycle_coefficient = 5000/Battery_Cycles
            if Battery_DoD==0.8:
                Alpha.append(8.32382*10**(-11)*(x**3)+8.912264*10**(-10)*(x**2)+6.706961*10**(-9)*(x)+1.814235*10**(-8))    
                Beta.append((1.403785*10**(-6)*(x**3)-4.530322*10**(-6)*(x**2)+1.324309*10**(-5)*(x)-2.212139*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.9:
                Alpha.append(8.32382*10**(-11)*(x**3)+8.912264*10**(-10)*(x**2)+6.706961*10**(-9)*(x)+1.814235*10**(-8))
                Beta.append((1.326799*10**(-6)*(x**3)-4.21017*10**(-6)*(x**2)+1.256349*10**(-5)*(x)-1.862879*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.7:
                Alpha.append(9.208524*10**(-11)*(x**3)+9.854044*10**(-10)*(x**2)+7.418433*10**(-9)*(x)+2.006416*10**(-8))
                Beta.append((1.543396*10**(-6)*(x**3)-5.03352*10**(-6)*(x**2)+1.451821*10**(-5)*(x)-2.625175*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.6:
                Alpha.append(9.208524*10**(-11)*(x**3)+9.854044*10**(-10)*(x**2)+7.418433*10**(-9)*(x)+2.006416*10**(-8))
                Beta.append((1.746515*10**(-6)*(x**3)-5.739906*10**(-6)*(x**2)+1.640342*10**(-5)*(x)-3.106159*10**(-6))*cycle_coefficient)
            elif Battery_DoD==0.5:
                Alpha.append(9.208524*10**(-11)*(x**3)+9.854044*10**(-10)*(x**2)+7.418433*10**(-9)*(x)+2.006416*10**(-8))
                Beta.append((2.044415*10**(-6)*(x**3)-6.759912*10**(-6)*(x**2)+1.917865*10**(-5)*(x)-3.760983*10**(-6))*cycle_coefficient)
        elif Battery_Type==3: # 3=Lead Acid
                cycle_coefficient = 3000/Battery_Cycles
                Alpha.append(2.283105*10**(-6))
                Beta.append((-1.012639*10**(-7)*(z**3)+1.534911*10**(-6)*(z**2)-8.427153*10**(-6)*(z)+2.813216*10**(-5))*cycle_coefficient)
     
    Alpha.append(Alpha[len(Alpha)-1])
    Beta.append(Beta[len(Beta)-1])

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
        
        return  Available_Energy/(model.Battery_Depth_of_Discharge)


#%% 
def Initialize_Generator_Marginal_Cost(model,g,y):
    return model.Fuel_Specific_Cost[g]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])
   
"Partial Load Effect"
def Initialize_Generator_Start_Cost(model,g,y):
    return model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g]*model.Generator_pgen[g]

def Initialize_Generator_Marginal_Cost_milp(model,g,y):
    return ((model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g])-model.Generator_Start_Cost[g,y])/model.Generator_Nominal_Capacity_milp[g] 

"Grid Connection"
if Grid_Availability_Simulation:
    grid_avail(average_n_outages, average_outage_duration, n_years, year_grid_connection)

if Grid_Connection:
    availability = pd.read_csv('Inputs/Grid Availability.csv', delimiter=';', header=0)
    # availability_excel = pd.read_excel('Inputs/Generation.xlsx', sheet_name = "Grid Availability")
else:
    # Create an empty DataFrame for non-grid connection case, same as before
    availability = pd.concat([pd.DataFrame(np.zeros(n_years)).T for _ in range(8760)])
    availability.index = pd.Index(range(8760))
    availability.columns = range(1, n_years + 1)

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
