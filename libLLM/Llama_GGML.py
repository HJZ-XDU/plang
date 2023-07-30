#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

from LLM import LLMBase
from llama_cpp import Llama
import copy

class Llama_GGML(LLMBase):

    def __init__(self, modelFilePath, *args, **kwargs):
        super(Llama_GGML, self).__init__(modelName=Llama_GGML.__name__, modelFilePath=modelFilePath, *args, **kwargs)

        print('Creating', Llama_GGML.__name__, '...')
        self.model = Llama(model_path=modelFilePath, *args, **kwargs)
        print(Llama_GGML.__name__, 'is created.')

    def tokenize(self, characterString):
        return self.model.tokenize(text=str(characterString).encode('utf-8'), add_bos=False)

    def detokenize(self, tokenArray):
        return self.model.detokenize(tokenArray).decode('utf-8')

    def nextTokenProbability(self, tokenArray: list):
        self.model.reset()
        # self.model.eval(self.model.tokenize(str(characterString).encode('utf-8'), add_bos=True)) # 在以字符串为输入时，会自动添加bos token。修改为以token list作为输入，则需要手动添加bos token。
        tokenArray = copy.deepcopy(tokenArray) # 在插入bos token之前做一次深拷贝，防止污染外部变量
        tokenArray.insert(0, self.model.token_bos()) # 在tokens的前面添加bos token，用于指示模型推理开始位置
        self.model.eval(tokenArray)
        # return self.model.sample() # 这个是返回一个采样的token，不是所有token的概率
        return self.model.eval_logits[-1] # 这里是eval_logits是二维的，第一个维度可能是返回token的数量(数量为1个token)，第二个维度是概率

    def complete(self, characterString, temperature, stop, maxTokens, repeatPenalty):
        self.model.reset()
        completion = self.model(prompt=characterString, max_tokens=maxTokens, temperature=temperature, stop=stop, repeat_penalty=repeatPenalty)
        return completion['choices'][0]['text'] # 选择生成的一个序列
