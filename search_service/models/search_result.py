from typing import List, Dict
from search_service.models.table import Table
from search_service.models.dashboard import Dashboard


class SearchResult:
    def __init__(self, *,
                 total_results: int,
                 results: Dict) -> None:
        self.total_results = total_results
        self.results = results

    def __repr__(self) -> str:
        return 'SearchResult(total_results={!r}, results{!r})'.format(self.total_results, self.results)
