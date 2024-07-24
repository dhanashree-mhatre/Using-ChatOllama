from langchain_core.tools import tool
from langchain import hub 
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv('.env')

@tool
def multiply(first_num:int,second_num:int):
    """Multiply two integers together."""
    return first_num*second_num

@tool 
def add(first_num:int,second_num:int):
    "Add two integers."
    return first_num+second_num

@tool
def exponentiate(base:int,exponent:int):
    "Exponentiate the base to the exponent power."
    return base**exponent

tools=[multiply,add,exponentiate]

prompt = hub.pull("hwchase17/openai-tools-agent")
llm =ChatOllama(model="tinyllama")
agent=create_tool_calling_agent(llm=llm,tools=tools,prompt=prompt)
agent_executor=AgentExecutor(agent=agent,tools=tools,verbose=True)

agent_executor.invoke(
    {
        "input": "Take 3 to the 16 power and multiply that by the sum of nine and three, then square the whole result"
    }
)