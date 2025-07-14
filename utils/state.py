from pydantic import BaseModel
from typing import Optional, List, TypedDict


class User_Info(BaseModel):
    name: Optional[str] = None
    agreed_to_coffee: Optional[bool] = None


class ConversationState(TypedDict):
    history: List[str]
    info: User_Info
