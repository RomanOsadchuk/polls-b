from datetime import datetime
from uuid import uuid4

import pytest
from storages import ChoicesStorage, QuestionsStorage
from entities import Choice, Question
from use_cases.choices.vote import vote_for_choice


@pytest.fixture
def question(event_loop):
    result = Question(
        uuid=uuid4(),
        pub_date=datetime(2022, 1, 1),
        question_text="How are you?",
    )
    event_loop.run_until_complete(QuestionsStorage.insert_one(result))
    yield result
    event_loop.run_until_complete(QuestionsStorage.delete_all())


@pytest.fixture
def choices(event_loop, question):
    result = [
        Choice(uuid=uuid4(), question_uuid=question.uuid, choice_text="no", votes=2),
        Choice(uuid=uuid4(), question_uuid=question.uuid, choice_text="ok", votes=8),
    ]
    for choice in result:
        event_loop.run_until_complete(ChoicesStorage.insert_one(choice))
    yield result
    event_loop.run_until_complete(ChoicesStorage.delete_all())


@pytest.mark.asyncio
async def test_retrieve_question(question, choices):
    choice_dict = await vote_for_choice(choices[1].uuid)
    updated_choice = await ChoicesStorage.retrieve_by_uuid(choices[1].uuid)
    assert choice_dict["votes"] == choices[1].votes + 1
    assert updated_choice.votes == choices[1].votes + 1
