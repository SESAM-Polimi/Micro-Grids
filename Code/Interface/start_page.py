import tkinter as tk
from tkinter import font as tkFont

class ToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self):
        "Display text in tooltip window"
        self.x, self.y, cx, cy = self.widget.bbox("insert")
        self.x += self.widget.winfo_rootx() + 25
        self.y += self.widget.winfo_rooty() + 20

        # Creates a toplevel window
        self.tipwindow = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))

        label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                      background="#ffffff", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None
        
def create_tooltip(widget, text):
        tool_tip = ToolTip(widget, text)
        widget.bind('<Enter>', lambda event: tool_tip.show_tip())
        widget.bind('<Leave>', lambda event: tool_tip.hide_tip())

class StartPage(tk.Frame):
    def check_lost_load_fraction(self,*args):
        # Get the value of Lost Load Fraction
        fraction = self.Lost_Load_Fraction_var.get()
        # If the fraction is greater than 0, enable the Cost Entry and Label, else disable them
        if fraction > 0.0:
            self.Lost_Load_Specific_Cost_entry.config(state='normal')
            self.Lost_Load_Specific_Cost_label.config(state='normal')
        else:
            self.Lost_Load_Specific_Cost_entry.config(state='disabled')
            self.Lost_Load_Specific_Cost_label.config(state='disabled')
    
    # Function to toggle the state of Generator Partial Load
    def toggle_generator_partial_load(self,*args):
        if self.MILP_Formulation_var.get() == 1:
            self.Generator_Partial_Load_checkbutton.config(state='normal')
        else:
            self.Generator_Partial_Load_var.set(0)  # Reset to 0 if MILP is not selected
            self.Generator_Partial_Load_checkbutton.config(state='disabled')
            

    # Function to toggle the state of Plot Max Cost
    def toggle_Plot_Max_Cost(self,*args):
            if self.Multiobjective_Optimization_var.get() == 1:
                self.Plot_Max_Cost_radio1.config(state='normal')
                self.Plot_Max_Cost_radio0.config(state='normal')
            else:
                self.Plot_Max_Cost_var.set(0)  # Reset to No if Multi-Objective Optimization is not selected
                self.Plot_Max_Cost_radio1.config(state='disabled')
                self.Plot_Max_Cost_radio0.config(state='disabled')
        
    # Function to toggle the grid options based on the grid connection
    def toggle_grid_options(self,*args):
            if self.Grid_Connection_var.get() == 1: 
                self.Grid_Availability_Simulation_checkbutton.config(state='normal')
                self.Grid_Availability_Simulation_label.config(state='normal')
                self.Grid_Connection_Type_label.config(state='normal')
                self.Grid_Connection_Type_radio1.config(state='normal')
                self.Grid_Connection_Type_radio2.config(state='normal')
            else: 
                self.Grid_Availability_Simulation_var.set(0)
                self.Grid_Connection_Type_var.set(1)
                self.Grid_Availability_Simulation_checkbutton.config(state='disabled')
                self.Grid_Availability_Simulation_label.config(state='disabled')
                self.Grid_Connection_Type_label.config(state='disabled')
                self.Grid_Connection_Type_radio1.config(state='disabled')
                self.Grid_Connection_Type_radio2.config(state='disabled')
        
    # Function to toggle the state of WACC parameters
    def toggle_wacc_parameters(self):
        state = 'normal' if self.WACC_Calculation_var.get() == 1 else 'disabled'
        for label, entry in self.wacc_parameters_entries:
            label.config(state=state)
            entry.config(state=state)
            if state == 'disabled':
                entry.var.set('')
                
    def on_next_button(self):
        # First, update the GeneratorPage parameters
        milp_formulation = self.MILP_Formulation_var.get()
        partial_load = self.Generator_Partial_Load_var.get()
        generator_page = self.controller.frames.get("GeneratorPage")
        battery_page = self.controller.frames.get("BatteryPage")
        generator_page.update_gen_parameters_defaults(milp_formulation, partial_load)
        if milp_formulation == 1 : battery_page.display_extra_parameter()
        # Then, navigate to the RECalculationPage
        self.controller.show_frame("RECalculationPage")
            
                
    def validate_integer(self, P):
        if P == "": return True
        if P.isdigit():
            return True
        else:
            self.bell()  # System bell if invalid input
            return False
        
    def validate_float(self, P):
        if P == "": return True
        try: 
            value = float(P)
            if value >= 0 : return True
            else: return False
        except ValueError:
            self.bell()  # System bell if invalid input
            return False
        
    def validate_fraction(self, P):
        if P == "": return True
        try: 
            value = float(P)
            if value <= 1 : return True
            else: 
                self.bell()
                return False
        except ValueError:
            self.bell()  # System bell if invalid input
            return False

        
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)

        # Section title: MicroGridsPy - Data Input
        self.title_label = tk.Label(self, text="MicroGridsPy - Data Input", font=self.title_font, fg="black")
        self.title_label.grid(row=0, column=0, columnspan=1, pady=10)  # Increase columnspan for alignment

        # Section title: Model Configuration
        self.title_label = tk.Label(self, text="Model Configuration", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')


        # Model Configuration Parameters
        #-------------------------------

        # Total Project Duration 
        tk.Label(self, text="Total Project Duration [Years]:", anchor='w').grid(row=2, column=0, sticky='w')
        self.Years_var = tk.IntVar(value=20)
        vcmd = (self.register(self.validate_integer), '%P')
        self.Years_entry = tk.Entry(self, textvariable=self.Years_var, validate='key', validatecommand=vcmd)
        self.Years_entry.grid(row=2, column=1, sticky='w')
        create_tooltip(self.Years_entry, "Enter the duration of the project in years")

        # Step Duration
        tk.Label(self, text="Step Duration [Years]:", anchor='w').grid(row=3, column=0, sticky='w')
        self.Step_Duration_var = tk.IntVar(value=1)
        vcmd = (self.register(self.validate_integer), '%P')
        self.Step_Duration_entry = tk.Entry(self, textvariable=self.Step_Duration_var,validate='key', validatecommand=vcmd)
        self.Step_Duration_entry.grid(row=3, column=1,sticky='w')
        create_tooltip(self.Step_Duration_entry, "Duration of each investment decision step in which the project lifetime will be split")

        # Min_Last_Step_Duration
        tk.Label(self, text="Minimum Last Step Duration [Years]:", anchor='w').grid(row=4, column=0, sticky='w')
        self.Min_Step_Duration_var = tk.IntVar(value=1)
        vcmd = (self.register(self.validate_integer), '%P')
        self.Min_Step_Duration_entry = tk.Entry(self, textvariable=self.Min_Step_Duration_var,validate='key', validatecommand=vcmd)
        self.Min_Step_Duration_entry.grid(row=4, column=1,sticky='w')
        create_tooltip(self.Min_Step_Duration_entry, "Minimum duration of the last investment decision step, in case of non-homogeneous divisions of the project lifetime")

        # Real_Discount_Rate
        tk.Label(self, text="Discount Rate [-]:", anchor='w').grid(row=5, column=0, sticky='w')
        self.Real_Discount_Rate_var = tk.DoubleVar(value=0.1)
        vcmd = (self.register(self.validate_float), '%P')
        self.Real_Discount_Rate_entry = tk.Entry(self, textvariable=self.Real_Discount_Rate_var,validate='key', validatecommand=vcmd)
        self.Real_Discount_Rate_entry.grid(row=5, column=1,sticky='w')
        create_tooltip(self.Real_Discount_Rate_entry, "Real discount rate accounting also for inflation")

        # Start Date Entry
        tk.Label(self, text="Start Date of the Project:",anchor='w').grid(row=6, column=0, sticky='w')
        self.StartDate_var = tk.StringVar(value="01/01/2023 00:00:00")
        self.StartDate_entry = tk.Entry(self, textvariable=self.StartDate_var)
        self.StartDate_entry.grid(row=6, column=1,sticky='w')
        create_tooltip(self.StartDate_entry, "MM/DD/YYYY HH:MM:SS format")



        # Optimization Setup Parameters
        #-------------------------------

        # Section title: Optimization setup
        self.title_label = tk.Label(self, text="Optimization setup", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=1, column=2, columnspan=1, pady=10, sticky='w', padx=(30, 0))  # Align to west (left), start from column 2

        # Renewable Penetration
        tk.Label(self, text="Renewable Penetration [-]", anchor='w').grid(row=2, column=2, sticky='w',padx=(30, 0))
        self.Renewable_Penetration_var = tk.DoubleVar(value=0.0)
        vcmd = (self.register(self.validate_fraction), '%P')
        self.Renewable_Penetration_entry = tk.Entry(self, textvariable=self.Renewable_Penetration_var,validate='key', validatecommand=vcmd)
        self.Renewable_Penetration_entry.grid(row=2, column=3,padx=(30, 0))
        create_tooltip(self.Renewable_Penetration_entry, "Minimum fraction of electricity produced by renewable sources")

        # Battery Independence
        tk.Label(self, text="Battery Independence [Days]", anchor='w').grid(row=3, column=2, sticky='w',padx=(30, 0))
        self.Battery_Independence_var = tk.StringVar(value="0")
        vcmd = (self.register(self.validate_integer), '%P')
        self.Battery_Independence_entry = tk.Entry(self, textvariable=self.Battery_Independence_var,validate='key', validatecommand=vcmd)
        self.Battery_Independence_entry.grid(row=3, column=3,padx=(30, 0))
        create_tooltip(self.Battery_Independence_entry, "Number of days of battery independence")

        # Lost Load Fraction
        tk.Label(self, text="Lost Load Fraction [-]", anchor='w').grid(row=4, column=2, sticky='w',padx=(30, 0))
        self.Lost_Load_Fraction_var = tk.DoubleVar(value=0.0)
        vcmd = (self.register(self.validate_float), '%P')
        self.Lost_Load_Fraction_entry = tk.Entry(self, textvariable=self.Lost_Load_Fraction_var,validate='key', validatecommand=vcmd)
        self.Lost_Load_Fraction_entry.grid(row=4, column=3,padx=(30, 0))
        create_tooltip(self.Lost_Load_Fraction_entry, "Maximum admissible loss of load as a fraction")
        self.Lost_Load_Fraction_var.trace('w', self.check_lost_load_fraction)

        # Lost Load Specific Cost
        self.Lost_Load_Specific_Cost_var = tk.DoubleVar(value=0.0)
        vcmd = (self.register(self.validate_float), '%P')
        self.Lost_Load_Specific_Cost_label = tk.Label(self, text="Lost Load Specific Cost [USD/Wh]", anchor='w')
        self.Lost_Load_Specific_Cost_label.grid(row=5, column=2, sticky='w',padx=(30, 0))
        self.Lost_Load_Specific_Cost_entry = tk.Entry(self, textvariable=self.Lost_Load_Specific_Cost_var,validate='key', validatecommand=vcmd)
        self.Lost_Load_Specific_Cost_entry.grid(row=5, column=3,padx=(30, 0))
        create_tooltip(self.Lost_Load_Specific_Cost_entry, "Value of the unmet load in USD per Wh.")
        self.Lost_Load_Specific_Cost_label.config(state='disabled')
        self.Lost_Load_Specific_Cost_entry.config(state='disabled')

        # Investment_Cost_Limit
        tk.Label(self, text="Investment Cost Limit [USD]",anchor='w').grid(row=6, column=2,sticky='w',padx=(30, 0))
        self.Investment_Cost_Limit_var = tk.DoubleVar(value="500000")
        vcmd = (self.register(self.validate_float), '%P')
        self.Investment_Cost_Limit_entry = tk.Entry(self, textvariable=self.Investment_Cost_Limit_var,validate='key', validatecommand=vcmd)
        self.Investment_Cost_Limit_entry.grid(row=6, column=3,padx=(30, 0))
        create_tooltip(self.Investment_Cost_Limit_entry, "Upper limit to investment cost (considered only in case Optimization_Goal='Operation cost')")

        #----------------------------------------------------------------------------------------------------------------------------

        # Optimization Goal
        self.Optimization_Goal_var = tk.IntVar(value=1)
        tk.Label(self, text="Optimization Goal:",anchor='w').grid(row=8, column=0,sticky='w',ipady=20)
        self.Optimization_Goal_radio1 = tk.Radiobutton(self, text="NPC", variable=self.Optimization_Goal_var, value=1)
        self.Optimization_Goal_radio1.grid(row=8, column=1, sticky='w')
        self.Optimization_Goal_radio0 = tk.Radiobutton(self, text="Operation cost", variable=self.Optimization_Goal_var, value=0)
        self.Optimization_Goal_radio0.grid(row=8, column=1, sticky='e')
        create_tooltip(self.Optimization_Goal_radio1, "Net Present Cost oriented optimization")
        create_tooltip(self.Optimization_Goal_radio0, "Non-Actualized Operation Cost-oriented optimization")

        # Model Components
        self.Model_Components_var = tk.IntVar(value=0)
        tk.Label(self, text="Backup Systems:", anchor='w').grid(row=9, column=0, sticky='w')
        self.Model_Components_radio0 = tk.Radiobutton(self, text="Batteries and Generators", variable=self.Model_Components_var, value=0)
        self.Model_Components_radio0.grid(row=9, column=1, sticky='w')
        self.Model_Components_radio1 = tk.Radiobutton(self, text="Batteries Only", variable=self.Model_Components_var, value=1)
        self.Model_Components_radio1.grid(row=10, column=1, sticky='w')
        self.Model_Components_radio2 = tk.Radiobutton(self, text="Generators Only", variable=self.Model_Components_var, value=2)
        self.Model_Components_radio2.grid(row=11, column=1, sticky='w')


        # Model Advanced Features
        #-------------------------------

        self.title_label = tk.Label(self, text="Advanced Features", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=12, column=0, columnspan=1, pady=10, sticky='w')


        # MILP Formulation
        self.MILP_Formulation_var = tk.IntVar(value=0)
        tk.Label(self, text="Model Formulation:", anchor='w').grid(row=13, column=0, sticky='w')
        self.MILP_Formulation_radio0 = tk.Radiobutton(self, text="LP", variable=self.MILP_Formulation_var, value=0)
        self.MILP_Formulation_radio0.grid(row=13, column=1, sticky='w')
        self.MILP_Formulation_radio1 = tk.Radiobutton(self, text="MILP", variable=self.MILP_Formulation_var, value=1)
        self.MILP_Formulation_radio1.grid(row=13, column=1, sticky='e')
        self.MILP_Formulation_var.trace('w', self.toggle_generator_partial_load)
        create_tooltip(self.MILP_Formulation_radio0, "Linear Programming")
        create_tooltip(self.MILP_Formulation_radio1, "Multiple Integers Linear Programming")

        # Generator Partial Load
        self.Generator_Partial_Load_var = tk.IntVar(value=0)
        self.Generator_Partial_Load_label = tk.Label(self, text="Generator Partial Load:", anchor='w')
        self.Generator_Partial_Load_label.grid(row=14, column=0, sticky='w')
        self.Generator_Partial_Load_checkbutton = tk.Checkbutton(self, text="Activate", variable=self.Generator_Partial_Load_var, onvalue=1, offvalue=0)
        self.Generator_Partial_Load_checkbutton.grid(row=14, column=1, sticky='w')
        self.Generator_Partial_Load_label.config(state='disabled')
        self.Generator_Partial_Load_checkbutton.config(state='disabled')
        self.toggle_generator_partial_load()


        # Multiobjective Optimization
        self.Multiobjective_Optimization_var = tk.IntVar(value=0)
        tk.Label(self, text="Multi-Objective Optimization:", anchor='w').grid(row=15, column=0, sticky='w')
        self.Multiobjective_Optimization_checkbutton = tk.Checkbutton(self, text="Activate", variable=self.Multiobjective_Optimization_var, onvalue=1, offvalue=0)
        self.Multiobjective_Optimization_checkbutton.grid(row=15, column=1, sticky='w')
        create_tooltip(self.Multiobjective_Optimization_checkbutton, "Optimization of NPC/operation cost and CO2 emissions")
        self.Multiobjective_Optimization_var.trace('w', self.toggle_Plot_Max_Cost)

        # Define the variable for Plot Max Cost options
        self.Plot_Max_Cost_var = tk.IntVar(value=0)
        self.Plot_Max_Cost_label = tk.Label(self, text="Plot Max Cost:", anchor='w')
        self.Plot_Max_Cost_label.grid(row=16, column=0, sticky='w')
        self.Plot_Max_Cost_radio1 = tk.Radiobutton(self, text="Yes", variable=self.Plot_Max_Cost_var, value=1, state='disabled')
        self.Plot_Max_Cost_radio1.grid(row=16, column=1, sticky='w')
        create_tooltip(self.Plot_Max_Cost_radio1, "Pareto curve has to include the point at maxNPC/maxOperationCost")
        self.Plot_Max_Cost_radio0 = tk.Radiobutton(self, text="No", variable=self.Plot_Max_Cost_var, value=0, state='disabled')
        self.Plot_Max_Cost_radio0.grid(row=16, column=1, sticky='e')
        self.Plot_Max_Cost_label.config(state='disabled')
        self.toggle_Plot_Max_Cost()


        # Greenfield
        self.Greenfield_Investment_var = tk.IntVar(value=0)
        tk.Label(self, text="Type of Investment:",anchor='w').grid(row=17, column=0,sticky='w')
        tk.Radiobutton(self, text="Greenfield", variable=self.Greenfield_Investment_var, value=1).grid(row=17, column=1, sticky='w')
        tk.Radiobutton(self, text="Brownfield", variable=self.Greenfield_Investment_var, value=0).grid(row=17, column=1, sticky='e')


        # Grid Connection Radiobuttons
        self.Grid_Connection_var = tk.IntVar(value=0)
        self.Grid_Connection_var.trace('w', self.toggle_grid_options)
        tk.Label(self, text="Grid Connection:", anchor='w').grid(row=18, column=0, sticky='w')
        self.Grid_Connection_radio = tk.Radiobutton(self, text="On-grid", variable=self.Grid_Connection_var, value=1)
        self.Grid_Connection_radio.grid(row=18, column=1, sticky='w')
        create_tooltip(self.Grid_Connection_radio, "Simulate grid connection during project lifetime")
        tk.Radiobutton(self, text="Off-grid", variable=self.Grid_Connection_var, value=0).grid(row=18, column=1, sticky='e')

        # Grid Availability Simulation
        self.Grid_Availability_Simulation_var = tk.IntVar(value=0)
        self.Grid_Availability_Simulation_label = tk.Label(self, text="Grid Availability:", anchor='w')
        self.Grid_Availability_Simulation_label.grid(row=19, column=0, sticky='w')
        self.Grid_Availability_Simulation_label.config(state='disabled')
        self.Grid_Availability_Simulation_checkbutton = tk.Checkbutton(self, text="Activate", variable=self.Grid_Availability_Simulation_var, onvalue=1, offvalue=0)
        create_tooltip(self.Grid_Availability_Simulation_checkbutton, "Simulate grid availability matrix")
        self.Grid_Availability_Simulation_checkbutton.grid(row=19, column=1, sticky='w')
        self.Grid_Availability_Simulation_checkbutton.config(state='disabled')

        # Grid Connection Type Radiobuttons
        self.Grid_Connection_Type_var = tk.IntVar(value=1)
        self.Grid_Connection_Type_label = tk.Label(self, text="Grid Connection Type:", anchor='w', state='disabled')
        self.Grid_Connection_Type_label.grid(row=20, column=0, sticky='w')
        self.Grid_Connection_Type_radio1 = tk.Radiobutton(self, text="Purchase", variable=self.Grid_Connection_Type_var, value=1, state='disabled')
        self.Grid_Connection_Type_radio1.grid(row=20, column=1, sticky='w')
        self.Grid_Connection_Type_radio2 = tk.Radiobutton(self, text="Sell/Purchase", variable=self.Grid_Connection_Type_var, value=2, state='disabled')
        self.Grid_Connection_Type_radio2.grid(row=20, column=1, sticky='e')
        self.toggle_grid_options()


        # WACC Calculation Checkbutton
        self.WACC_Calculation_var = tk.IntVar(value=0)
        self.WACC_Calculation_label = tk.Label(self, text="WACC Calculation:", anchor='w')
        self.WACC_Calculation_label.grid(row=13, column=2, sticky='w',padx=(30, 0))
        self.WACC_Calculation_checkbutton = tk.Checkbutton(self, text="Activate", variable=self.WACC_Calculation_var, onvalue=1, offvalue=0, command=self.toggle_wacc_parameters)
        self.WACC_Calculation_checkbutton.grid(row=13, column=3, sticky='w')
        
        vcmd = (self.register(self.validate_float), '%P')

        # WACC Parameters
        wacc_parameters = {
            "cost_of_equity": 0.12,
            "cost_of_debt": 0.11,
            "tax": 0.02,
            "equity_share": 0.10,
            "debt_share": 0.90
            }

        # Create labels and entries for WACC parameters in the adjusted columns
        self.wacc_parameters_entries = []
        for i, (param, value) in enumerate(wacc_parameters.items(), start=14):  # Adjust the starting row accordingly
            label = tk.Label(self, text=param)
            label.grid(row=i, column=2, sticky='w',padx=(40, 0))  # Place the labels in column 3
            var = tk.DoubleVar(value=value)
            entry = tk.Entry(self, textvariable=var, state='normal', validate='key', validatecommand=vcmd)  # Initially set state to 'normal' to show the value
            entry.var = var
            entry.grid(row=i, column=3, sticky='w')  # Place the entry fields in column 4
            label.config(state='disabled')  # Then disable the entry
            entry.config(state='disabled')  # Then disable the entry
            self.wacc_parameters_entries.append((label, entry))

        # Button to go to RE Calculation page
        go_to_re_calc_button = tk.Button(self, text="Next", command=self.on_next_button)
        go_to_re_calc_button.grid(row=22, column=3)
        
    def get_input_data(self):
        return {
            'Years': self.Years_var.get(),
            'Step_Duration': self.Step_Duration_var.get(),
            'Min_Last_Step_Duration': self.Min_Step_Duration_var.get(),
            'Discount_Rate': self.Real_Discount_Rate_var.get(),
            'Start_Date': self.StartDate_var.get(),
            'Renewable_Penetration': self.Renewable_Penetration_var.get(),
            'Battery_Independence': self.Battery_Independence_var.get(),
            'Lost_Load_Fraction': self.Lost_Load_Fraction_var.get(),
            'Lost_Load_Specific_Cost': self.Lost_Load_Specific_Cost_var.get(),
            'Investment_Cost_Limit': self.Investment_Cost_Limit_var.get(),
            'Optimization_Goal': self.Optimization_Goal_var.get(),
            'Model_Components': self.Model_Components_var.get(),
            'MILP_Formulation': self.MILP_Formulation_var.get(),
            'Generator_Partial_Load': self.Generator_Partial_Load_var.get(),
            'Multiobjective_Optimization': self.Multiobjective_Optimization_var.get(),
            'Plot_Max_Cost': self.Plot_Max_Cost_var.get(),
            'Greenfield_Investment': self.Greenfield_Investment_var.get(),
            'Grid_Connection': self.Grid_Connection_var.get(),
            'Grid_Availability_Simulation': self.Grid_Availability_Simulation_var.get(),
            'Grid_Connection_Type': self.Grid_Connection_Type_var.get(),
            'WACC_Calculation': self.WACC_Calculation_var.get(),
            # Add entries for each WACC parameter
            **{f'WACC_{param}': var.get() for param, var in self.wacc_parameters_entries}
        }

        



