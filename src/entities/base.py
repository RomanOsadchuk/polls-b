from collections.abc import Iterable
from dataclasses import asdict, dataclass
from uuid import UUID


@dataclass
class BaseEntity:
    uuid: UUID

    def as_dict(self, exclude: Iterable[str] = None) -> dict:
        result = asdict(self)
        if exclude:
            for field in exclude:
                result.pop(field)
        return result
