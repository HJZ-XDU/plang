# PromptLanguage (plang): 一种面向大语言模型(LLM)提示(prompt)的字符串优先编程语言
# PromptLanguage (plang): a string first-class citizen programming language for Large Language Models (LLMs) prompting

将大语言模型(LLMs)看作一种处理知识（文字）的新型计算机范式，那么它需要一门编程语言。为此，我们设计了PromptLanguage (plang)语言，它是一种字符串为一等公民的面向大语言模型提示工程的编程语言。其核心语法规则遵循：默认解析为字符串、通过字体样式区分字符串与代码（例如：字体颜色），进而实现字符串优先且对任何字符都透明。
该语言具有以下特性：

1. 符合直觉的交互式prompt开发；
2. 运行在LLMs上，自动管理context，与外部API便捷交互；
3. 引导LLMs按照预期行为和格式输出；
4. 面向prompt编程，所想既所得；
5. 面向直观、大型、复杂交互（人、物、环境等）的提示工程；
6. 兼容python生态；

**plang尚不完善，欢迎测试、讨论、提交代码（例如：函数库、模型库、示例库等）。**


[//]: # (new type of general-purpose natural language computer.)

## 安装和测试
### 克隆库
```
git clone ...
```

### 安装环境
```
pip install ...
```

### 下载模型
```
当前支持GGML格式模型，更多模型扩展中
```

### 运行示例代码 
```
python plang.py -h
python plang.py -m Llama_GGML -p /path/to/ggml.bin ./examples/sampleTest/sampleTest.p.backtick.md -l ./examples/sampleTest/lib.py
```

## 快速开始
### 关键字
| 关键字     | 含义     | 备注     |
|---------|--------|--------|
| _样式_    | 标记代码区域 | 暂不支持   |
| as      | 赋值     |        |
| or/and  | 列表     |        |
| ;       | 句尾(可选) | 断句歧义使用 |
| do/done | 代码块    | 元编程    |
| `       | 标记代码区域 | 当前版本   |

### 语法

1. 使用字体样式区分字符串和代码（例如：颜色），当前版本使用一对``` ` ```区分代码，暂对``` ` ```符号不透明；
2. 函数和变量调用为：`函数/变量名 参数键值对`

整体规则如下：
```
any prompt string

`funciton/variableName [parameterName parameterValue] [...] [as variableName] [;]`

any prompt string
```
其中，`[]`表示可选，`...`表示0个或多个。

### 函数
```
...
```

## 示例
### 聊天机器人
描述：8行代码实现支持历史记录上下文的聊天机器人。

代码：
```
`while condition` true `then do`
## USER:
`read from` console`;`

## ASSISTANT:
`complete stop at` # `or` : `temperature is` 0.9`;`

`done`
```
样式化代码：

![./examples/chatbotWithHistoryContext/chatbot.p.png](./examples/chatbotWithHistoryContext/chatbot.p.png)

执行结果：
```
## USER:
> 你好，我叫Tony
你好，我叫Tony

## ASSISTANT:
您好，欢迎来到我的世界！有什么我可以帮助您的吗？

## USER:
> 请问你知道我的名字叫什么吗？
请问你知道我的名字叫什么吗？

## ASSISTANT:
是的，我知道。你的名字叫做Tony。

## USER:
> 
```
### 更多
见./examples目录：
```
cd ./examples
ls
```

## TODOs
* [ ] 完善已有函数功能 (./libLang/)
* [ ] 添加更多函数 (./libLang/)
    * [ ] 按照正则表达式生成文本 (./libLang/fill.py 注册参数为："fill", ["regex", ])
* [ ] 添加更多示例 (./examples/)
* [ ] 支持更多模型格式 (./libLLM/)
* [ ] 建立贡献目录 (./contribution/)
* [ ] 完善开发和贡献文档 (./readme.md、./contribution.md)
* [ ] 已知Bug
    * [ ] 参数名与函数名相同时，会将参数名解析为函数名
    * [ ] 名字前缀相同时，会按照最短前缀名字解析

## 相关工作
...
