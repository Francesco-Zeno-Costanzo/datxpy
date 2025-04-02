'''
Some useful functions
'''
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import griddata


def fill_nodata(X, Y, Z, thr):
    '''
    Fill missing or invalid data from a 2D grid by replacing
    specified threshold values with NaN and interpolating missing
    values using nearest-neighbor interpolation via scipy.interpolate.griddata

    Parameters
    ----------
    X, Y : 2darray
        Independent variables representing the grid coordinates.
    Z : 2darray
        Dependent variable representing the height values, where Z = f(X, Y).
    thr : float
        Threshold value representing missing data in Z.
        All occurrences of this value  will be replaced
        with NaN and interpolated.

    Returns
    -------
    Z : 2darray
        The modified Z array with missing values interpolated using the nearest-neighbor method.
    '''

    Z = Z.astype(float)
    Z[Z == thr] = np.nan

    mask = ~np.isnan(Z)

    points = np.column_stack((X[mask], Y[mask]))
    values = Z[mask]
    Z      = griddata(points, values, (X, Y), method='nearest')
    
    return Z


def remove_nodata(Z, thr):
    '''
    Remove invalid data from a 2D grid by replacing
    specified threshold values with NaN.

    Parameters
    ----------
    Z : 2darray
        Dependent variable representing the height values
    thr : float
        Threshold value representing invalid data in Z.
        All occurrences of this value  will be replaced
        with NaN.
    
    Returns
    -------
    z : 2darray
        The modified Z array.
    '''
    z = np.copy(Z)
    z = z.astype(float)
    z[z >= thr] = np.nan

    return z

def plane(xy, a, b, c):
    '''
    Equation of a plane: z = ax + by + c
    '''
    x, y = xy
    return a * x + b * y + c


def remove_offset(X, Y, Z):
    '''
    Removes the offset from a Z heightmap by eliminating the planar tilt.

    Parameters
    ----------
    X, Y : 2darray
        Independent variables representing the grid coordinates.
    Z : 2darray
        Dependent variable representing the height values, where Z = f(X, Y).

    
    Returns
    -------
    params : 1darray
        optimal parameters for the plane
    z_data : 2darray
        Array with the same shape of Z.
        Data with the fitted plane removed to remove the baseline
    '''
    
    ny, nx = Z.shape

    # Flatten data for fit
    x_data = X.ravel()
    y_data = Y.ravel()
    z_data = np.copy(Z.ravel())    

    # Fit with plane function
    params, _ = curve_fit(plane, (x_data, y_data), z_data)

    z_data = z_data - plane((x_data, y_data), *params)

    return params, z_data.reshape(ny, nx)
