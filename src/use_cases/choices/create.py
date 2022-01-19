from uuid import uuid4, UUID
from entities import Choice
from storages import ChoicesStorage, QuestionsStorage
from ..exceptions import NotFoundError, NotUniqueError


async def create_choice(question_uuid: UUID, choice_text: str) -> dict:

    question = await QuestionsStorage.retrieve_by_uuid(question_uuid)
    if question is None:
        raise NotFoundError("Question not found")

    params = {"question_uuid": question_uuid, "choice_text": choice_text}
    same_choice = await ChoicesStorage.find_one(params=params)
    if same_choice is not None:
        raise NotUniqueError("Choice already exists")

    new_choice = Choice(
        uuid=uuid4(),
        question_uuid=question_uuid,
        choice_text=choice_text,
    )
    await ChoicesStorage.insert_one(new_choice)
    return new_choice.as_dict()
