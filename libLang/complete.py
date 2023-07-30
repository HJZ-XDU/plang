#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import utils

@plang.registerFunctionDecorator('complete', ['stop at', 'temperature is'])
def complete(**kwargs):
    # 获取参数
    temperature = float(utils.readFunctionParameter('temperature is', kwargs, defaultValue=0))
    stopList = [string.strip() for string in utils.readFunctionListParameter('stop at', kwargs, defaultValue=[])]

    # 获取llm和prompt实例
    llm = kwargs['llm']
    promptString = str(kwargs['prompt'])

    # 调用llm
    promptAppendString = llm.complete(promptString, temperature=temperature, stop=stopList)

    return kwargs['result'](promptAppend=promptAppendString, value=promptAppendString)
