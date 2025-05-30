# <img src="plang.png" width="30" height="30"> PromptLanguage (plang): a string first-class citizen programming language for Large Language Models (LLMs) prompting
(Auto-translated by Google Gemini. Chinese version [here](readme_zh.md).)

Considering Large Language Models (LLMs) as a new computing paradigm for processing knowledge (text), they require a programming language. To this end, we designed PromptLanguage (plang), a programming language where strings are first-class citizens, oriented towards prompt engineering for Large Language Models. Its core syntax rules follow: default parsing to strings, distinguishing strings from code through font styles (e.g., font color), thereby achieving string priority and transparency for any character.
The language has the following features:

1. Intuitive and interactive prompt development;
2. Runs on LLMs, automatically manages context, and interacts conveniently with external APIs;
3. Guides LLMs to output according to expected behavior and format;
4. Prompt-oriented programming, what you think is what you get;
5. Prompt engineering for intuitive, large-scale, complex interactions (human, object, environment, etc.);
6. Compatible with the Python ecosystem;

**plang is still under development. We welcome testing, discussions, and code contributions (e.g., function libraries, model libraries, example libraries, etc.).**


[//]: # (new type of general-purpose natural language computer.)

## Installation and Testing
### Automatic Installation
```bash
pip install git+https://github.com/HJZ-XDU/plang.git
```

### Manual Installation
#### Clone Repository
```bash
git clone https://github.com/HJZ-XDU/plang.git
```

#### Install Environment

```bash
pip install llama_cpp_python regex numpy
```
Note: `llama_cpp_python` version 0.1.79 and above supports GGUF format, versions below 0.1.78 support GGML format. Please choose the version according to your model format.

Or go to [llama_cpp_python](https://github.com/abetlen/llama-cpp-python) for more information.

### Download Models

Currently supports GGML and GGUF format models, more model extensions are in progress.

GGML and GGUF format models can be downloaded from [huggingface.co/TheBloke](https://huggingface.co/TheBloke).

### Run Example Code
```bash
 $ plang.py [--help] [--model [MODEL]] --path PATH [--nContext [NCONTEXT]] [--lib [LIB ...]] [--verbose] FILE
```
Example
```bash
$ python -u plang.py \
  --model Llama_GGML \
  --path /path/to/model.gguf \
  --lib ./examples/sampleTest/lib.py \
  ./examples/chatbotWithHistoryContext/chatbot.p.backtick.md
```
Parameter Description:
- `FILE`: plang program path.
- `--path, -p`: LLM model file path.
-  `--help, -h` (optional): Show help message and exit.
- `--model, -m` (optional): LLM model name, defaults to `Llama_GGML`.
- `--nContext, -n` (optional): LLM context length, defaults to `2048`.
- `--lib, -l` (optional): Library files that may be used in the program, multiple can be specified.
- `--verbose, -v` (optional): Enable verbose mode, output debug information, disabled by default.

## Quick Start
### Keywords
| Keyword     | Meaning     | Notes     |
|---------|--------|--------|
| _Style_    | Mark code area | Character terminal   |
| as      | Assignment     |        |
| or/and  | List     |        |
| ;       | End of sentence (optional) | Used for sentence disambiguation |
| do/done | Code block    | Metaprogramming    |
| `       | Mark code area | **Interim**   |

### Syntax

1. Use font styles to distinguish strings and code (e.g., color). The current version uses a pair of ``` ` ``` to distinguish code, and is temporarily not transparent to the ``` ` ``` symbol;
2. Function and variable calls are: `function/variableName parameterKeyValuePair`

The overall rules are as follows:
```
[some prompt string]

[`function/variableName [parameterName parameterValue] [...] [as variableName] [;]`]

[some prompt string]
```
Where `[]` indicates optional, and `...` indicates 0 or more.

### Built-in Functions

<details>

<summary>complete</summary>

#### Function Signature:

```
`complete [prompt is` parameterValue] [`stop at` parameterValue] [`temperature is` parameterValue] 
```

#### Function Description:

This function is used to perform inference on a given prompt using a large language model. Custom stop tokens and the temperature parameter for inference can be defined.

#### Parameter Description:

`prompt is` (optional): Specifies the prompt for the large language model. If this item is not present, the large language model's prompt will be set to all text parsed in the program previously.

`stop at` (optional): Sets the collection of inference stop tokens.

`temperature is` (optional): Sets the temperature parameter for large language model inference.

#### Return Value Description:

prompt: The resulting string from model inference (the prompt return value will be added to the program context).

as: The resulting string from model inference (the as return value will be assigned to the variable after as).

#### Usage Example:
```
`complete prompt is` How many days in a common year? `stop at` # `or` : `temperature is` 0.9 `;`
```
#### Styled Code:
![./examples/functionTest/completeReadme.p.png](examples/functionReadme/completeReadme.p.png)

#### Execution Result:
```
A common year has 365 days.
```
***
</details>

<details>
<summary>select</summary>

#### Function Signature:
```
`select from` parameterValue [`or` parameterValue] […] 
```

#### Function Description:

This function is used to constrain the output of the large language model, making it output one of the elements from the set after `from`. The selection is based on the probability of the large language model's inference results.

#### Parameter Description:

`from`: This parameter accepts a collection of elements.

#### Return Value Description:

prompt: The element with the highest probability from the collection after `from`.

as: The element with the highest probability from the collection after `from`.

#### Usage Example:
```
`select from` A `or` B `or` C 
```
Styled Code:

![./examples/functionTest/selectReadme.p.png](examples/functionReadme/selectReadme.p.png)

Execution Result:
```
A
```

***
</details>

<details>
<summary>match</summary>

#### Function Signature:
```
`match regex` parameterValue [`with max token` parameterValue]
```

#### Function Description:

This function is used to constrain the output of the large language model, generating text based on a regular expression.

#### Parameter Description:

`regex`: This parameter accepts a regular expression.

`with max token`: This parameter accepts an integer, representing the maximum matching length of the regular expression.

#### Return Value Description:

prompt: Text generated by the large language model based on the regular expression.

as: Text generated by the large language model based on the regular expression.

#### Usage Example:
```
`match regex` \(\d{3}\) 555-\d{4,} `with max token` 14 `;`
```
#### Styled Code:

![./examples/functionTest/matchReadme.p.png](examples/functionReadme/matchReadme.p.png)

#### Execution Result:
```
(189) 555-5555
```

***
</details>

<details>
<summary>read</summary>

#### Function Signature:

```
`read from` parameterValue
```

#### Function Description:

This function accepts external input, currently only supporting input from the command line.

#### Parameter Description:

`from`: This parameter accepts the source of external input, currently only supporting `console`.

#### Return Value Description:

prompt: The content of the external input.

as: The content of the external input.

#### Usage Example:
```
`read from` console
```

#### Styled Code:

![./examples/functionTest/readReadme.p.png](examples/functionReadme/readReadme.p.png)

#### Execution Result:
```
> hi
hi
```
***
</details>
<details>
<summary>set</summary>

#### Function Signature:

```
`set value/not` parameterValue
```

#### Function Description:

When using `value`, this function is used for assignment operations and needs to be used with `as`.

When using `not`, this function is used to determine if `parameterValue` is in the false list.

False list: `[None, 0, False, 'None', '0', 'False', '', list(), tuple(), dict(), set()]`

#### Parameter Description:

`value`: This parameter accepts the value to be assigned.

`not`: This parameter accepts an expression or variable name, indicating whether the value to be assigned is in the false list.

#### Return Value Description:

prompt: Empty string `''`.

as: When using `value`, returns the value of `value`; when using `not`, returns `true` or `false`. The determination is based on whether the value of `value` is in the specified false list.

#### Usage Example:
```
`set value` true `as variable`
`set not variable as variable`
variable：`variable`
```
#### Styled Code:

![./examples/functionTest/setReadme.p.png](examples/functionReadme/setReadme.p.png)

#### Execution Result:
```
variable：False
```
***

</details>
<details>
<summary>call</summary>

#### Function Signature:

```
`call function` parameterValue [`with parameter` parameterValue [`and` parameterValue] […] ]
```

#### Function Description:

Calls a function by its name. Parameters must be passed in the order defined by the function.

#### Parameter Description:

`function`: This parameter accepts the function name.

`with parameter`: This parameter accepts the function's parameters. Multiple parameters can be specified, but they must be passed in the order defined by the function.

#### Return Value Description:

prompt: Empty string `''`.

as: The return value of the called function.

#### Usage Example:
```
`call function` complete `with parameter` How many days in a common year? `and` # `and` 0.9 `as result`
result：`result`
```

#### Styled Code:

![./examples/functionTest/callReadme.p.png](examples/functionReadme/callReadme.p.png)

#### Execution Result:
```
A common year, also known as a non-leap year, has 365 days.
result：
A common year, also known as a non-leap year, has 365 days.
```
***

</details>
<details>
<summary>if</summary>

#### Function Signature:

```
`if condition` parameterValue `then do`
parameterValue(program)
`done`
```

#### Function Description:

This function implements an if conditional statement. Whether the if block is executed depends on the value of `condition`. If the value of `condition` is in the false list, the if block is not executed; otherwise, it is executed.

False list: `[None, 0, False, 'None', '0', 'False', '', list(), tuple(), dict(), set()]`

#### Parameter Description:

`condition`: This parameter accepts an expression or variable name, representing the condition for the loop.

`then`: This parameter accepts the code block of the loop body, containing the operations to be executed in the loop.

#### Return Value Description:

prompt: Empty string `''`.

as: The value of `condition`.

#### Usage Example:
```
`if condition` true `then do`
This statement will be executed.
`done`
```
Styled Code:

![./examples/functionTest/ifReadme.p.png](examples/functionReadme/ifReadme.p.png)

#### Execution Result:
```
This statement will be executed.
```
***
</details>
<details>
<summary>while</summary>

#### Function Signature:

```
`while condition` parameterValue `then do`
parameterValue(program)
`done`
```

#### Function Description:

This function implements the functionality of a while loop statement. Whether the while loop is executed depends on the value of `condition`. If the value of `condition` is in the false list, the while loop is not executed; otherwise, it is executed.

False list: `[None, 0, False, 'None', '0', 'False', '', list(), tuple(), dict(), set()]`

#### Parameter Description:

`condition`: This parameter accepts an expression or variable name, representing the condition for the loop.

`then`: This parameter accepts the code block of the loop body, containing the operations to be executed in the loop.

#### Return Value Description:

prompt: Empty string `''`.

as: The value of `condition`.

#### Usage Example:
```
`while condition` true `then do`
executing loop body
`done`
```
#### Styled Code:

![./examples/functionTest/whileReadme.p.png](examples/functionReadme/whileReadme.p.png)

#### Execution Result:
```
executing loop body
executing loop body
executing loop body
...
```
***
</details>

<details>
<summary>for</summary>

#### Function Signature:
```
`for each` parameterValue [`or` parameterValue] […] `then`
parameterValue(program)
`done`
```

#### Function Description:

This function iterates through each element in `each`, and for each element, executes the operations in the loop body within `then`.

#### Parameter Description:

`each`: This parameter accepts the collection of elements to be iterated over.

`then`: This parameter accepts the code block of the loop body, containing the operations to be executed in the loop.

#### Return Value Description:

prompt: Empty string `''`.

as: The current element being iterated over in the `for` loop.

#### Usage Example:

```
`for each` a `or` b `or` c `then do`
item： `item`
`done as item`
```
#### Styled Code:

![./examples/functionTest/forReadme.p.png](examples/functionReadme/forReadme.p.png)

#### Execution Result:
```
item： a
item： b
item： c
```
***
</details>

<details>

<summary>compare</summary>
Function Signature:

```
`compare value` parameterValue [`and` parameterValue] […]
```

#### Function Description:

This function is used to compare whether all elements in the `value` collection are identical.

#### Parameter Description

`value`: Accepts the collection of elements for comparison.

#### Return Value Description:

prompt: Empty string `''`.

as: Returns `true` if all elements in the `value` collection are identical, otherwise `false`.

#### Usage Example:
```
`compare value` true `and` false `as isEqual`
isEqual：`isEqual`
```

#### Styled Code:

![./examples/functionTest/compareReadme.p.png](examples/functionReadme/compareReadme.p.png)

#### Execution Result:
```
isEqual：False
```

***
</details>

<details>

<summary>break</summary>

#### Function Signature:
```
`break`
```

#### Function Description:

When used within a loop, it is used to exit the loop, regardless of whether the loop's condition is met.

#### Parameter Description:

None

#### Return Value Description:

prompt: Empty string `''`.

as: `'break'`.

#### Usage Example:
```
`while condition` true `then do
break`
This statement will not be executed.
`done`
This statement will be executed.
```
#### Styled Code:

![./examples/functionTest/breakReadme.p.png](examples/functionReadme/breakReadme.p.png)

#### Execution Result:
```
This statement will be executed.
```
***
</details>

<details>
<summary>continue</summary>

#### Function Signature:

```
`continue` 
```

#### Function Description:

Implements the continue statement, mainly used in loop structures. It is typically used when, under certain conditions, one wishes to skip the current iteration and proceed directly to the next.

#### Parameter Description:

None

#### Return Value Description:

prompt: Empty string `''`.

as: `'continue'`.

#### Usage Example:
```
`for each` a `or` b `then do`
This statement will be executed: `item`
`continue`
This statement will not be executed: `item`
`done as item`
```

#### Styled Code:

![./examples/functionTest/continueReadme.p.png](examples/functionReadme/continueReadme.p.png)

Execution Result:
```
This statement will be executed: a
This statement will be executed: b
```
***
</details>

<details>

<summary>comment</summary>

#### Function Signature:

```
`# /` variableValue
```

#### Function Description:

This function is used for commenting.

#### Parameter Description:

`/` : The value accepted by this parameter will be commented out.

#### Return Value Description:

prompt: Empty string `''`.

as: No return value, i.e., `None`.

#### Usage Example:
```
This statement will not be commented out.
`# /` This statement will be commented out.
```
#### Styled Code:

![./examples/functionTest/commentReadme.p.png](examples/functionReadme/commentReadme.p.png)

#### Execution Result:
```
This statement will not be commented out.
```
***
</details>

## Examples
### Chatbot
Description: 8 lines of code implement a chatbot that supports history context.

Code:
```
`while condition` true `then do`
## USER:
`read from` console`;`

## ASSISTANT:
`complete stop at` # `or` : `temperature is` 0.9`;`

`done`
```
Styled Code:

![./examples/chatbotWithHistoryContext/chatbot.p.png](./examples/chatbotWithHistoryContext/chatbot.p.png)

Command Line Startup Statement:
```
$ python plang.py \
  --model Llama_GGML \
  --path /path/to/model.gguf \
  ./examples/chatbotWithHistoryContext/chatbot.p.backtick.md
```

Execution Result:
```
## USER:
> Hello, my name is Tony
Hello, my name is Tony

## ASSISTANT:
Hello, welcome to my world! How can I help you?

## USER:
> Do you know my name?
Do you know my name?

## ASSISTANT:
Yes, I do. Your name is Tony.

## USER:
> 
```
### ReAct Tool Invocation
Description: Access the plangSearchTool to answer questions about plang.

Code:
```
Answer the following questions as best you can. You have access to the following tools:

plangSearchTool: Useful for when you need to answer questions about plang. The input parameter are search keywords.
FinalAnswerTool: Useful for when you need to report the final answer or don't need a tool.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [plangSearchTool, FinalAnswerTool]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Action: FinalAnswerTool
Final Answer: the final answer to the original input question

Begin!

`while condition` true `then do`
Question: `read from` console`;`
`while condition` true `then do`
Thought:`complete stop at` Action`;`
Action: `select from` plangSearchTool `or` FinalAnswerTool `as nameTool;`
`compare value nameTool and` FinalAnswerTool `as isFinalAnswerTool;`
`if condition isFinalAnswerTool then do
break
done`
Action Input:`complete stop at` Observation `as parameterTool;`
Observation: `call function nameTool with parameter parameterTool;`
`done`
Final Answer:`complete stop at` Question`;`

`done`
```
Styled Code:

![./examples/ReAct/react.p.png](./examples/ReAct/react.p.png)

Command Line Startup Statement:
```
$ python plang.py \
  --model Llama_GGML \
  --path /path/to/model.gguf \
  --lib ./examples/ReAct/lib.py \
  ./examples/ReAct/react.p.backtick.md
```

Execution Result
```
Answer the following questions as best you can. You have access to the following tools:

plangSearchTool: Useful for when you need to answer questions about plang. The input parameter are search keywords.
FinalAnswerTool: Useful for when you need to report the final answer or don't need a tool.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [plangSearchTool, FinalAnswerTool]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Action: FinalAnswerTool
Final Answer: the final answer to the original input question

Begin!

Question: > What is plang?
What is plang?
Thought: I need to find out what plang is, so I will use plangSearchTool.
Action: plangSearchTool
Action Input: plang
Observation: {"keyword": "plang", "result": "PromptLanguage (plang): a string first-class citizen programming language for Large Language Models (LLMs) prompting"}
Thought: I now know the final answer.
Action: FinalAnswerTool
Final Answer: plang is a string first-class citizen programming language for Large Language Models (LLMs) prompting.

Question: > 
```

### miniAutoGen
Description: Multiple agents self-organize to speak, write code, and execute code to complete user instructions.

Code:
```
Below is a conversation organized in Markdown format between a customer, project manager, programmer, and tester:

## Project Manager:
Welcome to the group chat! Work together to resolve Customer's task.

## Project Manager:
Customer, you are responsible for presenting the requirements.

## Project Manager:
Project Manager (me), I'm responsible for overall scheduling and reply the word **TERMINATE** after confirming that the requirement is fulfilled.

## Project Manager:
Programmer, you are responsible for writing the Python code and placing the code in a Markdown code block.

## Project Manager:
Tester, you are responsible for run the code and report the results.

## Project Manager:
Hi Customer, what's your requirements?

## Customer:
`read from` console`;`

`while condition` true `then do`
## `select from` Customer `or` Project Manager `or` Programmer `or` Tester `as speaker;`:
`compare value speaker and` Tester `as isTester;`
`if condition isTester then do
python run code message`

`continue
done`
`complete stop at` ## `or` TERMINATE `as message;`
`set not message as isEmptyMessage;`
`if condition isEmptyMessage then do`
TERMINATE
`break
done`

`done`
```
Styled Code:

![./examples/miniAutoGen/miniAutoGen.p.png](./examples/miniAutoGen/miniAutoGen.p.png)

Command Line Startup Statement:
```
$ python plang.py \
  --model Llama_GGML \
  --path /path/to/model.gguf \
  --lib ./examples/miniAutoGen/lib.py \
  ./examples/miniAutoGen/miniAutoGen.p.backtick.md
```
Execution Result:
```
Below is a conversation organized in Markdown format between a customer, project manager, programmer, and tester:

## Project Manager:
Welcome to the group chat! Work together to resolve Customer's task.

## Project Manager:
Customer, you are responsible for presenting the requirements.

## Project Manager:
Project Manager (me), I'm responsible for overall scheduling and reply the word **TERMINATE** after confirming that the requirement is fulfilled.

## Project Manager:
Programmer, you are responsible for writing the Python code and placing the code in a Markdown code block.

## Project Manager:
Tester, you are responsible for run the code and report the results.

## Project Manager:
Hi Customer, what's your requirements?

## Customer:
> Calculating prime numbers between 0 and 10.
Calculating prime numbers between 0 and 10.

## Programmer:
Here is the Python code to calculate prime numbers between 0 and 10:

```python
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

numbers = [i for i in range(11)]
prime_numbers = [i for i in numbers if is_prime(i)]
print(prime_numbers)
`` ` 

## Tester:
The Python interpreter returns: {"stdout": "[2, 3, 5, 7]\n", "stderr": ""}

## Project Manager:
Great job! Customer, your requirement is fulfilled. 

## Project Manager:
TERMINATE
```

### More
See the ./examples directory:
```
cd ./examples
ls
```

## TODOs
* [ ] Improve existing function features (./libLang/)
* [ ] Add more functions (./libLang/)
    * [x] Generate text according to regular expressions (./libLang/fill.py register parameters as: "fill", ["regex", ]) // Note: "fill" -> "match"
* [ ] Add more examples (./examples/)
* [ ] Support more model formats (./libLLM/)
* [ ] Establish contribution directory (./contribution/)
* [ ] Improve development and contribution documentation (./readme.md, ./contribution.md)
* [ ] Known Bugs
    * [ ] When a parameter name is the same as a function name, the parameter name will be parsed as a function name
    * [ ] When name prefixes are the same, it will be parsed according to the shortest prefix name

## Related Work (prompting technology)
- String Template Type
  - Natural language text
  - Text interspersed with "placeholders"
- API Programming Type
  - Code Programming
    - LangChain: https://github.com/langchain-ai/langchain
    - Semantic Kernel: https://github.com/microsoft/semantic-kernel
    - MiniChain: https://github.com/srush/MiniChain
    - AutoGen: https://github.com/microsoft/autogen
    - CrewAI: https://github.com/joaomdmoura/crewAI
  - Graphical Programming
    - Langflow: https://github.com/logspace-ai/langflow
    - Flowise: https://github.com/FlowiseAI/Flowise
    - Prompt flow: https://github.com/microsoft/promptflow
  - Configuration Files
    - Guardrails: https://github.com/guardrails-ai/guardrails
    - NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails
- Embedding Prompts in Programs Type
  - guidance: https://github.com/guidance-ai/guidance
  - LMQL: https://github.com/eth-sri/lmql
  - SGLang: https://github.com/sgl-project/sglang
  - LCEL (LangChain): https://python.langchain.com/docs/expression_language/
  - Marvin: https://github.com/PrefectHQ/marvin
  - TypeChat: https://github.com/microsoft/TypeChat
- Embedding Programs in Prompts Type
  - PromptLanguage (plang) [ours]: https://github.com/HJZ-XDU/plang

## Acknowledged Projects
- llama-cpp-python：https://github.com/abetlen/llama-cpp-python