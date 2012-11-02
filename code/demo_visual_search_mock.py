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
from skeye.cogs import latch, what, where, watch, zoomin, mark


bot = cogbot(
    reelmemory(
        visualmap(
            'itau00.png',
            descript('agencia', what((88, 110), (263, 363)), what((88, 110), (318, 363)))
        ),
        visualmap(
            'itau01.png',
            descript('name', what((148, 391), (15, 438)), what((279, 328), (190, 265)))
        ),
        visualmap(
            'itau02.png',
            descript('keyboard', what((499, 806), (385, 741))),
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
    latch(watch(0, 'agencia', source='itau2_00.png'), mark('itau2_00.png', 'marked_itau2_00_agencia.png')),
    latch(watch(1, 'name', source='itau2_01.png'), mark('itau2_01.png', 'marked_itau2_01_name.png')),
    zoomin(watch(2, 'keyboard', source='itau2_02.png'),
        latch(watch(2, 2), mark('itau2_02.png', 'marked_itau2_02_key_0_2.png')),
        latch(watch(2, 0), mark('itau2_02.png', 'marked_itau2_02_key_1_0.png')),
        latch(watch(2, 1), mark('itau2_02.png', 'marked_itau2_02_key_2_1.png')),
        latch(watch(2, 1), mark('itau2_02.png', 'marked_itau2_02_key_3_1.png')),
        latch(watch(2, 0), mark('itau2_02.png', 'marked_itau2_02_key_4_0.png')),
        latch(watch(2, 9), mark('itau2_02.png', 'marked_itau2_02_key_5_9.png')),
        latch(watch(2, 1), mark('itau2_02.png', 'marked_itau2_02_key_6_1.png')),
        latch(watch(2, 7), mark('itau2_02.png', 'marked_itau2_02_key_7_7.png')),
        latch(watch(2, 'OK'), mark('itau2_02.png', 'marked_itau2_02_key_ok.png'))
    )
)


if __name__ == '__main__':
    results = bot()
    print('Ok')

