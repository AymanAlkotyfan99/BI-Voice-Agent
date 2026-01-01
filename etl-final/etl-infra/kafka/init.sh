#!/bin/bash

kafka-topics --create --if-not-exists \
  --topic connection_topic \
  --bootstrap-server kafka:9092

kafka-topics --create --if-not-exists \
  --topic schema_topic \
  --bootstrap-server kafka:9092

kafka-topics --create --if-not-exists \
  --topic extracted_rows_topic \
  --bootstrap-server kafka:9092

kafka-topics --create --if-not-exists \
  --topic clean_rows_topic \
  --bootstrap-server kafka:9092

kafka-topics --create --if-not-exists \
  --topic load_rows_topic \
  --bootstrap-server kafka:9092

kafka-topics --create --if-not-exists \
  --topic metadata_topic \
  --bootstrap-server kafka:9092
