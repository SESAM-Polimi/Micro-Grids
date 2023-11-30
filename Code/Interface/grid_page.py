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

class GridPage(tk.Frame):
    
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
        extra_params = [
            ("Grid_Average_Number_Outages", 43.48, "Average number of outages in the national grid in a year (0 to simulate ideal power grid)"),
            ("Grid_Average_Outage_Duration", 455.0, "Average duration of an outage [min] (0 to simulate ideal power grid)")]

        for param, value, tooltip_text in extra_params:
            row = len(self.grid_params_entries) + 4  # Calculate the next row number dynamically
            # Create and grid the label for the extra parameter
            label = tk.Label(self, text=param)
            label.grid(row=row, column=0, sticky='w')
            # Create and grid the entry for the extra parameter
            var = tk.StringVar(value=value)
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=row, column=1, sticky='w')
            create_tooltip(entry, tooltip_text)  # Assuming create_tooltip is a pre-defined function

            # Store the label and entry in the list for future reference or clearing
            self.grid_params_entries.append((var, label, entry))

        
    def get_validation_command(self, param, default):
        fraction_params = {...}  
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
        
        self.title_label = tk.Label(self, text="On-Grid Model", font=self.title_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')
        
        self.title_label = tk.Label(self, text="Grid Connection", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')
        
        # Define and grid the parameters as labels and entries
        self.grid_params = {
            "Year_Grid_Connection": 1,
            "Grid_Sold_El_Price": 0.0,
            "Grid_Purchased_El_Price": 0.138,
            "Grid_Distance": 0.5,
            "Grid_Connection_Cost": 14000.0,
            "Grid_Maintenance_Cost": 0.025,
            "Maximum_Grid_Power": 80.0,
            "Grid_Average_Number_Outages": 43.48,
            "Grid_Average_Outage_Duration": 455.0,
            "National_Grid_Specific_CO2_emissions": 0.1495
        }
        
        self.grid_params_tooltips = {
            "Year_Grid_Connection": "Year at which microgrid is connected to the national grid (starting from 1)",
            "Grid_Sold_El_Price": "Price at which electricity is sold to the grid [USD/kWh]",
            "Grid_Purchased_El_Price": "Price at which electricity is purchased from the grid [USD/kWh]",
            "Grid_Distance": "Distance from grid connection point [km]",
            "Grid_Connection_Cost": "Investment cost of grid connection, i.e., extension of power line + transformer costs [USD/km]",
            "Grid_Maintenance_Cost": "O&M cost for maintenance of the power line and transformer as a fraction of investment cost [-]",
            "Maximum_Grid_Power": "Maximum active power that can be injected/withdrawn to/from the grid [kW]",
            "Grid_Average_Number_Outages": "Average number of outages in the national grid in a year (0 to simulate ideal power grid)",
            "Grid_Average_Outage_Duration": "Average duration of an outage [min] (0 to simulate ideal power grid)",
            "National_Grid_Specific_CO2_emissions": "Specific CO2 emissions by the considered national grid [kgCO2/kWh]"
            }

        self.grid_params_entries = []
        for i, (param, value) in enumerate(self.grid_params.items(), start=3):  # Adjust the starting row index if needed
            label_text = param.replace('_', ' ')
            label = tk.Label(self, text=label_text)
            label.grid(row=i, column=0, sticky='w')
            var = tk.StringVar(value=value)
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=i, column=1, sticky='w')
            tooltip_text = self.grid_params_tooltips.get(param, "No description available")
            create_tooltip(entry, tooltip_text)
            self.grid_params_entries.append((var, label, entry))
    
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


