from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from shared.utils.surreal_client import SurrealClient
from shared.utils.response import make_response

from .query_builder import build_select_query
from .serializers import LogSerializer


class BaseLogView(APIView):

    table_name = None  # define per child

    def get(self, request):
        try:
            sql = build_select_query(self.table_name)
            raw = SurrealClient().query(sql)
            data = LogSerializer.serialize(raw)
            return Response(make_response(True, "Logs fetched", data))
        except Exception as e:
            return Response(make_response(False, str(e)))


class ConnectionLogsView(BaseLogView):
    table_name = "connection_logs"


class SchemaLogsView(BaseLogView):
    table_name = "schema_logs"


class ExtractLogsView(BaseLogView):
    table_name = "extract_logs"


class TransformLogsView(BaseLogView):
    table_name = "transform_logs"


class LoadLogsView(BaseLogView):
    table_name = "load_logs"
