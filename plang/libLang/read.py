#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

from .. import plang
from .. import utils

@plang.registerFunctionDecorator('read', ['from', ])
def read(**kwargs):
    # 获取变量
    sourceString = utils.readFunctionParameter('from', kwargs, defaultValue='console').strip()

    if sourceString == 'console':
        dataString = input('> ')
    else:
        raise Exception(f"unsupport source {sourceString}")

    return kwargs['result'](promptAppend=dataString, value=dataString)
