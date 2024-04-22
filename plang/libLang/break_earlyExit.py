#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

from .. import plang
from .. import executor

@plang.registerFunctionDecorator('break', [])
def break_earlyExit(**kwargs):
    executorContext: executor.Executor = kwargs['context']
    executorContext.parserStatus.setEarlyExit(reasonString='break')
    return kwargs['result'](promptAppend='', value='break')
