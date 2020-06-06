from distutils.core import setup
from distutils.extension import Extension

extensions  = [Extension("kalman_filter", ["_pythonExtension.c", "kalman_filter.cpp"])]

setup(name = "kalman_filter",
      version='1.0',
      ext_modules=extensions
      )