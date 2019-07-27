from typing import Set
from .base import Base


class Metric(Base):
    def __init__(self, *,
                 name: str,
                 description: str,
                 type: str,
                 dashboards: str,
                 tags: str) -> None:
        self.name = name
        self.description = description
        self.type = type
        self.dashboards = dashboards
        self.tags = tags

    @classmethod
    def get_attrs(cls) -> Set:
        return {
            'name',
            'description',
            'type',
            'dashboards',
            'tags'
        }

    def __repr__(self) -> str:
        return 'Metric(name={!r}, description={!r},' \
               'type={!r}, dashboards={!r}), tags={!r})' \
            .format(self.name,
                    self.description,
                    self.type,
                    self.dashboards,
                    self.tags)
