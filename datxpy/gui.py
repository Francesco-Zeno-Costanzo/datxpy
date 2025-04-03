import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from datxpy.reader import HDF5Reader
from datxpy.utils import *

class HDF5_GUI:
    '''
    Class that manages the graphical interface for displaying data.
    The code is designed to load a single .datx file at a time and make
    a single 2d graph at a time of one of the quantities present in the
    measurements entry. There are operations that can be performed such
    as filling in empty values through an interpolation or eliminating
    a trend present in the data by removing a baseline by fitting a plane.
    Finally, it is possible to save the created graph.
    '''
    def __init__(self, root):
        '''
        Class constructor, here all the necessary buttons are created

        Parameters
        ----------
        root : tkinter.Tk object
            main window
        '''
        # Main window
        self.root = root
        self.root.title("HDF5 Data Viewer")
        self.root.geometry("1200x800")  

        # Left part of the main window here there will be the buttons and the info of the uploaded file
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        # Right part of the main window to show the plot 
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button for uploading file
        self.load_button = tk.Button(self.left_frame, text="Upload File .datx", command=self.load_file)
        self.load_button.pack(pady=5, fill=tk.X)

        self.file_label = tk.Label(self.left_frame, text="No files loaded")
        self.file_label.pack(pady=5)

        # Window section to see file info        
        self.tree = ttk.Treeview(self.left_frame, columns=("Type",), show="tree headings", height=10)
        self.tree.heading("#0", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.pack(pady=5, fill=tk.BOTH, expand=True)

        self.data_label = tk.Label(self.left_frame, text="Data in Measurement")
        self.data_label.pack(pady=5)

        # Window section for possible data to plot
        self.var_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, height=5)
        self.var_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        # Buttons
        self.plot_button = tk.Button(self.left_frame, text="Plot Data",
                                     command=self.plot_raw_data).pack(pady=5, fill=tk.X)
        
        self.fill_no_data_button = tk.Button(self.left_frame, text="Fill No Data",
                                             command=self.fill_no_data_func).pack(pady=5, fill=tk.X)
        
        self.modi_button = tk.Button(self.left_frame, text="Remove Baseline",
                                     command=self.modify_data).pack(pady=5, fill=tk.X)        
        
        self.save_button = tk.Button(self.left_frame, text="Save Plot",
                                     command=self.save_plot).pack(pady=5, fill=tk.X)

        self.save_button = tk.Button(self.left_frame, text="Save current data",
                                     command=self.save_data).pack(pady=5, fill=tk.X)
        
        # Section of the window for the plot 
        self.figure, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Useful quantities
        self.reader   = None
        self.data     = None
        self.colorbar = None
        self.last_dat = []


    def load_file(self):
        ''' Load datx file and show structure
        '''
        filepath = filedialog.askopenfilename(filetypes=[("HDF5 files", "*.datx")])
        if not filepath:
            return

        try:
            self.reader = HDF5Reader(filepath)
            self.data = self.reader.read()
            self.file_label.config(text=f"File uploaded: {filepath.split('/')[-1]}")
            self.tree.delete(*self.tree.get_children())
            self.var_listbox.delete(0, tk.END)

            self.populate_tree(self.tree, self.data)
            
            if "Measurement" in self.data:
                for var, val in self.data["Measurement"].items():
                    if "values" in val:
                        self.var_listbox.insert(tk.END, var)

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def populate_tree(self, parent, data, parent_id=""):
        '''
        Populates the HDF5 structure in the treeview, showing type and value if scalar

        This function recursively inserts items into a treeview widget, representing 
        the hierarchical structure of an HDF5 file or a nested dictionary. If an item 
        is a dictionary, it is treated as a group and further expanded. If it is a 
        scalar or an array, its type and value (if applicable) are displayed.

        Parameters
        ----------
        parent : ttk.Treeview
            The treeview widget where the hierarchical data will be inserted.
        data : dict
            A nested dictionary representing the HDF5 structure to be visualized.
        parent_id : str, optional, default ""
            The ID of the parent item in the treeview. This is used to maintain 
            the hierarchical structure.

        Notes
        -----
        - Groups (i.e., dictionary keys with nested dictionaries) are labeled as "Group".
        - Scalar values are displayed with their actual value.
        - NumPy arrays are labeled as "array" without displaying their content.
        '''
        for key, value in data.items():
            
            if isinstance(value, dict):
                # Insert group into the ttk.Treeview
                item_id = parent.insert(parent_id, "end", text=key, values=("Groups", ""))
                self.populate_tree(parent, value, item_id)
            
            else:
                # Determine data type
                dtype     = "array" if isinstance(value, np.ndarray) else "number"
                value_str = str(value) if dtype == "number" else "array"
                
                # Insert scalar or array into the ttk.Treeview
                parent.insert(parent_id, "end", text=key, values=(value_str))


    def plot_data(self, op):
        '''
        Function to plot data

        Parameters
        ----------
        op : str, {"raw", "fill", "baseline"}
            Operation to apply to the data before plotting it.

            The options are:

            - **"raw"**: The data is plotted as read from the file.
            - **"fill"**: The NaN values are filled using nearest neighbor interpolation.
            - **"baseline"**: The data is fitted with a plane, which is then removed.
        '''

        if self.reader is None or self.data is None:
            messagebox.showerror("Error", "No files loaded")
            return
        
        try :
            idx = self.var_listbox.curselection()
            var = self.var_listbox.get(idx[0])

        except :
            messagebox.showerror("Error", "Select one quantity")
            return

        # Manages window cleaning
        if hasattr(self, "colorbar") and self.colorbar is not None:
            try:
                self.colorbar.remove()
            except AttributeError:
                pass

            self.colorbar = None  
            self.figure.canvas.draw_idle() 
        
        self.ax.cla()
       
        z_vals  = np.copy(self.data["Measurement"][var]['values'])
        no_data = self.data["Measurement"][var]['attributes']['No Data']

        z_unit = self.data["Measurement"][var]['attributes']['Unit']
        if z_unit == "NanoMeters":
        # From nanometer to micrometer
            z_vals  *= 1e-3  
            no_data *= 1e-3
            z_unit   = "μm"
        
        x_grid, y_grid = np.meshgrid(np.arange(0, z_vals.shape[1]),
                                     np.arange(0, z_vals.shape[0]))
        
        # From arbitrary units in micrometers
        x_grid = x_grid * self.data["Measurement"][var]['attributes']['X Converter']['Parameters'][1] * 1e6
        y_grid = y_grid * self.data["Measurement"][var]['attributes']['Y Converter']['Parameters'][1] * 1e6

        # Operation to do 
        if op == 'raw':
            z = remove_nodata(z_vals, no_data)

        if op == 'fill':
            z = fill_nodata(x_grid, y_grid, z_vals, no_data)

        if op == 'baseline':
            z    = fill_nodata(x_grid, y_grid, z_vals, no_data)
            _, z = remove_offset(x_grid, y_grid, z)
        
        # Store current selected data
        self.last_dat.append(x_grid)
        self.last_dat.append(y_grid)
        self.last_dat.append(z)

        # Plot
        im = self.ax.pcolormesh(x_grid, y_grid, z, cmap='plasma')
        
        # Color bar and plot setting
        z_min = np.nanmin(z)
        z_max = np.nanmax(z)
        tickz = np.linspace(z_min, z_max, num=9, endpoint=True)
        tickl = [f"{v:.2f}" for v in tickz] 
        tickl[ 0] = f'{tickl[ 0]} {z_unit}'
        tickl[-1] = f'{tickl[-1]} {z_unit}'
        
        self.colorbar = self.figure.colorbar(im, ax=self.ax)
        self.colorbar.set_ticks(tickz)
        self.colorbar.set_ticklabels(tickl)
        self.ax.set_aspect('equal')
        plt.xlabel('x [μm]', fontsize=15)
        plt.ylabel('y [μm]', fontsize=15)

        self.canvas.draw()

    
    def plot_raw_data(self):
        ''' 
        Function to plot raw data from file.
        Call plot_data with op="raw"
        '''
        self.plot_data('raw')

   
    def fill_no_data_func(self):
        ''' 
        Fill the no data values and update the plot.
        Call plot_data with op="fill"
        '''
        self.plot_data('fill')

    
    def modify_data(self):
        ''' 
        Remove baseline and update plot.
        Call plot_data with op="baseline"
        '''
        self.plot_data('baseline')
    

    def save_plot(self):
        '''
        Function for saving the final plot
        '''
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG files", "*.png"),
                                                       ("JPEG files", "*.jpg"),
                                                       ("All Files", "*.*")])
        if not filepath:
            return  
       
        try:
            self.figure.savefig(filepath, bbox_inches='tight')
            messagebox.showinfo("Saving completed", f"Plot saved in:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Unable to save the plot: {e}")


    def save_data(self):
        '''
        Function for saving the current selected data in csv ot txt file
        '''

        if self.reader is None or self.data is None:
            messagebox.showerror("Error", "No files loaded")
            return
        
        if not self.last_dat:
            msg_0 = 'To save the file you must first make the plot,'
            msg_1 = 'the data will be saved as they are displayed'
            messagebox.showerror("Error", f"{msg_0} {msg_1}")
            return
        
        idx = self.var_listbox.curselection()
        var = self.var_listbox.get(idx)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), 
                       ("csv files","*.csv")],
            initialfile=f"{var}.txt",
        )

        if not file_path:
            return
        
        try:
            
            with open(file_path, "w") as f:
                for matrix in self.last_dat:
                    np.savetxt(f, matrix)
                    f.write("\n")

            messagebox.showinfo("Saving completed", f"Data saved in:\n{file_path}")
            del self.last_dat[:]

        except Exception as e:
            messagebox.showerror("Error", f"Unable to save the plot: {e}")

def main():
    '''
    Entry point. Run the GUI
    '''
    root = tk.Tk()
    HDF5_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
