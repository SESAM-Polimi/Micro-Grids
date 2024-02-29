"""
MicroGridsPy - Multi-year capacity-expansion (MYCE)

Linear Programming framework for microgrids least-cost sizing,
able to account for time-variable load demand evolution and capacity expansion.

Authors: 
    Alessandro Onori   - Department of Energy, Politecnico di Milano
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
import matplotlib.pyplot as plt
import re
import os
from RE_calculation import RE_supply
from Demand import demand_generation
from Grid_Availability import grid_availability as grid_avail


#%% This section extracts the values of Scenarios, Periods, Years from data.dat and creates ranges for them


current_directory = os.path.dirname(os.path.abspath(__file__))
inputs_directory = os.path.join(current_directory, '..', 'Inputs')
data_file_path = os.path.join(inputs_directory, 'Parameters.dat')
demand_file_path = os.path.join(inputs_directory, 'Demand.csv')
ice_file_path = os.path.join(inputs_directory, 'Ice.csv')
res_file_path = os.path.join(inputs_directory, 'RES_Time_Series.csv')
tamb_file_path = os.path.join(inputs_directory, 'Tamb.csv')
fuel_file_path = os.path.join(inputs_directory, 'Fuel Specific Cost.csv')
grid_file_path = os.path.join(inputs_directory, 'Grid Availability.csv')
results_directory = os.path.join(current_directory, '..', 'Results')
plots_directory = os.path.join(current_directory, '..', 'Results/Plots')

Data_import = open(data_file_path).readlines()

Fuel_Specific_Start_Cost = []
Fuel_Specific_Cost_Rate = []

for i in range(len(Data_import)):
    # Project Settings
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
    # Optimization Constraints
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
    # Model Switches
    if "param: MILP_Formulation" in Data_import[i]:      
        MILP_Formulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: MultiGood_Ice" in Data_import[i]:      
        MultiGood_Ice = int((re.findall('\d+',Data_import[i])[0]))
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
    if "param: Grid_Connection " in Data_import[i]:      
        Grid_Connection = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Availability_Simulation" in Data_import[i]:      
        Grid_Availability_Simulation = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Model_Components " in Data_import[i]:      
        Model_Components = int((re.findall('\d+',Data_import[i])[0]))
    if "param: WACC_Calculation " in Data_import[i]:      
        WACC_Calculation = int((re.findall('\d+',Data_import[i])[0]))
    # Specific Parameters values
    if "param: COP_n" in Data_import[i]:
        COP_n = float((re.findall('\d+\.*\d+',Data_import[i])[0]))
    if "param: eta_ice_tank_nom" in Data_import[i]:
        eta_ice_tank_nom = float((re.findall('\d+\.*\d+',Data_import[i])[0]))
    if "param: Grid_Average_Number_Outages" in Data_import[i]:      
        average_n_outages = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Grid_Average_Outage_Duration" in Data_import[i]:       
        average_outage_duration = int((re.findall('\d+',Data_import[i])[0]))
    if "param: Year_Grid_Connection " in Data_import[i]:      
        year_grid_connection = int((re.findall('\d+',Data_import[i])[0]))
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

#%% This section imports, generates and plots the different types of demands

def plot_average_daily_demand(demand_data, output_path):
    n_years = demand_data.shape[1]
    hours_per_day = 24

    plt.figure(figsize=(12, 6))

    # Calculate and plot average daily demand for each year
    for year in range(n_years):
        # Reshape yearly data into days and hours (assuming 365 days per year)
        yearly_data = demand_data.iloc[:, year].values.reshape(-1, hours_per_day)
        # Calculate average demand for each hour
        average_daily_demand = np.mean(yearly_data, axis=0) / 1000
        plt.plot(average_daily_demand, label=f'Year {year + 1}')

    plt.title('Average Daily Electric Demand for Each Year')
    plt.xlabel('Hour of Day')
    plt.ylabel('Power [kW]')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close() 

if Demand_Profile_Generation:
    Demand = demand_generation()
    print("Electric demand data generated endogenously using archtypes")
    plot_path = os.path.join(plots_directory, 'Electric Demand.png')
    plot_average_daily_demand(Demand, plot_path)
    print("Electric demand plot saved in Results/Plots")
else:
    Demand = pd.read_csv(demand_file_path, delimiter=';', decimal=',', header=0)
    Demand = Demand.drop(Demand.columns[0], axis=1)
    if n_scenarios == 1: Demand = Demand.iloc[:, :n_years]
    print("Electric demand data loaded exogenously from excel file")
    plot_path = os.path.join(plots_directory, 'Electric Demand.png')
    plot_average_daily_demand(Demand, plot_path)
    print("Electric demand plot saved in Results/Plots")

# Drop columns where all values are NaN, as they don't contain any useful data
Demand = Demand.dropna(how='all', axis=1)
Electric_Energy_Demand_Series = pd.Series(dtype=float)
# Adjust the loop to iterate over the actual column names of the DataFrame
for col in Demand.columns[0:]:
    dum = Demand[col].reset_index(drop=True)
    Electric_Energy_Demand_Series = pd.concat([Electric_Energy_Demand_Series, dum])
frame = [scenario, year, period]
index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
Electric_Energy_Demand = pd.DataFrame(Electric_Energy_Demand_Series)
Electric_Energy_Demand.index = index

Electric_Energy_Demand_2 = pd.DataFrame()
# Iterate over scenarios and years, assuming scenario and year are defined and match the CSV structure
for s in scenario:
    Electric_Energy_Demand_Series_2 = pd.Series()
    for y in year:
        # Construct the column name as it appears in the CSV headers
        if Demand_Profile_Generation: column_name = int(f'{(s-1)*len(year) + y}')
        else: column_name = f'{(s-1)*len(year) + y}'
        if column_name in Demand.columns:
            dum_2 = Demand[column_name].dropna().reset_index(drop=True)
            Electric_Energy_Demand_Series_2 = pd.concat([s for s in [Electric_Energy_Demand_Series_2, dum_2] if not s.empty])
        else:
            print(f"Warning: Column '{column_name}' does not exist in the Demand DataFrame")
    Electric_Energy_Demand_2[s] = Electric_Energy_Demand_Series_2

# Create a RangeIndex for Energy_Demand_2
index_2 = pd.RangeIndex(1, n_years * n_periods + 1)
Electric_Energy_Demand_2.index = index_2

"Electric Demand"
def Initialize_Demand(model, s, y, t):
    """
    Initializes electric demand based on the scenario, year, and period.

    Parameters:
    model (object): The model for which to initialize electric demand.
    s (int): Scenario number.
    y (int): Year.
    t (int): Time period.

    Returns:
    float: The electric demand.
    """
    return float(Electric_Energy_Demand[0][(s, y, t)])

def plot_average_daily_ice_demand(demand_data, output_path):
    n_years = demand_data.shape[1]
    hours_per_day = 24

    plt.figure(figsize=(12, 6))

    # Calculate and plot average daily demand for each year
    for year in range(n_years):
        # Reshape yearly data into days and hours (assuming 365 days per year)
        yearly_data = demand_data.iloc[:, year].values.reshape(-1, hours_per_day)
        # Calculate average demand for each hour
        average_daily_demand = np.mean(yearly_data, axis=0)
        plt.plot(average_daily_demand, label=f'Year {year + 1}')

    plt.title('Average Daily Ice Demand for Each Year')
    plt.xlabel('Hour of Day')
    plt.ylabel('Ice Mass [kg]')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close() 

if MultiGood_Ice == 1:
    Ice = pd.read_csv(ice_file_path, delimiter=';', decimal=',', header=0)
    Ice = Ice.drop(Ice.columns[0], axis=1)
    if n_scenarios == 1: Ice = Ice.iloc[:, :n_years]
    print("Ice demand data loaded exogenously from excel file")
    plot_path = os.path.join(plots_directory, 'Ice Demand.png')
    plot_average_daily_ice_demand(Ice, plot_path)
    print("Ice demand plot saved in Results/Plots")

    # Drop columns where all values are NaN, as they don't contain any useful data
    Ice = Ice.dropna(how='all', axis=1)
    Ice_Demand_Series = pd.Series(dtype=float)
    # Adjust the loop to iterate over the actual column names of the DataFrame
    for col in Ice.columns[0:]:
        dum = Ice[col].reset_index(drop=True)
        Ice_Demand_Series = pd.concat([Ice_Demand_Series, dum])
    frame = [scenario, year, period]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
    Ice_Demand = pd.DataFrame(Ice_Demand_Series)
    Ice_Demand.index = index

    Ice_Demand_2 = pd.DataFrame()
    # Iterate over scenarios and years, assuming scenario and year are defined and match the CSV structure
    for s in scenario:
        Ice_Demand_Series_2 = pd.Series()
        for y in year:
            # Construct the column name as it appears in the CSV headers
            column_name = f'{(s-1)*len(year) + y}'
            if column_name in Ice.columns:
                dum_2 = Ice[column_name].dropna().reset_index(drop=True)
                Ice_Demand_Series_2 = pd.concat([s for s in [Ice_Demand_Series_2, dum_2] if not s.empty])
            else:
                print(f"Warning: Column '{column_name}' does not exist in the Demand DataFrame")
        Ice_Demand_2[s] = Ice_Demand_Series_2

    # Create a RangeIndex for Energy_Demand_2
    index_2 = pd.RangeIndex(1, n_years * n_periods + 1)
    Ice_Demand_2.index = index_2


"Ice Demand"
def Initialize_Ice_Demand(model, s, y, t):
    """
    Initializes Ice demand based on the scenario, year, and period.

    Parameters:
    model (object): The model for which to initialize electric demand.
    s (int): Scenario number.
    y (int): Year.
    t (int): Time period.

    Returns:
    float: The Ice demand.
    """
    if MultiGood_Ice: return float(Ice_Demand[0][(s, y, t)])
    else: None

#%% This section imports or generates the renewables and temperature time series data 

def plot_renewable_energy_availability(renewable_energy_data, output_path):
    hours_per_day = 24

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Assuming first column is solar (resource 1), second is wind (resource 2)
    resource_colors = ['yellow', 'lightblue']

    # Plotting first resource
    col = renewable_energy_data.columns[1]  # Resource 1
    yearly_data = renewable_energy_data[col].values.reshape(-1, hours_per_day)
    average_daily_availability = np.mean(yearly_data, axis=0)
    line1 = ax1.fill_between(range(hours_per_day), average_daily_availability, color=resource_colors[0], alpha=0.5, label=f'Resource 1')
    ax1.set_xlabel('Hour of Year')
    ax1.set_ylabel('RES 1 - Electricity production per unit [W]')
    ax1.grid(True)

    # Creating a second y-axis for the second resource
    ax2 = ax1.twinx()
    col = renewable_energy_data.columns[2]  # Resource 2
    yearly_data = renewable_energy_data[col].values.reshape(-1, hours_per_day)
    average_daily_availability = np.mean(yearly_data, axis=0)
    line2 = ax2.fill_between(range(hours_per_day), average_daily_availability, color=resource_colors[1], alpha=0.5, label=f'Resource 2')
    ax2.set_ylabel('RES 2 - Electricity production per unit [W]')

    plt.title('Renewable Energy Resource Availability')

    # Combining legends from both axes
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels, loc='upper right')

    plt.savefig(output_path)
    plt.close()

if RE_Supply_Calculation == 0: 
    Renewable_Energy = pd.read_csv(res_file_path, delimiter=';', decimal=',', header=0)
    print("Renewables Time Series data loaded exogenously from excel file")
    plot_path = os.path.join(plots_directory, 'Renewables Availability.png')
else:
    Renewable_Energy,T_amb = RE_supply()
    Renewable_Energy = Renewable_Energy.set_index(pd.Index(range(1, n_periods+1)), inplace=False)
    print("Renewables Time Series data generated endogenously using NASA POWER")

plot_renewable_energy_availability(Renewable_Energy, plots_directory)
print("Renewables Availability plot saved in Results/Plots")

def Initialize_RES_Energy(model, s, r, t):
    """
    Initializes renewable energy supply based on the specified scenario, resource, and time period.

    Parameters:
    model (object): The model for which the renewable energy supply is initialized.
    scenario (int): The scenario number.
    resource (int): The resource index.
    time_period (int): The time period index.

    Returns:
    float: The amount of renewable energy supplied.
    """
    column = (s - 1) * model.RES_Sources + r
    return float(Renewable_Energy.iloc[t - 1, column]) 

if MultiGood_Ice:
    if RE_Supply_Calculation == 0: 
        Tamb = pd.read_csv(tamb_file_path, delimiter=';', decimal=',', header=0)
        if n_scenarios == 1: Tamb = Tamb.iloc[:, 1:n_years+1]
        else: 
            Tamb.drop(Tamb.columns[0], axis=1, inplace=True)
            
    else:
        # Initialize Tamb with T_amb for the first year
        Tamb = T_amb.copy()
        # Append T_amb for each subsequent year
        for y in range(2, n_years + 1):
            # Reset index before concatenation to align the rows
            Tamb = pd.concat([Tamb, T_amb.reset_index(drop=True)], axis=1)
        # Rename the columns to reflect the year
        Tamb.columns = range(1, n_years + 1)
        
    # Drop columns where all values are NaN, as they don't contain any useful data
    Tamb = Tamb.dropna(how='all', axis=1)
    Tamb_Series = pd.Series(dtype=float)
    # Adjust the loop to iterate over the actual column names of the DataFrame
    for col in Tamb.columns[0:]:
        dum = Tamb[col].reset_index(drop=True)
        Tamb_Series = pd.concat([Tamb_Series, dum])
    frame = [scenario, year, period]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
    Tamb = pd.DataFrame(Tamb_Series, columns=['Tamb'])
    Tamb.index = index
    
    # Calculating Tav and nmin
    Tav = []
    nmin = []
    grouped = Tamb.groupby(level=['scenario', 'year'])
    for name, group in grouped:
        year_mean = group['Tamb'].mean()
        Tav.append(year_mean)
        min_index = group['Tamb'].idxmin()[2]
        nmin.append(min_index)

    tref = 25  # Reference temperature [°C]

def Initialize_Tamb(model, s, y, t):
    """
    Initializes the ambient temperature based on the specified scenario, year, and time period.

    Parameters:
    model (object): The model for which the temperature is initialized.
    scenario (int): The scenario number.
    year (int): The year index.
    time_period (int): The time period index.

    Returns:
    float: The ambient temperature for the given scenario, year, and time period.
    """
    
    if MultiGood_Ice: return float(Tamb.loc[(s, y, t), 'Tamb'])
    else: None

#%% This section defines the number of investment steps as well as assigns each year to its corresponding step

def Initialize_Upgrades_Number(model):
    """
    Calculates the number of upgrades for the given model.

    Parameters:
    model (object): The model for which to calculate upgrades.

    Returns:
    int: Number of upgrades.
    """
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
    """
    Initializes year-upgrade tuples for the model.

    Parameters:
    model (object): The model for which to initialize year-upgrade tuples.

    Returns:
    list: List of year-upgrade tuples.
    """
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


#%% This section initializes economic parameters related to the project

def Initialize_Discount_Rate(model):
    """
    Calculates and initializes the discount rate for the model.

    Parameters:
    model (object): The model for which to calculate the discount rate.

    Returns:
    float: The calculated discount rate.
    """
    if WACC_Calculation:
        if equity_share == 0:
            discount_rate = cost_of_debt*(1-tax)
        else:
           # Definition of Leverage (L): risk perceived by investors, or viceversa as the attractiveness of the investment to external debtors.
           L = debt_share/equity_share 
           discount_rate = cost_of_debt*(1-tax)*L/(1+L) + cost_of_equity*1/(1+L)
           print("Weighted Average Cost of Capital calculation completed")
    else:
        discount_rate = Discount_Rate_default
    return discount_rate

################################################################## ELECTRICITY PRODUCTION ##########################################################################

#%% This section initializes parameters related to the battery bank

def Initialize_Battery_Unit_Repl_Cost(model):
    """
    Initializes the unit replacement cost of the battery based on the model parameters.

    Parameters:
    model (object): The model containing parameters related to battery cost and performance.

    Returns:
    float: The calculated unit replacement cost of the battery.
    """
    Unitary_Battery_Cost = model.Battery_Specific_Investment_Cost - model.Battery_Specific_Electronic_Investment_Cost
    return Unitary_Battery_Cost/(model.Battery_Cycles*2*(model.Battery_Depth_of_Discharge))
      

def Initialize_Battery_Minimum_Capacity(model,ut): 
    """
    Calculates the minimum capacity required for the battery bank based on the model's demand profile and battery independence criteria.

    Parameters:
    model (object): The model containing parameters and configurations for battery and demand.
    ut (int): The current upgrade step in the model.

    Returns:
    float: The minimum required battery capacity to ensure the desired level of battery independence.
    """
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
        
        return Available_Energy/(model.Battery_Depth_of_Discharge)


#%% This section initializes parameters related to generators and fuels

def Initialize_Fuel_Specific_Cost(model, g, y):
    """
    Initializes the specific cost of fuel for a generator type and a specific year. The function supports
    importing data from a file or calculating the cost based on a rate of increase.

    Parameters:
    model (object): The model for which the fuel cost is being initialized.
    g (int): The generator type index.
    y (int): The year index.

    Returns:
    float: The specific fuel cost for the given generator type and year.
    """
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
    """
    Initializes the starting specific cost of fuel for a generator type. This function is used when
    the fuel cost is fixed and not subject to annual variation.

    Parameters:
    model (object): The model for which the fuel cost is being initialized.
    g (int): The generator type index.

    Returns:
    float: The starting specific fuel cost for the given generator type.
    """
    return model.Fuel_Specific_Start_Cost[g] 

def Initialize_Generator_Marginal_Cost(model,g,y):
    """
    Initializes the marginal cost of operation for a generator type considering fuel cost, heating value of the fuel,
    and generator efficiency. This function is applicable when the fuel cost varies annually.

    Parameters:
    model (object): The model for which the marginal cost is being initialized.
    g (int): The generator type index.
    y (int): The year index.

    Returns:
    float: The marginal cost of operation for the specified generator type and year.
    """
    if Fuel_Specific_Cost_Calculation == 1: 
        return model.Fuel_Specific_Cost[g,y]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])
    else: None

def Initialize_Generator_Marginal_Cost_1(model,g):
    """
    Calculates the marginal cost of operation for a generator type with a fixed fuel cost,
    taking into account the heating value of the fuel and generator efficiency.

    Parameters:
    model (object): The model for which the marginal cost is being initialized.
    g (int): The generator type index.

    Returns:
    float: The marginal cost of operation for the specified generator type.
    """
    if Fuel_Specific_Cost_Calculation == 0: 
        return model.Fuel_Specific_Cost_1[g]/(model.Fuel_LHV[g]*model.Generator_Efficiency[g])
    else: None
    
def Initialize_Generator_Start_Cost(model,g,y):
    """
    Initializes the start-up cost of a generator for a given year. This cost is based on the generator's marginal cost,
    nominal capacity, and a part-load operation parameter. Applicable in dynamic fuel cost scenarios and MILP formulation.

    Parameters:
    model (object): The model for which the start-up cost is being initialized.
    g (int): The generator type index.
    y (int): The year index.

    Returns:
    float: The start-up cost for the specified generator type and year.
    """
    if Fuel_Specific_Cost_Calculation == 1 and MILP_Formulation == 1: 
        return model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g]*model.Generator_pgen[g]
    else: None

def Initialize_Generator_Start_Cost_1(model,g):
    """
    Initializes the start-up cost of a generator in a scenario with fixed fuel cost and considering MILP formulation.
    This cost is derived from the generator's marginal cost, nominal capacity, and part-load operation parameter.

    Parameters:
    model (object): The model for which the start-up cost is being initialized.
    g (int): The generator type index.

    Returns:
    float: The start-up cost for the specified generator type.
    """
    if Fuel_Specific_Cost_Calculation == 0 and MILP_Formulation == 1 and Generator_Partial_Load == 1: 
        return model.Generator_Marginal_Cost_1[g]*model.Generator_Nominal_Capacity_milp[g]*model.Generator_pgen[g]
    else: None

def Initialize_Generator_Marginal_Cost_milp(model,g,y):
    """
    Calculates the marginal cost for a generator under MILP formulation for dynamic fuel cost scenarios. 
    This cost accounts for the generator's operational characteristics, including nominal capacity and start-up costs.

    Parameters:
    model (object): The model for which the marginal cost is being initialized.
    g (int): The generator type index.
    y (int): The year index.

    Returns:
    float: The marginal cost for the specified generator type and year under MILP formulation.
    """
    if Fuel_Specific_Cost_Calculation == 1 and MILP_Formulation == 1: 
        return ((model.Generator_Marginal_Cost[g,y]*model.Generator_Nominal_Capacity_milp[g])-model.Generator_Start_Cost[g,y])/model.Generator_Nominal_Capacity_milp[g] 
    else: None

def Initialize_Generator_Marginal_Cost_milp_1(model,g):
    """
    Determines the marginal cost for a generator in scenarios with fixed fuel costs and MILP formulation. 
    This cost calculation considers the generator's nominal capacity and start-up cost.

    Parameters:
    model (object): The model for which the marginal cost is being initialized.
    g (int): The generator type index.

    Returns:
    float: The marginal cost for the specified generator type under MILP formulation with fixed fuel costs.
    """
    if Fuel_Specific_Cost_Calculation == 0 and MILP_Formulation == 1 and Generator_Partial_Load == 1: 
        return ((model.Generator_Marginal_Cost_1[g]*model.Generator_Nominal_Capacity_milp[g])-model.Generator_Start_Cost_1[g])/model.Generator_Nominal_Capacity_milp[g] 
    else: None
    
#%% This section initializes parameters related to grid connection

"Grid Connection"
if Grid_Connection == 1:
    if Grid_Availability_Simulation: 
        grid_avail(average_n_outages, average_outage_duration, n_years, year_grid_connection,n_scenarios, n_periods)
        availability = pd.read_csv(grid_file_path, delimiter=';', header=0)
    else: availability = pd.read_csv(grid_file_path, delimiter=';', header=0)

    # Create grid_availability Series
    grid_availability_Series = pd.Series()
    for i in range(1, n_years * n_scenarios + 1):
        dum = availability[str(i)]
        grid_availability_Series = pd.concat([s for s in [grid_availability_Series, dum] if not s.empty])

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
            grid_availability_Series_2 = pd.concat([s for s in [grid_availability_Series_2, dum_2] if not s.empty])
        grid_availability_2[s] = grid_availability_Series_2

    # Create a RangeIndex
    index_2 = pd.RangeIndex(1, n_years * n_periods + 1)
    grid_availability_2.index = index_2

def Initialize_Grid_Availability(model, s, y, t): 
    """
    Initializes the grid availability based on the specified scenario, year, and time period.

    Parameters:
    model (object): The model for which the grid availability is being initialized.
    s (int): The scenario number.
    y (int): The year.
    t (int): The time period.

    Returns:
    float: The grid availability for the specified scenario, year, and time period.
    """
    if Grid_Connection: return float(grid_availability[0][(s,y,t)])
    else: 0

def Initialize_National_Grid_Inv_Cost(model):
    """
    Calculates the initial investment cost of connecting to the national grid,
    considering the distance to the grid, specific connection cost, and discount rate.

    Parameters:
    model (object): The model for which the grid investment cost is being initialized.

    Returns:
    float: The total investment cost for connecting to the national grid.
    """
    if Grid_Connection: return model.Grid_Distance*model.Grid_Connection_Cost* model.Grid_Connection/((1+model.Discount_Rate)**(model.Year_Grid_Connection-1))
    else: 0
    
def Initialize_National_Grid_OM_Cost(model):
    """
    Calculates the operation and maintenance cost for the national grid connection,
    accounting for the specific connection cost, grid maintenance cost, and discount rate over the project lifetime.

    Parameters:
    model (object): The model for which the grid O&M cost is being initialized.

    Returns:
    float: The total operation and maintenance cost for the national grid connection.
    """
    Grid_OM_Cost = (model.Grid_Connection_Cost * model.Grid_Connection * model.Grid_Distance) * model.Grid_Maintenance_Cost
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

    if Grid_Connection: return Grid_Fixed_Cost.iloc[0]['Total']
    else: 0

################################################################## ICE PRODUCTION ##########################################################################

#%% This section initializes parameters related to ice tank

def Initialize_Eta_Ice_Tank(model, s, y, t):
    """
    Initializes the efficiency of the ice tank based on ambient temperature for each scenario, year, and time period.
    The ice tank efficiency empirically decreases with the increase of the ambient temperature.

    Parameters:
    model (object): The model for which the ice tank efficiency is initialized.
    s (int): Scenario number.
    y (int): Year.
    t (int): Time period.

    Returns:
    float: The efficiency of the ice tank for the given scenario, year, and time period.
    """
    if MultiGood_Ice:
        # Calculate efficiency for all combinations using vectorized operations
        Tamb['eta'] = eta_ice_tank_nom - 0.0004 * (Tamb['Tamb'] - tref)

        # Retrieve the efficiency for the specific scenario, year, and time period
        return float(Tamb.loc[(s, y, t), 'eta'])
    else:
        return None
    

def Initialize_Ice_Tank_Minimum_Capacity(model,ut):
    """
    Calculates the minimum ice tank capacity required based on the ice demand profile and ice tank independence criteria.

    Parameters:
    model (object): The model containing parameters and configurations for ice demand and ice tank.
    ut (int): The current upgrade step in the model.

    Returns:
    float: The minimum required ice tank capacity to ensure the desired level of ice tank independence.
    """
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
    

#%% This section initializes parameters related to refrigeration cycle to meet the ice demand

if MultiGood_Ice:
    cop_list = []
    for s in scenario:
        for y in year:
            for t in period:
                # Access the temperature for each specific scenario, year, and period
                temperature = float(Tamb.loc[(s, y, t), 'Tamb'])
                cop_value = COP_n - 0.03 * (temperature - tref)
                cop_list.append(max(cop_value, 0))  # Ensure COP is not negative

    # Create the DataFrame with the corresponding MultiIndex
    cop_df = pd.DataFrame(cop_list, columns=['COP'])
    cop_df.index = pd.MultiIndex.from_product([scenario, year, period], names=['scenario', 'year', 'period'])
    print("COP calculation completed for all scenarios, years, and periods")
    
def Initialize_COP(model, s, y, t):
    """
    Initializes the Coefficient of Performance (COP) for the ice tank based on the ambient temperature and empirical relationship.

    Parameters:
    model (object): The model for which the COP is initialized.
    s (int): Scenario number.
    y (int): Year.
    t (int): Time period.

    Returns:
    float: The COP for the ice tank for the given scenario, year, and time period.
    """
    if MultiGood_Ice: return float(cop_df.loc[(s, y, t), 'COP'])
    else: return None

if MultiGood_Ice:
    # Initialize an array to store groundwater temperatures for each hour of the year, for each scenario and year
    Tgw_array = np.empty([n_scenarios * n_years * n_periods])
    # Initialize an index to keep track of the position in Tgw_array
    index = 0  
    # Iterate over each scenario and year
    for s in range(1, n_scenarios + 1):
        for y in range(1, n_years + 1):
            # For each day of the year, calculate the daily average groundwater temperature
            for i_day in range(1, 366):  # Assuming 365 days in a year
                # Calculate daily average temperature based on the day of the year and the day with the lowest temperature
                Ti = Tav[y-1] - 3 * np.cos(((2 * np.pi) / 365) * (i_day - nmin[y-1]))
                # Assign this daily average temperature to each hour of the day
                for hour in range(24):
                    Tgw_array[index] = Ti
                    index += 1
    # Create a DataFrame from the Tgw_array with the calculated temperatures
    Tgw_df = pd.DataFrame(Tgw_array, columns=['Temperature'])
    # Create a MultiIndex for the DataFrame using scenarios, years, and periods (hours)
    frame = [list(range(1, n_scenarios + 1)), list(range(1, n_years + 1)), list(range(1, n_periods + 1))]
    index = pd.MultiIndex.from_product(frame, names=['scenario', 'year', 'period'])
    Tgw_df.index = index
    print("Groundwater Temperature calculation completed for all scenarios, years, and periods")

    
def Initialize_Tgw(model, s, y, t):
    """
    Initializes the groundwater temperature based on the specified scenario, year, and time period.

    Parameters:
    model (object): The model for which the groundwater temperature is initialized.
    scenario (int): The scenario number.
    year (int): The year index.
    time_period (int): The time period index.

    Returns:
    float: The groundwater temperature for the given scenario, year, and time period.
    """
    if MultiGood_Ice: return float(Tgw_df.loc[(s, y, t), 'Temperature'])
    else: return None