#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .algorithm import tone_mapping
from .tools import eprint, dither

__version__ = '1.0.1'
__title__ = 'TMO4CT'
__summary__ = ('Distance-weighted local histogram equalization'
               ' based tone mapping for CT images.')
__uri__ = 'https://github.com/dvolgyes/TMO4CT'
__license__ = 'AGPL v3'
__author__ = 'David Völgyes'  # Author of the source code. The article has co-authors.
__email__ = 'david.volgyes@ieee.org'
__doi__ = '10.5281/zenodo.1319084'  # Concept DOI, always redirects to the latest version.
__description__ = """
This algorithm is a tone mapping / dynamic range reduction algorithm
mainly for CT images, but it should work with regular (color) photos too.
"""

__bibtex__ = ("""
@misc{david_volgyes_2018_1319084,
  author       = {David Völgyes},
  title        = {{A Weighted Histogram-Based Tone Mapping Algorithm for CT Images - source code}},
  month        = jul,
  year         = 2018,
  doi          = {""" + __doi__ + """},
  url          = {https://doi.org/""" + __doi__ + """}
}
""")

__reference__ = (
    """David Völgyes. (2018, July 22). A Weighted Histogram-Based Tone Mapping Algorithm for CT Images - source code (Version v"""
    + __version__
    + """).
Zenodo. https://doi.org/"""
    + __doi__)

tone_mapping = tone_mapping
TMO = tone_mapping
eprint = eprint
dither = dither
