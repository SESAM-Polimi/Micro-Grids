import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox

class NavigationFrame(tk.Frame):
    def __init__(self, parent, back_command, next_command, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        parent_row_index = 35 
        
        # Span across all columns of the parent.
        self.grid(row=parent_row_index, column=0, sticky='ew', columnspan=parent.grid_size()[0])
        
        # Configure the background color and a blue border
        self.configure(background='white', highlightbackground='light blue', highlightthickness=2) 

        self.back_button = ttk.Button(self, text="Back", command=back_command)
        self.back_button.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        self.next_button = ttk.Button(self, text="Next", command=next_command)
        self.next_button.grid(row=0, column=2, sticky='e', padx=10, pady=10)

        # Configure the grid within NavigationFrame to align the buttons properly
        self.grid_columnconfigure(0, weight=1)  # The column for the back button, if used
        self.grid_columnconfigure(1, weight=0)  # The column for the next button
        self.grid_columnconfigure(2, weight=1)

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

    def display_extra_parameter_milp(self):
        param = "Generator_Nominal_Capacity_milp"
        value = 5000
        tooltip_text = "Nominal capacity of each generator [W]"
        row = len(self.gen_entries) + 5  # Calculate the next row number dynamically
        
        # Create and grid the label for the extra parameter
        label = ttk.Label(self, text=param)
        label.grid(row=row, column=0, sticky='w')
    
        # Create and grid the entry for the extra parameter
        var = tk.DoubleVar(value=value)
        entry = ttk.Entry(self, textvariable=var)
        entry.grid(row=row, column=1, sticky='w')
        create_tooltip(entry, tooltip_text)
    
        # Append the entry's variable to the appropriate list in self.gen_entries
        self.gen_entries.append((var, label, entry))
        self.gen_params_defaults[param] = value
        
    def display_extra_parameter(self):
        extra_params = {
        "Generator_Nominal_Capacity_milp": (5000, "Nominal capacity of each generator [W]"),
        "Generator_Min_output": (0.3, "Minimum percentage of energy output for the generator in part load [%]"),
        "Generator_pgen": (0.01, "Percentage of the total operation cost of the generator system at full load [%]")
        }

        for param, (value, tooltip_text) in extra_params.items():
            row = len(self.gen_entries) + 5  # Calculate the next row number dynamically

            # Create and grid the label for the extra parameter
            label = ttk.Label(self, text=param)
            label.grid(row=row, column=0, sticky='w')

            # Create and grid the entry for the extra parameter
            var = tk.DoubleVar(value=value)
            entry = ttk.Entry(self, textvariable=var)
            entry.grid(row=row, column=1, sticky='w')
            create_tooltip(entry, tooltip_text)

            # Append the entry's variable to the appropriate list in self.gen_entries
            self.gen_entries.append((var, label, entry))
            self.gen_params_defaults[param] = value

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
     # First, clear all existing entries.
     self.clear_gen_entries()

     # Get the number of generator sources to configure
     try: 
        gen_sources = int(self.Generator_Types_entry.get())
     except: gen_sources = 1

     # Reset the gen_entries list
     self.gen_entries = []

     text_parameters = ['Generator_Names', 'Fuel_Names']

     # Start adding new entries from the fourth row
     row_start = 4

     for param, default in self.gen_params_defaults.items():
        for i in range(gen_sources):
            # Calculate the row for the current parameter
            row = row_start + list(self.gen_params_defaults.keys()).index(param)
            vcmd = self.get_validation_command(param, default)

            # Check if it's a text parameter and set the appropriate variable type
            if param in text_parameters:
                temp_var = tk.StringVar(value=default)
            else:
                temp_var = tk.DoubleVar(value=default)

            # Create the label only for the first column
            if i == 0:
                label = ttk.Label(self, text=param)
                label.grid(row=row, column=0, sticky='w')
            else:
                label = None

            # Create the entry
            entry = ttk.Entry(self, textvariable=temp_var, validate='key', validatecommand=vcmd)
            entry.grid(row=row, column=1 + i, sticky='w')

            # Append the new entry to gen_entries
            self.gen_entries.append((temp_var, label, entry))

    def clear_gen_entries(self):
     for var, label, entry in self.gen_entries:
        if label: 
            label.destroy()
        entry.destroy()

            
    def get_input_data(self):
     gen_data = {'Generator_Types': self.Generator_Types_var.get()}
     num_gen_types = int(self.Generator_Types_var.get())

     # Initialize a dictionary to store the values for each parameter
     param_values = {param: [] for param in self.gen_params_defaults}

     # Iterate over the entries and aggregate values by parameter
     for var, label, entry in self.gen_entries:
        if label:
            param = label.cget('text')
            # Reset the current list for this parameter if we're on the first generator type
            if len(param_values[param]) >= num_gen_types:
                param_values[param] = [var.get()]
            else:
                param_values[param].append(var.get())
        else:
            # Find the parameter this value belongs to by matching the variable in param_values
            for key, values in param_values.items():
                if len(values) < num_gen_types:
                    param_values[key].append(var.get())
                    break

     # Assign values to gen_data, deciding whether to store a list or a single value
     for param, values in param_values.items():
         gen_data[param] = values

     return gen_data
            
    def on_confirm_gen(self):
            self.controller.refresh_plot_page()
            
    def on_confirm_and_next(self):
     all_filled = True
     for var, label, entry in self.gen_entries:
         try : value = str(entry.get())
         except: value = ''
         if not str(value).strip():  
            # Use the label's text to show which field needs to be filled
            messagebox.showwarning("Warning", f"Please fill in the required field for {label.cget('text') if label else 'unknown parameter'}.")
            entry.focus_set()  # Set focus to the empty entry
            all_filled = False
            break

     if not all_filled:
        return

     # If all fields are filled, proceed to gather the input data and go to the next page
     self.get_input_data()
     self.on_confirm_gen()
     self.controller.show_GridPage()


                
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
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
        
        text_parameters = ['Generator_Names', 'Fuel_Names']
        
        self.gen_entries_widgets = []  # List to hold entry widgets for clearing

        # Custom font definitions
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12, underline=True)

        # Title label
        self.title_label = ttk.Label(self, text="Technologies Parameters", font=self.title_font)
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')

        # Renewable parameters label
        self.title_label = ttk.Label(self, text="Generator", font=self.subtitle_font)
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')

        # RES types entry
        ttk.Label(self, text="Generator Types:").grid(row=3, column=0, sticky='w')
        self.Generator_Types_var = tk.IntVar(value=1)  # Default value set to 1
        vcmd = (self.register(self.validate_integer), '%P')  # Validation command
        self.Generator_Types_entry = ttk.Entry(self, textvariable=self.Generator_Types_var, validate='key', validatecommand=vcmd)
        self.Generator_Types_entry.grid(row=3, column=1, sticky='w')

        # Update configuration button
        self.update_button = ttk.Button(self, text="Update Parameters Configuration", command=self.update_gen_configuration)
        self.update_button.grid(row=3, column=2)

        self.gen_entries = []
        for i, (param, value) in enumerate(self.gen_params_defaults.items(), start=4):  
            label_text = param
            label = ttk.Label(self, text=label_text)
            label.grid(row=i, column=0, sticky='w')
            if param in text_parameters: var = tk.StringVar(value=value)
            else: var = tk.DoubleVar(value=value)
            vcmd = self.get_validation_command(param, value)
            entry = ttk.Entry(self, textvariable=var, validate='key', validatecommand=vcmd)
            entry.grid(row=i, column=1, sticky='w')
            tooltip_text = self.gen_params_tooltips.get(param, "No description available")
            create_tooltip(entry, tooltip_text)
            self.gen_entries.append((var, label, entry))

        self.nav_frame = NavigationFrame(self, back_command=controller.show_previous_page_from_generator, next_command=self.on_confirm_and_next)
        
        # self.confirm_button = ttk.Button(self, text="Confirm", command=self.on_confirm_and_next)
        # self.confirm_button.grid(row=50, column=3, sticky='w')
        
        # back_button = ttk.Button(self, text="Back", command=controller.show_previous_page_from_generator)
        # back_button.grid(row=30, column=0, sticky='w')
        
        

