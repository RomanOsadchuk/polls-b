from datetime import datetime
from uuid import uuid4

import pytest
from adapters.mongodb import ChoicesColl, QuestionsColl
from entities import Choice, Question
from use_cases.questions.retrieve import retrieve_question


@pytest.fixture
def question(event_loop):
    result = Question(
        uuid=uuid4(),
        pub_date=datetime(2022, 1, 1),
        question_text="How are you?",
    )
    event_loop.run_until_complete(QuestionsColl.insert_one(result))
    yield result
    event_loop.run_until_complete(QuestionsColl.delete_all())


@pytest.fixture
def choices(event_loop, question):
    result = [
        Choice(uuid=uuid4(), question_uuid=question.uuid, choice_text="no", votes=2),
        Choice(uuid=uuid4(), question_uuid=question.uuid, choice_text="ok", votes=8),
    ]
    for choice in result:
        event_loop.run_until_complete(ChoicesColl.insert_one(choice))
    yield result
    event_loop.run_until_complete(ChoicesColl.delete_all())


@pytest.mark.asyncio
async def test_retrieve_question(question, choices):

    question_dict = await retrieve_question(question.uuid)
    assert question_dict["uuid"] == question.uuid
    assert question_dict["pub_date"] == question.pub_date
    assert question_dict["question_text"] == question.question_text

    # also checking alphabetical ordering
    for i, choice_dict in enumerate(question_dict["choices"]):
        assert choice_dict["uuid"] == choices[i].uuid
        assert choice_dict["votes"] == choices[i].votes
        assert choice_dict["choice_text"] == choices[i].choice_text


@pytest.mark.asyncio
async def test_retrieve_non_existing_question():
    bad_uuid = uuid4()
    with pytest.raises(ValueError):
        await retrieve_question(bad_uuid)
