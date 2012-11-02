#! /usr/bin/env python
#coding=utf-8

r'''A loosely-coupled library of processing functions.

    The base package implements Skeye's core logic as a loosely-coupled library
    of processing functions. Therefore, even if none of the more specialized
    frameworks (e.g. cogs) is fit for the problem at hand, the user can still
    use the base package's functions as building blocks for a more customized
    solution.
    
    Functions in this package can be divided in three categories:
    
    * Data processing algorithms -- these implement the biological- and
      cognitive-inspired algorithms that prompted the development of Skeye;

    * Data processing facilities -- these implement common operations that
      simplify the construction of more complex functions;

    * Programming facilities -- these implement common programming patterns
      (e.g. conversions between data types) that simplify basic programming
      tasks.
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

from itertools import izip

from Image import open as loadimage
from Image import ANTIALIAS

from numpy import dstack, indices, zeros, ndarray
from numpy import argmax, conj, mean, vdot
from numpy import where, logical_and, logical_xor
from numpy.fft import rfft2, irfft2

from scipy.misc import fromimage, toimage


# Programming facilities
#
# These functions implement common programming patterns (e.g. conversions
# between data types) that simplify basic programming tasks.


def fancy_index(values):
    r'''Turns a sequence of 2- and/or 3-tuples into a tuple of slices, which can
        then be used for "fancy indexing" of numpy arrays.
    '''
    slicer = lambda i: slice(*i) if isinstance(i, tuple) else i
    return tuple(slicer(i) for i in values)


def singleton(cls):
    r'''Class decorator. Turns the decorated class into a single instance of
        itself.
    '''
    return cls()


def snapshot(image=None, size=None):
    r'''Acquires an image as a numpy array.

        If the image argument is None, a screenshot is grabbed. otherwise, the
        given image is converted to a 2- or 3-dimensional numpy array, depending
        on whether it's colour or grayscale.
    '''
    if isinstance(image, ndarray):
        return image

    if image == None:
        try:
            from ImageGrab import grab
            image = grab()
            image.save('screenshot.png')
        except:
            from os import system
            name = 'screenshot.png'
            command = "scrot %s" % name
            system(command)
            image = loadimage(name)
    elif isinstance(image, basestring):
        image = loadimage(image)
        image.load()

    if size != None:
        (m, n) = size
        image = image.resize((n, m), ANTIALIAS)

    return dstack(fromimage(channel) for channel in image.split())


class ballot(object):
    r'''A ballot object keeps track of how many times objects of an identical
        category ("votes") have been presented. At any one time, it can be
        queried for the most frequent ("winner") category.
    '''
    def __init__(self):
        r'''Creates a new ballot.
        '''
        self.__ballot = {}
        self.__top = 0
        self.__winner = None

    def vote(self, candidate):
        r'''Adds a category occurrence ("vote") to the ballot.
        '''
        vote = str(candidate)
        (votes, candidate) = self.__ballot.get(vote, (0, candidate))
        votes += 1
        if votes > self.__top:
            self.__top = votes
            self.__winner = candidate

        self.__ballot[vote] = (votes, candidate)

    def winner(self):
        r'''Returns the currently most seen ("winner") category.
        '''
        return self.__winner


class failure(Exception):
    r'''Default exception used to report operation failures.
    '''
    pass


class varargs(tuple):
    r'''An argument sequence of varying length.
    '''
    pass


# Data processing facilities
#
# These functions implement common operations that simplify the construction of
# more complex functions.


def angle(a, b):
    r'''Returns the cosine of the angle between two vectors a and b, as a real
        number between 0 and 1.
    '''
    return vdot(a, b) / (mag(a) * mag(b))


def crop(array, shape):
    r'''Reduces the array's dimensions to the given shape, discarding the data
        outside the restricted range. Raises an exception if any range dimension
        is larger than the original array's.
    '''
    if array.shape == shape:
        return array

    index = tuple(slice(0, n) for n in shape)
    return array[index]


def mag(x):
    r'''Returns the magnitude ("length") of a vector x.
    '''
    return vdot(x, x) ** 0.5


def searchmax(inputs):
    r'''Returns the coordinates of the highest value in a two-dimensional
        matrix.
    '''
    i = argmax(inputs)
    n = inputs.shape[1]
    return (i // n, i % n)


# Data processing algorithms
#
# These functions implement the biological- and cognitive-inspired algorithms
# that prompted the devlopment of Skeye.


def correlate(image, filter):
    r'''Performs a normalized cross-correlation between an image and a search
        template. For more details, see:

        http://en.wikipedia.org/wiki/Cross_correlation#Normalized_cross-correlation
    '''
    si = rfft2(image - mean(image))
    sf = rfft2(filter - mean(filter), image.shape)
    return irfft2(si * conj(sf))


def templatesearch(image, template):
    image = image.astype(float)
    template = template.astype(float)

    signals = correlate(image, template)
    topleft = searchmax(signals)

    index = tuple(slice(i, i + n) for (i, n) in izip(topleft, template.shape))
    spot = image[index]
    precision = angle(crop(template, spot.shape), spot)

    return (spot, topleft, precision)


@singleton
class bayer(object):
    def __init__(self):
        self.filters = {}
        self.largest = (zeros((0, 0)),)

    def __call__(self, image=None):
        inputs = snapshot(image)
        filter = self.__getfilter(inputs.shape[0:2])
        return inputs[filter]

    def __getfilter(self, shape):
        def bayerfilter(shape):
            plane = tuple(i for i in indices(shape))
            colors = (
                # where(logical_and(indexes[0] % 2 != 0, indexes[1] % 2 != 0), 0, 0) + # Red # No need to specify red, as its index is 0
                where(logical_xor(plane[0] % 2 == 0, plane[1] % 2 == 0), 1, 0) + # Green
                where(logical_and(plane[0] % 2 == 0, plane[1] % 2 == 0), 2, 0) # Blue
            )

            return plane + (colors,)

        filter = self.filters.get(shape)
        if filter == None:
            if all(a > b for (a, b) in izip(self.largest[0].shape, shape)):
                index = tuple(slice(0, n) for n in shape)
                filter = tuple(ranges[index] for ranges in self.largest)
            else:
                filter = bayerfilter(shape)
                self.largest = filter

            self.filters[shape] = filter

        return filter

    def filter(self, image):
        data = snapshot(image)
        mosaic = self(data)
        return self.toimage(mosaic)

    def toimage(self, data):
        index = self.__getfilter(data.shape)
        channels = zeros(index[0].shape + (3,))
        channels[index] = data
        return toimage(channels)

