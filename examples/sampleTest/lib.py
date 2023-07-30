#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang

@plang.registerFunctionDecorator('turn', ['on', 'off'])
def turn(**kwargs):
    # 这是一个简单测测试，仅实现turn函数的on参数的响应

    import random
    if random.random() < 0.5:
        promptAppend = f"打开{kwargs['on']}成功，已打开{kwargs['on']}"
        returnValue = "True"
    else:
        promptAppend = f"打开{kwargs['on']}失败，原因为{kwargs['on']}不在线，请检查网络"
        returnValue = "False"


    return kwargs['result'](promptAppend=promptAppend, value=returnValue)
