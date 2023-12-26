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

"""
将A、B、C依次作为functionName函数的参数并调用该函数（意味着call元编程不能使用默认参数功能，必须按顺序提供所有参数）
`call function` functionName `with parameter` A `and` B `and` C
"""
@plang.registerFunctionDecorator('call', ['function', 'with parameter'])
def call(**kwargs):

    executorContext: executor.Executor = kwargs['context']
    functionNameString = utils.readFunctionParameter('function', kwargs, defaultValue='').strip()
    parameterValueStringList = [parameterValueString.strip() for parameterValueString in utils.readFunctionListParameter(name='with parameter', kwargFunctionDict=kwargs, defaultValue=[])]

    if not functionNameString: # 注意：parameterValueStringList有可能为空，即当被call函数没有参数时
        raise Exception(f"empty tool name: {functionNameString=}, {parameterValueStringList=}")

    # 创建函数call子程序并依次填充参数
    functionCallBlockContainer: program.BlockContainer = program.BlockContainer()
    functionCallBlockContainer.c(f'{functionNameString}')
    for functionParameterKeyIndex, functionParameterKeyString in enumerate(executorContext.getFunction(functionNameString).getParameterKeyStringList()):
        functionCallBlockContainer.c(f' {functionParameterKeyString}').p(f' {parameterValueStringList[functionParameterKeyIndex]}')
    functionCallBlockContainer.c(' as _;') # 默认返回值名称为：_
    #functionCallBlockContainer.print()

    # 新建执行器并执行函数call代码
    newExecutorContext: executor.Executor = executorContext.fork(functionCallBlockContainer)
    newExecutorContext.run()

    return kwargs['result'](promptAppend='', value=newExecutorContext.getVariable('_'))  # 返回值为被call函数的返回值