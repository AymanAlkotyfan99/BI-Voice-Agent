from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .file_storage import save_uploaded_file
from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.surreal_client import SurrealClient
from shared.utils.metadata_schema import MetadataSchema
from .utils import  test_db_connection
from shared.utils.response import make_response

class UploadFileView(APIView):
    """
    Handles file uploads and stores locally, logs metadata.
    """

    def post(self, request):
        if "file" not in request.FILES:
            return Response(make_response(False, "No file provided"), status=400)

        uploaded_file = request.FILES["file"]
        saved_path = save_uploaded_file(uploaded_file)

        # Log metadata to SurrealDB
        surreal = SurrealClient()
        surreal.insert("upload_logs", {
            "filename": uploaded_file.name,
            "path": saved_path,
            "size": uploaded_file.size
        })

        # Publish to Kafka connection_topic to trigger ETL pipeline
        producer = KafkaMessageProducer()
        connection_message = {
            "type": "file",
            "filename": uploaded_file.name,
            "path": saved_path,
            "size": uploaded_file.size
        }
        producer.send("connection_topic", connection_message)
        print(f"[CONNECTOR] Published file upload to connection_topic: {uploaded_file.name}")
        
        # Emit connection metadata
        connection_metadata = MetadataSchema.create_connection_metadata(
            source_type="file",
            source_id=uploaded_file.name,
            connection_info=connection_message
        )
        producer.send("metadata_topic", connection_metadata)

        return Response(make_response(True, "File uploaded successfully", {
            "saved_path": saved_path
        }), status=200)


class ConnectDBView(APIView):
    """
    Tests DB connection and sends DB config to Kafka for detector-service.
    """

    def post(self, request):
        required = ["db_type", "host", "user", "password", "database", "port"]

        for field in required:
            if field not in request.data:
                return Response(make_response(False, f"Missing field: {field}"), status=400)

        db_type = request.data["db_type"]
        host = request.data["host"]
        user = request.data["user"]
        password = request.data["password"]
        database = request.data["database"]
        port = request.data["port"]

        # 1) test connection
        success, message = test_db_connection(db_type, host, user, password, database, port)

        if not success:
            return Response(make_response(False, message), status=400)

        # 2) send config to Kafka connection_topic
        producer = KafkaMessageProducer()
        connection_message = {
            "type": "database",
            "db_type": db_type,
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
        }
        producer.send("connection_topic", connection_message)
        print(f"[CONNECTOR] Published DB connection to connection_topic: {db_type}://{host}/{database}")
        
        # Emit connection metadata
        connection_metadata = MetadataSchema.create_connection_metadata(
            source_type="database",
            source_id=database,
            connection_info={k: v for k, v in connection_message.items() if k != "password"}  # Don't log password
        )
        producer.send("metadata_topic", connection_metadata)

        # 3) log connection metadata
        surreal = SurrealClient()
        surreal.insert("connection_logs", {
            "db_type": db_type,
            "host": host,
            "database": database
        })

        return Response(make_response(True, "DB connected successfully"), status=200)
