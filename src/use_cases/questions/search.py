from adapters.mongodb import QuestionsColl


async def search_questions(offset: int, limit: int) -> list[dict]:
    result_list = []
    search_kwargs = {"ordering": "-pub_date", "limit": limit, "offset": offset}
    async for question in QuestionsColl.search(**search_kwargs):
        result_list.append(question.as_dict())
    return result_list
