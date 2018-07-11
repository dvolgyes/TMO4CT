Tone mapping for CT images
==========================

Travis:[![Build Status](https://travis-ci.org/dvolgyes/TMO4CT.svg?branch=master)](https://travis-ci.org/dvolgyes/TMO4CT)
Coveralls:[![Coverage Status](https://coveralls.io/repos/github/dvolgyes/TMO4CT/badge.svg?branch=master)](https://coveralls.io/github/dvolgyes/TMO4CT?branch=master)
Codecov:[![codecov](https://codecov.io/gh/dvolgyes/TMO4CT/branch/master/graph/badge.svg)](https://codecov.io/gh/dvolgyes/TMO4CT)

[![pyversion](https://img.shields.io/pypi/pyversions/TMO4CT.svg)](https://pypi.org/project/TMO4CT/)
[![PyPI - License](https://img.shields.io/pypi/l/TMO4CT.svg)](https://github.com/dvolgyes/TMO4CT/raw/master/LICENSE.txt)

The primary aim was to develop a simple and effective tone
mapping for CT images. The exact details are published
in this article: UNDER REVIEW (will be updated if the paper is accepted)

The code is implemented in Python3, and requires Python3.5 or newer.
For higher execution speed, Numba is used. However, sometimes Numba
can be quite difficult to install, therefore, it is not a strict requirement,
and the code is able to run without Numba too, but with a significantly lower speed.


Installation
------------

The code could be installed directly from Github:
```
pip install git+https://github.com/dvolgyes/TMO4CT
```
or cloning the directory, or installed from PyPI:
```
pip install TMO4CT
```

The code and the paper about it  are currently under review.
PyPI is a bit strict about publishing the same version only once.
Until the paper is not accepted, the version number is smaller than 1.0,
and the code is not deposited elsewhere than PyPI, github (and the journal).
After publication, the version will be bumped to 1.0, and the code
will be deposited at <https://zenodo.org>.

Usage
-----

Aftern installation, the command line options can be queried:
```
TMO4CT_cli.py -h
```

The code could be used as a library too.

Examples
--------

Examples are presented in the 'examples' directory.
The code is able to process color images, however,
it only works on the lightness/brightness/luminosity/etc.
channel, and leaves the colors intact. The reason originates
in the scope. The primary aim was to enhance CT visualization.
There are many tone mapping operators for color photography,
and some of them takes color appearance very seriously,
producing nice tone mapped HDR images. CTs are grayscale images,
and different from regular photos. This algorithm is
not meant to replace regular tone mapping operators,
but to give an alternative for CT images.

Anyway, regular photos are usually more understandable for
human beings than CT images, and it is a great way to demonstrate
the advantages and pitfalls. For instance, the small, hidden details
are much more visible in the tone mapped version, but image noise, hidden
staircasing could be highlighted if the enhancement is too strong.

  Original                                                                                              |  Tone mapped
:------------------------------------------------------------------------------------------------------:|:-------------------------:
<img src="https://github.com/dvolgyes/TMO4CT/raw/master/examples/ship1k.png" width="376" height="376">  |  <img src="https://github.com/dvolgyes/TMO4CT/raw/master/examples/ship1k_tone_mapped.png" width="376" height="376">



Remarks
-------

The code expects 16bit tiff or png files,
but most CT files are stored in DICOM. DICOM conversion
is a but challenging, but there is a convenient tool
for this very task: [dcm2hdr](https://github.com/dvolgyes/dcm2hdr).

It is simple:
```
dcm2hdr.py INPUT_FILE OUTPUT_FILE
```
For more details, visit dcm2hdr's website: <https://github.com/dvolgyes/dcm2hdr>

Issues
------
If you have any issue to report, please use Github's issue tracker.
