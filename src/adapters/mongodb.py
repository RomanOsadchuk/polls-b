from collections.abc import AsyncGenerator
from typing import Generic, Optional, TypeVar
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient
from entities import BaseEntity, Choice, Question
from settings import DB_URL


EntityType = TypeVar("EntityType", bound=BaseEntity)


class BaseMotorAdapter(Generic[EntityType]):
    collection_name = None
    entity_class = None

    @classmethod
    def get_collection(cls):
        database = AsyncIOMotorClient(DB_URL).get_default_database()
        return database[cls.collection_name]

    @classmethod
    async def insert_one(cls, entity_instance: EntityType) -> None:
        await cls.get_collection().insert_one(entity_instance.as_dict())

    @classmethod
    async def find_one(cls, params: dict) -> Optional[EntityType]:
        doc = await cls.get_collection().find_one(params)
        if doc is not None:
            doc.pop("_id")
            return cls.entity_class(**doc)

    @classmethod
    async def retrieve_by_uuid(cls, uuid: UUID) -> Optional[EntityType]:
        return await cls.find_one({"uuid": uuid})

    @classmethod
    async def rewrite_fields(cls, uuid: UUID, new_fields: dict) -> None:
        await cls.get_collection().update_one(
            {'uuid': uuid}, {'$set': new_fields}
        )

    @classmethod
    async def search(
        cls,
        params: dict = None,
        ordering: str = None,
        limit: int = 0,
        offset: int = 0,
    ) -> AsyncGenerator[EntityType, None, None]:

        pipeline = []
        if params:
            pipeline += [{"$match": params}]
        if ordering is not None:
            sort_order = -1 if ordering.startswith("-") else 1
            sort_field = ordering.lstrip("-")
            pipeline += [{"$sort": {sort_field: sort_order}}]
        if offset > 0:
            pipeline += [{"$skip": offset}]
        if limit > 0:
            pipeline += [{"$limit": limit}]
        async for doc in cls.get_collection().aggregate(pipeline):
            doc.pop("_id")
            yield cls.entity_class(**doc)

    @classmethod
    async def delete_all(cls) -> None:
        await cls.get_collection().delete_many({})


class QuestionsColl(BaseMotorAdapter[Question]):
    collection_name = "questions"
    entity_class = Question


class ChoicesColl(BaseMotorAdapter[Choice]):
    collection_name = "choices"
    entity_class = Choice
