import tkinter as tk
from tkinter import font as tkFont
from tkinter import scrolledtext
import time
from pyomo.environ import AbstractModel
from Model_Creation import Model_Creation
from Model_Resolution import Model_Resolution
from Results import ResultsSummary, TimeSeries, PrintResults
from Plots import DispatchPlot, SizePlot

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

class RunPage(tk.Frame):
        
    def run_model(self):
        self.status_label.config(text="Status: Running...")
        self.output_text.insert(tk.END, "Model is running...\n")
        
        try:
            start = time.time()  # Start time counter
            model = AbstractModel()  # Define type of optimization problem

            Model_Creation(model)  # Creation of the Sets, parameters and variables.

            # Resolve the model instance
            instance = Model_Resolution(model)

            Time_Series = TimeSeries(instance)
            Optimization_Goal = instance.Optimization_Goal.extract_values()[None]
            Results = ResultsSummary(instance, Optimization_Goal, Time_Series)
            
            # Assume ResultsSummary returns a string of results
            results = f"Model run complete in {time.time() - start:.2f} seconds. Output:\n{Results}"
            self.output_text.insert(tk.END, results)
            self.status_label.config(text="Status: Complete")
        except Exception as e:
            self.output_text.insert(tk.END, f"An error occurred:\n{e}")
            self.status_label.config(text="Status: Error")

        self.output_text.yview(tk.END)  # Scroll to the bottom to show latest output


    def clear_output(self):
        # This method can be called to clear the output text widget
        self.output_text.delete(1.0, tk.END)
        
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        title_label = tk.Label(self, text="Run the Model", font=("Helvetica", 16))
        title_label.pack(pady=20)

        # Run button
        run_button = tk.Button(self, text="RUN", command=self.run_model)
        run_button.pack()

        # Output scrolled text
        self.output_text = scrolledtext.ScrolledText(self, width=70, height=20, wrap=tk.WORD)
        self.output_text.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self, text="Status: Ready", font=("Helvetica", 10))
        self.status_label.pack()

