#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import utils

@plang.registerFunctionDecorator('set', ['value', 'not'])
def setFunction(**kwargs): # 注意：按命名惯例，函数名应该叫set，但与python内部命名冲突
    result = None

    if 'value' in kwargs.keys():
        if isinstance(kwargs['value'], list):
            valueStringList = [valueString.strip() for valueString in utils.readFunctionListParameter(name='value', kwargFunctionDict=kwargs, defaultValue=[])]
            result = valueStringList
        else:
            valueString = utils.readFunctionParameter(name='value', kwargFunctionDict=kwargs, defaultValue='').strip()
            result = valueString
        return kwargs['result'](promptAppend='', value=result)

    if 'not' in kwargs.keys():
        if isinstance(kwargs['not'], list):
            notStringList = [notString.strip() for notString in utils.readFunctionListParameter(name='not', kwargFunctionDict=kwargs, defaultValue=[])]
            result = notStringList in utils.falseList # 注意：这里判断是否在false里，而不是true，因此相当于自动带了not
        else:
            notString = utils.readFunctionParameter(name='not', kwargFunctionDict=kwargs, defaultValue='').strip()
            result = notString in utils.falseList # 注意：这里判断是否在false里，而不是true，因此相当于自动带了not
        return kwargs['result'](promptAppend='', value=result)

    return kwargs['result'](promptAppend='', value=result)
