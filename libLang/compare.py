#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import utils

@plang.registerFunctionDecorator('compare', ['value', ])
def compare(**kwargs):

    valueStringList = [valueString.strip() for valueString in utils.readFunctionListParameter(name='value', kwargFunctionDict=kwargs, defaultValue=[])]

    result = True
    if valueStringList:
        firstValueString = valueStringList[0]
        for tempValueString in valueStringList:
            if tempValueString != firstValueString:
                result = False
                break

    return kwargs['result'](promptAppend='', value=result)
