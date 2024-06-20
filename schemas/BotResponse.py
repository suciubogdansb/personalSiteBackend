from openai import BaseModel


class BotResponse(BaseModel):
    message: str
    role: str