#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from contextlib import contextmanager, ContextDecorator
from gc import collect as garbage_collector
from contracts import contract, new_contract
import numpy as np


def eprint(*args, **kwargs):
    """
    Print messages to the standard error, instead of the standard out.
    >>> eprint("message")
    """
    print(*args, file=sys.stderr, **kwargs)


try:
    from numba import jit
except ImportError:
    eprint("""
  There is no NUMBA installed!
  The code use a pure python fallback.')
  Try: pip install numba')
  or visit: https://numba.pydata.org/ for details.""")

    def jit(x): return x

new_contract('path', os.path.exists)
new_contract('dir', os.path.isdir)
new_contract('filename', os.path.isfile)
new_contract('link', os.path.islink)
new_contract('dtype', lambda x: isinstance(x, np.dtype))


def ceil_int(data):
    """
    >>> ceil_int(3.5)
    4
    >>> ceil_int((3.5,4.1))
    (4, 5)
    """
    if type(data) in [list, tuple]:
        result = []
        for x in data:
            result.append(int(np.ceil(x)))
        return type(data)(result)
    return int(np.ceil(data))


class collect(ContextDecorator):
    """
    A decorator which performs garbage collection
    before and after the execution of the function.

    >>> if True:
    ...     @collect()
    ...     def test_function(x):
    ...         return x
    ...     test_function(123)
    123
    """

    def __enter__(self):
        garbage_collector()
        return self

    def __exit__(self, *exc):
        garbage_collector()
        return False


@jit
def rebin(a, out):
    I, J = a.shape
    X, Y = out.shape
    out.fill(0)
    for i in range(I):
        for j in range(J):
            U = float(i) * X / I
            V = float(j) * Y / J
            u = int(U)
            v = int(V)
            f1_ = (U-u)
            f2_ = (V-v)
            f1 = 1.0 - f1_
            f2 = 1.0 - f2_
            out[u, v] += f1*f2*a[i, j]

            if u+1 < X:
                out[u+1, v] += f1_*f2*a[i, j]
            if v+1 < Y:
                out[u, v+1] += f1*f2_*a[i, j]
            if (u+1 < X) and (v+1 < Y):
                out[u+1, v+1] += f1_*f2_*a[i, j]
    return out


@jit
def dither_FS(image, levels=None, dtype=np.uint):

    if levels is None:
        levels = image.max() + 1
    result = np.floor(image).astype(np.float)
    error = image - result
    w, h = image.shape
    A, B, C, D = 7./16, 3./16, 5./16, 1./16
    e = 0
    for i in range(w):
        for j in range(h):
            e = error[i][j]
            if e >= 1:
                result[i, j] += 1
                e -= 1.0
            if j+1 < h:
                error[i, j+1] += A*e
            if i+1 < w and j > 0:
                error[i+1, j-1] += B*e
            if i+1 < w:
                error[i+1, j] += C*e
            if i+1 < w and j+1 < h:
                error[i+1, j+1] += D*e
    return np.clip(result.reshape(image.shape), 0, levels-1).astype(dtype)


@collect()
def dither_basic(image, levels=None, dtype=np.uint):
    if levels is None:
        levels = int(image.max())+1
    result = np.floor(image).ravel()
    error = np.diff(np.floor(np.cumsum(image.ravel() - result))
                    ).astype(np.bool).astype(np.float32)
    result[1:] += error
    return np.clip(result.reshape(image.shape), 0, levels-1).astype(dtype)


@collect()
@contract(image='array[NxM](float32)|array[NxM](float64)',
          levels='None|int,>1')
def dither(image, levels=None, method='floyd', dtype=np.uint8):
    """
    >>> dither(np.arange(16).reshape(4,4)/4.0,levels=4)
    array([[0, 0, 0, 1],
           [1, 1, 1, 2],
           [2, 2, 3, 2],
           [3, 3, 3, 3]], dtype=uint8)
    >>> dither(np.arange(16).reshape(4,4)/4.0,levels=4, method='basic')
    array([[0, 0, 0, 1],
           [1, 1, 2, 2],
           [2, 2, 2, 3],
           [3, 3, 3, 3]], dtype=uint8)

    """
    if method in ['floyd', 'fs', 'floyd-steinberg']:
        # Floyd steinberg dithering
        return dither_FS(image, levels, dtype)
    # basic dithering
    return dither_basic(image, levels, dtype)


@contextmanager
@contract(f='file|filename|str')
def delete_file_ctx(f):
    """
    Delete a given file after the context.
    For temporary files, you should rather consider to use tmpfile_ctx.

    >>> if True:
    ...     import tempfile
    ...     fn = tempfile.mkstemp()[1]
    ...     with delete_file_ctx(fn):
    ...         print(os.path.exists(fn))
    ...     print(os.path.exists(fn))
    True
    False

    >>> if True:
    ...     import tempfile
    ...     fn = tempfile.mkstemp()[1]
    ...     f = open(fn)
    ...     with delete_file_ctx(f):
    ...         print(os.path.exists(f.name))
    ...     print(os.path.exists(f.name))
    True
    False

    >>> if True:
    ...     import tempfile
    ...     fn = tempfile.mkstemp()[1]
    ...     f = open(fn)
    ...     with delete_file_ctx(f):
    ...         f.close()
    ...         print(os.path.exists(f.name))
    ...     print(os.path.exists(f.name))
    True
    False
    """

    yield
    if hasattr(f, 'read'):
        name = f.name
        if not f.closed:
            f.close()
        os.remove(name)
    else:
        os.remove(f)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
