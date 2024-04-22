#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

from .. import plang
from .. import utils

@plang.registerFunctionDecorator('complete', ['prompt is', 'stop at', 'temperature is'])
def complete(**kwargs):
    # 获取参数
    temperatureFloat = utils.readFunctionParameter(name='temperature is', kwargFunctionDict=kwargs, parameterType=float, defaultValue=0)
    stopStringList = [string.strip() for string in utils.readFunctionListParameter('stop at', kwargs, defaultValue=[])]

    # 获取llm和prompt实例
    llm = kwargs['llm']
    promptString = str(kwargs['prompt']) if 'prompt is' not in kwargs.keys() else utils.readFunctionParameter(name='prompt is', kwargFunctionDict=kwargs, defaultValue='').strip()

    # 调用llm
    promptAppendString = llm.complete(promptString, temperature=temperatureFloat, stop=stopStringList)

    return kwargs['result'](promptAppend=promptAppendString, value=promptAppendString)
