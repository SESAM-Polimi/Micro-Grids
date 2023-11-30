import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

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

class PlotPage(tk.Frame):
    
    def refresh_page(self):
        # Get the updated values from the controller
        res_sources = int(self.controller.get_res_sources_value())
        gen_types = int(self.controller.get_generator_types_value())

        # Re-setup the page with the new values
        self.setup_page(res_sources, gen_types)

    def setup_page(self, res_sources, gen_types):
        # Clear previous entries
        for entry in self.res_color_entries + self.gen_color_entries + list(self.single_color_entries.values()):
            entry.destroy()
        self.res_color_entries.clear()
        self.gen_color_entries.clear()
        self.single_color_entries.clear()

        # Starting row for the color inputs on the grid
        row_start = 7

        # Create entries for RES colors based on res_sources
        row_start = self.create_multiple_color_inputs("RES Colors", 'FF8800', row_start, res_sources, self.res_color_entries)

        # Create entries for Generator colors based on gen_types
        row_start = self.create_multiple_color_inputs("Generator Colors", '00509D', row_start, gen_types, self.gen_color_entries)

        # Create entries for other color parameters
        row_start = self.create_single_color_inputs(row_start)

    def create_multiple_color_inputs(self, label_text, default_color, row_start, num_sources, entries_list):
        # Only create the label if there are no entries yet
        if not entries_list:
            ttk.Label(self, text=label_text + ":").grid(row=row_start, column=0, pady=5, sticky='e')
        for i in range(num_sources):
            # Skip creating the default entry if it already exists
            if i == 0 and entries_list:
                continue
            color_entry = ttk.Entry(self, width=10)
            color_entry.insert(0, default_color if i == 0 else "")
            color_entry.grid(row=row_start, column=i + 1, padx=5, pady=2)
            entries_list.append(color_entry)
        return row_start + 1  # Increment row for the next set of inputs

    def create_single_color_inputs(self, row_start):
        for param, default_color in self.plot_params_defaults.items():
            ttk.Label(self, text=f"{param.replace('_', ' ')}:").grid(row=row_start, column=0, pady=5, sticky='e')
            color_entry = ttk.Entry(self, width=10)
            color_entry.insert(0, default_color)
            color_entry.grid(row=row_start, column=1, padx=5, pady=2)
            self.single_color_entries[param] = color_entry
            row_start += 1
        return row_start
        
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
    
        # Define default color parameters and their initial values
        self.plot_params_defaults = {
            "Battery_Color": '4CC9F0',
            "Lost_Load_Color": 'F21B3F',
            "Curtailment_Color": 'FFD500',
            "Energy_To_Grid_Color": '008000',
            "Energy_From_Grid_Color": '800080'
        }

        # Initialize the data structures to hold the entry widgets
        self.res_color_entries = []
        self.gen_color_entries = []
        self.single_color_entries = {}
        
        # Define custom font
        self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=12,underline=True)
    
        
        self.title_label = ttk.Label(self, text="Plots Parameters", font=self.subtitle_font)
        self.title_label.grid(row=2, column=0, columnspan=1, pady=10, sticky='w')

        # Call setup_page with initial values
        self.refresh_page()
        
        self.nav_frame = NavigationFrame(self, back_command=controller.show_previous_page_from_plot, next_command=controller.save_all_data)


        # save_button = ttk.Button(self, text="Save and Submit", command=controller.save_all_data)
        # save_button.grid(row=50, column=3)
        
        # next_button = ttk.Button(self, text="Next", command=lambda: controller.show_frame("RunPage"))
        # next_button.grid(row=51, column=1, sticky='w')
        
        # # Button to go back to StartPage
        # back_button = ttk.Button(self, text="Back", command=controller.show_previous_page_from_plot)
        # back_button.grid(row=51, column=0, sticky='w')
        
    def get_input_data(self):
        plot_data = {}
        # Retrieve the values for RES colors
        plot_data['RES_Colors'] = [entry.get() for entry in self.res_color_entries]
        # Retrieve the values for Generator colors
        plot_data['Generator_Colors'] = [entry.get() for entry in self.gen_color_entries]
        # Retrieve the values for single color parameters
        for param, entry in self.single_color_entries.items():
            plot_data[param] = '"' + entry.get() + '"'

        return plot_data


