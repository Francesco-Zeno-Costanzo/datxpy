.. datxpy documentation master file, created by
   sphinx-quickstart on Thu Apr  3 13:49:59 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
datxpy documentation
====================


Welcome to the official documentation of **datxpy**, a software for read and display data files in .datx format.

**Documentation index:**

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   modules
   datxpy
   datxpy.reader
   datxpy.gui
   datxpy.utils

-----------------

**What is datxpy?**
----------------------------------
`datxpy` is a Python package designed to read and visualize files in .datx format with an intuitive graphical interface or importing in your code the class for raeading the file.

📌 **Main features**:

- 📊 **Data display**: Loading and displaying data in a 2D plot with a colormap for the third dimension.
- 🔧 **Analysis tools**: Remove a possible present baseline and save the visualized data in .txt or .csv format.
- 🖥 **User-friendly graphical interface** based on Tkinter.

-----------------

**How to get started?**
--------------------------------
To install the package, use:

.. code-block:: bash

   "to do"

Directly from the GitHub repository:

.. code-block:: bash

    git clone https://github.com/Francesco-Zeno-Costanzo/datxpy.git
    cd datxpy
    pip install -e .

To launch the graphical interface:

.. code-block:: bash

   datxpy-gui

-----------------


**Feedback**
-----------------
If you find a bug or have suggestions, open an issue at [GitHub](https://github.com/Francesco-Zeno-Costanzo/datxpy).

-----------------

**Index and search**
--------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

