#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import os

import utils
import LLM
[__import__(f"libLLM.{fileName[:-3]}") for fileName in os.listdir('./libLLM') if fileName.endswith(".py")]
import program
import executor

# 注册静态变量API
def registerVariable(name: str, variable):
    return executor.Executor._upsertStaticVariable(name=name, value=variable)

# 注册静态函数API（修饰器）
def registerFunctionDecorator(name: str, parameterKeyStringList: list = None):
    # 上述为带有参数的装饰器，需先定义内部装饰器
    def innerDecorator(func):
        executor.Executor._upsertStaticFunction(name=name, function=func, parameterKeyStringList=parameterKeyStringList)
        return func

    return innerDecorator  # 然后返回内部装饰器

# 载入默认静态库
[__import__(f"libLang.{fileName[:-3]}") for fileName in os.listdir('./libLang') if fileName.endswith(".py")]

# 从*.p.backtick.md中加载文件，仅支持plan text和code(`)两种markdown语法
# 用markdown的plan text表示prompt block、用code表示code block，其它语法将被忽略; 仅为借用IDE的语法高亮功能。
def loadProgramFromBacktickMarkdown(filePath: str):
    promptProgram = program.BlockContainer()

    with open(filePath, mode='r') as file:
        text = file.read()

    codeBlockMode = False
    tmpBlockString = ''
    for char in text:
        if not codeBlockMode and char == '`' and len(tmpBlockString) != 0: # prompt模式遇到`，则表示prompt块结束，进入block块
            promptProgram.appendPromptBlock(program.PromptBlock(tmpBlockString))
            tmpBlockString = ''
            codeBlockMode = True
        elif codeBlockMode and char == '`'  and len(tmpBlockString) != 0: # code模式遇到``，则表示code块结束，进入prompt块
            promptProgram.appendCodeBlock(program.CodeBlock(tmpBlockString))
            tmpBlockString = ''
            codeBlockMode = False
        else:
            tmpBlockString += char

    return promptProgram

# xxx 加载LLM main：15

# 载入程序 main：18 - 39

# 实例化执行器 main：43

# 载入库函数和变量 main：45 - 59

# 执行程序 main：63

# xxx 执行结果和上下文可视化 main：63 - 67

# API界面：该文件内实现，均为为方便编程和命令行使用的界面API和参数
if __name__ == '__main__':
    # 实例化LLM对象 ggml-ChineseAlpaca-13B-q4_0.bin baichuan-vicuna-7b.ggmlv3.q4_0.bin
    llm = LLM.LLM('Llama_GGML', '/Users/hujingzhao/tshare/Llama/ggml-ChineseAlpaca-13B-q4_0.bin', n_ctx=1000)

    # 载入自定义静态变量和函数
    # __import__('examples.sampleTest.lib')
    utils.importModuleFromFile('./examples/sampleTest/lib.py')

    # 载入程序
    customProgram = loadProgramFromBacktickMarkdown('./examples/sampleTest/sampleTest.p.backtick.md')
    # customProgram.print()

    # 实例化执行器
    customExecutor = executor.Executor(blockContainer=customProgram, llm=llm)

    # 载入自定义动态变量和函数
    customExecutor.upsertVariable('varTest', '[this is a test var]')
    @customExecutor.registerFunctionDecorator('funTest', [])
    def funTest(**kwargs):
        return "[this a test function without args]"

    # 打印一些测试内容
    # print('\n', customExecutor.names)

    #执行程序
    executedCustomProgram = customExecutor.run()
    # print(executedCustomProgram)