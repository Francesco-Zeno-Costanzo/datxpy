'''
Class for reading and decoding HDF5 files (.datx)    
'''
import h5py
import numpy as np


class HDF5Reader:
    '''
    A class to read and decode HDF5 (.datx) files,
    converting their contents into Python dictionaries.

    This class allows programmatic access to HDF5 data, but the same operations 
    can also be performed via a graphical user interface (GUI) by running gui.py

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from utils import fill_nodata, remove_nodata  # Import utility functions

    >>> file_path = "c2701-spessore.datx"
    >>> reader = HDF5Reader(file_path)

    # Display file structure
    >>> reader.show_struct()

    # Read and extract measurement data
    >>> data = reader.read()
    >>> surface = data['Measurement']['Thickness']

    # Convert nanometers to micrometers
    >>> z_vals  = surface['values'] * 1e-3
    >>> no_data = surface['attributes']['No Data'] * 1e-3

    # Create the grid for plotting
    >>> x_grid, y_grid = np.meshgrid(np.arange(0, z_vals.shape[1]),
    ...                              np.arange(0, z_vals.shape[0]))
    >>> x_grid = x_grid * surface['attributes']['X Converter']['Parameters'][1] * 1e6
    >>> y_grid = y_grid * surface['attributes']['Y Converter']['Parameters'][1] * 1e6

    # Remove no-data values and plot initial data
    >>> z_vals = remove_nodata(z_vals, no_data)
    >>> plt.pcolormesh(x_grid, y_grid, z_vals, cmap='plasma')
    >>> plt.xlabel('x [μm]', fontsize=15)
    >>> plt.ylabel('y [μm]', fontsize=15)
    >>> cbar = plt.colorbar()
    >>> plt.show()

    # Process data: fill missing values
    >>> z_vals = fill_nodata(x_grid, y_grid, z_vals, no_data)

    # Plot final processed data
    >>> plt.pcolormesh(x_grid, y_grid, z_vals, cmap='plasma')
    >>> plt.xlabel('x [μm]', fontsize=15)
    >>> plt.ylabel('y [μm]', fontsize=15)
    >>> cbar = plt.colorbar()
    >>> plt.show()
    '''

    def __init__(self, file_path):
        '''
        Initialize the HDF5Reader with a file path.

        Parameters
        ----------
        file_path : str
            The path to the HDF5 file.
        '''
        self.file_path = file_path
        self.data      = None

    def hdf5_structure(self, g, indent=0):
        ''' 
        Recursive function to explore the HDF5 file structure
        
        Parameters
        ----------
        g : h5py.Group
            The current group to explore.
        indent : int, optional, default 0
            Tabulation for structure visualizzation.
        '''
        for key in g.keys():
            item = g[key]
            if isinstance(item, h5py.Group):
                print(" " * indent + f"[Group] {key}")
                self.hdf5_structure(item, indent + 4)
            elif isinstance(item, h5py.Dataset):
                print(" " * indent + f"[Dataset] {key} - Shape: {item.shape}, Dtype: {item.dtype}")


    def convert(self, g):
        '''
        Function that convert a h5py.Group object into a dictionary

        Parameters
        ----------
        g : h5py.Group
            The group to convert
        ''' 
        return {k: self.decode_group(v) for k, v in zip(g.keys(), g.values())}


    def void2dict(self, obj):
        '''
        Converts a NumPy structured array into a list of dictionaries.

        Parameters
        ----------
        obj : np.void
            The structured array to convert.

        Returns
        -------
        list of dict
            Each dictionary represents a record in the structured array, 
            with field names as keys and corresponding values.
        '''
        return [dict(zip(obj.dtype.names, self.decode_group(record))) for record in obj]


    def decode_group(self, g):
        '''
        Recursively decodes an HDF5 group, dataset, or attribute into a Python dictionary,
        handling different data types such as numpy arrays, lists, and byte strings.
        
        Parameters:
        g : h5py.Group, h5py.Dataset, h5py.AttributeManager, np.ndarray, bytes, list, tuple
            The HDF5 group, dataset, attribute, or other data structure to decode.

        Returns
        -------
        dict, list, tuple, str, or number
            - HDF5 groups are converted into nested dictionaries.
            - Datasets are stored as dictionaries with `values` and `attributes`.
            - Structured NumPy arrays become lists of dictionaries.
            - Byte strings are decoded into normal Python strings.
            - Lists and tuples with a single element are returned as the element itself.
        '''
        if isinstance(g, h5py.Group):
            # Convert the group to a dictionary
            data = self.convert(g)
            # If the group has attributes, decode them and store them under 'attributes'
            if len(g.attrs):
                data['attributes'] = self.decode_group(g.attrs)
            return data
        
        elif isinstance(g, h5py.AttributeManager):
            # Convert HDF5 attributes to a Python-compatible format
            return self.convert(g)
        
        elif isinstance(g, h5py.Dataset):
            # Convert an HDF5 dataset into a dictionary with attributes
            data = {'attributes': self.decode_group(g.attrs)}
            try:
                data['values'] = g[()]
            except Exception as e:
                # If an error occurs while accessing dataset values, ignore it
                # This means the dataset is empty
                pass
            return data
        
        elif isinstance(g, np.ndarray):
            # If it's a single numerical value stored in an array, return the scalar
            if np.issubdtype(g.dtype, np.number) and g.shape == (1,):
                return g[0]
            
            # If it's an object array, decode each element recursively
            elif g.dtype == 'object':
                return self.decode_group([self.decode_group(x) for x in g])
            
            # If it's a structured numpy array, convert it to a dictionary
            elif np.issubdtype(g.dtype, np.void):
                return self.decode_group(self.void2dict(g))
            else:
                return g
        
        elif isinstance(g, np.void):
            # If it's a void type (structured data), decode recursively
            return self.decode_group([self.decode_group(x) for x in g])
        
        elif isinstance(g, bytes):
            # Decode byte strings into normal Python strings
            return g.decode()
        
        elif isinstance(g, list) or isinstance(g, tuple):
            # If it's a list or tuple with a single element, return that element directly
            return g[0] if len(g) == 1 else g
        else:
            # Return the value as is if it doesn't match any known type
            return g

  
    def read(self):
        '''
        Read the .datx file nd decodes its contents.

        Return
        ------
        dict
            A dictionary containing the structured representation of the file.

        Notes
        -----
        - This method updates `self.data` with the file contents.
        - If the file is invalid or not found, an exception will be raised.
        '''
        with h5py.File(self.file_path, "r") as f:
            self.data = self.decode_group(f)

            return self.data


    def show_struct(self):
        '''
        Function for print the structure of the file
        '''
        with h5py.File(self.file_path, "r") as f:
            print("Structure of the file:")
            self.hdf5_structure(f)

