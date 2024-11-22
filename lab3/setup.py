from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

# Define the extension module
extensions = [
    Extension(
        "conjugate_gradient",                  # Module name
        ["conjugate_gradient.pyx"],           # Source file
        include_dirs=[numpy.get_include()],   # Include NumPy headers
        extra_compile_args=["-fopenmp", "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"],  # Enable OpenMP and suppress deprecated API warning
        extra_link_args=["-fopenmp"]          # Link with OpenMP
    )
]

# Setup script
setup(
    name="Conjugate Gradient Solver with OpenMP",
    ext_modules=cythonize(extensions),
    zip_safe=False,
)

