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
        

class RECalculationPage(tk.Frame):
    
    def get_input_data(self):
        """Retrieve input data from entry widgets."""
        input_data = {'RE_Supply_Calculation': self.RE_Supply_Calculation_var.get()}
        for var, label, entry in self.re_calc_params_entries:
            param = label.cget("text").rstrip(':')
            input_data[param] = var.get()  # Retrieve the value from the entry widget
        return input_data
    def toggle_re_calc_parameters(self, *args):
        state = 'normal' if self.RE_Supply_Calculation_var.get() == 1 else 'disabled'
        for var, label, entry in self.re_calc_params_entries:
            label.config(state=state)
            entry.config(state=state)
            if state == 'disabled':
                var.set('')  # Clear the entry when disabling
                
    def update_warning(self, *args):
        if self.RE_Supply_Calculation_var.get() == 0:  # If RES calculation is NOT activated
            self.warning_label.grid(row=1, column=0, columnspan=4, sticky="ew")  # Show the warning
        else:
            self.warning_label.grid_remove()  # Hide the warning
                
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)

        # Section title: Model Configuration
        self.title_label = tk.Label(self, text="Endogenous RES Time Series Calculation", font=self.subtitle_font, fg="black")
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')
        
        # RE_Supply_Calculation Checkbutton
        self.RE_Supply_Calculation_var = tk.IntVar(value=0)
        tk.Label(self, text="RES Supply Calculation:", anchor='w').grid(row=3, column=0, sticky='w')
        self.RE_Supply_Calculation_checkbutton = tk.Checkbutton(self, text="Activate", variable=self.RE_Supply_Calculation_var, onvalue=1, offvalue=0,command=self.toggle_re_calc_parameters)
        self.RE_Supply_Calculation_checkbutton.grid(row=3, column=0, sticky='e')
        create_tooltip(self.RE_Supply_Calculation_checkbutton, "Select to simulate solar PV and wind production time series using NASA POWER data")
        self.RE_Supply_Calculation_var.trace('w', self.update_warning)
        
        # Define and grid the parameters as labels and entries
        self.re_calc_params = {
            "lat": "-11 33 56.4",
            "lon": "30 21 3.4",
            "time_zone": "+2",
            "nom_power" : "300", 							
            "tilt" : "10",								
            "azim" : "180",							
            "ro_ground" : "0.2",						
            "k_T" : "-0.37",								
            "NMOT" : "45",										
            "T_NMOT" : "20",								
            "G_NMOT" : "800",								
            "turbine_type" : 'HA',							
            "turbine_model" : 'NPS100c-21',				      	         
            "drivetrain_efficiency" : "0.9"
        }

        self.re_calc_params_entries = []
        
        for i, (param, value) in enumerate(self.re_calc_params.items(), start=4):  # Adjust the starting row
            label_text = param
            label = tk.Label(self, text=label_text)
            label.grid(row=i, column=0, sticky='w')
            var = tk.StringVar(value=value)
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=i, column=0, sticky='e')
            # Initially disable the entries
            label.config(state='disabled')
            entry.config(state='disabled')
            self.re_calc_params_entries.append((var, label, entry))
            

        # Create the warning label and grid it
        self.warning_label = tk.Label(self, text="If RES Supply Calculation is deactivated, you must provide the RES Time Series Data as CSV file (refer to the online documentation for more details)", wraplength=500, justify="left", fg="red")
        self.warning_label.grid(row=30, column=0, columnspan=4, sticky="ew")
        
        # Button to go to RE Calculation page
        go_to_demand_calc_button = tk.Button(self, text="Next", command=lambda: controller.show_frame("ArchetypesPage"))
        go_to_demand_calc_button.grid(row=40, column=3)
        
  


