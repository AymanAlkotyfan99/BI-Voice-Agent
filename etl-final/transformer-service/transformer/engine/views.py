from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.surreal_client import SurrealClient
from shared.utils.response import make_response

from .cleaning_rules import CleaningRules
from .transformer_logic import TransformerLogic


class TestTransformView(APIView):
    """
    Manual test endpoint for transformation.
    """

    def post(self, request):

        table = request.data.get("table")
        row = request.data.get("row")

        try:
            cleaned = CleaningRules().apply_all(row)
            transformed = TransformerLogic().transform_row(cleaned)

            return Response(make_response(True, "Transformed", {
                "cleaned": cleaned,
                "transformed": transformed,
            }))
        except Exception as e:
            return Response(make_response(False, str(e)))
