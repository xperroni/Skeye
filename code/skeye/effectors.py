#! /usr/bin/env python
#coding=utf-8

r'''Utilities to interact with the external world.
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

import platform
from os import system
from time import sleep

from skeye import singleton


# Mouse click constants
Left = object()
Right = object()


class _desktop_windows(object):
    def __init__(self):
        from win32com.client import Dispatch
        self.__client = Dispatch('AutoItX3.Control')
        self.__buttons = {Left: 'left', Right: 'right'}

    def click(self, x, y, button=Left, delay=0):
        self.__client.MouseClick(self.__buttons[button], x, y, 1, 50)

    def run(self, command):
        self.__client.Run(command)

    def write(self, text):
        self.__client.Send(text.replace('\n', '{ENTER}'), 0)



class _desktop_x11(object):
    r'''X11 desktop automator, wraps xdotool.

        http://www.semicomplete.com/projects/xdotool/xdotool
    '''
    def __init__(self):
        self.__buttons = {Left: 1, Right: 2}

    def click(self, x, y, button=Left, delay=100):
        system('xdotool mousemove %d %d' % (x, y))
        sleep(delay)
        system('xdotool click %d' % self.__buttons[button])

    def run(self, command):
        system(command)

    def write(self, text):
        keys = [c if c != '\n' else 'KP_Enter' for c in text]
        command = 'xdotool key ' + ' '.join(keys)
        system(command)


@singleton
class desktop(object):
    r'''Desktop automation API.
    
        Methods in the 'deesktop' class enable Skeye to interact with the
        underlying graphical desktop environment. Currently supported
        operations are moving the mouse cursor and clicking the final
        location, writing text, and running other applications.

        Both Linux and Windows are supported, however different external
        applications must be installed for automation to work on either
        platform:

        * For Windows, install AutoIt v3 [ http://www.autoitscript.com/ ];

        * For Linux, install xdotool [ http://www.semicomplete.com/projects/xdotool/ ].
    '''
    def __init__(self):
        self.__client = None

    def __call__(self, command, *args, **opts):
        f = getattr(self.__getclient(), command)
        return f(*args, **opts)

    def __getattr__(self, name):
        return getattr(self.__getclient(), name)

    def __getclient(self):
        if self.__client == None:
            if platform.system() == 'Windows':
                self.__client = _desktop_windows()
            else:
                self.__client = _desktop_x11()

        return self.__client
