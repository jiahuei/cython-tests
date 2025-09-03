import glob

from Cython.Build import cythonize
from setuptools import find_packages, setup

# Find all Python files in the octo package
python_files = glob.glob("src/**/*.py")

setup(
    name="octo",
    version="1.0.0",
    packages=find_packages(),
    ext_modules=cythonize(python_files),
    zip_safe=False,
)
