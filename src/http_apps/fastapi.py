from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel

from use_cases import choices as choices_uc
from use_cases import questions as questions_uc


app = FastAPI()


# ==== questions

class QuestionData(BaseModel):
    question_text: str
    choices_texts: list[str] = []


@app.post("/questions/")
async def create_question(question_data: QuestionData):
    return await questions_uc.create_question(**question_data.dict())


@app.get("/questions/")
async def search_questions(offset: int = 0, limit: int = 10):
    return await questions_uc.search_questions(offset, limit)


@app.get("/questions/{question_uuid}/")
async def retrieve_question(question_uuid: UUID):
    return await questions_uc.retrieve_question(question_uuid)


# ==== choices

class ChoiceData(BaseModel):
    question_uuid: UUID
    choice_text: str


@app.post("/choices/")
async def create_choice(choice_data: ChoiceData):
    return await choices_uc.create_choice(**choice_data.dict())


@app.post("/choices/{choice_uuid}/vote/")
async def vote(choice_uuid: UUID):
    return await choices_uc.vote_for_choice(choice_uuid)
