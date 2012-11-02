#! /usr/bin/env python
#coding=utf-8

r'''A framework for programming simple cognitive tasks.

    Cogbots (short for "cognitive robots") are simple programmable agents that
    can be described in terms of a predefined 'memory' defining the agent's
    initial state, and a sequence of 'commands' that implement its behavior,
    interacting with both the memory and surrounding environment as they run.
    When a Cogbot is activated, it executes its commands sequentially,
    returning a list of the commands' outputs after it finishes.

    Any kind of object can be specified as the bot's memory, but since commands
    will often need to query it for data, logically the object must conform to
    their expectations. The default memory class in 'skeye.cogs' is 'reelmemory',
    which behaves just like a linked list. Individual memories must of course
    be represented by some kind of object; currently the only pre-defined class
    fulfilling this role is 'visualmap', which holds together a visual snapshot
    (i.e. an image) and descriptions of objects found within it. Objects are
    described by sequences of operations 'what' and 'where': 'what'
    "differentiates" an object from the image, whereas 'where' "integrates" a
    previously differentiated object into a larger one.

    Commands are expected to be callables that accept a single argument 'context',
    which is set to the Cogbot itself. Both functions and callable objects can
    be used, therefore customizable "command classes" can be created -- and are
    in fact an integral part of the 'skeye.cogs' package. The special command
    classes 'batch' and 'latch' take sequences of commands as instantiation
    arguments: when executed, 'batch' runs every command passing them the same
    arguments it was invoked with and returns the list of outputs, whereas
    'latch' passes the input arguments plus the output of the previous command
    in the sequence, and returns the output of the last command.
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

from itertools import izip, product
from time import sleep

from Image import open as open_image
from ImageDraw import Draw

from skeye import fancy_index, ballot, failure, varargs
from skeye import bayer, templatesearch
from skeye import effectors


Screenshot = None


class cogbot(object):
    r'''A CogBot (short for Cognitive Robot) is a simple programmable agent. It
        is mainly composed of a sequence of commands, which may interact with
        the surrounding environment as well as with the agent's memory.
    '''
    def __init__(self, memory, *commands):
        r'''Creates a new CogBot from a pre-set memory and a command sequence.
        '''
        self.memory = memory
        self.commands = batch(*commands)

    def __call__(self):
        r'''Runs the CogBot. Programmed commands are executed sequentially.
        '''
        commands = self.commands
        return commands(context=self)


class batch(object):
    def __init__(self, *actions):
        self.actions = actions

    def __call__(self, *args, **context):
        return tuple(action(*args, **context) for action in self.actions)

    def __str__(self):
        return tostr('batch', self.actions)


class latch(object):
    def __init__(self, *actions):
        self.actions = actions

    def __call__(self, *args, **context):
        args = varargs(args)
        for action in self.actions:
            if not isinstance(args, varargs):
                args = (args,)

            args = action(*args, **context)

        return args

    def __str__(self):
        return tostr('latch', self.actions)


class reelmemory(list):
    r'''A simple sequencial memory.
    '''
    def __init__(self, *memories):
        r'''Creates a new reel memory out of a collection of individual
            memories.
        '''
        self.extend(memories)


class descript(tuple):
    r'''A descript is the counterpart of a percept: whereas the percept
        represents an actual object, the descript provides the template after
        which that object is matched (or put another way, from which the percept
        is created).

        A descript is composed of a label (i.e. its name) and a sequence of
        differentiation ("what") and/or integration ("where") operations.
    '''
    def __new__(cls, label, *commands):
        return tuple.__new__(cls, (label, latch(*commands)))


class percept(object):
    r'''A percept is a representation of a visual object. It provides basic
        information on its position and dimensions, possibly relative to a
        larger, "parent" percept.
    '''
    def __init__(self, data, offset=(0, 0), parent=None):
        r'''Creates a new percept out of a raw pixel data object, a position
            offset and an optional parent percept. If the parent percept is
            supplied, the offset is taken to be relative to this parent,
            otherwise it is taken as relative to the overall scene.
        '''
        self.data = data
        self.offset = offset
        self.parent = parent

    @property
    def center(self):
        r'''Returns the percept's center coordinates, relative to the overall
            scene.
        '''
        return tuple((sum(t) / len(t)) for t in self.region)

    @property
    def region(self):
        r'''Returns a set of coordinates ((r0, rn), (c0, cn)) describing a
            square around the percept. Values are relative to the overall scene.
        '''
        return tuple((i, i + n) for (i, n) in izip(self.topleft, self.data.shape))

    @property
    def topleft(self):
        parent = self.parent
        offset = self.offset

        if parent == None:
            return offset

        return tuple(k + i for (k, i) in izip(parent.topleft, offset))


class visualmap(object):
    r'''A memory of a visual scene, from which various objects may be
        discretized by sequences of differentiation ("what") and/or integration
        ("where") operations.
    '''
    def __init__(self, memory, *descriptors, **rois):
        r'''Creates a new visual map out of a memory object, a collection of
            object descriptors, and an optional dictionary of Regions of
            Interest (ROI's).
        '''
        self.memory = bayer(memory)
        self.descriptors = dict(descriptors)
        self.rois = rois

    def __call__(self, label, inputs):
        r'''Searches for the the labeled object in a new scene, represented by
            the data inputs.
        '''
        descriptor = self.descriptors[label]
        return descriptor(inputs, context=self)


def tostr(name, children):
    tab = ' ' * 4
    return (
        name + '(\n' + tab +
        ', '.join(str(child).replace('\n', '\n' + tab) for child in children) +
        '\n)'
    )


class what(object):
    def __init__(self, *roi, **options):
        self.roi = fancy_index(roi)
        self.precision = options.get('precision', 0.0)

    def __call__(self, inputs, context):
        template = context.memory[self.roi]
        (spotted, topleft, precision) = templatesearch(inputs.data, template)
        if precision < self.precision:
            print precision
            raise failure()

        return percept(spotted, topleft, inputs)

    def __str__(self):
        return 'what{0!s}'.format(tuple(self.roi))


class where(object):
    def __init__(self, label):
        self.label = label

    def __call__(self, spotted, context):
        parent = spotted.parent
        topleft = parent.topleft
        contours = context.rois[self.label]

        roi = tuple((i, i + n) for (i, n) in izip(spotted.offset, spotted.data.shape))

        def inroi(i, r):
            for ((a, n), x) in izip(r, i):
                if not (a <= x < n):
                    return False

            return True

        counts = ballot()
        for i in product(*[range(*x) for x in roi]):
            for c in contours:
                if inroi(i, c):
                    counts.vote(c)

        roi = counts.winner()
        if roi != None:
            return percept(parent.data[fancy_index(roi)], tuple(i[0] for i in roi), parent)
        else:
            return spotted

    def __str__(self):
        return "where('%s')" % self.label


class look(what):
    def __init__(self, image, *roi):
        what.__init__(self, *roi)
        self.image = image

    def __call__(self, context):
        inputs = percept(bayer(self.image))
        return what.__call__(self, inputs, context)


class locate(object):
    def __init__(self, index, label, delay=0, source=Screenshot):
        self.delay = delay
        self.index = index
        self.label = label
        self.source = source

    def __call__(self, inputs=None, context=None):
        sight = context.memory[self.index]
        description = sight.descriptors[self.label]

        if inputs != None:
            return description(inputs, context=sight)

        while True:
            sleep(self.delay)
            inputs = percept(bayer(self.source))
            try:
                return description(inputs, context=sight)
            except failure:
                pass


class lookout(object):
    def __init__(self, perceptor, index, *labels):
        self.perceptor = perceptor
        self.index = index
        self.labels = labels

    def __call__(self, context):
        perceptor = self.perceptor
        memory = context.memory[self.index]
        inputs = perceptor(context=memory)
        return [memory(label, inputs) for label in self.labels]


class zoomin(object):
    def __init__(self, perceptor, *actions):
        self.perceptor = perceptor
        self.actions = actions

    def __call__(self, context):
        perceptor = self.perceptor
        inputs = perceptor(context=context)
        return [action(inputs, context=context) for action in self.actions]


class automate(object):
    def __init__(self, command, *arguments):
        self.command = command
        self.arguments = arguments

    def __call__(self, *args, **context):
        effectors.desktop(self.command, *self.arguments)


Left = effectors.Left
Right = effectors.Right

class click(object):
    def __init__(self, button):
        self.button = button

    def __call__(self, perceived, context):
        (y, x) = perceived.center
        effectors.desktop.click(x, y, self.button)


class mark(object):
    def __init__(self, source, saveas):
        self.source = source
        self.saveas = saveas

    def __call__(self, perceived, context):
        if perceived == None:
            return

        ((y0, y1), (x0, x1)) = perceived.region
        image = open_image(self.source)
        draw = Draw(image)
        draw.rectangle((x0, y0, x1, y1), outline=(255, 0, 0))
        image.save(self.saveas)
