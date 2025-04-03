# datxpy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Documentation Status](https://readthedocs.org/projects/datxpy/badge/?version=latest)](https://datxpy.readthedocs.io/en/latest/?badge=latest)

Simple code to read and display data files in .datx format

## Installation 
For now, the only way to install **datxpy** is by cloning the repository:

```bash
git clone https://github.com/Francesco-Zeno-Costanzo/datxpy.git
cd datxpy
pip install -r requirements.txt
pip install 
```

## HDF5Reader

reader.py contains a class to read and decode HDF5 (.datx) files, converting their contents into Python dictionaries.
This class allows programmatic access to HDF5 data, but the same operations 
can also be performed via a graphical user interface (GUI). 
The GUI also implements some possible operations to be done to possibly improve the quality of the data.

### Usage in code
It is possible to import only the module for reading the file into your code and then perform the analysis of the case you are interested in.
```python
import numpy as np
import matplotlib.pyplot as plt

from datxpy.reader import HDF5Reader
from datxpy.utils import fill_nodata, remove_nodata
# Import utility functions as these are normal operations
# that you might want to do (they are the same ones implemented in the GUI)

file_path = "---.datx"
reader = HDF5Reader(file_path)

# Display file structure
reader.show_struct()

# Read and extract measurement data
data = reader.read()
surface = data['Measurement']['Thickness']

# Convert nanometers to micrometers
z_vals  = surface['values'] * 1e-3
no_data = surface['attributes']['No Data'] * 1e-3

# Create the grid for plotting
x_grid, y_grid = np.meshgrid(np.arange(0, z_vals.shape[1]),
                             np.arange(0, z_vals.shape[0]))
x_grid = x_grid * surface['attributes']['X Converter']['Parameters'][1] * 1e6
y_grid = y_grid * surface['attributes']['Y Converter']['Parameters'][1] * 1e6

# Remove no-data values and plot initial data
z_vals = remove_nodata(z_vals, no_data)
plt.pcolormesh(x_grid, y_grid, z_vals, cmap='plasma')
plt.xlabel('x [μm]', fontsize=15)
plt.ylabel('y [μm]', fontsize=15)
cbar = plt.colorbar()
plt.show()

# Process data: fill missing values
z_vals = fill_nodata(x_grid, y_grid, z_vals, no_data)

# Plot final processed data
plt.pcolormesh(x_grid, y_grid, z_vals, cmap='plasma')
plt.xlabel('x [μm]', fontsize=15)
plt.ylabel('y [μm]', fontsize=15)
cbar = plt.colorbar()
plt.show()
```
## GUI usage
You only need to run:
```bash
datxpy-gui
```