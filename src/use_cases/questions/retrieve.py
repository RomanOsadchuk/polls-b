from uuid import UUID
from storages import ChoicesStorage, QuestionsStorage
from ..exceptions import NotFoundError


async def retrieve_question(question_uuid: UUID) -> dict:
    question = await QuestionsStorage.retrieve_by_uuid(question_uuid)
    if question is None:
        raise NotFoundError("Question not found")
    result_dict = question.as_dict()
    result_dict["choices"] = []

    search_kwargs = {
        "params": {"question_uuid": question_uuid},
        "ordering": "choice_text",
    }
    async for choice in ChoicesStorage.search(**search_kwargs):
        result_dict["choices"].append(choice.as_dict(exclude={"question_uuid"}))
    return result_dict
