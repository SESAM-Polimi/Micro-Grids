import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk
from ttkthemes import ThemedTk

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
    

class ArchetypesPage(tk.Frame):
    
    def get_input_data(self):
        input_data = {'Demand_Profile_Generation': self.Demand_Profile_Generation_var.get()}
        for var, label, entry in self.demand_calc_params_entries:
            param = label.cget("text")
            input_data[param] = var.get()  # Retrieve the value from the entry widget
        return input_data
    
    def toggle_demand_calc_parameters(self, *args):
        state = 'normal' if self.Demand_Profile_Generation_var.get() == 1 else 'disabled'
        for var, label, entry in self.demand_calc_params_entries:
            label.config(state=state)
            entry.config(state=state)
            if state == 'disabled':
                var.set('')  # Clear the entry when disabling
                
    def update_warning(self,*args):
        if self.Demand_Profile_Generation_var.get() == 0:  # If RES calculation is NOT activated
            self.warning_label.grid(row=1, column=0, columnspan=4, sticky="ew")  # Show the warning
        else:
            self.warning_label.grid_remove()  # Hide the warning
                
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)

        # Section title: Model Configuration
        self.title_label = ttk.Label(self, text="Endogenous Demand Time Series Calculation", font=self.subtitle_font)
        self.title_label.grid(row=1, column=0, columnspan=1, pady=10, sticky='w')
        
        # RE_Supply_Calculation Checkbutton
        self.Demand_Profile_Generation_var = tk.IntVar(value=0)
        ttk.Label(self, text="Demand Profile Generation:", anchor='w').grid(row=3, column=0, sticky='w')
        self.Demand_Profile_Generation_checkbutton = ttk.Checkbutton(self, text="Activate", variable=self.Demand_Profile_Generation_var, onvalue=1, offvalue=0,command=self.toggle_demand_calc_parameters)
        self.Demand_Profile_Generation_checkbutton.grid(row=3, column=0, sticky='e')
        create_tooltip(self.Demand_Profile_Generation_checkbutton, "Select to simulate a load demand profile with built-in demand archetypes")
        self.Demand_Profile_Generation_var.trace('w', self.update_warning)
        
        # Define and grid the parameters as labels and entries
        self.demand_calc_params = {
            "demand_growth": "0", 
            "cooling_period": "AY",
            "h_tier1": "252",
            "h_tier2": "160",
            "h_tier3": "50",
            "h_tier4": "36",
            "h_tier5": "5",
            "schools": "1",
            "hospital_1": "0",
            "hospital_2": "1",
            "hospital_3": "0",
            "hospital_4": "0",
            "hospital_5": "0"
            }

        self.demand_calc_params_entries = []
        for i, (param, value) in enumerate(self.demand_calc_params.items(), start=4):  # Adjust the starting row
            label_text = param
            label = ttk.Label(self, text=label_text)
            label.grid(row=i, column=0, sticky='w')
            var = tk.StringVar(value=value)
            entry = ttk.Entry(self, textvariable=var)
            entry.grid(row=i, column=0, sticky='e')
            # Initially disable the entries
            label.config(state='disabled')
            entry.config(state='disabled')
            self.demand_calc_params_entries.append((var, label, entry))
            

        # Create the warning label and grid it
        self.warning_label = ttk.Label(self, text="If Demand_Profile_Generation is deactivated, you must provide the Demand Time Series Data as CSV file (refer to the online documentation for more details)", wraplength=500, justify="left")
        self.warning_label.grid(row=25, column=0, columnspan=4, sticky="ew")
        
        self.nav_frame = NavigationFrame(self, back_command=lambda: controller.show_frame("RECalculationPage"), next_command=lambda: controller.show_frame("TechnologiesPage"))
        
        # Button to go to RE Calculation page
        # go_to_technologies_button = ttk.Button(self, text="Next", command=lambda: controller.show_frame("TechnologiesPage"))
        # go_to_technologies_button.grid(row=30, column=3)
        
        # # Button to go back to StartPage
        # back_button = ttk.Button(self, text="Back", command=lambda: controller.show_frame("RECalculationPage"))
        # back_button.grid(row=30, column=0,sticky='w')



