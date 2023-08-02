#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import program
import copy
import importlib.util
import executor
import typing

"""
功能：从codeString中拆分以wordStringList中字符串开头的前、后部分子串
含义：如果字符串是以wordList开头，则返回word和串的后半部分，否则返回false
"""
def splitWordFromHead(codeString: str, wordStringList: list):
    for word in wordStringList:
        if codeString.startswith(word):
            # 如果检测到了word，则返回word和串的余下部分
            return word, codeString[len(word):].strip()
    # 如果没有检测到word，则返回false和None
    return False, None

"""
功能：使用character从codeString中分割拆分字符串开头的前、后部分子串
含义：如果字符串中包含character，则返回codeString串的前、后半部分，否则返回false
"""
def splitByCharacterFromHead(codeString: str, character: str):
    if character in codeString:
        word = ""
        for tmpCharacter in codeString:
            if tmpCharacter != character:
                word += tmpCharacter
            else:
                break # 检测到分割符就返回，则word中不包含分割符
        # 返回word和串的余下部分
        return word.strip(), codeString[len(word):].strip()
    else:
        # 如果没有检测到character，则返回false和None
        return False, None

# """
# 功能：判断stringList中的字符串是否出现在blockConveyor提供的后续code block中，其中list隐含了判断的优先级
# 含义：如果后续程序中有指定code string则返回True，否则返回False
# """
# def isRestCodeBlockHasAnyStringList(blockConveyor: program.BlockConveyor, stringList: list):
#     # 首先把blockConveyor对象复制一遍，is函数应该没有副作用
#     blockConveyor = copy.deepcopy(blockConveyor)
#
#     # 遍历所有block
#     currentBlock = blockConveyor.nextBlock()
#     while currentBlock != None:
#         if isinstance(currentBlock, program.CodeBlock): # 如果是code block则查看其中是否包含指定字符串
#             for string in stringList:
#                 if string in str(currentBlock):
#                     return True, string # 找到，返回true
#                 else:
#                     continue
#         elif isinstance(currentBlock, program.PromptBlock): # 如果是prompt block则跳过
#             continue
#         else: # 如果既不是code block，也不是prompt block则抛出异常
#             raise Exception(f"unsupport block type: {currentBlock.__class__} => {currentBlock}")
#
#         # 当前block判断完毕，获取下个block
#         currentBlock = blockConveyor.nextBlock()
#
#     # 如果前面未返回，则说明后续code block中不包含指定字符串
#     return False

def importModuleFromFile(filePath: str):
    # 从文件名中提取模块名
    moduleName = filePath.split('/')[-1].replace('.py', '')
    # 创建一个新的模块规范对象
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    # 导入模块
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def integrateReturnSyntaxSugar4Function(runtime: executor.Executor, kwargFunctionDict: dict):

    def returnPromptAndValue(promptAppend: str, value = None):
        if 'as' in kwargFunctionDict.keys():
            runtime.upsertVariable(name=kwargFunctionDict['as'], value=value)
        return  promptAppend

    return returnPromptAndValue

def readFunctionParameter(name: str, kwargFunctionDict: dict, parameterType: typing.Callable=str, defaultValue=None):
    return parameterType(kwargFunctionDict[name] if name in kwargFunctionDict.keys() else defaultValue)

def readFunctionListParameter(name: str, kwargFunctionDict: dict, parameterType: typing.Callable=str, defaultValue=()):
    if name in kwargFunctionDict.keys():
        if isinstance(kwargFunctionDict[name], list):
            return [parameterType(item) for item in kwargFunctionDict[name]]
        else:
            return [parameterType(kwargFunctionDict[name]), ] # 如果不是list，则转为单元素list返回
    else:
        return parameterType(defaultValue)

# xxx False条件判定待检验
falseList = [None, 0, False, 'None', '0', 'False', '', list(), tuple(), dict(), set()]