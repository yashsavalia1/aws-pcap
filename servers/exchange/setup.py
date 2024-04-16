from distutils.core import setup, Extension

module = Extension('Nsleep', sources=["nanosleep.c"])
setup(
        name='NSleep_Package',
        version='0.01',
        description='Package for accessing the nanosleep function in the c library time.h',
        ext_modules=[module]
        )
