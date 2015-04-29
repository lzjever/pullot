__version__ = '0.0.01'

import logging
try:
    # not available in python 2.6
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Add NullHandler to prevent logging warnings
logging.getLogger(__name__).addHandler(NullHandler())

from pullot.clients import SelectClient
from pullot.servers import SelectServer
from pullot.framebuffer import FrameBuffer
