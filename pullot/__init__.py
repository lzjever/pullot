# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright (c) 2015 Percy Li
# See LICENSE for details.


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

from pullot.framebuffer import FrameBuffer , TSFrameBuffer
from pullot.clients import SelectClient
from pullot.servers import SelectServer
