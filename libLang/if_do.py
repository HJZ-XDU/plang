#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import executor
import utils
import program

@plang.registerFunctionDecorator('if', ['condition', 'then'])
def if_do(**kwargs):

    executorContext: executor.Executor = kwargs['context']
    conditionString = utils.readFunctionParameter(name='condition', kwargFunctionDict=kwargs, defaultValue='').strip()
    thenBlockContainer: program.BlockContainer = kwargs['then']

    if conditionString not in utils.falseList:
        newExecutorContext = executorContext.fork(thenBlockContainer)
        newExecutorContext.upsertVariable(name=kwargs['as'], value=conditionString) if 'as' in kwargs.keys() else None  # 及时写入返回值（as语法），方便if内部访问if语句的条件
        newExecutorContext.run()

    return kwargs['result'](promptAppend='', value=conditionString)  # if语句的返回值是condition，很合理
