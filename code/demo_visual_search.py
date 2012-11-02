#! /usr/bin/env python
#coding=utf-8

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

from skeye.cogs import cogbot, reelmemory, visualmap, descript
from skeye.cogs import latch, what, where, locate, zoomin
from skeye.cogs import automate, click, Left


bot = cogbot(
    reelmemory(
        visualmap(
            'itau00.png',
            descript('agencia', what((88, 110), (263, 533), precision=0.9), what((88, 110), (318, 363)))
        ),
        visualmap(
            'itau01.png',
            descript('name', what((148, 391), (15, 438), precision=0.98), what((200, 391), (15, 438)), what((279, 328), (190, 265)))
        ),
        visualmap(
            'itau02.png',
            descript('keyboard', what((499, 806), (385, 741), precision=0.94)),
            descript(0, what((655, 675), (419, 430)), where('buttons')),
            descript(1, what((655, 675), (599, 610)), where('buttons')),
            descript(2, what((655, 675), (659, 670)), where('buttons')),
            descript(3, what((655, 675), (539, 550)), where('buttons')),
            descript(4, what((655, 675), (479, 490)), where('buttons')),
            descript(5, what((655, 675), (691, 702)), where('buttons')),
            descript(6, what((655, 675), (571, 582)), where('buttons')),
            descript(7, what((655, 675), (451, 462)), where('buttons')),
            descript(8, what((655, 675), (631, 642)), where('buttons')),
            descript(9, what((655, 675), (511, 522)), where('buttons')),
            descript('OK', what((723, 744), (585, 630))),
            buttons=(
                ((156, 216), (34, 81)),   # Button "0 ou 7"
                ((156, 216), (94, 141)),  # Button "4 ou 9"
                ((156, 216), (154, 201)), # Button "3 ou 6"
                ((156, 216), (214, 261)), # Button "1 ou 8"
                ((156, 216), (274, 321))  # Button "2 ou 5"
            )
        )
    ),
    automate('run', r'"C:\Program Files\Internet Explorer\iexplore.exe" "http://www.itau.com.br"'),
    #automate('run', 'chromium-browser "http://www.itau.com.br"'),
    latch(locate(0, 'agencia', delay=3), click(Left)),
    automate('write', '0863963445\n'),
    latch(locate(1, 'name', delay=3), click(Left)),
    zoomin(locate(2, 'keyboard', delay=3),
        latch(locate(2, 2), click(Left)),
        latch(locate(2, 0), click(Left)),
        latch(locate(2, 1), click(Left)),
        latch(locate(2, 1), click(Left)),
        latch(locate(2, 0), click(Left)),
        latch(locate(2, 9), click(Left)),
        latch(locate(2, 1), click(Left)),
        latch(locate(2, 7), click(Left)),
        latch(locate(2, 'OK'), click(Left))
    )
)


if __name__ == '__main__':
    bot()

