from datetime import datetime
from uuid import uuid4

import pytest
from entities import Choice, Question
from storages import ChoicesStorage, QuestionsStorage
from use_cases.exceptions import NotFoundError, NotUniqueError
from use_cases.choices.create import create_choice


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
def choice(event_loop, question):
    result = Choice(uuid=uuid4(), question_uuid=question.uuid, choice_text="ok", votes=8)
    event_loop.run_until_complete(ChoicesStorage.insert_one(result))
    yield result
    event_loop.run_until_complete(ChoicesStorage.delete_all())


@pytest.mark.asyncio
async def test_successful_create(question):

    choice_text = "no"
    choice_dict = await create_choice(question.uuid, choice_text)
    assert choice_dict["question_uuid"] == question.uuid
    assert choice_dict["choice_text"] == choice_text

    choice = await ChoicesStorage.retrieve_by_uuid(choice_dict["uuid"])
    assert choice.question_uuid == question.uuid
    assert choice.choice_text == choice_text


@pytest.mark.asyncio
async def test_create_bad_question(question):
    bad_uuid = uuid4()
    with pytest.raises(NotFoundError):
        await create_choice(bad_uuid, "yes")


@pytest.mark.asyncio
async def test_duplicated_choice(question, choice):
    with pytest.raises(NotUniqueError):
        await create_choice(question.uuid, choice.choice_text)
