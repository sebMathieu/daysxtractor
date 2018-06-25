from setuptools import setup, find_packages

setup(name='daysxtractor',
      version='2.0.0',
      description='Extract a given number of representative days of a set of time series.',
      url='https://github.com/sebMathieu/daysxtractor',
      author='Sebastien Mathieu',
      packages=find_packages(),
      install_requires=['pyomo', 'xlrd', 'xlwt', 'python-dateutil'],
      zip_safe=False)
