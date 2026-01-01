FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY connector-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy service source
COPY connector-service /app/connector-service

# Copy shared utils/models
COPY shared /app/shared

ENV PYTHONPATH="/app/shared:/app"

EXPOSE 8000

CMD ["python", "connector-service/connector/manage.py", "runserver", "0.0.0.0:8000"]
