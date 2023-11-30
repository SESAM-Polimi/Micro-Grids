import tkinter as tk
from tkinter import ttk
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
        


class TechnologiesPage(tk.Frame):
    
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
    
    def clear_res_entries(self):
        for widgets in self.res_entries_widgets:
            for widget in widgets:
                widget.destroy()
        self.res_entries_widgets = []
        
    def get_validation_command(self, param, default):
        fraction_params = {"RES_Inverter_Efficiency", "RES_Specific_OM_Cost"}  
        if param in fraction_params:
            return (self.register(self.validate_fraction), '%P')
        elif isinstance(default, int):
            return (self.register(self.validate_integer), '%P')
        elif isinstance(default, float):
            return (self.register(self.validate_float), '%P')
        return None
        
    def update_res_configuration(self):
        self.clear_res_entries()  # Clear all existing RES entries and labels

        try:
            res_sources = int(self.RES_Sources_entry.get())
        except ValueError:
            print("Please enter a valid integer for the number of RES types.")
            return

        # Clear the previous StringVars to avoid holding onto old data
        self.res_entries = {param: [] for param in self.res_params_defaults}
        
        for i in range(res_sources):
            widgets_for_res = []  # Keep track of widgets for this generator source
            for j, (param, default) in enumerate(self.res_params_defaults.items(), start=5):
                vcmd = self.get_validation_command(param, default)
                # Create a StringVar for each entry
                temp_var = tk.StringVar(value=default if i == 0 else "")
                entry = tk.Entry(self, textvariable=temp_var, validate='key', validatecommand=vcmd if vcmd else '')
                entry.grid(row=j, column=i+1, sticky='w')
                widgets_for_res.append(entry)
                # Append the StringVar to the appropriate list in the self.res_entries dictionary
                self.res_entries[param].append(temp_var)
            self.res_entries_widgets.append(widgets_for_res)
            
    def get_input_data(self):
        res_data = {}
        num_res_types = int(self.RES_Sources_var.get())  # Get the number of RES types
        for param in self.res_params_defaults.keys():
            # Fetch the values from the StringVars associated with the entries
            values = [var.get() for var in self.res_entries[param][:num_res_types]]
            # Store as a list or a single value
            res_data[param] = values 
        return res_data
            
    def on_confirm_res(self):
            self.controller.refresh_plot_page()
            
    def on_confirm_and_next(self):
        # This method is linked to the confirm button and will call save_res_data
        self.get_input_data()
        self.controller.refresh_plot_page()  # Update the plot page with the new data
        self.controller.show_next_page()  # Go to the next page
                
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Define the default parameters and their initial values
        self.res_params_defaults = {
            "RES_Names": "Solar PV",
            "RES_Nominal_Capacity": 1000,
            "RES_Inverter_Efficiency": 0.98,
            "RES_Specific_Investment_Cost": 1.5,
            "RES_Specific_OM_Cost": 0.02,
            "RES_Lifetime": 25,
            "RES_units": 1,
            "RES_years": 20,
            "RES_unit_CO2_emission": 0
        }
        
        # Initialize the dictionary to hold the StringVars for each parameter
        self.res_entries = {param: [] for param in self.res_params_defaults}
        
        # Initialize the dictionary to hold the StringVars for each parameter
        self.res_entries = {param: [] for param in self.res_params_defaults}
        self.res_entries_widgets = []  # List to hold entry widgets for clearing

        # Custom font definitions
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12, underline=True)

        # Title label
        self.title_label = tk.Label(self, text="Technologies Parameters", font=self.title_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')

        # Renewable parameters label
        self.title_label = tk.Label(self, text="Renewables", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')

        # RES types entry
        tk.Label(self, text="Number of RES Types:").grid(row=3, column=0, sticky='w')
        self.RES_Sources_var = tk.IntVar(value=1)  # Default value set to 1
        vcmd = (self.register(self.validate_integer), '%P')  # Validation command
        self.RES_Sources_entry = tk.Entry(self, textvariable=self.RES_Sources_var, validate='key', validatecommand=vcmd)
        self.RES_Sources_entry.grid(row=3, column=1, sticky='w')

        # Update configuration button
        self.update_button = tk.Button(self, text="Update Parameters Configuration", command=self.update_res_configuration)
        self.update_button.grid(row=3, column=2)

        for j, param in enumerate(self.res_params_defaults, start=5):
            tk.Label(self, text=param).grid(row=j, column=0, sticky='w')

        # Initially, call update to create one set of entries for default RES sources count
        self.update_res_configuration()
        
        self.confirm_button = tk.Button(self, text="Confirm", command=self.on_confirm_and_next)
        self.confirm_button.grid(row=50, column=3, sticky='w')
        
        # Button to go back to StartPage
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ArchetypesPage"))
        back_button.grid(row=50, column=0,sticky='w')
        


