from uuid import UUID
from adapters.mongodb import ChoicesColl


async def vote_for_choice(choice_uuid: UUID) -> dict:
    choice = await ChoicesColl.retrieve_by_uuid(choice_uuid)
    if choice is None:
        raise ValueError("Not found")

    choice.votes += 1
    await ChoicesColl.rewrite_fields(
        choice_uuid, {"votes": choice.votes}
    )
    return choice.as_dict()
