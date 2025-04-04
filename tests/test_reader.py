import unittest
import numpy as np
from unittest.mock import MagicMock, patch

from datxpy.reader import HDF5Reader

class TestHDF5Reader(unittest.TestCase):

    @patch("h5py.File")
    def test_read(self, mock_h5py_file):

        mock_file = MagicMock()                  # Mock for file 
        mock_h5py_file.return_value = mock_file  # Mock for h5py.File function
        
        # Use __enter__ for allow the use of with statement
        # and create a simple dictionary as a mock return value
        # to simulate the structure of the HDF5 file
        mock_file.__enter__.return_value = {
            'Measurement' : {
                'Thickness' : {
                    'values' : np.random.rand(10, 10),
                    'unit' : 'mm'
                    }         
                }
            }

        reader = HDF5Reader("fake_path.datx")
        data = reader.read()

        self.assertIn("Measurement", data)
        self.assertIn("Thickness", data["Measurement"])
        self.assertIn("values", data["Measurement"]["Thickness"])
        self.assertIsInstance(data["Measurement"]["Thickness"]["values"], np.ndarray) 
        self.assertEqual(data["Measurement"]["Thickness"]["unit"], "mm")


    def test_void2dict(self):

        reader = HDF5Reader("fake_path.datx")
        dtype  = np.dtype([("field1", "i4"), ("field2", "f8")])
        data   = np.array([(1, 2.0), (3, 4.0)], dtype=dtype)
        
        result = reader.void2dict(data)
        
        self.assertEqual(len(result),         2)
        self.assertEqual(result[0]["field1"], 1)
        self.assertEqual(result[1]["field2"], 4.0)

    def test_decode_group_bytes(self):

        reader = HDF5Reader("fake_path.datx")
        result = reader.decode_group(b"hello")

        self.assertEqual(result, "hello")

    def test_decode_group_number(self):

        reader = HDF5Reader("fake_path.datx")
        result = reader.decode_group(np.array([42]))
        
        self.assertEqual(result, 42)

if __name__ == "__main__":
    unittest.main()
