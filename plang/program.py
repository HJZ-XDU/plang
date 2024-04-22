#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tony Hu
@email: mail@tonyhu.xyz
"""

class BlockBase:

    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return self.string

class PromptBlock(BlockBase):

    def __init__(self, string: str):
        super(PromptBlock, self).__init__(string)

class CodeBlock(BlockBase):

    def __init__(self, string: str):
        super(CodeBlock, self).__init__(string)

class BlockContainer:

    def __init__(self):
        self.blocks = list()

    # 方便手工录入程序（自动化程序应使用appendPromptBlock），从字符串追加prompt block
    def p(self, string: str):
        self.appendPromptBlock(PromptBlock(string))
        return self

    # 方便手工录入程序（自动化程序应使用appendCodeBlock），从字符串追加code block
    def c(self, string: str):
        self.appendCodeBlock(CodeBlock(string))
        return self

    def appendPromptBlock(self, promptBlock: PromptBlock):
        self.blocks.append(promptBlock)
        return self

    # def insertPromptBlock(self, index: int, promptBlock: PromptBlock):
    #     self.blocks.insert(index, promptBlock)
    #     return self

    def appendCodeBlock(self, codeBlock: CodeBlock):
        self.blocks.append(codeBlock)
        return  self

    # def insertCodeBlock(self, index: int, codeBlock: CodeBlock):
    #     self.blocks.insert(index, codeBlock)
    #     return self

    def replaceBlockWithBlockList(self, index: int, blockList: list):
        self.blocks[index: index+1] = blockList
        return self

    def getBlockNumber(self):
        return len(self.blocks)

    def getBlock(self, index):
        return self.blocks[index]

    def print(self):
        for block in self.blocks:
            if isinstance(block, CodeBlock):
                print(f"\033[92m{block}\033[0m", end='')
            elif isinstance(block, PromptBlock):
                print(block, end='')
            else:
                raise Exception(f"unsupport block type: {block.self.__class__} => {block}")

import re
class BlockConveyor:
    def __init__(self, blockContainer:BlockContainer):
        self.blockContainer = blockContainer
        self.blockIndex = -1 # 已传送block下标

    def nextBlock(self):
        if self.blockIndex < self.blockContainer.getBlockNumber() - 1:
            self.blockIndex += 1
            return self.blockContainer.getBlock(self.blockIndex)
        else:
            return None

    def isNextBlockType(self, classType):
        if self.blockIndex < self.blockContainer.getBlockNumber() - 1:
            nextBlock = self.blockContainer.getBlock(self.blockIndex + 1)
        else:
            # nextBlock = None
            # xxx 当没有下一个block时，程序结束，默认下一个block类型未空prompt block (合理预设，减少探测时工作量，否则所有条件都要考虑程序是否结束)
            nextBlock = PromptBlock("")

        return True if isinstance(nextBlock, classType) else False

    def nextLazyBlocksContainer(self, beginString: str, endString: str):
        lazyBlockContainer = BlockContainer()
        currentBlock = self.blockContainer.getBlock(self.blockIndex) # 检测到beginString进入该函数的那个code block不一定被处理完，因此这里直接用blockIndex取当前块继续处理

        isFirstBeginString = True # 是否为首个待处理块（包含进入该函数的beginString所在的块），因为需要一些特殊处理：例如去掉该块beginString之前的代码
        lazyStackLength = 0 # lazy模式分割栈，栈为0表示分割符闭合
        while currentBlock is not None:
            if isinstance(currentBlock, CodeBlock): # 如果是code block，则栈解析其中的起止符
                lazyCodeString = "" # 当前块的起止符“前”代码

                currentCodeString = str(currentBlock) # 当前块代码，随着消耗，含义将变为：当前块的起止符“后”代码
                skipCurrentCodeString = "" # 需跳过的进入该函数前首块已处理代码
                if isFirstBeginString: # 如果是进入该函数的首块（进入函数时beginString所在块），需抛弃beginString之前的代码，因为进入函数之前已被处理
                    match = re.search(beginString, currentCodeString)
                    if match:
                        skipCurrentCodeString = currentCodeString[0: match.end()] # 待剔除代码需要妥善保存，后面因分割重组代码时不可丢失任何实际代码
                        currentCodeString = currentCodeString[match.end(): ] # 剔除首个beginString及之前的代码
                        lazyStackLength += 1 # 首个beginString已处理，起止符栈+1
                        isFirstBeginString = not isFirstBeginString
                    else:
                        raise Exception(f"unexcept code block ({beginString=} not in block): {currentBlock}")

                    # xxx delete
                    # while len(currentCodeString) != 0:
                    #     if not currentCodeString.startswith(beginString):
                    #         currentCodeString = currentCodeString[1: ]
                    #     else:
                    #         currentCodeString = currentCodeString.lstrip(beginString)
                    #         lazyStackLength += 1
                    #         break
                    # isFirstBeginString = not isFirstBeginString
                if len(currentCodeString.strip()) == 0: # 如果剔除完了，也就是beginString是current code block的最后一个字，则直接进入下一个块的处理
                    # 在跳出本次循环之前，为下个待处理block做好准备
                    currentBlock = self.nextBlock()
                    if currentBlock is None:  # 若一直到程序末尾，起止符都没有闭合，则抛出异常
                        raise Exception(f"delimiter not close until the end of blocks: {lazyBlockContainer=}")
                    continue

                # 使用正则表达式匹配起止符号 注意：为了适应起止符存在字符串存在嵌套的情况，优先匹配较长串
                while True: # 不断查找起止符，当起止符栈为空时，返回整个函数
                    match = re.search(f"({beginString}|{endString})" if len(beginString) > len(endString) else f"({endString}|{beginString})", currentCodeString)
                    if match:
                        # 根据起止符类型，操作起止符栈
                        if match.group() == beginString:
                            lazyStackLength += 1
                        elif match.group() == endString:
                            lazyStackLength -= 1
                        else:
                            raise Exception(f"unexcept delimiter(not {beginString=} or {endString=}): {match.group()}")

                        # 根据起止符位置，将代码划分起止符前、起止符后 起名依据为：若当前终止符能使得起止符闭合
                        lazyCodeString += currentCodeString[0: match.end()]
                        currentCodeString = currentCodeString[match.end(): ]

                        if lazyStackLength == 0: # 若起止符已闭合则返回，则处理上下文，准备返回
                            # 将当前块按照终止拆分为当前和下一个两个块：终止符前的代码(lazyCodeString)替换当前块，终止符后(currentCodeString)的代码插入下一块 注意：新建CodeBlock前，需判断code string为否为空
                            splitBlockList = list()
                            splitBlockList.append(CodeBlock(skipCurrentCodeString)) if len(skipCurrentCodeString.strip()) != 0 else None # 注意：有一种情况时beginString和endString在同一个code block，此时不要忘了之前跳过的代码 代码重组不应改变代码含义
                            splitBlockList.append(CodeBlock(lazyCodeString)) if len(lazyCodeString.strip()) != 0 else None
                            splitBlockList.append(CodeBlock(currentCodeString)) if len(currentCodeString.strip()) != 0 else None

                            self.blockContainer.replaceBlockWithBlockList(index=self.blockIndex, blockList=splitBlockList) # 注意：被替换块的块索引指向已被处理块，则替换后索引指示处应为已处理块的末尾（待处理块的前一个）
                            # 则当前块索引应始终指向CodeBlock(lazyCodeString)，因为CodeBlock(currentCodeString)为未处理完，待分块后续处理块
                            self.blockIndex = self.blockIndex + 1 if len(skipCurrentCodeString.strip()) != 0 else self.blockIndex # 因此，若CodeBlock(skipCurrentCodeString)存在，则索引应向前走一块


                            # 把属于起止符之内的提交给LazyBlockContainer 注意：新建CodeBlock前，需判断lazyCodeString为否为空
                            lazyCodeString = lazyCodeString.strip().rstrip(endString) # 去掉最后的终止符
                            lazyBlockContainer.appendCodeBlock(CodeBlock(lazyCodeString)) if len(lazyCodeString.strip()) != 0 else None

                            return lazyBlockContainer # 函数返回
                    else:
                        # 不match有两种情况：1.整块不match：直接将currentCodeString写入lazyBlockContainer中。2.部分match，余下的currentCodeString不match：只要前面没有因lazyStackLength == 0而返回，lazyStack只计数，则余下的currentCodeString也应直接返回（此时需加上前半截计入lazyCodeString的部分，因为只计了个数）
                        # 因为第一种情况时，lazyCodeString一定为“”，因此这里直接简写
                        lazyBlockContainer.appendCodeBlock(CodeBlock(lazyCodeString + currentCodeString))

                        # 能执行到这里，说明整个块不match，或块内match但起止符未闭合
                        break # 则当前块处理完毕，推出循环，开始处理下个block
            elif isinstance(currentBlock, PromptBlock): # 如果是prompt block，其中必然不包含起止符（需为code模式），则直接写入lazyBlockContainer
                lazyBlockContainer.appendPromptBlock(currentBlock)
            else: # 如果既不是code block，也不是prompt block，则抛出异常
                raise Exception(f"unsupport block type: {currentBlock.__class__} => {currentBlock}")

            currentBlock = self.nextBlock()
            if currentBlock is None: # 若一直到程序末尾，起止符都没有闭合，则抛出异常
                print(f"{lazyBlockContainer=}:")
                lazyBlockContainer.print()
                raise Exception(f"delimiter not close until the end of blocks: {lazyBlockContainer=}")
