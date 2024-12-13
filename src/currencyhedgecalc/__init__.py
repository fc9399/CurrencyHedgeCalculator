# read version from installed package
from importlib.metadata import version
__version__ = version("currencyhedgecalc")

# __init__.py
from .currencyhedgecalc import CurrencyHedgeCalculator