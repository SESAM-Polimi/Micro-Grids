import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sys

class RedirectOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.stdout = sys.stdout

    def write(self, message):
        self.stdout.write(message)
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Auto-scroll to the end

    def flush(self):
        self.stdout.flush()
        
class RunPage(tk.Frame):
    
    def update_output(self, message):
        def _update():
            self.output_text.insert(tk.END, message)
            self.output_text.see(tk.END)  # Auto-scroll to the end
        self.after(0, _update)
        
    def show_dispatch_plot(self):
        # Load the saved plot image
        plot_image = Image.open("Results/Plots/DispatchPlot.png")
        plot_photo = ImageTk.PhotoImage(plot_image)
        
        resized_image = plot_image.resize((700, 400))
        plot_photo = ImageTk.PhotoImage(resized_image)

        # Create a new window or use an existing frame
        plot_window = tk.Toplevel(self)
        plot_window.title("Dispatch Plot")

        # Display the image in a label widget
        plot_label = tk.Label(plot_window, image=plot_photo)
        plot_label.image = plot_photo  # Keep a reference!
        plot_label.pack()
        
    def generate_plot(self):
        
            from Plots import DispatchPlot, SizePlot
            self.update_output("Generating plots....\n")
            PlotScenario = 1                     # Plot scenario
            PlotDate = self.start_date_entry.get() if self.start_date_entry.get() else '01/01/2023 00:00:00'
            PlotTime = int(self.plot_time_entry.get()) if self.start_date_entry.get() else 3
            PlotFormat = 'png'                   # Desired extension of the saved file (Valid formats: png, svg, pdf)
            PlotResolution = 400                 # Plot resolution in dpi (useful only for .png files, .svg and .pdf output a vector plot)

            DispatchPlot(self.instance, self.Time_Series,PlotScenario,PlotDate,PlotTime,PlotResolution,PlotFormat)  
            #CashFlowPlot(self.instance,Results,PlotResolution,PlotFormat)
            SizePlot(self.instance,self.Results,PlotResolution,PlotFormat)
            self.update_output("Plots ready to show\n")
        
    def show_size_plot(self):
        # Load the saved plot image
        plot_image = Image.open("Results/Plots/SizePlot.png")
        plot_photo = ImageTk.PhotoImage(plot_image)
        
        resized_image = plot_image.resize((500, 500))
        plot_photo = ImageTk.PhotoImage(resized_image)

        # Create a new window or use an existing frame
        plot_window = tk.Toplevel(self)
        plot_window.title("Dispatch Plot")

        # Display the image in a label widget
        plot_label = tk.Label(plot_window, image=plot_photo)
        plot_label.image = plot_photo  # Keep a reference!
        plot_label.pack()
        
    def run_model(self):
        
            import time
            from pyomo.environ import AbstractModel
            from Model_Creation import Model_Creation
            from Model_Resolution import Model_Resolution
            from Results import ResultsSummary, TimeSeries, PrintResults

            self.update_output("Running the model....\n")
            start = time.time()      # Start time counter
            model = AbstractModel()  # Define type of optimization problem
            Model_Creation(model)    # Creation of the Sets, parameters and variables.
            # Resolve the model instance
            self.instance = Model_Resolution(model)
            self.Time_Series = TimeSeries(self.instance)
            Optimization_Goal = self.instance.Optimization_Goal.extract_values()[None]
            self.Results = ResultsSummary(self.instance, Optimization_Goal, self.Time_Series)
            self.update_output("KEY RESULTS:\n")
            PrintResults(self.instance, self.Results, self.update_output)
            
            end = time.time()
            elapsed = end - start
            elapsed_message = f'\n\nModel run complete (overall time: {round(elapsed, 0)} s, {round(elapsed / 60, 1)} m)\n'
            self.update_output(elapsed_message)

        
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        # Title label
        title_label = ttk.Label(self, text="Run the Model", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, pady=20, padx=10, sticky='w')

        # Run button
        run_button = ttk.Button(self, text="RUN", command=self.run_model)
        run_button.grid(row=0, column=0, pady=20, padx=10,sticky='e')

        # Text widget for output
        self.output_text = tk.Text(self)
        self.output_text.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

        # Start Date Entry for Plot
        ttk.Label(self, text="Start Date for Plot:").grid(row=3, column=0, pady=5, padx=10, sticky='w')
        self.start_date_entry = ttk.Entry(self)
        self.start_date_entry.insert(0, "01/01/2023 00:00:00")
        self.start_date_entry.grid(row=3, column=0, pady=5, padx=10, sticky='e')
        
        # Number of days to plot
        ttk.Label(self, text="Number of days to plot:").grid(row=4, column=0, pady=5, padx=10, sticky='w')
        self.plot_time_entry = ttk.Entry(self)
        self.plot_time_entry.insert(0, 3)
        self.plot_time_entry.grid(row=4, column=0, pady=5, padx=10, sticky='e')

        # Buttons for showing plots
        self.generate_plot_button = ttk.Button(self, text="Generate Plots", command=self.generate_plot)
        self.generate_plot_button.grid(row=5, column=0,  pady=10, padx=10, sticky='w')
        
        # Buttons for showing plots
        self.show_dispatch_plot_button = ttk.Button(self, text="Show Dispatch Plot", command=self.show_dispatch_plot)
        self.show_dispatch_plot_button.grid(row=6, column=0, pady=10, padx=10, sticky = 'w')

        self.size_plot_button = ttk.Button(self, text="Show Size Plot", command=self.show_size_plot)
        self.size_plot_button.grid(row=6, column=0, pady=10, padx=10, sticky = 'e')
        

