#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import utils


@plang.registerFunctionDecorator('select', ['from', ])
def select(**kwargs):
    # 获取from参数
    fromStringList = [optionString.strip() for optionString in utils.readFunctionListParameter(name='from', kwargFunctionDict=kwargs, defaultValue=[])]

    # 获取llm和prompt上下文
    llm = kwargs['llm']
    promptTokenList = llm.tokenize(str(kwargs['prompt']))

    # 获取选项的token key：optionString value：token list
    fromTokenDict = dict()
    for optionString in fromStringList:
        fromTokenDict[optionString] = llm.tokenize(optionString)

    # 根据模型预测的下一个token不断清理前缀不符合的选项，直到剩一个选项
    while len(fromTokenDict) > 1:
        # nextTokenProbability = llm.nextTokenProbability(f"{promptString}<system role=Question>select from {', '.join(fromStringList)}</system>\n<system role=Answer>")
        # 计算下一个token的概率分布
        nextTokenProbability = llm.nextTokenProbability(promptTokenList)
        # 滤出选项首token的概率分布 key：token value：probability
        nextOptionTokenProbabilityDict = {tokenList[0]: nextTokenProbability[tokenList[0]] for tokenList in fromTokenDict.values()}
        # 选择概率最大的首token
        nextOptionGreedyToken, _ = max(nextOptionTokenProbabilityDict.items(), key=lambda x: x[1]) # x[1]选择value作为排序依据

        # 剔除首token不匹配的选项
        fromTokenDict = {optionString: TokenList[1: ] for optionString, TokenList in fromTokenDict.items() if TokenList[0] == nextOptionGreedyToken}

        # 将预测到的token加入prompt token list
        promptTokenList.append(nextOptionGreedyToken)

    # 上述处理完后，应该只剩一个选项，这个选项就是预测到的select值
    if len(fromTokenDict) == 1:
        selectedOptionString = list(fromTokenDict.keys())[-1]
    else:
        raise Exception(f"unexcept number of selected options (not one): {fromTokenDict}")

    return kwargs['result'](promptAppend=selectedOptionString, value=selectedOptionString)
