import glob

from Cython.Build import cythonize
from setuptools import find_packages, setup

setup(
    name="ooo",
    version="1.0.0",
    packages=find_packages(),
    ext_modules=cythonize(glob.glob("src/**/*.py", recursive=True)),
    zip_safe=False,
)
