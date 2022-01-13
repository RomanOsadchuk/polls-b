from datetime import datetime
from uuid import uuid4

from adapters.mongodb import ChoicesColl, QuestionsColl
from entities import Choice, Question


async def create_question(
    question_text: str,
    choices_texts: list[str] = None
) -> dict:

    new_question = Question(
        uuid=uuid4(),
        question_text=question_text,
        pub_date=datetime.now()
    )
    await QuestionsColl.insert_one(new_question)
    result_dict = new_question.as_dict()
    result_dict["choices"] = []

    choices_texts = set(choices_texts) if choices_texts else set()
    for choice_text in choices_texts:
        new_choice = Choice(
            uuid=uuid4(),
            question_uuid=new_question.uuid,
            choice_text=choice_text,
        )
        await ChoicesColl.insert_one(new_choice)
        choice_dict = new_choice.as_dict(exclude={"question_uuid"})
        result_dict["choices"].append(choice_dict)

    return result_dict
