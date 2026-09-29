
try:
    # check if fiona and rtree is installed
    import fiona
    import rtree
    from .geocoder_reverse_ne_fiona import Geocoder_Reverse_NE, Geocoder_Reverse_Exception
except ImportError as e:
    # if fiona and rtree are not installed, we will use the shapereader implementation
    from .geocoder_reverse_ne_pyshp import Geocoder_Reverse_NE, Geocoder_Reverse_Exception

# set __version__ from the package metadata
from importlib.metadata import version
__version__ = version("geocoder_reverse_natural_earth")
