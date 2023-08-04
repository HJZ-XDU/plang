#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

class LLMBase:

    def __init__(self, modelName, modelFilePath, *args, **kwargs):

        self.modelName = modelName
        self.modelFilePath = modelFilePath
        self.args = args
        self.kwargs = kwargs
        self.model = None

    # 输入是字符串，输出是int list
    def tokenize(self, characterString):
        raise NotImplementedError("NotImplemented in LLMBase")

    # 输入是int list，输出是字符串
    def detokenize(self, tokenArray):
        raise NotImplementedError("NotImplemented in LLMBase")

    # 输入是int list 输出是float list（长度与词表一致）
    def nextTokenProbability(self, tokenArray):
        raise NotImplementedError("NotImplemented in LLMBase")

    # 输入是字符串 输出是字符串
    def complete(self, characterString, temperature, stop, maxTokens, repeatPenalty):
        raise NotImplementedError("NotImplemented in LLMBase")

# LLM 代理
class LLM(LLMBase):

    def __init__(self, modelName, modelFilePath, *args, **kwargs):
        super(LLM, self).__init__(modelName, modelFilePath, *args, **kwargs)

        for llmClass in LLMBase.__subclasses__():
            if llmClass.__name__ == self.modelName:
                print(f"LLM {self.modelName} is detected.")
                self.model = llmClass(modelFilePath, *args, **kwargs)
                return
        raise Exception(f"LLM {self.modelName} is not detected.")

    def tokenize(self, characterString):
        return self.model.tokenize(characterString)

    def detokenize(self, tokenArray):
        return self.model.detokenize(tokenArray)

    def nextTokenProbability(self, tokenArray):
        return self.model.nextTokenProbability(tokenArray)

    #def complete(self, characterString, temperature=0, stop=[], maxTokens=128, repeatPenalty=1.1):
    def complete(self, characterString, **kwargs):
        kwargs.update(self.kwargs)

        temperature = 0 if 'temperature' not in kwargs.keys() else kwargs['temperature']
        stop = [] if 'stop' not in kwargs.keys() else kwargs['stop']
        maxTokens = 256 if 'maxTokens' not in kwargs.keys() else kwargs['maxTokens']
        repeatPenalty = 1.1 if 'repeatPenalty' not in kwargs.keys() else kwargs['repeatPenalty']

        return self.model.complete(characterString, temperature, stop, maxTokens, repeatPenalty)
