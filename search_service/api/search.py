from typing import Iterable, Any

from flask_restful import Resource, fields, marshal_with, reqparse, marshal

from search_service.proxy import get_proxy_client

table_fields = {
    "name": fields.String,
    "key": fields.String,
    # description can be empty, if no description is present in DB
    "description": fields.String,
    "cluster": fields.String,
    "database": fields.String,
    "schema_name": fields.String,
    "column_names": fields.List(fields.String),
    # tags can be empty list
    "tags": fields.List(fields.String),
    # last etl timestamp as epoch
    "last_updated_epoch": fields.Integer,
}

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

metric_fields = {
    "dashboard_group": fields.String,
    "dashboard_name": fields.String,
    "metric_name": fields.String,
    "metric_function": fields.String,
    # description can be empty, if no description is present in DB
    "metric_description": fields.String,
    "metric_type": fields.String,
    "metric_group": fields.String
}

table_result_fields = {
    "result_count": fields.Integer,
    "results": fields.List(fields.Nested(table_fields), default=[])
}

dashboard_result_fields = {
    "result_count": fields.Integer,
    "results": fields.List(fields.Nested(dashboard_fields), default=[])
}

metric_result_fields = {
    "result_count": fields.Integer,
    "results": fields.List(fields.Nested(metric_fields), default=[])
}

table_result_fields = {
    # "dashboards": fields.Nested(dashboard_result_fields),
    "tables": fields.Nested(table_result_fields),
    # "metrics": fields.Nested(metric_result_fields),
}

dashboard_result_fields = {
    # "dashboards": fields.Nested(dashboard_result_fields),
    "dashboards": fields.Nested(dashboard_result_fields),
    # "metrics": fields.Nested(metric_result_fields),
}

metric_result_fields = {
    # "dashboards": fields.Nested(dashboard_result_fields),
    "metrics": fields.Nested(metric_result_fields),
    # "metrics": fields.Nested(metric_result_fields),
}

table_search_results = {
    "total_results": fields.Integer,
    "results":  fields.Nested(table_result_fields)
}

dashboard_search_results = {
    "total_results": fields.Integer,
    "results":  fields.Nested(dashboard_result_fields)
}

metric_search_results = {
    "total_results": fields.Integer,
    "results":  fields.Nested(metric_result_fields)
}


class SearchAPI(Resource):
    """
    Search API
    """
    def __init__(self, **kwargs) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=True, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)

        super(SearchAPI, self).__init__()

    # @marshal_with(search_results)
    def get(self, **kwargs) -> Iterable[Any]:
        """
        Fetch search results based on query_term.
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)
        if kwargs.get('type_name') == 'table':
            self.proxy.index = 'tables_alias'
            marshaling_template = table_search_results
        elif kwargs.get('type_name') == 'dashboard':
            self.proxy.index = 'dashboard_alias'
            marshaling_template = dashboard_search_results
        elif kwargs.get('type_name') == 'metric':
            self.proxy.index = 'metric_alias'
            marshaling_template = metric_search_results
        else:
            raise NotImplementedError

        try:

            results = self.proxy.fetch_search_results(
                query_term=args['query_term'],
                page_index=args['page_index']
            )

            results = marshal(results, marshaling_template)

            return results, 200

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, 500


class SearchFieldAPI(Resource):
    """
    Search API with explict field
    """
    def __init__(self) -> None:
        self.proxy = get_proxy_client()

        self.parser = reqparse.RequestParser(bundle_errors=True)

        self.parser.add_argument('query_term', required=False, type=str)
        self.parser.add_argument('page_index', required=False, default=0, type=int)

        super(SearchFieldAPI, self).__init__()

#    @marshal_with(search_results)
    def get(self, *, field_name: str,
            field_value: str, **kwargs) -> Iterable[Any]:
        """
        Fetch search results based on query_term.

        :param field_name: which field we should search from(schema, tag, table)
        :param field_value: the value to search for the field
        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.parser.parse_args(strict=True)
        if kwargs.get('type_name') == 'table':
            self.proxy.index = 'tables_alias'
            marshaling_template = table_search_results
        elif kwargs.get('type_name') == 'dashboard':
            self.proxy.index = 'dashboard_alias'
            marshaling_template = dashboard_search_results
        elif kwargs.get('type_name') == 'metric':
            self.proxy.index = 'metric_alias'
            marshaling_template = metric_search_results
        else:
            raise NotImplementedError        

        try:
            results = self.proxy.fetch_search_results_with_field(
                query_term=args.get('query_term'),
                field_name=field_name,
                field_value=field_value,
                page_index=args['page_index']
            )

            results = marshal(results, marshaling_template)

            return results, 200

        except RuntimeError:

            err_msg = 'Exception encountered while processing search request'
            return {'message': err_msg}, 500
