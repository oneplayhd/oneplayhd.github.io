__author__ = 'Eric Weast'
__copyright__ = "Copyright 2014, Eric Weast"
__license__ = "GPL v2"

try:
    import sys
    import xbmcvfs
    translate = xbmcvfs.translatePath
    lib = translate('special://home/addons/script.module.thethunder/lib/thunderlib/')
    sys.path.append(lib)
except:
    pass
from .exceptions import EncodingError
from .exceptions import DecodingError
from .decoder import decode
from .decoder import decode_from_file
from .encode import encode
