Answer the following questions as best you can. You have access to the following tools:

CalculatorTool: Useful for when you need to answer questions about math. The input parameter is a mathematical expression.
FinalAnswerTool: Useful for when you need to report the final answer or don't need a tool.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [CalculatorTool, FinalAnswerTool]
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
Action: `select from` CalculatorTool `or` FinalAnswerTool `as nameTool;`
`compare value nameTool and` FinalAnswerTool `as isFinalAnswerTool;`
`if condition isFinalAnswerTool then do
break
done`
Action Input:`complete stop at` Observation `as parameterTool;`
Observation:`complete stop at` Thought`;`
`done`
Final Answer:`complete stop at` Question`;`

`done`
