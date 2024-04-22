#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

from .. import plang

# todo 解析器存在问题，不能处理函数名与参数名相同的情况（好像是解析起总是有限判定一个字符串是否为函数名）
@plang.registerFunctionDecorator('#', ['/', ])
def comment(**kwargs):
    # do nothing
    return kwargs['result'](promptAppend='', value=None)
