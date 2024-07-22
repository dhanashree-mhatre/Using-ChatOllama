from pydantic import BaseModel


class Message(BaseModel):
    content:str

class UserChatSessionBase(BaseModel):
    pass