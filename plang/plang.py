#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import os

from . import utils
from . import LLM
[__import__(f"libLLM.{fileName[:-3]}", globals=globals() , level=1) for fileName in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/libLLM') if fileName.endswith(".py")]
from . import program
from . import executor
import argparse

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
[__import__(f"libLang.{fileName[:-3]}", globals=globals() , level=1) for fileName in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/libLang') if fileName.endswith(".py")]

# 从*.p.backtick.md中加载文件，仅支持plan text和code(`)两种markdown语法
# 用markdown的plan text表示prompt block、用code表示code block，其它语法将被忽略; 仅为借用IDE的语法高亮功能。
def loadProgramFromBacktickMarkdown(filePath: str):
    promptProgram = program.BlockContainer()

    with open(filePath, mode='r') as file:
        text = file.read()

    codeBlockMode = False
    tmpBlockString = ''
    for char in text:
        if not codeBlockMode and char == '`': # prompt模式遇到`，则表示prompt块结束，进入block块
            promptProgram.appendPromptBlock(program.PromptBlock(tmpBlockString)) if len(tmpBlockString) != 0 else None
            tmpBlockString = ''
            codeBlockMode = True
        elif codeBlockMode and char == '`': # code模式遇到``，则表示code块结束，进入prompt块
            promptProgram.appendCodeBlock(program.CodeBlock(tmpBlockString)) if len(tmpBlockString) != 0 else None
            tmpBlockString = ''
            codeBlockMode = False
        else:
            tmpBlockString += char

    # 最后一个"`"之后的字符也要按状态存入block
    if codeBlockMode:
        promptProgram.appendCodeBlock(program.CodeBlock(tmpBlockString)) if len(tmpBlockString) != 0 else None
    else:
        promptProgram.appendPromptBlock(program.PromptBlock(tmpBlockString)) if len(tmpBlockString) != 0 else None

    return promptProgram

# API界面：该文件内实现，均为为方便编程和命令行使用的界面API和参数
def main():
    # 声明命令行参数及解析
    argParse = argparse.ArgumentParser()
    argParse.add_argument("file", metavar='FILE', type=str, nargs=None, help="plang program file path")  # 程序文件路径 必选
    argParse.add_argument("--model", "-m", type=str, nargs='?', help="llm model name",
                          default='Llama_GGML')  # llm模型名 可选
    argParse.add_argument("--path", "-p", type=str, required=True, help="model file path")  # llm 模型文件 必选
    argParse.add_argument("--nContext", "-n", type=int, nargs='?', help="length of llm context",
                          default=2048)  # llm上下文长度 可选
    argParse.add_argument("--lib", '-l', type=str, nargs='*', help='libs for program', default=[])  # 程序中可能用到的库文件 可选
    argParse.add_argument("--verbose", "-v", action='store_true', help="output debug info",
                          default=False)  # 是否启用verbose模型 可选
    commandArgument = argParse.parse_args()

    # 实例化LLM对象 ggml-ChineseAlpaca-13B-q4_0.bin baichuan-vicuna-7b.ggmlv3.q4_0.bin '/Users/hujingzhao/tshare/Llama/ggml-ChineseAlpaca-13B-q4_0.bin'
    llm = LLM.LLM(modelName=commandArgument.model, modelFilePath=commandArgument.path, n_ctx=commandArgument.nContext,
                  verbose=commandArgument.verbose)

    # 载入自定义静态变量和函数
    for libFilePath in commandArgument.lib:
        utils.importModuleFromFile(libFilePath)

    # 载入程序
    supportProgramFileSuffix = ('.p.backtick.md',)
    if commandArgument.file.endswith(supportProgramFileSuffix):
        customProgram = loadProgramFromBacktickMarkdown(commandArgument.file)
    else:
        raise Exception(f"unsupport program file type [not in {supportProgramFileSuffix}]: {commandArgument.file}")
    # 按需打印程序
    if commandArgument.verbose:
        customProgram.print()

    # 实例化执行器
    customExecutor = executor.Executor(blockContainer=customProgram, llm=llm)

    # 载入自定义动态变量和函数
    # 以下示例已移动值./examples/sampleTest/lib.py
    # customExecutor.upsertVariable('varTest', '[this is a test var]')
    # @customExecutor.registerFunctionDecorator('funTest', [])
    # def funTest(**kwargs):
    #     return "[this a test function without args]"

    # 打印一些测试内容
    # print('\n', customExecutor.names)

    # 执行程序
    executedCustomProgram = customExecutor.run()
    # print(executedCustomProgram)

    # 返回程序执行状态
    exit(-1 if customExecutor.parserStatus.isEarlyExit() else 0)

if __name__ == '__main__':
    # export entry would be: plang.plang:main
    main()
