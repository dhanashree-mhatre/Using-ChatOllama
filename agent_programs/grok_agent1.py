from langchain_core.prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.tools import tool 
from typing import Optional
from pydantic import BaseModel, Field

@tool
def get_weather(location:str,unit:Optional[str]):
    """Get the current weather for given location"""
    return f"{location} Cloudy with a chance of rain"

chat=ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    groq_api_key="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"
)
tools=[get_weather]

def toolhelper(res):
    tool_mode={tool.name:tool for tool in tools}
    tool_calls=res.tool_calls.copy()
    
    for tool_call in tool_calls:
        tool_call["output"]=tool_mode[tool_call["name"]].invoke(tool_call["args"])

    return tool_calls

tool_model=chat.bind_tools(tools,tool_choice="auto")
chain=tool_model | toolhelper
# res=chain.invoke("What is the weather in india in celcius?")
# print(res)

class Joke(BaseModel):
    """Tell the user a joke"""
    setup: str=Field(description="The setup of the joke")
    punchline:str=Field(description="The punchline of the joke")
    rating:Optional[int]=Field(description="How funny the joke was rate it from 1 to 10")


# structured_llm=chat.with_structured_output(Joke)
#output=structured_llm.invoke("Tell me a joke about cats")
#print(output)

class Poem(BaseModel):
    """Tell the user a poem"""
    title: str=Field(description="The title of the poem")
    body: str=Field(description="The body of the poem")
    author: str=Field(description="The author of the poem")


prompt = ChatPromptTemplate.from_messages([("human", "Write a haiku about {topic}")])

structured_llm=chat.with_structured_output(Poem)
chain = prompt | structured_llm
for chunk in chain.stream({"topic": "The sun"}):
    print(chunk,flush=True,end="")
    #print(chunk.content, end="", flush=True)