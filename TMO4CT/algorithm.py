#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys
from gc import collect as garbage_collector
from scipy.interpolate import RegularGridInterpolator
from functools import partial

# try:
from .tools import rebin, ceil_int, eprint
# except ImportError:
#    from .tools import rebin, ceil_int, eprint


def crop(array, width, height):
    return array[width:-width, height:-height]


def distance_p(x, y, p):
    return np.power(np.abs(x)**p + np.abs(y)**p, 1./p)


def distance_eucledian(x, y):
    return np.sqrt(x**2+y**2)


def distance_manhattan(x, y):
    return np.abs(x) + np.abs(y)


def distance_maximum(x, y):
    return np.maximum(np.abs(x), np.abs(y))


def mask_generation(mask,
                    CENTER,
                    exps,
                    factors,
                    R_cutoff=np.inf,
                    distance=distance_eucledian):
    # power-law based mask
    # center pixel should get CENTER value, but it does not cause
    # any signicant change. It could be 1, 2pi, etc.
    # cut-off: only for demonstration purposes: if it is not inf,
    # it will generate halos

    mask.fill(0.0)
    w, h = mask.shape
    # xoffset
    if w % 2 == 0:
        xoffset = 0.5
    else:
        xoffset = 0.
    if h % 2 == 0:
        yoffset = 0.5
    else:
        yoffset = 0.

    wmin = w // 2
    hmin = h // 2
    wmax = w - wmin
    hmax = h - hmin

    for (exp, factor) in zip(exps, factors):
        for x in range(-wmin, wmax):
            for y in range(-hmin, hmax):
                i, j = x + wmin, y+hmin
                d = distance(x+xoffset, y+yoffset)
                if d >= R_cutoff:
                    mask[i, j] = 0
                else:
                    if exp is not None and (exp != 0):
                        if x != 0 or y != 0:
                            mask[i, j] += factor * np.power(d, -exp)
                        else:
                            mask[i, j] = CENTER
                    else:
                        mask[i, j] = 1.0
    mask /= mask.sum()
    return mask


def conv(layer, mask, fmask=None):
    # Convolution with some caching
    # the mask is always the same, so it is enough to calculate it once
    # this is approximately 33% of the functions job, so
    # it yields around 50% speedup in FFT.
    w, h = layer.shape
    W, H = layer.shape
    w = w//2
    h = h//2
    layer = np.pad(layer, ((w, w), (h, h)), mode='reflect')
    if fmask is None:
        mask = np.pad(mask, ((w, w), (h, h)), mode='constant')
        mask = np.fft.fftshift(mask)
        fmask = np.fft.rfft2(mask)
    result = np.fft.irfft2(np.fft.rfft2(layer)*fmask)
    result = crop(result, w, h)

    return result.astype(np.float32), fmask


def tone_mapping(data_orig, data,
                 verbosity=0,
                 tempfile='temp.raw',
                 GAIN=None,
                 exps=None,
                 factors=None,
                 MAX=None,
                 R_cutoff=np.inf,
                 weight=None,
                 downscale=None,
                 precision=np.float32,
                 distance_metric='eucledian'):

    if weight is None:
        weight = np.ones(shape=data.shape, dtype=np.float32)

    original_shape = data_orig.shape

    if downscale is not None:
        downscaled_shape = ceil_int((original_shape[0] // downscale,
                                     original_shape[1] // downscale))
    else:
        downscaled_shape = original_shape

    garbage_collector()

    max_value = data.max()
    mask = np.zeros(shape=downscaled_shape, dtype=np.float32)

    if distance_metric.lower() == 'eucledian':
        distance = distance_eucledian
    elif distance_metric.lower() == 'maximum':
        distance = distance_maximum
    elif distance_metric.lower() in 'manhattan':
        distance = distance_manhattan
    else:
        try:
            p = float(distance_metric)
            distance = partial(distance_p, p=p)
        except ValueError:
            eprint('Unrecognized distance type')
            sys.exit(1)

    mask = mask_generation(mask,
                           MAX,
                           exps,
                           factors,
                           R_cutoff,
                           distance=distance)

    garbage_collector()

    # This is the main part:
    # Binary layer is generated, with downsampling, if needed
    # this binary layer is convolved with the mask
    # and the result is stored in a histogram.
    # If necessary, this histogram could be stored on disk
    # to save memory.
    #

    test = np.zeros(dtype=precision,
                    shape=(max_value + 1, *downscaled_shape))

    layer = np.zeros(shape=downscaled_shape, dtype=np.float32)
    percent = 0
    fmask = None
    for i in range(max_value + 1):
        if i * 100 // (max_value) > percent:
            percent = i * 100 // (max_value + 1)
            if verbosity > 2:
                sys.stdout.write('Progress: {}{}\r'.format(percent, '%'))
                sys.stdout.flush()

        binary_layer = (data == i)

        if np.any(binary_layer):
            binary_layer = binary_layer.astype(np.float32)
            layer = rebin(binary_layer, layer)
            x, fmask = conv(layer, mask, fmask)
            test[i, ...] = x

    if verbosity > 2:
        sys.stdout.write('                       \n')
        sys.stdout.flush()
    mask = None
    layer = None
    garbage_collector()

    CLIP = GAIN / test.shape[0]
    test /= np.sum(test, axis=0)[None, :, :]
    test = np.minimum(test, CLIP, out=test, dtype=precision)
    s = (1 - np.sum(test, axis=0, dtype=precision)) / test.shape[0]
    test = test + s[None, :, :].astype(precision)
    s = None
    garbage_collector()
    cdf = np.cumsum(test, axis=0, dtype=np.float32)
    test = None

    garbage_collector()

    norm_factors = cdf[-1, :, :].reshape(1, cdf.shape[1], cdf.shape[2])
    cdf /= norm_factors

    garbage_collector()

    px = np.linspace(0, original_shape[0] - 1, num=cdf.shape[1], endpoint=True)
    py = np.linspace(0, original_shape[1] - 1, num=cdf.shape[2], endpoint=True)
    pbin = np.linspace(0, cdf.shape[0] - 1, num=cdf.shape[0], endpoint=True)

    # for spatial and gray-shade interpolation
    interpolator = RegularGridInterpolator((pbin, px, py), cdf, )
    px, py, pbin = None, None, None

    idx_array = np.indices(original_shape)
    idx_array = np.concatenate(
        [data_orig.reshape((1,) + original_shape), idx_array],
        axis=0).reshape(3, -1).T
    garbage_collector()

    idx_arrays = np.array_split(idx_array, 10)
    idx_array = None
    garbage_collector()

    # the whole array might be too huge, this is just a trick to
    # process the data in several (10) steps.
    #
    result = []
    for idx_array in idx_arrays:
        result.append(interpolator(idx_array))
    idx_arrays, idx_arrays = None, None
    garbage_collector()

    result = np.concatenate(result).reshape(original_shape)
    garbage_collector()

    return result
