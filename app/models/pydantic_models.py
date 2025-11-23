# app/models/pydantic_models.py
from pydantic_models import BaseModel
#the output format
class AnswerResponse(BaseModel):
    answer:str
    pages: list[int]