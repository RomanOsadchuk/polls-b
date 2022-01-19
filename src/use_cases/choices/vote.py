from uuid import UUID
from storages import ChoicesStorage
from ..exceptions import NotFoundError


async def vote_for_choice(choice_uuid: UUID) -> dict:
    choice = await ChoicesStorage.retrieve_by_uuid(choice_uuid)
    if choice is None:
        raise NotFoundError("Choice not found")

    choice.votes += 1
    await ChoicesStorage.rewrite_fields(
        choice_uuid, {"votes": choice.votes}
    )
    return choice.as_dict()
