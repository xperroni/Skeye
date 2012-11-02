#! /usr/bin/env python
#coding=utf-8

r'''Fourier transform-enabled cross-correlation temaple matcher.

This is a demonstration of the cross-correlation formula described
in [ http://www.fmwconcepts.com/imagemagick/fourier_transforms/fourier.html#normcrosscorr ].

See also [ http://en.wikipedia.org/wiki/Phase_correlation ] for an alternate
(possibly more noise-resistant?) approach.
'''

__license__ = r'''
Copyright (c) Helio Perroni Filho <xperroni@gmail.com>

This file is part of Skeye.

Skeye is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Skeye is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Skeye. If not, see <http://www.gnu.org/licenses/>.
'''

__version__ = '1'

from numpy import min, max, where
from scipy.misc import toimage

from skeye import bayer, correlate, searchmax


def main():
    image = bayer('itau02.png')
    template = bayer('keyboard.png')

    correlation = correlate(image, template)
    c_max = max(correlation)
    c_min = min(correlation)

    signal = (correlation - c_min) * 255 / (c_max - c_min)
    toimage(signal).save('signal.png')

    winner = where(correlation == c_max, 255, 0)
    toimage(winner).save('winner.png')
    print searchmax(winner)


if __name__ == '__main__':
    main()

