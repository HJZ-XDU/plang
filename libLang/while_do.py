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

    executorContext: executor.Executor = kwargs['context']
    def conditionStringLive(): # 注意：condition可能会在循环过程中被then改变，因此这里没有直接获取字符串，而是定义了一个live函数
        conditionStringStatic = kwargs['condition']
        if '_conditionName' in kwargs.keys(): # 如果该变量存在，说明condition是从Variable解析来的，此处选择从上下文中动态访问变量值
            return executorContext.getVariable('_conditionName').getValueString()
        else:
            return conditionStringStatic
    thenBlockContainer: program.BlockContainer = kwargs['then']

    while conditionStringLive() not in utils.falseList:
        executorContext.upsertVariable(name=kwargs['as'], value=conditionStringLive()) if 'as' in kwargs.keys() else None # 动态更新返回值（as语法）
        executorContext.fork(thenBlockContainer).run()


    return kwargs['result'](promptAppend='', value=conditionStringLive()) # while语句的返回值是condition，很合理 注意：该变量可能会在循环中改变
