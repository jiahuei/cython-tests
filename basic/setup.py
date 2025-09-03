import glob

from Cython.Build import cythonize
from setuptools import find_packages, setup

# Find all Python files in the mathlib package
python_files = glob.glob("octo/*.py")

setup(
    name="mathlib",
    version="1.0.0",
    packages=find_packages(),
    ext_modules=cythonize(python_files),
    zip_safe=False,
)
