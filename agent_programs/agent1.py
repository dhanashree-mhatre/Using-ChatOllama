from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent
)
from langchain_core.tools import Tool 
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import datetime

def get_current_time(*args,**kwargs):
    ''' Returns current time in HH:MM AM/PM format '''
    
    now=datetime.datetime.now()
    return now.strftime("%I:%M %p")


tools=[
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you want to get current time."
    ),
]

prompt=hub.pull("hwchase17/react")

# llm=ChatOllama(
#     model="tinyllama",
#     temperature=0
# )
#llm_with_tools=llm.bind_tools([multiply])
llm=ChatOpenAI(model="gpt-3.5-turbo")

agent=create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True
)
agent_executer=AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)
response=agent_executer.invoke({"input":"what time it is?"})
print("response", response)


