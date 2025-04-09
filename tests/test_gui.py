import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import numpy as np
from datxpy.gui import HDF5_GUI

class TestHDF5GUI(unittest.TestCase):

    def setUp(self):
        ''' Setup the GUI for testing
        '''
        self.root = tk.Tk()
        self.app  = HDF5_GUI(self.root)

    def tearDown(self):
        ''' Destroy the GUI after testing
        '''
        self.root.destroy()

    @patch("datxpy.gui.filedialog.askopenfilename")
    @patch("datxpy.gui.HDF5Reader")
    def test_load_file_success(self, mock_reader_class, mock_askopenfilename):
        ''' Test loading a file successfully
        '''
        # Simulate file selection
        mock_askopenfilename.return_value = "fake.datx"

        # Simulate the reader class and its read method
        mock_reader = MagicMock()
        mock_reader.read.return_value = {
            "Measurement": {
                "Thickness": {
                    "values": np.ones((2, 2)),
                    "attributes": {
                        "No Data": 0.0,
                        "Unit": "NanoMeters",
                        "X Converter": {"Parameters": [0, 1e-6]},
                        "Y Converter": {"Parameters": [0, 1e-6]},
                    },
                }
            }
        }
        mock_reader_class.return_value = mock_reader

        # Call the method and check that no exceptions are raised
        self.app.load_file()

        # Check that the file was loaded and the reader was created
        self.assertEqual(self.app.reader, mock_reader)
        self.assertIn("Measurement", self.app.data)

    def test_plot_data_no_file(self):
        ''' Test plotting data without loading a file
        '''
        with patch("datxpy.gui.messagebox.showerror") as mock_msg:
            self.app.plot_data("raw")
            mock_msg.assert_called_once_with("Error", "No files loaded")

    def test_save_data_without_plot(self):
        ''' Test saving data without plotting
        '''
        self.app.reader = MagicMock()
        self.app.data = {"Measurement": {}}
        self.app.last_dat = []

        with patch("datxpy.gui.messagebox.showerror") as mock_msg:
            self.app.save_data()
            self.assertIn("must first make the plot", mock_msg.call_args[0][1])

    def test_plot_data_no_selection(self):
        ''' Test plotting data without selecting a quantity
        '''
        self.app.reader = MagicMock()
        self.app.data = {
            "Measurement": {
                "Var": {
                    "values": np.array([[1, 2], [3, 4]]),
                        "attributes": {"No Data": -999,
                            "Unit": "NanoMeters",
                            "X Converter": {"Parameters": [0, 1e-6]},
                            "Y Converter": {"Parameters": [0, 1e-6]}
                        }
                    }
                }
            }

        with patch("datxpy.gui.messagebox.showerror") as mock_msg:
            self.app.plot_data("raw")
            mock_msg.assert_called_once_with("Error", "Select one quantity")

if __name__ == "__main__":
    unittest.main()
