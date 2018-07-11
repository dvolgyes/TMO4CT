#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from src import (__description__, __version__, __author__,
                 __email__, __summary__, __license__)


requirements = ['pycontracts', 'scipy', 'numpy', 'imageio',
                'tifffile', 'dcm2hdr', 'scikit-image', 'python-magic']

setup_requirements = []

test_requirements = []

setup(
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description=__summary__,
    install_requires=requirements,
    license=__license__,
    long_description=__description__,
    include_package_data=True,
    keywords=['tonemapping', 'CT'],
    name='tonemapping for CT',
    packages=find_packages(include=['src']),
    scripts=['src/TMO4CT.py'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dvolgyes/TMO4CT',
    version=__version__,
    zip_safe=False,
)