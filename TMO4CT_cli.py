#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python libraries
import os
import sys
from gc import collect as garbage_collector

# Additional libraries
import numpy as np   # http://www.numpy.org/
import skimage      # http://scikit-image.org/
import skimage.color

# https://andreacensi.github.io/contracts
from contracts import contract, check
import imageio
import tifffile as tiff

from TMO4CT.tools import eprint, dither
from TMO4CT.algorithm import tone_mapping
from TMO4CT import __version__, __description__, __title__
# Libraries implemented for the article
# try:
#    from TMO4CT.tools import dither, eprint   # Various tools
# except ImportError:
#    from .tools import dither, eprint

# try:
#    from algorithm import tone_mapping     # Tone mapping implementation
# except ImportError:
#    from .algorithm import tone_mapping     # Tone mapping implementation


def if_not_none(a, b):
    if b is None:
        return a
    return b


@contract(filename='filename', ftype='None|str')
def read_image(filename, ftype=None):
    if ftype is None or ftype == 'autodetect':
        try:
            import magic  # here: https://github.com/ahupp/python-magic
        except ImportError:
            eprint('python-magic is not installed but it is required')
            eprint('  for file type auto detection.')
            sys.exit(1)
        return read_image(filename, ftype=magic.from_file(filename, mime=True))

    if ftype == 'application/dicom':
        eprint('DICOM format is not supported, convert it to 16bit PNG.')
        eprint('DCM2HDR is able to convert DICOMs to 16bit tiff/png.')
        sys.exit(-1)
    elif ftype == 'image/tiff':
        img = tiff.imread(filename)
        return img, 'image'
    elif ftype.startswith('image/'):
        return imageio.imread(filename), 'image'
    eprint('File format is not detected or not supported.')
    sys.exit(-1)


def main():
    from optparse import OptionParser

    parser = OptionParser(description=__description__,
                          prog=__title__,
                          version='%prog ' + __version__)
    parser.add_option('-t', '--type',
                      action='store',
                      type='string',
                      dest='filetype',
                      help='Input file type (default: autodetect)',
                      default='autodetect')

    parser.add_option('-o', '--output_type',
                      action='store',
                      type='string',
                      dest='outtype',
                      help='Output file type (default: jpg)',
                      default='jpg')

    parser.add_option('-O', '--output_dir',
                      action='store',
                      type='string',
                      dest='outdir',
                      help="Output directory (default: input file's dir.)")

    parser.add_option('-P', '--postfix',
                      action='store',
                      type='string',
                      dest='postfix',
                      help='postfix for the output (default: _tone_mapped)',
                      default='_tone_mapped')

    parser.add_option('-c', '--contrast-limit',
                      action='store',
                      type='float',
                      dest='climit',
                      help='contrast limit in 1/N units (default: infinite)',
                      default=1e29)

    parser.add_option('-e', '--exponent',
                      action='append',
                      type='float',
                      dest='exps',
                      help='weight = factor/r^exponent (default exp=inf)',
                      )

    parser.add_option('-f', '--factor',
                      action='append',
                      type='float',
                      dest='factors',
                      help='weight = factor/r^exponent (default factor=1.0)',
                      )

    parser.add_option('-m', '--meta',
                      action='store_true',
                      dest='meta',
                      help='Record metadata to OUTPUT_FILE.meta',
                      default=True)

    parser.add_option('--no-meta',
                      action='store_false',
                      dest='meta',
                      help='Do NOT record metadata.',
                      default=True)

    parser.add_option('-M', '--maximum',
                      action='store',
                      type='float',
                      dest='MAX',
                      help='center-pixel weight (default: 1.0)',
                      default=1.0)

    parser.add_option('-R', '--R-cutoff',
                      action='store',
                      type='float',
                      dest='R_cutoff',
                      help='radial cutoff(default: no cutoff)',
                      default=np.inf)

    parser.add_option('--dynamic_range_bottom',
                      action='store',
                      type='float',
                      dest='dynamic_bottom',
                      help='bottom of the dynamic range (default: image min)')

    parser.add_option('--dynamic_range_top',
                      action='store',
                      type='float',
                      dest='dynamic_top',
                      help='top of the dynamic range (default: image max)')

    parser.add_option('-v',
                      action='count',
                      dest='verbose',
                      help='Verbosity level, can be repeated,' +
                      ' e.g. -vvv. (default: non-verbose mode)',
                      default=0)

    parser.add_option('-b', '--bin_count',
                      action='store',
                      type='int',
                      dest='bins',
                      help='number of bins (default: 0 - no binning)',
                      default=0)

    parser.add_option('-s', '--color_space',
                      action='store',
                      type='string',
                      dest='colorspace',
                      help='color space for processing (default: HSV)',
                      default='HSV')

    parser.add_option('-S', '--color_channel',
                      action='store',
                      type='int',
                      dest='color_channel',
                      help='color channel to be processed, starting ' +
                      'with 0 (default: 2 for HSV, 1 for XYZ, 0 for Y**)',
                      )

    parser.add_option('-x', '--downscale_ratio',
                      action='store',
                      type='float',
                      dest='downscale',
                      help='downscale factor, e.g. 2.0 (default: 1.0)')

    parser.add_option('--distance_metric',
                      action='store',
                      type='string',
                      dest='distance',
                      default='eucledian',
                      help='Distance type. Valid parameters ' +
                      '"eucledian", "maximum", "manhattan"' +
                      'or any 0<p<inf float number.')

    color_channel_mapping = {
        'HSV': 2,
        'YIQ': 0,
        'YCbCr': 0,
        'YPbPr': 0,
        'YUV': 0}
    color_channel_scale_factor = {
        'HSV': 1.0,
        'YIQ': 1.0,
        'YCbCr': 235.,
        'YPbPr': 1.0,
        'YUV': 1.0}

    (options, args) = parser.parse_args()

    # Test of input parameters
    check('int, >=0', options.bins, 'number of bins')
    check('float, >0', options.climit, 'contrast limit')

    if len(args) == 0:
        parser.print_help()
        sys.exit(0)

    # Check power function definition
    if options.exps is None:
        options.exps = [1.0, ]
    if options.factors is None:
        options.factors = (1.0,) * len(options.exps)
    if len(options.factors) != len(options.exps):
        eprint('The number of exponents and scaling factors must match!')
        sys.exit(0)

    for path in args:
        check('filename', path)

        if options.verbose > 0:
            eprint('\nFile: {}'.format(path))
        garbage_collector()
        dirname, filename = os.path.split(path)
        fileroot, ext = os.path.splitext(filename)

        if not options.outtype.startswith('.'):
            options.outtype = '.' + options.outtype
        if options.outdir is None:
            options.outdir = dirname

        output_file = os.path.join(
            options.outdir,
            fileroot + options.postfix + options.outtype)

        # opening input file, and preprocessing
        image, itype = read_image(path, options.filetype)

        multi_channel = len(image.shape) > 2

        # ~# color space conversion, if necessary
        hidden_gray = False
        if multi_channel:
            if skimage.__version__ < '0.14.0':
                eprint('Remark: Color conversion in skimage is buggy'
                       + ' before 0.14. Use at least 0.14.')
                sys.exit(1)
            hidden_gray = True
            for ch in range(1, image.shape[-1]):
                hidden_gray = (hidden_gray and
                               np.all(image[..., 0] == image[..., ch]))
            if not hidden_gray:
                data = skimage.color.convert_colorspace(image,
                                                        'RGB',
                                                        options.colorspace)
                color_channel = color_channel_mapping[options.colorspace]
                img = (data[..., color_channel] /
                       color_channel_scale_factor[options.colorspace])
            else:
                image = image[..., 0]
                img = image
                multi_channel = False
        else:
            img = image

        m = if_not_none(img.min(), options.dynamic_bottom)
        M = if_not_none(img.max(), options.dynamic_top)
        img = np.clip(img, m, M)

        gain_limits = options.climit

        if options.bins <= 1:  # Use all
            img = img.astype(np.float32).reshape(img.shape)
            options.bins = int(img.max())+1
            dtype = np.uint8 if options.bins < 255 else np.uint16
            binned = img.astype(dtype)
        else:
            img = ((img - m) *
                   (float(options.bins-1) / float(M - m))).astype(np.float32)
            dtype = np.uint8 if options.bins < 255 else np.uint16
            binned = dither(img, levels=options.bins, method='fs', dtype=dtype)

        if options.verbose > 1:
            eprint('    Image dimensions     : {}'.format(image.shape))
            if multi_channel:
                eprint('    Color space, channel :' +
                       ' {}, #{}'.format(options.colorspace, color_channel))
            else:
                eprint('    Color space, channel : single channel data')
            eprint('    Dynamic range        : {} - {} '.format(m, M))

        if options.verbose > 2:
            eprint('\n    Command line: ', ' '.join(sys.argv))
        # main processing

        image = None

        garbage_collector()

        result = tone_mapping(img,
                              binned,
                              verbosity=options.verbose,
                              GAIN=gain_limits,
                              exps=options.exps,
                              factors=options.factors,
                              MAX=options.MAX,
                              R_cutoff=options.R_cutoff,
                              downscale=options.downscale,
                              distance_metric=options.distance
                              )

        result *= 255. / result.max()
        result = dither(result, levels=256, method='fs', dtype=np.uint8)

        img = None
        binned = None
        gain_limits = None
        garbage_collector()

        if options.verbose > 1:
            eprint('    Output file: {}'.format(output_file))
        if not multi_channel:
            if hidden_gray:
                result = np.dstack((result, result, result))
                imageio.imsave(output_file, result)
            else:
                imageio.imsave(output_file, result)

        # multichannel
        else:
            data[..., color_channel_mapping[options.colorspace]] = result * \
                color_channel_scale_factor[options.colorspace] / result.max()

            result = None
            image = None
            img = None
            garbage_collector()

            result = []
            for d in np.array_split(data, 15):
                result.append(skimage.color.convert_colorspace(
                    d,
                    options.colorspace,
                    'RGB'))
            data = None
            garbage_collector()
            rgb = np.concatenate(result)
            result = None
            garbage_collector()
            imageio.imsave(output_file, rgb)


if __name__ == '__main__':
    main()
