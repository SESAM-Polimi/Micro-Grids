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

class GeneratorPage(tk.Frame):

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
        
    def get_validation_command(self, param, default):
        fraction_params = {...}  
        if param in fraction_params:
            return (self.register(self.validate_fraction), '%P')
        elif isinstance(default, int):
            return (self.register(self.validate_integer), '%P')
        elif isinstance(default, float):
            return (self.register(self.validate_float), '%P')
        
    def update_gen_parameters_defaults(self, milp_formulation, partial_load):

        if milp_formulation == 1 and partial_load == 1:
         # Define the default generator parameters and their initial values
         self.gen_params_defaults = {
            "Generator_Names": "Diesel Genset 1",
            "Generator_Efficiency": 0.3,
            "Generator_Specific_Investment_Cost": 0.4,
            "Generator_Specific_OM_Cost": 0.08,
            "Generator_Lifetime": 20,
            "Fuel_Names": "Diesel",
            "Fuel_Specific_Cost": 1.17,
            "Fuel_LHV": 10140,
            "Generator_capacity": 0,
            "GEN_years": 0,
            "GEN_unit_CO2_emission": 0,
            "FUEL_unit_CO2_emission": 2.68,
            "Generator_Min_output" : 0.3,
            "Generator_Nominal_Capacity_milp" : 30000,
            "Generator_pgen" : 0.01
         }
         
        elif milp_formulation == 1 and partial_load == 0:
         # Define the default generator parameters and their initial values
         self.gen_params_defaults = {
            "Generator_Names": "Diesel Genset 1",
            "Generator_Efficiency": 0.3,
            "Generator_Specific_Investment_Cost": 0.4,
            "Generator_Specific_OM_Cost": 0.08,
            "Generator_Lifetime": 20,
            "Fuel_Names": "Diesel",
            "Fuel_Specific_Cost": 1.17,
            "Fuel_LHV": 10140,
            "Generator_capacity": 0,
            "GEN_years": 0,
            "GEN_unit_CO2_emission": 0,
            "FUEL_unit_CO2_emission": 2.68,
            "Generator_Nominal_Capacity_milp" : 30000
         }
         
        elif milp_formulation == 0 and partial_load == 0:
         # Define the default generator parameters and their initial values
         self.gen_params_defaults = {
            "Generator_Names": "Diesel Genset 1",
            "Generator_Efficiency": 0.3,
            "Generator_Specific_Investment_Cost": 0.4,
            "Generator_Specific_OM_Cost": 0.08,
            "Generator_Lifetime": 20,
            "Fuel_Names": "Diesel",
            "Fuel_Specific_Cost": 1.17,
            "Fuel_LHV": 10140.0,
            "Generator_capacity": 0.0,
            "GEN_years": 0,
            "GEN_unit_CO2_emission": 0.0,
            "FUEL_unit_CO2_emission": 2.68}
         
        self.gen_params_tooltips = {
            "Generator_Efficiency": "Average generator efficiency of each generator type [%]",
            "Generator_Specific_Investment_Cost": "Specific investment cost for each generator type [USD/W]",
            "Generator_Specific_OM_Cost": "O&M cost for each generator type as a fraction of specific investment cost [%]",
            "Generator_Lifetime": "Generator Lifetime [years]",
            "Fuel_Names": "Fuel names (to be specified for each generator, even if they use the same fuel)",
            "Fuel_Specific_Cost": "Specific fuel cost for each generator type [USD/lt]",
            "Fuel_LHV": "Fuel lower heating value (LHV) for each generator type [Wh/lt]",
            "Generator_capacity": "Existing Generator capacity [W]",
            "GEN_years": "How many years ago the component was installed [years]",
            "GEN_unit_CO2_emission": "Specific CO2 emissions associated to each generator type[kgCO2/kW]",
            "FUEL_unit_CO2_emission": "Specific CO2 emissions associated to the fuel [kgCO2/lt]"
        }
         
        row_start = 5
        for i, (param, default) in enumerate(self.gen_params_defaults.items()):
            # Create and place the label
            label = tk.Label(self, text=param)
            label.grid(row=row_start + i, column=0, sticky='w')
            # Create and place the entry
            entry = self.create_entry(param, default, row_start + i)
            tooltip_text = self.gen_params_tooltips.get(param, "No description available")
            create_tooltip(entry, tooltip_text)
            # Store the label and entry in a way that they can be cleared later if needed
            self.gen_entries_widgets.append((label, entry))
            
    def create_entry(self, param, default, row):
        vcmd = self.get_validation_command(param, default)
        entry = tk.Entry(self, textvariable=tk.StringVar(value=str(default)), validate='key', validatecommand=vcmd)
        entry.grid(row=row, column=1, sticky='w')
        return entry

    def get_validation_command(self, param, default):
        fraction_params = {"Generator_Efficiency", "Generator_Specific_OM_Cost", "Generator_Min_output", "Generator_pgen"}
        if param in fraction_params:
            return (self.register(self.validate_fraction), '%P')
        elif isinstance(default, int):
            return (self.register(self.validate_integer), '%P')
        elif isinstance(default, float):
            return (self.register(self.validate_float), '%P')
        return None

    def update_gen_configuration(self):
        #self.clear_gen_entries()  # Clear all existing RES entries and labels
        try: gen_sources = int(self.Generator_Types_entry.get())
        except : gen_sources = 1

        # Clear the previous StringVars to avoid holding onto old data
        self.gen_entries = {param: [] for param in self.gen_params_defaults}
        
        fraction_params = {"Generator_Efficiency", "Generator_Specific_OM_Cost", "Generator_Min_output", "Generator_pgen"}
        
        for i in range(gen_sources):
            widgets_for_gen = []  # Keep track of widgets for this generator source
            for j, (param, default) in enumerate(self.gen_params_defaults.items(), start=5):
                if param in fraction_params:
                    # If the parameter is expected to be a quoted text, use the validate_quoted_text function
                    vcmd = (self.register(self.validate_fraction), '%P')
                elif isinstance(default, int):
                    # If the default value is an integer, use the validate_integer function
                    vcmd = (self.register(self.validate_integer), '%P')
                elif isinstance(default, float):
                    # If the default value is a float, use the validate_float function
                    vcmd = (self.register(self.validate_float), '%P')
                else: vcmd = None
                
                # Create a StringVar for each entry
                temp_var = tk.StringVar(value=default if i == 0 else "")
                entry = tk.Entry(self, textvariable=temp_var,validate='key', validatecommand=vcmd)
                entry.grid(row=j, column=i+1, sticky='w')
                widgets_for_gen.append(entry)
                # Append the StringVar to the appropriate list in the self.res_entries dictionary
                self.gen_entries[param].append(temp_var)
            self.gen_entries_widgets.append(widgets_for_gen)
            
    def get_input_data(self):
        gen_data = {}
        gen_types = int(self.Generator_Types_entry.get())
        for param in self.gen_params_defaults.keys():
            # Fetch the values from the StringVars associated with the entries
            values = [var.get() for var in self.gen_entries[param][:gen_types]]
            # Store as a list or a single value
            gen_data[param] = values 
        return gen_data
            
    def on_confirm_gen(self):
            self.controller.refresh_plot_page()
            
    def on_confirm_and_next(self):
            self.get_input_data()
            self.on_confirm_gen()  # Perform the confirm action first
            self.controller.show_GridPage()  # Then go to the next page
                
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        start_page = self.controller.frames["StartPage"]
        milp_formulation = start_page.MILP_Formulation_var.get()
        partial_load = start_page.Generator_Partial_Load_var.get()
        
        self.gen_params_defaults = {}
        
        # Initialize the dictionary to hold the StringVars for each parameter
        self.gen_entries = {param: [] for param in self.gen_params_defaults}
        self.gen_entries_widgets = []  # List to hold entry widgets for clearing

        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)


        self.title_label = tk.Label(self, text="Backup System", font=self.title_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')
        
        self.title_label = tk.Label(self, text="Generator", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')
        
        # Entry for number of generator types
        tk.Label(self, text="Number of Generator Types:").grid(row=3, column=0, sticky='w')
        self.Generator_Types_var = tk.IntVar(value=1)  # Default value set to 1
        vcmd = (self.register(self.validate_integer), '%P')
        self.Generator_Types_entry = tk.Entry(self, textvariable=self.Generator_Types_var, validate='key', validatecommand=vcmd)
        self.Generator_Types_entry.grid(row=3, column=1, sticky='w')
        
        self.update_gen_parameters_defaults(milp_formulation, partial_load)
        
        for j, param in enumerate(self.gen_params_defaults, start=5):
            tk.Label(self, text=param).grid(row=j, column=0, sticky='w')

        # Update configuration button for generators
        self.update_gen_button = tk.Button(self, text="Update Generator Configuration", command=self.update_gen_configuration)
        self.update_gen_button.grid(row=3, column=2)

        # Initially, call update to create one set of entries for default generator types count
        self.update_gen_configuration()
        
        self.confirm_button = tk.Button(self, text="Confirm", command=self.on_confirm_and_next)
        self.confirm_button.grid(row=50, column=3, sticky='w')
        
        back_button = tk.Button(self, text="Back", command=controller.show_previous_page_from_generator)
        back_button.grid(row=30, column=0, sticky='w')
        
        

