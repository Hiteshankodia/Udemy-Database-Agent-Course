from langchain.agents import tool
from langchain_openai import AzureChatOpenAI
from sql_agent import sql_agent 



llm = AzureChatOpenAI(
    
)

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

result = get_word_length.invoke("abc")


print("result")
print(result)



tools = [get_word_length, sql_agent]


#Binding the tools
llm_with_tools = llm.bind_tools(tools)

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You are very powerful assistant, but don't know current events,
            If you have queries related to movies run the sql agent. 
            If you have queries related to sports run the csv agent'''

        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)


from langchain.agents import AgentExecutor, create_tool_calling_agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = agent_executor.invoke({"input": "What is the length of this character - 'abc'"})

print('agent : ', result)


sql_result = agent_executor.invoke({'input' : 'Give me movie name with highest budget'})