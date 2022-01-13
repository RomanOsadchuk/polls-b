from uuid import uuid4, UUID
from adapters.mongodb import ChoicesColl, QuestionsColl
from entities import Choice


async def create_choice(
    question_uuid: UUID,
    choice_text: str,
) -> dict:

    question = await QuestionsColl.retrieve_by_uuid(question_uuid)
    if question is None:
        raise ValueError("invalid question_uuid")

    params = {"question_uuid": question_uuid, "choice_text": choice_text}
    same_choice = await ChoicesColl.find_one(params=params)
    if same_choice:
        raise ValueError("choice_text already exists")

    new_choice = Choice(
        uuid=uuid4(),
        question_uuid=question_uuid,
        choice_text=choice_text,
    )
    await ChoicesColl.insert_one(new_choice)
    return new_choice.as_dict()
