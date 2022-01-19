from datetime import datetime
from uuid import uuid4

import pytest
from entities import Question
from storages import QuestionsStorage
from use_cases.questions.search import search_questions


@pytest.fixture
def questions(event_loop):
    result = [
        Question(uuid=uuid4(), pub_date=datetime(2022, 1, 1), question_text="Q3?"),
        Question(uuid=uuid4(), pub_date=datetime(2022, 1, 2), question_text="Q2?"),
        Question(uuid=uuid4(), pub_date=datetime(2022, 1, 3), question_text="Q1?"),
    ]
    for question in result:
        event_loop.run_until_complete(QuestionsStorage.insert_one(question))
    yield result
    event_loop.run_until_complete(QuestionsStorage.delete_all())


@pytest.mark.asyncio
async def test_questions_order(questions):
    questions_list = await search_questions(-1, -1)
    for question_dict, question in zip(questions_list, reversed(questions)):
        assert question_dict["uuid"] == question.uuid
        assert question_dict["pub_date"] == question.pub_date
        assert question_dict["question_text"] == question.question_text


@pytest.mark.asyncio
async def test_questions_offset(questions):
    offset = 2
    questions_list = await search_questions(offset=offset, limit=-1)
    assert len(questions_list) == len(questions) - offset


@pytest.mark.asyncio
async def test_questions_limit(questions):
    limit = 2
    questions_list = await search_questions(offset=-1, limit=limit)
    assert len(questions_list) == limit
