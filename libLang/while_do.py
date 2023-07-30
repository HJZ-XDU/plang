#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import program
import executor
import utils

@plang.registerFunctionDecorator('while', ['condition', 'then'])
def while_do(**kwargs):

    conditionString = kwargs['condition'].strip()
    thenBlockContainer: program.BlockContainer = kwargs['then']
    executorContext: executor.Executor = kwargs['context']

    while conditionString not in utils.falseList:
        executorContext.fork(thenBlockContainer).run()


    return kwargs['result'](promptAppend='', value='') # 条件控制语句一般没有返回值吧
