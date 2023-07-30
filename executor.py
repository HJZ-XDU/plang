#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

import program
import utils
import typing
import LLM
import copy

class Prompt:

    def __init__(self, string=""):
        self.string = string.strip()

    def appendString(self, string):
        # xxx 尚不确定是否要根据中英文自动修正空格；strip()函数似乎并不只是去除空格，把换行也去掉了
        # self.string += f" {string.strip()}"

        # xxx 是否应保留？ 约束换行个数：若衔接处\n大于两个，则去掉新添加字符串左侧使得衔接处\n大于两个的\n
        allowedMaxEnterCount = 2
        # 计算原串右侧\n的个数
        sourceString = copy.deepcopy(self.string)
        leftEnterCount = len(sourceString) - len(sourceString.rstrip('\n'))
        # 计算新串左侧\n的个数
        newString = copy.deepcopy(string)
        rightEnterCount = len(newString) - len(newString.lstrip('\n'))
        # 如果衔接处总个数大于等于2个 则保留右侧 max((2-左侧个数), 0)个\n（假设\n个数足够）
        if (leftEnterCount + rightEnterCount) >= allowedMaxEnterCount:
            maintainCountInRight = max(allowedMaxEnterCount - leftEnterCount, 0) # 右侧字符串应保留\n个数
            deleteCountInRight = allowedMaxEnterCount - maintainCountInRight # 右侧字符串应删除\n个数
            deleteCountInRight = min(deleteCountInRight, rightEnterCount) # 取应删除个数与实际个数的最小值

            # 执行裁剪
            string = string[deleteCountInRight: ]

        # 即时打印终端，按需配置
        print(string, end='')

        # 追加
        # xxx 可能需要改进为按结构追加（方便支持多模态）
        self.string += string

    def __str__(self):
        return self.string

class Variable:
    def __init__(self, value):
        self.value = value

    def getValueString(self):
        return str(self.value)

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def __repr__(self):
        objType = type(self)
        # return f'<{objType.__module__}.{objType.__name__} object at {hex(id(self))} value is "{self.value}">'
        return f'<{objType.__module__}.{objType.__name__} object, value is "{self.value}">'

class Function:
    def __init__(self, function, parameterKeyStringList: list = None):
        self.function = function
        self.parameterKeyStringList = parameterKeyStringList if parameterKeyStringList != None else list()

    def getParameterKeyStringList(self):
        return self.parameterKeyStringList

    def call(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def __repr__(self):
        objType = type(self)
        return f'<{objType.__module__}.{objType.__name__} object, function is {self.function}, parameter key is {self.parameterKeyStringList}>'

class Executor:

    _staticNames = dict()

    def __init__(self, blockContainer: program.BlockContainer, llm: LLM.LLM):
        # 优先级： 关键词(or and ； done) > 变量 > 函数（函数放最后，因为函数是透明的）
        self.blockContainer = blockContainer # 程序
        self.blockConveyor = program.BlockConveyor(self.blockContainer) # 逐块递送block
        self.currentPrompt = Prompt() # 已代码展开确认prompt
        self.names = dict() # 变量和函数名字表

        self.llm = llm

        # 自动载入静态names
        self.names.update(self._staticNames)

    def fork(self, blockContainer: program.BlockContainer):
        newExecutor = Executor(blockContainer=blockContainer, llm=self.llm)

        # fork: 应继承的有上下文
        newExecutor.currentPrompt = self.currentPrompt
        newExecutor.names = self.names

        return newExecutor

    def run(self):
        currentBlock = self.blockConveyor.nextBlock()

        entryFunction, kwargFunctionDict = None, None
        while currentBlock != None:
            entryFunction, kwargFunctionDict = self.parseBlock(currentBlock, entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)
            currentBlock = self.blockConveyor.nextBlock()

        return self.currentPrompt

    def upsertVariable(self, name: str, value):
        self.names[name] = Variable(value=value)
        return self.names[name]

    def getVariable(self, name: str) -> Variable:
        if name not in self.names.keys():
            raise Exception(f"variable name {name} does not exist")
        if not isinstance(self.names[name], Variable):
            raise Exception(f"name {name} is not a instance of Variable: {type(self.names[name])}")
        return self.names[name]

    def upsertFunction(self, name: str, function: typing.Callable, parameterKeyStringList: list = None):
        self.names[name] = Function(function=function, parameterKeyStringList=parameterKeyStringList)
        return self.names[name]

    def registerFunctionDecorator(self, name: str, parameterKeyStringList: list = None):
        # 上述为带有参数的装饰器，需先定义内部装饰器
        def innerDecorator(func):
            self.upsertFunction(name=name, function=func, parameterKeyStringList=parameterKeyStringList)
            return func

        return innerDecorator  # 然后返回内部装饰器

    @classmethod
    def _upsertStaticVariable(cls, name: str, value):
        cls._staticNames[name] = Variable(value=value)
        return cls._staticNames[name]

    @classmethod
    def _upsertStaticFunction(cls, name: str, function: typing.Callable, parameterKeyStringList: list = None):
        cls._staticNames[name] = Function(function=function, parameterKeyStringList=parameterKeyStringList)
        return cls._staticNames[name]

    def parseBlock(self, block: program.BlockBase, entryFunction: Function=None, kwargFunctionDict: dict=None):
        currentBlock = block
        if currentBlock is None: # 注意检查：如果currentBlock是none，则说明程序已执行完毕，直接返回
            return None, None # 程序执行完毕，清空函数上下文状态（合理预设）

        if isinstance(currentBlock, program.PromptBlock): # 如果是prompt block
            if entryFunction is not None and kwargFunctionDict is not None: # 如果entryFunction和kwargFunctionDict都不为None，说明函数形参名正在寻找形参值
                # 则将prompt block内容作为形参值填写
                currentparameterKey = list(kwargFunctionDict.keys())[-1] # 取最后一个形参名
                if kwargFunctionDict[currentparameterKey] is None: # 如果形参仅初始化
                    kwargFunctionDict[currentparameterKey] = str(currentBlock) # 则直接填写
                elif isinstance(kwargFunctionDict[currentparameterKey], list): # 如果形参类型为list
                    kwargFunctionDict[currentparameterKey].append(str(currentBlock)) # 则直接写入
                else: # 其他类型抛出异常（仅支持string和stringList的形参）
                    raise Exception(f"unsupport function parameter type (not string(None) or list): {currentparameterKey} => {kwargFunctionDict[currentparameterKey].__class__}")
            else: # 其他情况，则prompt block应直接作为已确定prompt填充
                self.currentPrompt.appendString(str(currentBlock))
            return entryFunction, kwargFunctionDict # 当前block处理完毕，可返回
        elif isinstance(currentBlock, program.CodeBlock): # 如果是code block
            entryFunction, kwargFunctionDict = self.parseCodeBlock(currentBlock, entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)
            return entryFunction, kwargFunctionDict # 当前block处理完毕，可返回
        else: # 如果既不是prompt block，也不是code block
            raise Exception(f"unsupport block type: {currentBlock.__class__} => {currentBlock}")

    def parseCodeBlock(self, codeBlock: program.CodeBlock, entryFunction: Function=None, kwargFunctionDict: dict=None):
        currentBlock = codeBlock
        if currentBlock is None: # 注意检查：如果currentBlock是none，则说明程序已执行完毕，直接返回
            return None, None # 程序执行完毕，清空函数上下文状态（合理预设）

        codeString = str(currentBlock).strip()
        # xxx 进来直接判定names，会导致函数变量名与names相同时，无法被识别（好像是：仅在非函数内部和形参名寻找形参值时才需判断）
        name, codeStringRest = utils.splitWordFromHead(codeString, self.names.keys()) if self._shouldFindName(entryFunction, kwargFunctionDict) else (False, None)  # 因为代码名字可以带有空格，这里使用字符串匹配，而不是空格拆分命令各部分
        if name:  # 如果找到了名字
            # print(f"\033[92m找到了name：{name}\033[0m")
            # 则进进一步判断name是变量，还是函数
            if isinstance(self.names[name], Variable):  # 如果name是个变量
                # 如果变量出现在非函数中，则直接写入，如果变量出现在函数中，则应该是函数的形参值
                if entryFunction is None: # 如果不在函数内部
                    # 则直接解析函数名
                    self.currentPrompt.appendString(self.names[name].getValueString())  # 在string-first语言中，变量都是字符串，这里直接返回变量的取值即可

                    # 当前codeString的前半部分处理完毕，开始继续处理后半部分codeString
                    if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                        entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                        return entryFunction, kwargFunctionDict  # 递归闭合后返回
                    else:  # 如果代码串处理完，则当前block处理完毕
                        return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                elif entryFunction is not None and kwargFunctionDict is not None: # 如果在函数内部，且有形参名在寻找形参值
                    # 则写入形参值
                    currentParameterKey = list(kwargFunctionDict.keys())[-1]  # 取最后一个形参名
                    if kwargFunctionDict[currentParameterKey] is None:  # 如果形参仅初始化
                        kwargFunctionDict[currentParameterKey] = self.names[name].getValue()  # 则直接填写
                        kwargFunctionDict[f"_{currentParameterKey}Name"] = name  # 同时写入变量形参值元信息（变量名）
                    elif isinstance(kwargFunctionDict[currentParameterKey], list):  # 如果形参类型为list
                        kwargFunctionDict[currentParameterKey].append(self.names[name].getValueString())  # 则直接写入
                        # xxx list形参是否需要返回value（不是上面的valueString）以及支持_name元属性 （核心在于or语法是否为现场解析：暂定为是）
                    else:  # 其他类型抛出异常（仅支持string和stringList的形参）
                        raise Exception(f"unsupport function parameter type (not string(None) or list): {currentParameterKey} => {kwargFunctionDict[currentParameterKey].__class__}")

                    # 当前codeString的前半部分处理完毕，开始继续处理后半部分codeString
                    if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                        entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                        return entryFunction, kwargFunctionDict  # 递归闭合后返回
                    else:  # 如果代码串处理完，则当前block处理完毕
                        # 在函数内、形参名在寻找形参值、形参值已填充 若下一个块为prompt block，则代表函数终止，应执行 （形参对已闭合，后续只能是其他形参名或结束）
                        if self.blockConveyor.isNextBlockType(program.PromptBlock):  # 如果下一个块是prompt块
                            # 则说明函数结束，应立即执行，则调用函数并返回
                            kwargFunctionDict['context'] = self # 将执行器上下文作为参数之一传递给函数
                            kwargFunctionDict['result'] = utils.integrateReturnSyntaxSugar4Function(runtime=self, kwargFunctionDict=kwargFunctionDict) # 将集成返回prompt与as值的语法糖函数入口作为参数之一传递给函数
                            kwargFunctionDict['llm'] = self.llm # 将llm作为参数之一传递给函数 （llm可以通过context访问到，但考虑到可能会频繁调用llm，这里相当于提供一个快捷方式）
                            kwargFunctionDict['prompt'] = self.currentPrompt # 将当前已确定prompt作为参数之一传递给函数 （prompt可以通过context访问到，但考虑到可能会频繁调用prompt，这里相当于提供一个快捷方式）
                            self.currentPrompt.appendString(str(entryFunction(**kwargFunctionDict)))  # 以有参形式调用，并将结果追加至已确定的prompt
                            # 注意：函数调用确认后，entryFunction和kwargFunctionDict状态均应设置为None（表示非函数或形参状态）
                            entryFunction, kwargFunctionDict = None, None

                            return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                        elif self.blockConveyor.isNextBlockType(program.CodeBlock):  # 如果下一个块是code块
                            # 则当前函数有可能被截断（后续可能还有形参），应作保留状态，并返回（当前块已处理完毕）
                            return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                        else:  # 如果既不是prompt block，也不是code block，则抛出异常
                            raise Exception(f"unsupport block type: not {program.CodeBlock} or {program.PromptBlock}")
                else: # 如果不再函数内部，且却有形参名在寻找形参值，则抛出异常
                    raise Exception(f"unexcept variable name {name} where function is {entryFunction} and kwargs is {kwargFunctionDict}")
            elif isinstance(self.names[name], Function): # 如果name是个函数
                # print(f"\033[92m找到了函数：{name}\033[0m")
                # 查找函数入口实例，继续解析函数形参表（注意函数可能没有参数）
                entryFunction = self.names[name]
                # 当前codeString的前半部分已解析为函数入口实例，开始继续处理后半部分codeString
                if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                    entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                    return entryFunction, kwargFunctionDict  # 递归闭合后返回
                else: # 如果代码串处理完，可能是无参数函数或参数在后续块，则需要以后续codeblock来判定 ~（or/and/非names/变量names则继续，；/as/done则结束）~
                    # xxx todo 因如函数支持args和kwargs，无法区分无参函数与单参args，暂时只支持kwargs参数形式，看后面能不能找到可区分的规则
                    if self.blockConveyor.isNextBlockType(program.CodeBlock): # 如果后面是code block，说明后面应该是另一个函数、函数参数、as赋值
                        entryFunction, kwargFunctionDict = self.parseCodeBlock(self.blockConveyor.nextBlock(), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 则递归解析
                        return entryFunction, kwargFunctionDict  # 递归闭合后返回
                    elif self.blockConveyor.isNextBlockType(program.PromptBlock): # 如果函数name后不是code block（而是prompt block），则entryFunction是无参函数
                        kwargFunctionDict = {"context": self} # 注意：以无参形式调用函数，也需向函数提供执行器上下文
                        kwargFunctionDict['result'] = utils.integrateReturnSyntaxSugar4Function(runtime=self, kwargFunctionDict=kwargFunctionDict)  # 将集成返回prompt与as值的语法糖函数入口作为参数之一传递给函数
                        kwargFunctionDict['llm'] = self.llm  # 将llm作为参数之一传递给函数 （llm可以通过context访问到，但考虑到可能会频繁调用llm，这里相当于提供一个快捷方式）
                        kwargFunctionDict['prompt'] = self.currentPrompt  # 将当前已确定prompt作为参数之一传递给函数 （prompt可以通过context访问到，但考虑到可能会频繁调用prompt，这里相当于提供一个快捷方式）
                        self.currentPrompt.appendString(str(entryFunction(**kwargFunctionDict)))  # 直接以无参形式调用，并将结果追加至已确定的prompt
                        # 注意：函数调用确认后，entryFunction和kwargFunctionDict状态均应设置为None（表示非函数或形参状态）
                        return None, None  # 当前block处理完毕，直接返回
                    else:
                        raise Exception(f"unsupport block type: not {program.CodeBlock} or {program.PromptBlock}")
            else:  # 如果既不是变量，也不是函数
                raise Exception(f"unsupport name type: {name} => {self.names[name].__class__}")
        else:  # 如果没找到名字
            # code block中的内容会是下面之一：函数名、变量名、参数名、终止符号，其中函数和变量名记录在names中；若在函数中，则判断是否为参数名或终止符；若不在函数中，则报错。
            if entryFunction: # 如果是在函数内部
                # 则判断是形参名，还是形参值
                parameterKey, codeStringRest = utils.splitWordFromHead(codeString, entryFunction.getParameterKeyStringList())
                if parameterKey: # 如果找到了形参名
                    # 则初始化形参
                    if kwargFunctionDict != None:
                        kwargFunctionDict[parameterKey] = None
                    else:
                        kwargFunctionDict = {parameterKey: None}

                    if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                        entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                        return entryFunction, kwargFunctionDict  # 递归闭合后返回
                    else:  # 如果代码串处理完，则当前block处理完毕
                        return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                else: # 如果没找到形参名
                    # 在函数内部，如果code block非形参名，则code block只能是保留字 （or/and，as，；）、形参值（name）
                    listReservedWord, codeStringRest = utils.splitWordFromHead(codeString, ['or', 'and'])
                    if listReservedWord: # 如果找到了or/and
                        # 则将当前（最后一个）形参转为list
                        if kwargFunctionDict is not None: # 必须有形参时才能转
                            currentParameterKey = list(kwargFunctionDict.keys())[-1]  # 取最后一个形参名
                            kwargFunctionDict[currentParameterKey] = [kwargFunctionDict[currentParameterKey], ] if not isinstance(kwargFunctionDict[currentParameterKey], list) else kwargFunctionDict[currentParameterKey]

                            if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                                entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                                return entryFunction, kwargFunctionDict  # 递归闭合后返回
                            else:  # 如果代码串处理完，则当前block处理完毕
                                return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                        else: # 没有形参，但出现or/and时，则抛出异常
                            raise Exception(f"unexcept reserved word {listReservedWord} (no kwargs): {entryFunction} => {kwargFunctionDict}")

                    terminationReservedWord, codeStringRest = utils.splitWordFromHead(codeString, ['as', ';'])
                    if terminationReservedWord in ['as']: # 当检测到as关键字时
                        # 为函数初始化as形参名 （出现as形参名 则代表函数需项name注册指定变量名作为函数结果赋值）
                        kwargFunctionDict['as'] = '_' # 默认name取“_” （与python保持一致）

                        if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                            entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                            return entryFunction, kwargFunctionDict  # 递归闭合后返回
                        else:  # 如果代码串处理完，则当前block处理完毕
                            return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回
                    elif terminationReservedWord in [';']: # 当检测到；关键字时，表示函数语句结束
                        # 则调用函数并返回
                        kwargFunctionDict['context'] = self  # 将执行器上下文作为参数之一传递给函数
                        kwargFunctionDict['result'] = utils.integrateReturnSyntaxSugar4Function(runtime=self, kwargFunctionDict=kwargFunctionDict)  # 将集成返回prompt与as值的语法糖函数入口作为参数之一传递给函数
                        kwargFunctionDict['llm'] = self.llm  # 将llm作为参数之一传递给函数 （llm可以通过context访问到，但考虑到可能会频繁调用llm，这里相当于提供一个快捷方式）
                        kwargFunctionDict['prompt'] = self.currentPrompt  # 将当前已确定prompt作为参数之一传递给函数 （prompt可以通过context访问到，但考虑到可能会频繁调用prompt，这里相当于提供一个快捷方式）
                        self.currentPrompt.appendString(str(entryFunction(**kwargFunctionDict)))  # 以有参形式调用，并将结果追加至已确定的prompt
                        # 注意：函数调用确认后，entryFunction和kwargFunctionDict状态均应设置为None（表示非函数或形参状态）
                        entryFunction, kwargFunctionDict = None, None

                        if codeStringRest != '':  # 如果代码串还没有处理完，递归处理
                            entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                            return entryFunction, kwargFunctionDict  # 递归闭合后返回
                        else:  # 如果代码串处理完，则当前block处理完毕
                            return entryFunction, kwargFunctionDict  # 当前block处理完毕，直接返回

                    # 列表符和终止符均已判定，接下来判定函数中as赋值
                    if 'as' in kwargFunctionDict.keys(): # 如果出现as关键字
                        # 则后续所有字母都被认为是待函数赋值变量名 （遇到prompt block或；则结束as）
                        variableName, codeStringRest = utils.splitByCharacterFromHead(codeString, ';') # 检测当前块是否有‘；’出现
                        if variableName: # 如果；分割出了字符串
                            # 则待函数赋值变量名已知，直接配置
                            kwargFunctionDict['as'] = variableName

                            # 然后递归处理后续串，因为至少';'在codeStringRest中
                            entryFunction, kwargFunctionDict = self.parseCodeBlock(program.CodeBlock(codeStringRest), entryFunction=entryFunction, kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                            return entryFunction, kwargFunctionDict  # 递归闭合后返回
                        else: # 如果；没有分割出了字符串
                            # 则依据下一个block的类型来判定具体行为
                            if self.blockConveyor.isNextBlockType(program.PromptBlock): # 如果下一个块是prompt块
                                # 则说明余下的内容都属于as，且函数结束，应立即执行
                                kwargFunctionDict['as'] = codeString
                                # 然后调用函数并返回
                                kwargFunctionDict['context'] = self  # 将执行器上下文作为参数之一传递给函数
                                kwargFunctionDict['result'] = utils.integrateReturnSyntaxSugar4Function(runtime=self, kwargFunctionDict=kwargFunctionDict)  # 将集成返回prompt与as值的语法糖函数入口作为参数之一传递给函数
                                kwargFunctionDict['llm'] = self.llm  # 将llm作为参数之一传递给函数 （llm可以通过context访问到，但考虑到可能会频繁调用llm，这里相当于提供一个快捷方式）
                                kwargFunctionDict['prompt'] = self.currentPrompt  # 将当前已确定prompt作为参数之一传递给函数 （prompt可以通过context访问到，但考虑到可能会频繁调用prompt，这里相当于提供一个快捷方式）
                                self.currentPrompt.appendString(str(entryFunction(**kwargFunctionDict)))  # 以有参形式调用，并将结果追加至已确定的prompt
                                # 注意：函数调用确认后，entryFunction和kwargFunctionDict状态均应设置为None（表示非函数或形参状态）
                                entryFunction, kwargFunctionDict = None, None

                                return entryFunction, kwargFunctionDict # 当前block处理完毕，直接返回
                            elif self.blockConveyor.isNextBlockType(program.CodeBlock): # 如果下一个块是code块
                                # 则当前as字段有可能被截断（待函数赋值变量名允许包含空格），应作为一个整体处理
                                # 则拼接后，递归处理
                                entryFunction, kwargFunctionDict = self.parseCodeBlock(
                                    program.CodeBlock(f"{codeString} {str(self.blockConveyor.nextBlock())})"),
                                    entryFunction=entryFunction,
                                    kwargFunctionDict=kwargFunctionDict)  # 注意：代码块的子串也一定是代码
                                return entryFunction, kwargFunctionDict  # 递归闭合后返回
                            else: # 如果既不是prompt block，也不是code block，则抛出异常
                                raise Exception(f"unsupport block type: not {program.CodeBlock} or {program.PromptBlock}")

                    # 最后判断函数中的names（仅变量）调用
                    # 如果形参值是names则解析，如果不是则报错
                    pass # 无需讨论，递归调用时，会被前面names处理代码响应

                    # 如果函数形参值要求的names不存在，则判断下是否为do，如果为do则启动lazy形参模型
                    lazyVariableReservedWord, codeStringRest = utils.splitWordFromHead(codeString, ['do', ])
                    if lazyVariableReservedWord:
                        lazyVariableBlockContainer: program.BlockContainer = self.blockConveyor.nextLazyBlocksContainer(beginString='do', endString='done')
                        currentParameterKey = list(kwargFunctionDict.keys())[-1]  # 取最后一个形参名
                        if kwargFunctionDict[currentParameterKey] is None:  # 如果形参仅初始化
                            # 则写入lazy模式匹配到的程序
                            kwargFunctionDict[currentParameterKey] = lazyVariableBlockContainer

                            # 函数执行判断时机：1.写入形参值后判断一次 2.函数名识别到之后判断一次（无参函数）3.识别到分号时 判断一次 3.as解析完后判断一次
                            # 这里属于特殊的（lazy mode）形参值写入后
                            if self.blockConveyor.isNextBlockType(program.PromptBlock):  # 如果下一个块是prompt块
                                # 则说明函数结束，应立即执行，则调用函数并返回
                                kwargFunctionDict['context'] = self  # 将执行器上下文作为参数之一传递给函数
                                kwargFunctionDict['result'] = utils.integrateReturnSyntaxSugar4Function(runtime=self, kwargFunctionDict=kwargFunctionDict)  # 将集成返回prompt与as值的语法糖函数入口作为参数之一传递给函数
                                kwargFunctionDict['llm'] = self.llm  # 将llm作为参数之一传递给函数 （llm可以通过context访问到，但考虑到可能会频繁调用llm，这里相当于提供一个快捷方式）
                                kwargFunctionDict['prompt'] = self.currentPrompt  # 将当前已确定prompt作为参数之一传递给函数 （prompt可以通过context访问到，但考虑到可能会频繁调用prompt，这里相当于提供一个快捷方式）
                                self.currentPrompt.appendString(str(entryFunction(**kwargFunctionDict)))  # 以有参形式调用，并将结果追加至已确定的prompt
                                # 注意：函数调用确认后，entryFunction和kwargFunctionDict状态均应设置为None（表示非函数或形参状态）
                                entryFunction, kwargFunctionDict = None, None

                            # codeStringRest被起止符自动插入至下一块，当前块处理完毕
                            return entryFunction, kwargFunctionDict  # 若当前块处理完毕则返回，若当前块未处理完毕，则codeStringRest余下代码被起止符自动插入至下一个块
                        else: # 否则抛出异常
                            raise Exception(f"got lazy program snippet, but parameter[-1] {currentParameterKey} in function {entryFunction} not None(initialization): {kwargFunctionDict[currentParameterKey]=} => {lazyVariableBlockContainer=}")

                    raise Exception(f"unexcept parameter (key or value) name '{codeString}': {entryFunction=} => {kwargFunctionDict=}")
            else: # 如果不在函数内部
                # 非函数内部（且非函数或变量names），则抛出异常（未出现在names中的code串，只能是函数形参，而形参只能在函数内部；函数内部已在if中处理，所以这里抛出异常）
                raise Exception(f"unexcept code block (not names or inFunction): {str(currentBlock)}")

            return entryFunction, kwargFunctionDict # 当前块处理完毕，可返回

    def _shouldFindName(self, entryFunction: Function=None, kwargFunctionDict: dict=None):

        # 如果as在形参表中，说明进入了as命名阶段；此时as具有最高优先级，可以覆盖所有names，所以此时应该直接跳过names匹配
        if entryFunction and kwargFunctionDict and 'as' in kwargFunctionDict.keys():
            return False

        return True