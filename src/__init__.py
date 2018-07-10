#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .algorithm import tone_mapping as TMO

__version__ = '0.1'
__title__ = 'TMO4CT'
__summary__ = ('Distance-weighted local histogram equalization'
               ' based tone mapping for CT images.')
__uri__ = 'https://gitlab.com/dvolgyes/TMO4CT'
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

__all__ = ['__version__',
           '__title__',
           '__summary__',
           '__uri__',
           '__license__',
           '__author__',
           '__email__',
           '__doi__',
           '__description__',
           '__bibtex__',
           '__reference__']

tone_mapping = TMO
