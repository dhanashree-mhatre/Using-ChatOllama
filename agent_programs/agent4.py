from operator import itemgetter
from typing import Dict,List

from langchain_core.messages import AIMessage
from langchain_core.tools import tool 
from langchain_core.runnables import Runnable,RunnablePassthrough
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os


@tool
def count_emails(last_n_days: int) -> int:
    """Multiply two integers together."""
    return last_n_days * 2


@tool
def send_email(message: str, recipient: str) -> str:
    "Add two integers."
    return f"Successfully sent email to {recipient}."



llm=ChatOpenAI(model="gpt-3.5-turbo", verbose=True)
tools = [count_emails, send_email]
llm_with_tools = llm.bind_tools(tools)

def call_tools(msg: AIMessage) -> List[Dict]:
    """Simple sequential tool calling helper."""
    tool_map = {tool.name: tool for tool in tools}
    tool_calls = msg.tool_calls.copy()
    for tool_call in tool_calls:
        tool_call["output"] = tool_map[tool_call["name"]].invoke(tool_call["args"])
    return tool_calls


chain = llm | call_tools

query="graet vensis poet line numaber 15 is what?"
prompt=f"""
You are good question optimier. Your work is to make this question more consise and proper.
so that the we can search throught the information.
query:{query}
"""
output=llm.invoke(prompt)
print(output)
# output=chain.invoke("how many emails did i get in the last 5 days?")

# print(output)

