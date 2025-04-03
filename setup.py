from setuptools import setup, find_packages

setup(
    name="datxpy",
    version="0.1.0",
    author="Francesco Zeno Costanzo",
    author_email="zenofrancesco99@gmail.com",
    description="A package for reading and displaying data contained in files with the extension (*.datx)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Francesco-Zeno-Costanzo/datxpy",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "h5py",
        "scipy"
    ],
    entry_points={
        "console_scripts": [
            "datxpy-gui=datxpy.gui:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)

