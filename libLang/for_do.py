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

'''
`for each` a `or` b `or` c `then do`
`set name` item/_ `as newItemName` # 因为在plang中“ ”（空格）不是特殊语法，所以变量定义关键字“as”只能放句尾，因此通过这种方法来实现对for item的命名

`done`
或者
`for each` item(这其实一个新变量，有点儿奇怪) `in` a `or` b `or` c `then do`
pass
`done`
或者
`for each` a `or` b `or` c `then do`
pass
`done as item` # for语句的返回值是for里的遍历内容，很合理
'''
@plang.registerFunctionDecorator('for', ['each', 'then'])
def for_do(**kwargs):
    executorContext: executor.Executor = kwargs['context']
    eachStringList: list = [item.strip() for item in utils.readFunctionListParameter(name='each', kwargFunctionDict=kwargs)] # 注意：在该实现中for语句开始执行之后，each指向的list内容不再重新读取
    thenBlockContainer: program.BlockContainer = kwargs['then']

    item = None # 避免eachStringList为空时，return语句中的item未定义
    for item in eachStringList:
        newExecutorContext = executorContext.fork(thenBlockContainer)
        newExecutorContext.upsertVariable(name=kwargs['as'], value=item) if 'as' in kwargs.keys() else None  # 动态更新返回值（as语法）
        newExecutorContext.run()
        if 'continue' in newExecutorContext.parserStatus:
            newExecutorContext.parserStatus.reset()  # 记得清除状态标记
            continue
        if 'break' in newExecutorContext.parserStatus:
            newExecutorContext.parserStatus.reset()  # 记得清除状态标记
            break

    return kwargs['result'](promptAppend='', value=item)  # for语句的返回值是item，很合理
