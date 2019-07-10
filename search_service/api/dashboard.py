from http import HTTPStatus
from typing import Iterable, Any

from flask_restful import Resource, fields, marshal_with, reqparse, marshal

from search_service.proxy import get_proxy_client

dashboard_fields = {
    "dashboard_group": fields.String,
    "dashboard_name": fields.String,
    # description can be empty, if no description is present in DB
    "description": fields.String,
    "last_reload_time": fields.String,
    "user_id": fields.String,
    "user_name": fields.String,
    "tags": fields.List(fields.String)
}

search_dashboard_results = {
    "total_results": fields.Integer,
    "results":  fields.Nested(dashboard_fields)
}

DASHBOARD_INDEX = 'dashboards_alias'


class SearchDashboardAPI(Resource):
    """
    Search Dashboard API
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=DASHBOARD_INDEX, type=str)

        super(SearchDashboardAPI, self).__init__()

    @marshal_with(search_dashboard_results)
    def get(self) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of dashboard results. List can be empty if query
        doesn't match any dashboards
        """
        args = self.parser.parse_args(strict=True)

        try:

            results = self.proxy.fetch_dashboard_search_results(
                query_term=args['query_term'],
                page_index=args['page_index'],
                index=args['index']
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR


class SearchDashboardFieldAPI(Resource):
    """
    Search Dashboard API with explict field
    """

    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)
        self.parser.add_argument('index', required=False, default=DASHBOARD_INDEX, type=str)
        super(SearchDashboardFieldAPI, self).__init__()

    @marshal_with(search_dashboard_results)
    def get(self, *, field_name: str,
            field_value: str, **kwargs) -> Iterable[Any]:
        """
        Fetch search results based on query_term.

        :param field_name: which field we should search from(schema, tag, dashboard)
        :param field_value: the value to search for the field
        :return: list of dashboard results. List can be empty if query
        doesn't match any dashboards
        """
        args = self.parser.parse_args(strict=True)

        try:
            results = self.proxy.fetch_dashboard_search_results_with_field(
                query_term=args.get('query_term', ''),
                field_name=field_name,
                field_value=field_value,
                page_index=args['page_index'],
                index=args.get('index')
            )

            return results, HTTPStatus.OK

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
