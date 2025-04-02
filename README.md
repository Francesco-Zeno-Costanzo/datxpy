# datxpy
Simple code to read and display data files in .datx format

## HDF5Reader

reader.py contains a class to read and decode HDF5 (.datx) files, converting their contents into Python dictionaries.
This class allows programmatic access to HDF5 data, but the same operations 
can also be performed via a graphical user interface (GUI) by running gui.py

### Usage in code

```python
import numpy as np
import matplotlib.pyplot as plt

from reader import HDF5Reader
from utils import fill_nodata, remove_nodata  # Import utility functions

file_path = "c2701-spessore.datx"
reader = HDF5Reader(file_path)

# Display file structure
reader.show_struct()

# Read and extract measurement data
data = reader.read()
intensity = data['Measurement']['Intensity']
surface   = data['Measurement']['Thickness']

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
python3 gui.py
```