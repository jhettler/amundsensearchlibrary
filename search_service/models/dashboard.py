from typing import Iterable


class Dashboard:
    def __init__(self, *,
                 dashboard_group: str,
                 dashboard_name: str,
                 description: str,
                 last_reload_time: list,
                 user_id: str,
                 user_name: str,
                 tags: str) -> None:
        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.description = description
        self.last_reload_time = last_reload_time
        self.user_id = user_id
        self.user_name = user_name
        self.tags = tags

    def __repr__(self) -> str:
        return 'Dashboard(dashboard_group={!r}, dashboard_name={!r}, ' \
               'description={!r}, last_reload_time={!r}, user_id={!r},' \
               'user_name={!r}, tags={!r})' \
                            .format(self.dashboard_group,
                                    self.dashboard_name,
                                    self.description,
                                    self.last_reload_time,
                                    self.user_id,
                                    self.user_name,
                                    self.tags)
