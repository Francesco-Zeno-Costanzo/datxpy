Usage
=====

GUI Usage
---------

To launch the graphical user interface, simply run:

.. code-block:: bash

    datxpy-gui

This will open a window where you can select the .datx file you want to analyze.
The GUI provides a user-friendly interface to visualize the data and perform various operations, such as filling missing values, removing no-data values, and more.

HDF5Reader
----------

The `reader.py` module contains a class to read and decode HDF5 (.datx) files, converting their contents into Python dictionaries.
This class allows programmatic access to HDF5 data (the same operations can also be performed via a graphical user interface).
After importing the module, you can create an instance of the `HDF5Reader` class by passing the path to the .datx file as an argument.

.. code-block:: python

    from datxpy.reader import HDF5Reader

    file_path = "---.datx"
    reader = HDF5Reader(file_path)
    # Display file structure
    reader.show_struct()
    # Read and extract measurement data
    data = reader.read()
 
From now on 'data' is a normal dictionary, which contains all the information organized in other dictionaries and which you can explore
by accessing the elements that interest you most.

Usage in Code
^^^^^^^^^^^^^

For example we can write a script to read the data and plot it using matplotlib.

.. code-block:: python

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

