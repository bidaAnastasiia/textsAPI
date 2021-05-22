from pydantic import BaseModel, PositiveInt


class Message(BaseModel):
    id: PositiveInt = None
    message_text: str
    views_counter: PositiveInt = 0
