#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
from plang import utils
import subprocess

@plang.registerFunctionDecorator('python', ['run code', ])
def python(**kwargs):
    def _extractCode(markdownCodeBlockString):
        start_index = markdownCodeBlockString.rfind("```python\n")  # 找到最后一个```python\n的索引
        end_index = markdownCodeBlockString.rfind("\n```")  # 找到最后一个\n```的索引
        if start_index == -1 or end_index == -1 or end_index < start_index:
            return "print('no markdown python code block detected')"  # 如果未找到合法的markdown code block，则返回生成未找到代码块的python code，以提示llm
        content = markdownCodeBlockString[start_index + len("```python\n"): end_index]  # 提取内容
        return content

    def _executeCode(codeString):
        # 启动新的Python解释器，并将代码作为命令行参数传递给它
        process = subprocess.Popen(['python', '-c', codeString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 获取执行结果
        output, error = process.communicate()

        # 将执行结果存储在字符串中
        output_str = f'The Python interpreter returns: {{"stdout": "{output.decode("utf-8")}", "stderr": "{error.decode("utf-8")}"}}'  # 使用适当的方法解码为文本形式

        # 返回执行结果
        return output_str

    pythonCodeString = _extractCode(utils.readFunctionParameter('run code', kwargs, defaultValue='').strip())
    #print(pythonCodeString)

    codeReturnString = _executeCode(pythonCodeString).replace("\n", "\\n") # 注意：\n应原文返回，而不是渲染为换行
    #print(codeReturnString)

    return kwargs['result'](promptAppend=codeReturnString, value=codeReturnString)
