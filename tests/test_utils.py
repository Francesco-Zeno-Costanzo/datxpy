import unittest
import numpy as np
from datxpy.utils import *

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        self.X, self.Y = np.meshgrid(np.arange(5), np.arange(5))
        self.Z = np.array([
            [1,   2, 3,      4, 5],
            [6,   7, 8,      9, 10],
            [11, 12, -999,  14, 15],
            [16, 17, 18,  -999, 20],
            [21, 22, 23,    24, 25]
        ])
        self.threshold = -999

    def test_fill_nodata(self):
        
        Z_filled = fill_nodata(self.X, self.Y, self.Z, self.threshold)

        self.assertFalse(np.any(Z_filled == self.threshold),
                        "There are still threshold values after interpolation.")
        
        self.assertFalse(np.any(np.isnan(Z_filled)),
                        "There are NaN values after interpolation.")
    
    def test_remove_nodata(self):
        Z_cleaned = remove_nodata(self.Z, self.threshold)
        
        self.assertTrue(np.all(np.isnan(Z_cleaned[2, 2])) and np.all(np.isnan(Z_cleaned[3, 3])),
                        "The threshold values ​​were not converted to NaN.")
    
    def test_remove_offset(self):
        
        params, Z_corrected = remove_offset(self.X, self.Y, self.Z)
        
        self.assertEqual(len(params), 3,
                        "The plan fit should return three parameters.")
        
        self.assertAlmostEqual(np.mean(Z_corrected), 0, delta=1e-6,
                               msg="The mean of the corrected Z should be about zero..")

if __name__ == '__main__':
    unittest.main()