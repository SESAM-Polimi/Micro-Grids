"""
MicroGridsPy - Multi-year capacity-expansion (MYCE)

Linear Programming framework for microgrids least-cost sizing,
able to account for time-variable load demand evolution and capacity expansion.

"""


from pyomo.environ import *
from pyomo.opt import SolverFactory
from matplotlib import pyplot as plt
import re
import sys


def Model_Resolution(model, datapath="Inputs/Model_data.dat",options_string="mipgap=0.05",
                     warmstart=False, keepfiles=False, load_solutions=False, logfile="Solver_Output.log"):  

    Data_file = "Inputs/Model_data.dat"
    Data_import = open(Data_file).readlines()

    for i in range(len(Data_import)):
        if "param: Renewable_Penetration" in Data_import[i]:      
            Renewable_Penetration = int((re.findall('\d+',Data_import[i])[0]))
        if "param: Battery_Independence" in Data_import[i]:      
            Battery_Independence = int((re.findall('\d+',Data_import[i])[0]))
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
        if "param: Generator_Partial_Load" in Data_import[i]:      
            Generator_Partial_Load = int((re.findall('\d+',Data_import[i])[0]))
    
    if (Generator_Partial_Load == 1 and MILP_Formulation == 0):
        print('###########################################################')
        print('INPUT NOT VALID: if MILP_Formulation NOT activated (= 0), Generator_Partial_Load must be NOT activated (= 0) too!')
        print('Please, edit file "Model_data.dat" and try again')
        print('ABORT')
        print('###########################################################')
        sys.exit()
        

    if Greenfield_Investment == 1 and MILP_Formulation == 1 :
        from Constraints import Constraints_Greenfield_Milp as C
    if Greenfield_Investment == 0 and MILP_Formulation == 1 :
        from Constraints import Constraints_Brownfield_Milp as C
    if Greenfield_Investment == 1 and MILP_Formulation == 0 :
        from Constraints import Constraints_Greenfield as C
    if Greenfield_Investment == 0 and MILP_Formulation == 0 : 
        from Constraints import Constraints_Brownfield as C   
 
    
#%% Economic constraints
    model.NetPresentCost = Constraint(rule=C.Net_Present_Cost)
    model.CO2emission = Constraint(rule=C.CO2_emission)
        
    model.ScenarioCO2emission    = Constraint(model.scenarios, 
                                              rule=C.Scenario_CO2_emission)
    model.ScenarioNetPresentCost = Constraint(model.scenarios, 
                                              rule=C.Scenario_Net_Present_Cost)
    model.VariableCostNonAct = Constraint(rule=C.Total_Variable_Cost)
    
    "Investment cost"
    model.InvestmentCost = Constraint(rule=C.Investment_Cost)
    if Optimization_Goal == 2:
        model.InvestmentCostLimit = Constraint(rule=C.Investment_Cost_Limit)

    "Fixed costs"    
    model.OperationMaintenanceCostAct = Constraint(rule=C.Operation_Maintenance_Cost_Act)
    model.OperationMaintenanceCostNonAct = Constraint(rule=C.Operation_Maintenance_Cost_NonAct)

    "Variable costs"
    model.TotalVariableCostAct         = Constraint(rule=C.Total_Variable_Cost_Act)
    model.FuelCostTotalAct             = Constraint(model.scenarios, 
                                            model.generator_types,
                                            rule=C.Total_Fuel_Cost_Act)
    model.TotalElectricityCostAct      = Constraint(model.scenarios,
                                                    rule=C.Total_Electricity_Cost_Act)   
    model.TotalRevenuesAct             = Constraint(model.scenarios,
                                                    rule=C.Total_Revenues_Act)
    model.TotalRevenuesNonAct          = Constraint(model.scenarios,
                                                    rule=C.Total_Revenues_NonAct)    
    model.BatteryReplacementCostAct    = Constraint(model.scenarios,
                                                 rule=C.Battery_Replacement_Cost_Act) 
    model.ScenarioLostLoadCostAct      = Constraint(model.scenarios, 
                                                 rule=C.Scenario_Lost_Load_Cost_Act)
    model.ScenarioVariableCostAct      = Constraint(model.scenarios,
                                                 rule=C.Scenario_Variable_Cost_Act)   

    model.FuelCostTotalNonAct          = Constraint(model.scenarios, 
                                                    model.generator_types,
                                                    rule=C.Total_Fuel_Cost_NonAct)
    model.TotalElectricityCostNonAct   = Constraint(model.scenarios,
                                                    rule=C.Total_Electricity_Cost_NonAct)     
    model.BatteryReplacementCostNonAct = Constraint(model.scenarios,
                                                    rule=C.Battery_Replacement_Cost_NonAct) 
    model.ScenarioLostLoadCostNonAct   = Constraint(model.scenarios, 
                                                    rule=C.Scenario_Lost_Load_Cost_NonAct)
    model.ScenarioVariableCostNonAct   = Constraint(model.scenarios,
                                                    rule=C.Scenario_Variable_Cost_NonAct)     

    "Salvage value"
    model.SalvageValue = Constraint(rule=C.Salvage_Value)
    
#%% Brownfield additional constraints
    
    if Greenfield_Investment == 0:
        model.REScapacity     = Constraint(model.scenarios, model.years_steps, 
                                           model.renewable_sources,
                                           model.periods,
                                           rule=C.RES_Capacity)
        model.BESScapacity    = Constraint(model.steps,
                                           rule=C.BESS_Capacity)
        model.GENcapacity     = Constraint(model.steps,                                                
                                           model.generator_types,
                                           rule=C.GEN_Capacity)


#%% Electricity generation system constraints 
    model.EnergyBalance = Constraint(model.scenarios, 
                                     model.years_steps, 
                                     model.periods, 
                                     rule=C.Energy_balance)

    "Renewable Energy Sources constraints"
    model.RenewableEnergy = Constraint(model.scenarios,
                                       model.years_steps, 
                                       model.renewable_sources,
                                       model.periods, 
                                       rule=C.Renewable_Energy)  # Energy output of the solar panels
    model.ResMinStepUnits = Constraint(model.years_steps,
                                       model.renewable_sources, 
                                       rule=C.Renewables_Min_Step_Units)
    if Renewable_Penetration > 0:
        model.RenewableEnergyPenetration = Constraint(model.steps, 
                                                      rule=C.Renewable_Energy_Penetration)

    "Battery Energy Storage constraints"
    model.StateOfCharge            = Constraint(model.scenarios, 
                                                model.years_steps,
                                                model.periods, 
                                                rule=C.State_of_Charge) # State of Charge of the battery
    model.MaximunCharge            = Constraint(model.scenarios,
                                                model.years_steps, 
                                                model.periods, 
                                                rule=C.Maximun_Charge) # Maximun state of charge of the Battery
    model.MinimunCharge            = Constraint(model.scenarios, 
                                                model.years_steps,
                                                model.periods,
                                                rule=C.Minimun_Charge) # Minimun state of charge
    model.MaxPowerBatteryCharge    = Constraint(model.steps, 
                                                rule=C.Max_Power_Battery_Charge)  # Max power battery charge constraint
    model.MaxPowerBatteryDischarge = Constraint(model.steps,
                                                rule=C.Max_Power_Battery_Discharge)    # Max power battery discharge constraint
    model.MaxBatIn                 = Constraint(model.scenarios,
                                                model.years_steps,
                                                model.periods, 
                                                rule=C.Max_Bat_in) # Minimun flow of energy for the charge fase
    model.Maxbatout                = Constraint(model.scenarios, 
                                                model.years_steps, 
                                                model.periods,
                                                rule=C.Max_Bat_out) #minimun flow of energy for the discharge fase
    model.BatteryMinStepCapacity   = Constraint(model.years_steps,                                             
                                                rule=C.Battery_Min_Step_Capacity)
    if MILP_Formulation:
        model.BatterySingleFlowDischarge = Constraint(model.scenarios,
                                                    model.years_steps,
                                                    model.periods, 
                                                    rule=C. Battery_Single_Flow_Discharge)
        model.BatterySingleFlowCharge = Constraint(model.scenarios,
                                                    model.years_steps,
                                                    model.periods, 
                                                    rule=C. Battery_Single_Flow_Charge)
        model.SingleFlowEnergyToGrid      = Constraint(model.scenarios,
                                                 model.years_steps,
                                                 model.periods,
                                                 rule=C.Single_Flow_Energy_To_Grid)
        model.SingleFlowEnergyFromGrid  = Constraint(model.scenarios,
                                                 model.years_steps,
                                                 model.periods,
                                                rule=C.Single_Flow_Energy_From_Grid)
        
    if Battery_Independence > 0:
        model.BatteryMinCapacity   = Constraint(model.steps, 
                                                rule=C.Battery_Min_Capacity)

    "Diesel generator constraints"
    if MILP_Formulation == 1 and Generator_Partial_Load == 1:
       model.MinimumGeneratorEnergyPartial     = Constraint(model.scenarios, 
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Minimum_Generator_Energy_Partial)
       model.MaximumGeneratorEnergyPartial     = Constraint(model.scenarios, 
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Maximum_Generator_Energy_Partial)
       model.MaximumGeneratorEnergyTotal       = Constraint(model.scenarios,
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Maximum_Generator_Energy_Total)
       model.GeneratorEnergyTotal              = Constraint(model.scenarios,
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Generator_Energy_Total)
       model.GeneratorUnitsTotal               = Constraint(model.scenarios,
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Generator_Units_Total)
       model.GeneratorMinStepCapacity          = Constraint(model.years_steps,
                                                            model.generator_types, 
                                                            rule=C.Generator_Min_Step_Capacity)
    elif MILP_Formulation == 1 and Generator_Partial_Load == 0:
       model.MaximumGeneratorEnergyTotal       = Constraint(model.scenarios, 
                                                            model.years_steps, 
                                                            model.generator_types,
                                                            model.periods, 
                                                            rule=C.Maximun_Generator_Energy_Total)
       model.GeneratorMinStepCapacity = Constraint(model.years_steps, 
                                                   model.generator_types, 
                                                   rule=C.Generator_Min_Step_Capacity)
    else:
       model.MaximunFuelEnergy        = Constraint(model.scenarios, 
                                                   model.years_steps, 
                                                   model.generator_types,
                                                   model.periods, 
                                                   rule=C.Maximun_Generator_Energy)
       model.GeneratorMinStepCapacity = Constraint(model.years_steps, 
                                                   model.generator_types, 
                                                   rule=C.Generator_Min_Step_Capacity)         
    "Grid constraints"  
    
    model.MaximumPowerFromGrid     = Constraint(model.scenarios,
                                                model.years_steps,
                                                model.periods,
                                                rule=C.Maximum_Power_From_Grid)
    model.MaximumPowerToGrid       = Constraint(model.scenarios,
                                                model.years_steps,
                                                model.periods,
                                                rule=C.Maximum_Power_To_Grid) 

    
    "Lost load constraints"
    model.MaximunLostLoad = Constraint(model.scenarios, model.years, 
                                    rule=C.Maximun_Lost_Load) # Maximum permissible lost load

    "Emission constrains"
    model.RESemission    = Constraint(rule=C.RES_emission)
    model.GENemission    = Constraint(rule=C.GEN_emission)
    model.FUELemission   = Constraint(model.scenarios, 
                                      model.years_steps, 
                                      model.generator_types,
                                      model.periods,
                                      rule=C.FUEL_emission)
    model.BESSemission   = Constraint(rule=C.BESS_emission)
    model.ScenarioFUELemission = Constraint(model.scenarios,
                                            rule=C.Scenario_FUEL_emission) 
    model.GRIDemission = Constraint(model.scenarios, 
                                    model.years_steps,
                                    model.periods,
                                    rule=C.GRID_emission)
    model.ScenarioGRIDemission = Constraint(model.scenarios,
                                            rule=C.Scenario_GRID_emission) 
    
     
    if Multiobjective_Optimization == 0:
        if Optimization_Goal == 1:
            model.ObjectiveFuntion = Objective(rule=C.Net_Present_Cost_Obj, 
                                               sense = minimize)
        elif Optimization_Goal == 2:
            model.ObjectiveFuntion = Objective(rule=C.Total_Variable_Cost_Obj, 
                                               sense = minimize)
        instance = model.create_instance(datapath) # load parameters
    
        print('\nInstance created')
    
        opt = SolverFactory('gurobi') # Solver use during the optimization
        timelimit = 100000

        if MILP_Formulation:
            opt.set_options('Method=3 BarHomogeneous=1 Crossover=1 MIPfocus=1 BarConvTol=1e-3 OptimalityTol=1e-3 FeasibilityTol=1e-4 TimeLimit=10000')
        else:
            opt.set_options('Method=2 BarHomogeneous=0 Crossover=0 BarConvTol=1e-4 OptimalityTol=1e-4 FeasibilityTol=1e-4 IterationLimit=1000')

        print('Calling solver...')
        results = opt.solve(instance, tee=True, options_string=options_string,
                            warmstart=warmstart,keepfiles=keepfiles,
                            load_solutions=load_solutions, logfile=logfile) # Solving a model instance 
        print('Instance solved')

        instance.solutions.load_from(results)  # Loading solution into instance
        return instance
        
    else:
        if Optimization_Goal == 1:
            model.f1 = Var()
            model.C_f1 = Constraint(expr = model.f1 == model.Net_Present_Cost)
            model.ObjectiveFuntion = Objective(expr = model.f1, 
                                                  sense=minimize)
            model.f2 = Var()
            model.C_f2 = Constraint(expr = model.f2 == model.CO2_emission)
            model.ObjectiveFuntion1 = Objective(expr = model.f2, 
                                                   sense=minimize)
        
            n = int(input("please indicate how many points (n) you want to analyse: "))
            
            #NPC min and CO2 emission max calculation
            model.ObjectiveFuntion1.deactivate()
            instance = model.create_instance(datapath)
            opt = SolverFactory('gurobi')
            if MILP_Formulation:
                opt.set_options('Method=3 BarHomogeneous=1 Crossover=0 BarConvTol=1e-4 OptimalityTol=1e-4 FeasibilityTol=1e-4 IterationLimit=1000')
            else:
                opt.set_options('Method=2 BarHomogeneous=0 Crossover=0 BarConvTol=1e-4 OptimalityTol=1e-4 FeasibilityTol=1e-4 IterationLimit=1000')
            print('Calling solver...')
            opt.solve(instance, tee=True)
            print('Instance solved') 
            NPC_min = value(instance.ObjectiveFuntion)
            CO2emission_max = value(instance.ObjectiveFuntion1)
            print('NPC_min [kUSD] =' +str(NPC_min/1e3),'CO2emission_max [ton] =' +str(CO2emission_max/1e3))
           
        
            #NPC max and CO2 emission min calculation
            model.ObjectiveFuntion.deactivate()
            model.ObjectiveFuntion1.activate()
            instance = model.create_instance(datapath)
            print('Calling solver...')
            opt.solve(instance, tee=True)
            print('Instance solved') 
            NPC_max = value(instance.ObjectiveFuntion)
            CO2emission_min = value(instance.ObjectiveFuntion1)
            print('NPC_max [kUSD] =' +str(NPC_max/1e3),'CO2emission_min [ton] =' +str(CO2emission_min/1e3))

            #normal eps method
            model.ObjectiveFuntion.activate()
            model.ObjectiveFuntion1.deactivate()        

            instance = model.create_instance(datapath)
            instance.e = Param(initialize=0, mutable=True)
            instance.C_e = Constraint(expr = instance.f2 == instance.e)
            
            if Plot_maxCost:
                step = int((CO2emission_max - CO2emission_min)/(n-1))
                steps = list(range(int(CO2emission_min),int(CO2emission_max),step)) 
            else:
                step = int((CO2emission_max - CO2emission_min)/n)
                steps = list(range(int(CO2emission_min),int(CO2emission_max),step)) 
                steps.pop(0)          
                
            f1_l,f2_l = [],[]
            for i in steps:  
                instance.e = i
                #print(value(instance.e))
                print('Calling solver...')
                results = opt.solve(instance, tee=True) # Solving a model instance
                print('Instance solved')  # Loading solution into instance
                f1_l.append(value(instance.f1)/1e3)
                f2_l.append(value(instance.f2)/1e3)
                instance.solutions.load_from(results)
                print('NPC [kUSD] = ' +str(value(instance.f1)/1e3),'CO2 emission [ton] = ' +str(value(instance.f2)/1e3))

            if len(f1_l)<n:
                 f1_l.append(NPC_min/1e3)
                 f2_l.append(CO2emission_max/1e3)        
            
            print ('\nNPC [kUSD] =' +str(f1_l))
            print ('\nCO2 emission [ton] =' +str(f2_l))
            CO2=(CO2emission_max-CO2emission_min)/1e3
            NPC=f1_l[0]*1000-NPC_min  
            print('Cost CO2 avoided [USD/ton] =' +str(round(NPC/CO2,3)))       
            plt.plot(f1_l, f2_l, 'o-', c='r', label='Pareto optimal front')
            plt.legend(loc='best')
            plt.xlabel('NPC(kUSD)')
            plt.ylabel('CO2 emission(ton)')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            
            steps = list(range(int(CO2emission_min),int(CO2emission_max),step)) 
                        
            if len(steps)<=n:
                steps.append(CO2emission_max)
            
            if Plot_maxCost:
                steps.insert(0,0)                
                
            i = int(input("please indicate which solution you prefer (starting from 1 to n in CO2 emission): ")) #asks the user how many profiles (i.e. code runs) he wants

            instance.e = steps[i] 
            print('Calling solver...')
            results = opt.solve(instance, tee=True) # Solving a model instance
            print('Instance solved')  # Loading solution into instance
            instance.solutions.load_from(results)
            print('NPC [kUSD] = ' +str(value(instance.f1)/1e3),'CO2 emission [ton] = ' +str(value(instance.f2)/1e3))
            return instance
        
        elif Optimization_Goal == 2:
            model.f1 = Var()
            model.C_f1 = Constraint(expr = model.f1 == model.Total_Variable_Cost)
            model.ObjectiveFuntion = Objective(expr = model.f1, 
                                                  sense=minimize)
            model.f2 = Var()
            model.C_f2 = Constraint(expr = model.f2 == model.CO2_emission)
            model.ObjectiveFuntion1 = Objective(expr = model.f2, 
                                                   sense=minimize)
        
            n = int(input("please indicate how many points (n) you want to analyse: "))
                        
            #NPC min and CO2 emission max calculation
            model.ObjectiveFuntion1.deactivate()
            instance = model.create_instance(datapath)
            opt = SolverFactory('gurobi')
            opt.set_options('Method=1 Crossover=0 BarConvTol=1e-4 OptimalityTol=1e-4 FeasibilityTol=1e-4 IterationLimit=1000') # !! only works with GUROBI solver
            print('Calling solver...')
            opt.solve(instance, tee=True)
            print('Instance solved') 
            OperationCost_min = value(instance.ObjectiveFuntion)
            CO2emission_max = value(instance.ObjectiveFuntion1)
            print('OperationCost_min [kUSD] =' +str(OperationCost_min/1e3),'CO2emission_max [ton] =' +str(CO2emission_max/1e3))
           
        
            #NPC max and CO2 emission min calculation
            model.ObjectiveFuntion.deactivate()
            model.ObjectiveFuntion1.activate()
            instance = model.create_instance(datapath)
            print('Calling solver...')
            opt.solve(instance, tee=True)
            print('Instance solved') 
            OperationCost_max = value(instance.ObjectiveFuntion)
            CO2emission_min = value(instance.ObjectiveFuntion1)
            print('OperationCost_max [kUSD] =' +str(OperationCost_max/1e3),'CO2emission_min [ton] =' +str(CO2emission_min/1e3))
            r=CO2emission_max-CO2emission_min
            
            #normal eps method
            model.ObjectiveFuntion.activate()
            model.ObjectiveFuntion1.deactivate()

            instance = model.create_instance(datapath)
            instance.e = Param(initialize=0, mutable=True)
            instance.C_e = Constraint(expr = instance.f2 == instance.e)

            if Plot_maxCost:
                step = int((CO2emission_max - CO2emission_min)/(n-1))
                steps = list(range(int(CO2emission_min),int(CO2emission_max),step)) 
            else:
                step = int((CO2emission_max - CO2emission_min)/n)
                steps = list(range(int(CO2emission_min),int(CO2emission_max),step)) 
                steps.pop(0)     

            f1_l,f2_l = [],[]
            for i in steps:  
               instance.e = i
               #print(value(instance.e))
               print('Calling solver...')
               results = opt.solve(instance, tee=True) # Solving a model instance
               print('Instance solved')  # Loading solution into instance
               f1_l.append(value(instance.f1)/1e3)
               f2_l.append(value(instance.f2)/1e3)
               instance.solutions.load_from(results)
               print('Operation Cost [kUSD] = ' +str(value(instance.f1)/1e3),'CO2 emission [ton] = ' +str(value(instance.f2)/1e3))

            if len(f1_l)<n:
                f1_l.append(OperationCost_min/1e3)
                f2_l.append(CO2emission_max/1e3)        

            print ('\nOperation Cost [kUSD] =' +str(f1_l))
            print ('\nCO2 emission [ton] =' +str(f2_l))
            plt.plot(f1_l, f2_l, 'o-', c='r', label='Pareto optimal front')
            plt.legend(loc='best')
            plt.xlabel('Operation Cost(kUSD)')
            plt.ylabel('CO2 emission(ton)')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            
            steps = list(range(int(CO2emission_min),int(CO2emission_max),step))
            
            if len(steps)<=n:
                steps.append(CO2emission_max)

            if Plot_maxCost:
                steps.insert(0,0) 

            i = int(input("please indicate which solution you prefer (starting from 1 to n in CO2 emission): ")) #asks the user how many profiles (i.e. code runs) he wants
                           
            instance.e = steps[i] 
            #print(value(instance.e))
            print('Calling solver...')
            results = opt.solve(instance, tee=True) # Solving a model instance
            print('Instance solved')  # Loading solution into instance
            instance.solutions.load_from(results)
            print('Operation Cost [kUSD] = ' +str(value(instance.f1)/1e3),'CO2 emission [ton] = ' +str(value(instance.f2)/1e3))
            return instance
        


           
          
        
    
                
                    
        
                
           