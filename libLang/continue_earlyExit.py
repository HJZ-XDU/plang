#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import executor

@plang.registerFunctionDecorator('continue', [])
def continue_earlyExit(**kwargs):
    executorContext: executor.Executor = kwargs['context']
    executorContext.parserStatus.setEarlyExit(reasonString='continue')
    return kwargs['result'](promptAppend='', value='continue')
