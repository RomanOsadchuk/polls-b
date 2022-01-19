from datetime import datetime
from uuid import UUID

import pytest
from storages import ChoicesStorage, QuestionsStorage
from use_cases.questions.create import create_question


@pytest.fixture
def question_text(event_loop):
    yield "am I good?"
    event_loop.run_until_complete(QuestionsStorage.delete_all())


@pytest.fixture
def choices_texts(event_loop):
    yield ["yeah", "nah", "eeh"]
    event_loop.run_until_complete(ChoicesStorage.delete_all())


@pytest.mark.asyncio
async def test_created_fields(question_text):
    datetime_before = datetime.now()
    question_dict = await create_question(question_text)
    datetime_after = datetime.now()

    assert question_dict["question_text"] == question_text
    assert datetime_before < question_dict["pub_date"] < datetime_after
    assert isinstance(question_dict["uuid"], UUID)

    question = await QuestionsStorage.retrieve_by_uuid(question_dict["uuid"])
    assert question.uuid == question_dict["uuid"]
    assert question.question_text == question_dict["question_text"]
    # assert question.pub_date == question_dict["pub_date"]


@pytest.mark.asyncio
async def test_created_choices(question_text, choices_texts):
    question_dict = await create_question(question_text, choices_texts)

    assert len(question_dict["choices"]) == len(choices_texts)
    for choice_dict in question_dict["choices"]:
        assert choice_dict["votes"] == 0
        choice = await ChoicesStorage.retrieve_by_uuid(choice_dict["uuid"])
        assert choice.votes == 0


@pytest.mark.asyncio
async def test_duplicated_choices(question_text, choices_texts):
    duplicated_texts = choices_texts + choices_texts[:2]
    question_dict = await create_question(question_text, duplicated_texts)
    assert len(question_dict["choices"]) == len(choices_texts)

    choices_count, search_params = 0, {"question_uuid": question_dict["uuid"]}
    async for _ in ChoicesStorage.search(params=search_params):
        choices_count += 1
    assert choices_count == len(choices_texts)
