from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from shared.utils.response import make_response
from shared.utils.surreal_client import SurrealClient

from .loader_logic import LoaderLogic


class TestLoaderView(APIView):

    def post(self, request):

        config = request.data.get("config")  # ClickHouse config
        table = request.data.get("table")
        row = request.data.get("row")

        try:
            loader = LoaderLogic(config)
            loader.load_row(table, row)

            SurrealClient().insert("load_logs", {
                "table": table,
                "row": row,
                "status": "inserted"
            })

            return Response(make_response(True, "Row inserted successfully."))
        except Exception as e:
            return Response(make_response(False, str(e)))
