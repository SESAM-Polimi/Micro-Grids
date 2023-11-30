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

class BatteryPage(tk.Frame):
    
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
        
    def display_extra_parameter(self):
        param = "Battery_Nominal_Capacity_milp"
        value = 5000
        tooltip_text = "Battery's nominal capacity units (MILP Formulation)"
        row = len(self.battery_calc_params_entries) + 4  # Calculate the next row number dynamically
        
        # Create and grid the label for the extra parameter
        label = tk.Label(self, text=param)
        label.grid(row=row, column=0, sticky='w')
        
        # Create and grid the entry for the extra parameter
        var = tk.StringVar(value=value)
        entry = tk.Entry(self, textvariable=var)
        entry.grid(row=row, column=1, sticky='w')
        create_tooltip(entry, tooltip_text)
        
        # Store the label and entry in the list for future reference or clearing
        self.battery_calc_params_entries.append((var, label, entry))
        
    def get_validation_command(self, param, default):
        fraction_params = {"Battery_Specific_OM_Cost", "Discharge efficiency of the battery bank", "Charge efficiency of the battery bank", "Depth of discharge of the battery bank", "Battery initial state of charge"}  
        if param in fraction_params:
            return (self.register(self.validate_fraction), '%P')
        elif isinstance(default, int):
            return (self.register(self.validate_integer), '%P')
        elif isinstance(default, float):
            return (self.register(self.validate_float), '%P')
        return None
        
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)
        
        self.title_label = tk.Label(self, text="Backup System", font=self.title_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')
        
        self.title_label = tk.Label(self, text="Battery bank", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')
        
        # Define and grid the parameters as labels and entries
        self.battery_calc_params = {
            "Battery_Specific_Investment_Cost": 0.333,
            "Battery_Specific_Electronic_Investment_Cost": 0.25,
            "Battery_Specific_OM_Cost": 0.06,
            "Battery_Discharge_Battery_Efficiency": 0.9,
            "Battery_Charge_Battery_Efficiency": 0.9,
            "Battery_Depth_of_Discharge": 0.2,
            "Maximum_Battery_Discharge_Time": 4,
            "Maximum_Battery_Charge_Time": 4,
            "Battery_Cycles": 5000,
            "Battery_Initial_SOC": 1,
            "Battery_capacity": 0.0,
            "BESS_unit_CO2_emission": 0.0
            }
        
        self.battery_calc_params_tooltips = {
            "Battery_Specific_Investment_Cost": "Specific investment cost of the battery bank [USD/Wh]",
            "Battery_Specific_Electronic_Investment_Cost": "Specific investment cost of non-replaceable parts (electronics) of the battery bank [USD/Wh]",
            "Battery_Specific_OM_Cost": "O&M cost of the battery bank as a fraction of specific investment cost [%]",
            "Battery_Discharge_Battery_Efficiency": "Discharge efficiency of the battery bank [%]",
            "Battery_Charge_Battery_Efficiency": "Charge efficiency of the battery bank [%]",
            "Battery_Depth_of_Discharge": "Depth of discharge of the battery bank [%]",
            "Maximum_Battery_Discharge_Time": "Maximum time to discharge the battery bank [h]",
            "Maximum_Battery_Charge_Time": "Maximum time to charge the battery bank [h]",
            "Battery_Cycles": "Maximum number of cycles before degradation of the battery [units]",
            "Battery_Initial_SOC": "Battery initial state of charge [%]",
            "Battery_capacity": "Existing Battery capacity [Wh]",
            "BESS_unit_CO2_emission": "CO2 emissions [kgCO2/kWh]"
        }

        self.battery_calc_params_entries = []
        for i, (param, value) in enumerate(self.battery_calc_params.items(), start=4):  
            label_text = param
            label = tk.Label(self, text=label_text)
            label.grid(row=i, column=0, sticky='w')
            var = tk.StringVar(value=value)
            vcmd = self.get_validation_command(param, value)
            entry = tk.Entry(self, textvariable=var, validate='key', validatecommand=vcmd)
            entry.grid(row=i, column=1, sticky='w')
            tooltip_text = self.battery_calc_params_tooltips.get(param, "No description available")
            create_tooltip(entry, tooltip_text)
            self.battery_calc_params_entries.append((var, label, entry))
    
        next_button = tk.Button(self, text="Next", command=controller.show_GeneratorPage)
        next_button.grid(row=30, column=3, sticky='w')
        
        back_button = tk.Button(self, text="Back", command=controller.show_previous_page_from_battery)
        back_button.grid(row=30, column=0, sticky='w')
        
        
    def get_input_data(self):
        input_data = {}
        for var, label, entry in self.battery_calc_params_entries:
            param = label.cget("text").rstrip(':')
            input_data[param] = var.get()  # Retrieve the value from the entry widget
        return input_data


