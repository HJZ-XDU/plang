#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
import utils
import regex
import numpy as np

@plang.registerFunctionDecorator('match', ['regex', 'with max token'])
def match(**kwargs):
    # 获取参数
    regexString = utils.readFunctionParameter('regex', kwargs, defaultValue='').strip()
    maxTokenInt = int(utils.readFunctionParameter('with max token', kwargs, defaultValue=2**64)) # 初始化成一个非常大的数字

    # 获取llm和prompt上下文
    llm = kwargs['llm']
    promptString = str(kwargs['prompt'])

    # 初始化已生成部分
    partialCompletionString = ''
    partialCompletionTokenCountInt = 0

    # 实例化正则表达式
    regexMatcher = regex.compile(regexString)

    while not regexMatcher.match(partialCompletionString) and partialCompletionTokenCountInt < maxTokenInt: # 检查是否完全匹配或达到最大token，满足则退出函数 | regexMatcher.match(nextCharacter).start() == 0
        # 获取next token概率分布
        nextTokenProbability = llm.nextTokenProbability(llm.tokenize(promptString+partialCompletionString)) # 根据已有prompt和已生成匹配字符，预测下一个可能匹配的字符的概率
        nextTokenProbabilityDescendIndex: list = np.argsort(-np.array(nextTokenProbability)).tolist() # 概率降序排序下标索引

        # 逐个比较，遇到第一个可以部分匹配的退出循环
        for tokenInt in nextTokenProbabilityDescendIndex:
            try:  # xxx 过滤掉单个token对应的detokenize code无法解码为utf-8的情况（也就是对于BBPE算法，>256 token id的，未登记词的情况）
                nextCharacter = llm.detokenize([tokenInt, ]) # xxx 这种解码方式只能解码一个token可以表示字，如果正则表达式需要多个token才能表示的字，可能会无法达到匹配条件 ps：这也是select是从选项tokenize中检查，而不是直接从next token detokenize中比较的原因
            except UnicodeDecodeError:
                continue

            if nextCharacter is not '' and regexMatcher.fullmatch(partialCompletionString + nextCharacter, partial=True): # 顺着概率降序遍历，遇到能部分满足正则表达式的则退出遍历循环 注意：fullmatch总是能匹配空字符串 参考：https://github.com/r2d4/rellm/tree/2d2f90bacaf08b1e9b1c08e2e1d8553f15f16363/rellm
                # 此时nextCharacter即为下一个部分满足正则表达式的字符
                partialCompletionString += nextCharacter
                partialCompletionTokenCountInt += 1
                print('_', end='') # xxx 用于支持动态显示匹配过程 | print(nextCharacter, end='') 注意：\t只能正确处理阿斯克码，不能正确处理汉字，因此这里使用'_'代替实际文字
                break

    print('\b \b' * len(partialCompletionString), end='') # xxx 用于支持动态显示匹配过程
    return kwargs['result'](promptAppend=partialCompletionString, value=partialCompletionString)
