from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.surreal_client import SurrealClient
from shared.utils.response import make_response

from .db_connector import DBConnector
from .row_extractor import RowExtractor


class RunExtractorView(APIView):

    def post(self, request):
        cfg = request.data.get("config")
        schema = request.data.get("schema")

        try:
            conn = DBConnector().connect(cfg)
            extractor = RowExtractor()
            producer = KafkaMessageProducer()

            for table, row in extractor.extract_rows(conn, list(schema.keys())):
                producer.send("extracted_rows_topic", {
                    "table": table,
                    "row": row
                })

            SurrealClient().insert("extract_logs", {
                "status": "done",
                "tables": list(schema.keys()),
            })

            return Response(make_response(True, "Extraction completed"))
        except Exception as e:
            return Response(make_response(False, str(e)))
