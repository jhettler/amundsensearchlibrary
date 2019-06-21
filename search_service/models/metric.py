from typing import Iterable


class Metric:
    def __init__(self, *,
                 dashboard_group: str,
                 dashboard_name: str,
                 metric_name: str,
                 metric_description: str,
                 metric_type: str,
                 metric_group: str) -> None:
        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.metric_name = metric_name
        self.metric_description = metric_description
        self.metric_type = metric_type
        self.metric_group = metric_group

    def __repr__(self) -> str:
        return 'Metric(dashboard_group={!r}, dashboard_name={!r}, ' \
               'metric_name={!r}, metric_description={!r},' \
               'metric_type={!r}, metric_group={!r})' \
                            .format(self.dashboard_group,
                                    self.dashboard_name,
                                    self.metric_name,
                                    self.metric_description,
                                    self.metric_type,
                                    self.metric_group)
