from collections.abc import AsyncGenerator
from typing import Generic, Optional, TypeVar
from dataclasses import fields
from datetime import datetime
from uuid import UUID as PythonUUID

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, \
    create_engine, delete, desc, insert, select, update
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from entities import BaseEntity, Choice, Question


EntityType = TypeVar("EntityType", bound=BaseEntity)


class SingletonDB:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        db_url = "postgres:postgres@localhost/polls"
        self.engine = create_engine(
            f"postgresql://{db_url}", echo=True, future=True)
        self.async_engine = create_async_engine(
            f"postgresql+asyncpg://{db_url}", echo=True)
        self.meta_data = MetaData()


# ==== for database initialization

def to_sql_type(dataclass_field):
    if issubclass(dataclass_field.type, str):
        return String
    elif issubclass(dataclass_field.type, int):
        return Integer
    elif issubclass(dataclass_field.type, datetime):
        return DateTime
    elif issubclass(dataclass_field.type, PythonUUID):
        return PostgresUUID(as_uuid=True)
    else:
        raise TypeError("unsupported type")


def create_table(entity, meta_data):
    columns = [Column(f.name, to_sql_type(f)) for f in fields(entity)]
    return Table(entity.get_storage_name(), meta_data, *columns)


def init_database():
    db = SingletonDB()
    for entity in (Choice, Question):
        create_table(entity, db.meta_data)
    db.meta_data.create_all(db.engine)


# ==== for querying

class BaseMotorAdapter(Generic[EntityType]):
    entity_class = None
    __table = None

    @classmethod
    def get_table(cls):
        if cls.__table is None:
            meta_data = SingletonDB().meta_data
            cls.__table = create_table(cls.entity_class, meta_data)
        return cls.__table

    @classmethod
    async def insert_one(cls, entity_instance: EntityType) -> None:
        insert_dict = entity_instance.as_dict()
        stmt = insert(cls.get_table()).values(**insert_dict)
        async with SingletonDB().async_engine.connect() as conn:
            result = await conn.execute(stmt)
            await conn.commit()

    @classmethod
    async def find_one(cls, params: dict) -> Optional[EntityType]:
        table = cls.get_table()
        stmt = select(table)
        if params:
            where = [getattr(table.c, k) == v for k, v in params.items()]
            stmt = stmt.where(*where)
        async with SingletonDB().async_engine.connect() as conn:
            result = await conn.execute(stmt)
            row = result.fetchone()
            if row:
                return cls.entity_class(*row)

    @classmethod
    async def retrieve_by_uuid(cls, uuid: PythonUUID) -> Optional[EntityType]:
        return await cls.find_one({"uuid": uuid})

    @classmethod
    async def rewrite_fields(cls, uuid: PythonUUID, new_fields: dict) -> None:
        table = cls.get_table()
        stmt = update(table).where(table.c.uuid == uuid).values(**new_fields)
        async with SingletonDB().async_engine.connect() as conn:
            result = await conn.execute(stmt)
            await conn.commit()

    @classmethod
    async def search(
        cls,
        params: dict = None,
        ordering: str = None,
        limit: int = 0,
        offset: int = 0,
    ) -> AsyncGenerator[EntityType, None, None]:

        table = cls.get_table()
        stmt = select(table)
        if params:
            where = [getattr(table.c, k) == v for k, v in params.items()]
            stmt = stmt.where(*where)
        if ordering is not None:
            sort_col = getattr(table.c, ordering.lstrip("-"))
            if ordering.startswith("-"):
                sort_col = desc(sort_col)
            stmt = stmt.order_by(sort_col)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        async with SingletonDB().async_engine.connect() as conn:
            result = await conn.execute(stmt)
            for row in result:  # add async to search
                yield cls.entity_class(*row)

    @classmethod
    async def delete_all(cls) -> None:
        table = cls.get_table()
        stmt = delete(table).where(1 == 1)
        async with SingletonDB().async_engine.connect() as conn:
            result = await conn.execute(stmt)
            await conn.commit()


class QuestionsTable(BaseMotorAdapter[Question]):
    entity_class = Question


class ChoicesTable(BaseMotorAdapter[Choice]):
    entity_class = Choice
