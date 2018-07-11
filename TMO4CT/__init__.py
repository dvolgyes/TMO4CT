#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .algorithm import tone_mapping
from .tools import eprint, dither

__version__ = '0.6'
__title__ = 'TMO4CT'
__summary__ = ('Distance-weighted local histogram equalization'
               ' based tone mapping for CT images.')
__uri__ = 'https://github.com/dvolgyes/TMO4CT'
__license__ = 'AGPL v3'
__author__ = 'David Völgyes'  # Author of the code. The article has co-authors.
__email__ = 'david.volgyes@ieee.org'
__doi__ = 'unknown'
__description__ = """
This algorithm is a tone mapping / dynamic range reduction algorithm
mainly for CT images, but it should work with regular (color) photos too.
"""

__bibtex__ = (
    """Unpublished at this moment.
}"""
)
__reference__ = (
    """Unpublished."""
    + __version__
    + """).
Zenodo. https://doi.org/"""
    + __doi__
)

tone_mapping = tone_mapping
TMO = tone_mapping
eprint = eprint
dither = dither
