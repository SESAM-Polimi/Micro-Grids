"Module for Pyomo variables and parameters definition"

from pyomo.environ import Param, RangeSet, NonNegativeReals, Var, Set, Reals, Binary 
from Initialize import * # Import library with initialization functions for the parameters

def Model_Creation(model):

#%% PARAMETERS  

    "RES parameters"
    
    model.base_URL= Param()
    model.loc_id = Param()
    model.parameters_1 = Param()			
    model.parameters_2 = Param()			
    model.parameters_3 = Param() 				
    model.date_start =  Param() 						
    model.date_end =  Param()						
    model.community = Param() 			
    model.temp_res_1 = Param()						
    model.temp_res_2 = Param()							
    model.output_format = Param()					
    model.user = Param() 						
    model.lat = Param() 						
    model.lon = Param() 							
    model.time_zone = Param()								
    model.nom_power = Param()						
    model.tilt = Param()								   
    model.azim = Param()								   
    model.ro_ground = Param()						
    model.k_T = Param()							
    model.NMOT = Param()								   
    model.T_NMOT = Param()						
    model.G_NMOT = Param()							
    model.turbine_type = Param()							
    model.turbine_model = Param()				 	
    model.drivetrain_efficiency = Param()             			
        
    "Demand parameters"
    
    model.demand_growth = Param() 							
    model.cooling_period = Param() 							
    model.h_tier1 = Param()  								
    model.h_tier2 = Param()  							
    model.h_tier3 = Param()  							
    model.h_tier4 = Param() 								
    model.h_tier5 = Param()  								
    model.schools = Param()  							
    model.hospital_1 = Param()  							
    model.hospital_2 = Param()  							
    model.hospital_3 = Param()  							
    model.hospital_4 = Param()  						
    model.hospital_5 = Param()					
      
    "Project parameters"
    model.Periods         = Param(within=NonNegativeReals,
                                  initialize=Initialize_Periods)                          # Number of periods of analysis of the energy variables
    model.Years           = Param(within=NonNegativeReals)                          # Number of years of the project
    model.Step_Duration   = Param(within=NonNegativeReals)
    model.Min_Last_Step_Duration = Param(within=NonNegativeReals)
    model.Delta_Time      = Param(within=NonNegativeReals,
                                  initialize=Initialize_Delta_Time)                          # Time step in hours
    model.Classes         = Param(within=NonNegativeReals)  
    model.StartDate       = Param()                                                 # Start date of the analisis
    model.Scenarios                         = Param(within=NonNegativeReals) 
    model.Discount_Rate                     = Param(within=NonNegativeReals)                          # Discount rate of the project in %
    model.Investment_Cost_Limit             = Param(within=NonNegativeReals)
    model.Steps_Number                      = Param(initialize = Initialize_Upgrades_Number)
    model.RES_Sources                       = Param(within=NonNegativeReals)
    model.Generator_Types                   = Param(within=NonNegativeReals)   
    model.Year_Grid_Connection              = Param(within=NonNegativeReals) 
    model.Optimization_Goal                 = Param(within=NonNegativeReals,
                                                    initialize=Initialize_Optimization_Goal)
    model.Multiobjective_Optimization       = Param(within=NonNegativeReals,
                                              initialize=Initialize_Multiobjective_Optimization)
    model.Minute_Resolution                = Param(within=NonNegativeReals) 
    model.MILP_Formulation                  = Param(within=NonNegativeReals,
                                                    initialize=MILP_Formulation)
    model.Greenfield_Investment = Param(within=NonNegativeReals,
                                        initialize=Initialize_Greenfield_Investment)
    model.Renewable_Penetration = Param(within=NonNegativeReals,
                                        initialize=Initialize_Renewable_Penetration) 
    model.RE_Supply_Calculation = Param(within=NonNegativeReals) 
    model.Demand_Profile_Generation = Param(within=NonNegativeReals) 
    model.Grid_Connection = Param(within=NonNegativeReals) 
    model.Grid_Availability_Simulation = Param(within=NonNegativeReals) 
    model.Grid_Connection_Type = Param(within=NonNegativeReals) 
    model.Plot_Max_Cost        = Param(within=NonNegativeReals,
                                       initialize=Initialize_Plot_Max_Cost) 
                

    "Sets"
    model.periods = RangeSet(1, model.Periods)                                      # Creation of a set from 1 to the number of periods in each year
    model.years = RangeSet(1, model.Years)                                          # Creation of a set from 1 to the number of years of the project
    model.scenarios = RangeSet(1, model.Scenarios)                                  # Creation of a set from 1 to the number of scenarios to analized
    model.renewable_sources = RangeSet(1, model.RES_Sources)                        # Creation of a set from 1 to the number of RES technologies to analized
    model.generator_types = RangeSet(1, model.Generator_Types)                      # Creation of a set from 1 to the number of generators types to analized
    model.steps = RangeSet(1, model.Steps_Number)                                   # Creation of a set from 1 to the number of investment decision steps
    model.years_steps = Set(dimen = 2, 
                            initialize=Initialize_YearUpgrade_Tuples)    # 2D set of tuples: it associates each year to the corresponding investment decision step
    model.years_grid_connection = RangeSet(model.Year_Grid_Connection,
                                           model.Years)  # Creation of a set from year of grid connection to last year
    model.Scenario_Weight = Param(model.scenarios, 
                                  within=NonNegativeReals) 
    model.classes = RangeSet(1, model.Classes)      # Creation of a set from 1 to the number of classes of the thermal part

    "Parameters of RES" 
    model.RES_Names                    = Param(model.renewable_sources)               # RES names
    model.RES_Nominal_Capacity         = Param(model.renewable_sources,
                                               within=NonNegativeReals)               # Nominal capacity of the RES in W/unit
    model.RES_Inverter_Efficiency      = Param(model.renewable_sources)               # Efficiency of the inverter in %
    model.RES_Specific_Investment_Cost = Param(model.renewable_sources,
                                               within=NonNegativeReals)               # Cost of RES in USD/W
    model.RES_Specific_OM_Cost         = Param(model.renewable_sources,
                                               within=NonNegativeReals)               # Percentage of the total investment spend in operation and management of solar panels in each period in %                                             
    model.RES_Lifetime                 = Param(model.renewable_sources,
                                               within=NonNegativeReals)
    model.RES_units                    = Param(model.renewable_sources,
                                               within=NonNegativeReals)
    model.RES_years                    = Param(model.renewable_sources,
                                               within=NonNegativeReals)
    model.RES_unit_CO2_emission        = Param(model.renewable_sources,
                                               within=NonNegativeReals)                                    
    model.RES_Unit_Energy_Production   = Param(model.scenarios,
                                              model.renewable_sources,
                                              model.periods, 
                                              within=NonNegativeReals, 
                                              initialize=Initialize_RES_Energy)      # Energy production of a RES in Wh
    
    "Parameters of the solar collector"
    model.SC_Nominal_Capacity = Param(within=NonNegativeReals)     # Nominal capacity of the SC in kW/unit
    model.SC_Lifetime         = Param(within=NonNegativeReals)
    model.SC_Inv_Specific_Cost = Param(within=NonNegativeReals)    # Investment cost of SC unit in USD/kW
    model.SC_OM_Specific_Cost = Param(within=NonNegativeReals)     # % of the total investment spent in operation and management of SC unit in each period                                             
    model.SC_Unit_Energy_Production = Param(model.scenarios,
                                            model.classes, 
                                            model.periods,
                                            within=NonNegativeReals,
                                            initialize=Initialize_SC_Energy) # Energy production of a SC unit in W    

    
    "Parameters of the battery bank"
    model.Battery_Specific_Investment_Cost = Param(within=NonNegativeReals)                                     # Specific investment cost of the battery bank [USD/Wh]
    model.Battery_Specific_Electronic_Investment_Cost = Param(within=NonNegativeReals)   # Specific investment cost of non-replaceable parts (electronics) of the battery bank [USD/Wh]
    model.Battery_Specific_OM_Cost = Param(within=NonNegativeReals)                      # Percentage of the total investment spend in operation and management of batteries in each period in %
    model.Battery_Discharge_Battery_Efficiency = Param(within=NonNegativeReals)                                 # Efficiency of the discharge of the battery in %
    model.Battery_Charge_Battery_Efficiency    = Param(within=NonNegativeReals)                                 # Efficiency of the charge of the battery in  %
    model.Battery_Depth_of_Discharge       = Param()                                     # Depth of discharge of the battery (Depth_of_Discharge) in %
    model.Maximum_Battery_Discharge_Time   = Param(within=NonNegativeReals)              # Minimum time of charge of the battery in hours
    model.Maximum_Battery_Charge_Time      = Param(within=NonNegativeReals)              # Maximum time of discharge of the battery in hours                     
    model.Battery_Cycles                   = Param(within=NonNegativeReals)
    model.Unitary_Battery_Replacement_Cost = Param(within=NonNegativeReals, 
                                                   initialize=Initialize_Battery_Unit_Repl_Cost)
    model.Battery_Initial_SOC = Param(within=NonNegativeReals)
    model.Battery_capacity    = Param(within=NonNegativeReals)
    model.BESS_unit_CO2_emission = Param(within=NonNegativeReals)
    model.Battery_Independence  =   Param(within=NonNegativeReals,
                                          initialize=Initialize_Battery_Independence)
    model.Battery_Min_Capacity = Param(model.steps, 
                                       initialize=Initialize_Battery_Minimum_Capacity)
    model.BESS_Large_Constant = Param(within=NonNegativeReals,
                                      initialize = 10^6)
    "Parameters of the tank"
    model.Tank_Efficiency = Param()                  # Efficiency of the tank in %
    model.Tank_Depth_of_Discharge = Param()          # Depth of discharge of the tank in %
    model.Tank_Maximum_Discharge_Time = Param(within=NonNegativeReals)        # Maximum time of charge of the tank in hours
    model.Tank_Lifetime               = Param(within=NonNegativeReals)
    model.Tank_Specific_Investment_Cost = Param(within=NonNegativeReals)             # Investment cost of tank in USD/kWh
    model.Tank_Specific_OM_Cost = Param(within=NonNegativeReals)              # % of the total investment spend in operation and management of tank unit in each period

    "Parameters of the boilers"
    model.Boiler_Efficiency = Param()          # Boiler efficiency in %
    model.Lower_Heating_Value_NG = Param()     # Lower heating value of the natural gas in kWh/L
    model.NG_Unitary_Cost = Param(within=NonNegativeReals)          # Cost of natural gas in USD/L
    model.Boiler_Lifetime = Param(within=NonNegativeReals)
    model.Boiler_Specific_Investment_Cost = Param(within=NonNegativeReals) # Investment cost of the NG Boiler in USD/kW
    model.Boiler_Specific_OM_Cost = Param (within=NonNegativeReals) # % of the total investment spent in operation and management of boiler in each period

    "Parameters of the electric resistance"
    model.Electric_Resistance_Efficiency = Param()                               # Electric resistance efficiency in %
    model.Electric_Resistance_Lifetime   = Param(within=NonNegativeReals)
    model.Electric_Resistance_Specific_Investment_Cost = Param(within=NonNegativeReals) # Investment cost of the electric resistance in USD/kW
    model.Electric_Resistance_Specific_OM_Cost = Param(within=NonNegativeReals)  # % of the total investment spent in operation and management of electric resistance in each period
    
    "Parameters of the genset"
    model.Generator_Names             = Param(model.generator_types)                # Generators names
    model.Generator_Efficiency        = Param(model.generator_types,
                                              within=NonNegativeReals)              # Generator efficiency to trasform heat into electricity %
    model.Generator_Specific_Investment_Cost = Param(model.generator_types,
                                                     within=NonNegativeReals)       # Cost of the diesel generator
    model.Generator_Specific_OM_Cost  = Param(model.generator_types,
                                              within=NonNegativeReals)              # Cost of the diesel generator
    model.Generator_Lifetime          = Param(model.generator_types,
                                              within=NonNegativeReals)    
    model.Fuel_Names                  = Param(model.generator_types)                # Fuel names
    model.Fuel_LHV                    = Param(model.generator_types,
                                              within=NonNegativeReals)              # Low heating value of the fuel in kg/l
    model.Generator_capacity          = Param(model.generator_types, 
                                              within=NonNegativeReals)
    model.GEN_years                   = Param(model.generator_types,
                                               within=NonNegativeReals)
    model.GEN_unit_CO2_emission       = Param(model.generator_types,
                                              within=NonNegativeReals)
    model.FUEL_unit_CO2_emission      = Param(model.generator_types,
                                              within=NonNegativeReals)
    model.Fuel_Specific_Cost          = Param(model.generator_types, 
                                              within=NonNegativeReals)
    model.Generator_Marginal_Cost     = Param(model.scenarios, 
                                              model.years, 
                                              model.generator_types,
                                              initialize=Initialize_Generator_Marginal_Cost)   
    "Parameters of the National Grid"
    model.Grid_Sold_El_Price           = Param(within=NonNegativeReals)
    model.Grid_Purchased_El_Price      = Param(within=NonNegativeReals)
    model.Grid_Lifetime                = Param(within=NonNegativeReals)
    model.Grid_Distance                = Param(within=NonNegativeReals)
    model.Grid_Connection_Cost         = Param(within=NonNegativeReals)
    model.Grid_Maintenance_Cost        = Param(within=NonNegativeReals)
    model.Maximum_Grid_Power           = Param(within=NonNegativeReals)
    model.Grid_Availability            = Param(model.scenarios,
                                               model.years,
                                               model.periods,
                                               initialize = Initialize_Grid_Availability)
    model.Grid_Average_Number_Outages  = Param(within=NonNegativeReals) 
    model.Grid_Average_Outage_Duration = Param(within=NonNegativeReals)                
    model.National_Grid_Specific_CO2_emissions = Param(within=NonNegativeReals)  
    
 
    "Parameters of the electricity balance"                  
    model.Electric_Energy_Demand           = Param(model.scenarios, 
                                                    model.years, 
                                                    model.periods, 
                                                    initialize=Initialize_Electric_Demand)             # Energy Energy_Demand in W 
    model.Lost_Load_EE_Fraction      = Param(within=NonNegativeReals)                  # Lost load maxiumum admittable fraction in %
    model.Lost_Load_EE_Specific_Cost = Param(within=NonNegativeReals)                  # Value of lost load in USD/Wh 
    
    model.Thermal_Energy_Demand = Param(model.scenarios,
                                        model.years,
                                        model.classes,
                                        model.periods,
                                        initialize=Initialize_Thermal_Demand) # Thermal Energy Demand in kW 
    model.Lost_Load_Th_Fraction = Param(within=NonNegativeReals)      # Fraction of tolerated lost load in % of the total demand
    model.Lost_Load_Th_Specific_Cost = Param(within=NonNegativeReals)       # Value of lost load in USD/kWh
    
    model.Large_Constant = Param(within=NonNegativeReals,
                                      initialize = 10**6)
    
    "Parameters of the plot"
    model.RES_Colors        = Param(model.renewable_sources)                        # HEX color codes for RES
    model.Battery_Color     = Param()                                               # HEX color codes for Battery bank
    model.Generator_Colors  = Param(model.generator_types)                          # HEX color codes for Generators
    model.Lost_Load_Color   = Param()                                               # HEX color codes for Lost load
    model.Curtailment_Color = Param()                                               # HEX color codes for Curtailment
    model.Energy_To_Grid_Color = Param()                                            # HEX color codes for Energy to grid
    model.Energy_From_Grid_Color = Param()                                          # HEX color codes for Energy from grid
    
#%% VARIABLES

    "Variables associated to the RES"
    model.RES_Units             = Var(model.steps, 
                                      model.renewable_sources,
                                      within=NonNegativeReals)                      # Number of units of RES
    model.RES_Energy_Production = Var(model.scenarios, 
                                      model.years,
                                      model.renewable_sources,
                                      model.periods,
                                      within=NonNegativeReals)                      # Energy generated by the RES sistem in Wh
    model.RES_emission          = Var(within=NonNegativeReals)
    
    "Variables associated to the solar collectors"
    model.SC_Units = Var(model.steps,
                         model.classes,
                         within=NonNegativeReals)                                            # Number of units of SC
    model.SC_Energy_Production = Var(model.scenarios, 
                                     model.years,
                                     model.classes, 
                                     model.periods,
                                     within=NonNegativeReals)                   # Total energy generated for the SC system in kWh

    "Variables associated to the battery bank"
    model.Battery_Nominal_Capacity        = Var(model.steps, 
                                                within=NonNegativeReals)            # Capacity of the battery bank in Wh
    model.Battery_Outflow                 = Var(model.scenarios, 
                                                model.years, 
                                                model.periods,
                                                within=NonNegativeReals)            # Battery discharge energy in Wh
    model.Battery_Inflow                  = Var(model.scenarios,
                                                model.years, 
                                                model.periods, 
                                                within=NonNegativeReals)            # Battery charge energy in Wh
    
    model.Battery_SOC                     = Var(model.scenarios, 
                                                model.years, 
                                                model.periods, 
                                                within=NonNegativeReals)            # State of Charge of the Battery in Wh
    model.Battery_Maximum_Charge_Power    = Var(model.steps, 
                                                within=NonNegativeReals)
    model.Battery_Maximum_Discharge_Power = Var(model.steps,
                                                within=NonNegativeReals)
    model.Battery_Replacement_Cost_Act    = Var(model.scenarios,
                                                within=NonNegativeReals)
    model.Battery_Replacement_Cost_NonAct = Var(model.scenarios,
                                                within=NonNegativeReals)
    model.BESS_emission                   = Var(within=NonNegativeReals)
    
    model.Single_Flow_BESS                     = Var(model.scenarios, 
                                                model.years, 
                                                model.periods,
                                                within = Binary)
    
    "Variables associated to the tank"
    model.Tank_Nominal_Capacity = Var(model.steps,
                                      model.classes, 
                                      within=NonNegativeReals)                                # Capacity of the tank in kWh
    model.Tank_Outflow = Var(model.scenarios,
                             model.years,
                             model.classes, 
                             model.periods, 
                             within=NonNegativeReals)          # Tank outflow in kWh
    model.Tank_Inflow = Var(model.scenarios,
                            model.years,
                            model.classes, 
                            model.periods, 
                            within=NonNegativeReals)           # Tank inflow energy in kWh
    model.Tank_State_of_Charge = Var(model.scenarios, 
                                     model.years,
                                     model.classes, 
                                     model.periods, 
                                     within=NonNegativeReals)  # State of Charge of the tank in kWh
    model.Maximum_Tank_Discharge_Power = Var(model.classes, 
                                             within=NonNegativeReals)                         # Maximum discharge power in kW        

    "Variables associated to the diesel generator"
    model.Generator_Nominal_Capacity  = Var(model.steps, 
                                            model.generator_types,
                                            within=NonNegativeReals)                # Capacity  of the diesel generator in Wh
    model.Generator_Energy_Production = Var(model.scenarios, 
                                            model.years,
                                            model.generator_types,
                                            model.periods, 
                                            within=NonNegativeReals)                # Energy generated by the Diesel generator
    model.Total_Fuel_Cost_Act         = Var(model.scenarios,
                                            model.generator_types,
                                            within=NonNegativeReals)
    model.Total_Fuel_Cost_NonAct      = Var(model.scenarios, 
                                            model.generator_types,
                                            within=NonNegativeReals)
    model.GEN_emission                = Var(within=NonNegativeReals)
    model.FUEL_emission               = Var(model.scenarios, 
                                            model.years,
                                            model.generator_types,
                                            model.periods, 
                                            within=NonNegativeReals)
    model.Scenario_FUEL_emission      = Var(model.scenarios,
                                            within=NonNegativeReals)
    
    "Variable associated to the National Grid"  
    model.Total_Revenues_Act             = Var(model.scenarios,
                                               within=NonNegativeReals)
    model.Total_Revenues_NonAct          = Var(model.scenarios,
                                               within=NonNegativeReals)
    model.Total_Electricity_Cost_Act        = Var(model.scenarios,
                                              within=NonNegativeReals)
    model.Total_Electricity_Cost_NonAct     = Var(model.scenarios,
                                              within=NonNegativeReals)
    model.Energy_To_Grid                 = Var(model.scenarios, 
                                               model.years,
                                               model.periods, 
                                               within=NonNegativeReals)
    model.Energy_From_Grid               = Var(model.scenarios, 
                                               model.years,
                                               model.periods, 
                                               within=NonNegativeReals)
    model.GRID_emission                  = Var(model.scenarios, 
                                                model.years,
                                                model.periods, 
                                                within=NonNegativeReals)    
    model.Scenario_GRID_emission      = Var(model.scenarios,
                                            within=NonNegativeReals)
    
    model.Single_Flow_Grid            = Var(model.scenarios,
                                               model.years,
                                               model.periods, 
                                               within=Binary)  
    "Variables associated to the boilers"
    model.Boiler_Nominal_Capacity = Var(model.steps,
                                        model.classes, 
                                        within=NonNegativeReals)                      # Capacity of the boiler in kWh
    model.NG_Consumption = Var(model.scenarios,
                               model.years,
                               model.classes, 
                               model.periods,
                               within=NonNegativeReals) # Natural Gas consumed to produce thermal energy in Kg (considering Liquified Natural Gas)
    model.Boiler_Energy_Production = Var(model.scenarios, 
                                         model.years,
                                         model.classes, 
                                         model.periods,
                                         within=NonNegativeReals) # Energy generated by the boiler 
    model.Total_NG_Cost_Act = Var(model.scenarios,
                              model.classes, 
                              within=NonNegativeReals) 
    model.Total_NG_Cost_NonAct = Var(model.scenarios,
                                     model.classes, 
                                     within=NonNegativeReals) 

    "Variables associated to the electric resistance"
    model.Electric_Resistance_Nominal_Power = Var(model.steps,
                                                  model.classes,
                                                  model.steps, 
                                                  within=NonNegativeReals)    # Nominal power of the electric resistance in W
    model.Electric_Resistance_Energy_Consumption = Var(model.scenarios,
                                                       model.years,
                                                       model.classes, 
                                                       model.periods, 
                                                       within=NonNegativeReals) # Energy consumed by the electric resistance in each class in Wh 
    model.Electric_Resistance_Energy_Production = Var(model.scenarios,
                                                      model.years,
                                                      model.classes,
                                                      model.periods, 
                                                      within=NonNegativeReals)  # Energy generated by the electric resistance in each class in Wh 
    model.Tot_Electric_Resistance_Energy_Production = Var(model.scenarios,
                                                          model.years,
                                                          model.periods, 
                                                          within=NonNegativeReals)            # Total energy generated by the electric resistance in Wh 

    "Variables associated to the energy balance"
    
    model.MES_Formulation  =   Param(within=NonNegativeReals,
                                          initialize=Initialize_MES_Formulation)        
    model.Lost_Load_EE             = Var(model.scenarios, 
                                      model.years, 
                                      model.periods, 
                                      within=NonNegativeReals)                      # Energy not supplied by the system kWh
    model.Lost_Load_Th             = Var(model.scenarios,
                                         model.years,
                                         model.classes,
                                         model.periods, 
                                         within=NonNegativeReals) # Energy not suply by the system kWh
    model.Electric_Energy_Curtailment  = Var(model.scenarios,
                                      model.years,
                                      model.periods, 
                                      within=NonNegativeReals)                      # Curtailment of RES in kWh
    model.Thermal_Energy_Curtailment = Var(model.scenarios,
                                           model.years,
                                           model.classes,
                                           model.periods,
                                           within=NonNegativeReals)
    model.Scenario_Lost_Load_Cost_Act_EE    = Var(model.scenarios, 
                                                  within=NonNegativeReals) 
    model.Scenario_Lost_Load_Cost_NonAct_EE = Var(model.scenarios,
                                                  within=NonNegativeReals)    
    model.Scenario_Lost_Load_Cost_Act_Th = Var(model.scenarios,
                                               model.classes,
                                               within=NonNegativeReals)
    model.Scenario_Lost_Load_Cost_NonAct_Th = Var(model.scenarios,
                                                  model.classes,
                                                  within=NonNegativeReals) 

    
    

    "Variables associated to the project"
    model.Net_Present_Cost                    = Var(within=Reals)
    model.Scenario_Net_Present_Cost           = Var(model.scenarios, 
                                                    within=Reals) 
    model.Total_Variable_Cost                 = Var(within=Reals)
    model.CO2_emission                        = Var(within=NonNegativeReals)
    model.Scenario_CO2_emission               = Var(model.scenarios, 
                                                    within=NonNegativeReals)
    model.Investment_Cost                     = Var(within=NonNegativeReals)
    model.Salvage_Value                       = Var(within=Reals)   
    model.Total_Variable_Cost_Act             = Var(within=Reals) 
    model.Operation_Maintenance_Cost_Act      = Var(within=Reals)
    model.Operation_Maintenance_Cost_NonAct   = Var(within=Reals)
    model.Total_Scenario_Variable_Cost_Act    = Var(model.scenarios, 
                                                    within=Reals) 
    model.Total_Scenario_Variable_Cost_NonAct = Var(model.scenarios, 
                                                    within=Reals) 


