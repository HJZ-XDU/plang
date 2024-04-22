#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import plang
from plang import utils

@plang.registerFunctionDecorator('plangSearchTool', ['keyword', ])
def plangSearchTool(**kwargs):
    keywordString = utils.readFunctionParameter('keyword', kwargs, defaultValue='*').strip()

    plangDescriptionString = "PromptLanguage (plang): a string first-class citizen programming language for Large Language Models (LLMs) prompting"

    searchResultString = f'{{"keyword": "{keywordString}", "result": "{plangDescriptionString}"}}'

    return kwargs['result'](promptAppend=searchResultString, value=searchResultString)