# Technology Stack Documentation

Complete documentation of all technologies used across the BI Voice Agent system.

---

## Table of Contents

1. [Frontend](#frontend)
2. [Backend](#backend)
3. [ETL Pipeline](#etl-pipeline)
4. [AI / Intelligence Module](#ai--intelligence-module)
5. [Infrastructure & DevOps](#infrastructure--devops)
6. [Other Tools](#other-tools)

---

## Frontend

### Frameworks

#### React
- **Version:** ^18.2.0
- **Purpose:** Core UI framework for building the frontend application
- **Where Used:** All frontend components and pages (`frontend/src/`)
- **Details:** Provides component-based architecture, state management, and virtual DOM rendering

#### React DOM
- **Version:** ^18.2.0
- **Purpose:** React rendering library for web browsers
- **Where Used:** Entry point (`frontend/src/main.jsx`) and all React components
- **Details:** Handles rendering React components to the DOM

### Routing

#### React Router DOM
- **Version:** ^6.20.0
- **Purpose:** Client-side routing for single-page application
- **Where Used:** `frontend/src/App.jsx`, all page components
- **Details:** Enables navigation between pages without full page reloads, supports protected routes

### State Management

#### Zustand
- **Version:** ^4.4.7
- **Purpose:** Lightweight state management library
- **Where Used:** `frontend/src/store/auth.js` for authentication state
- **Details:** Manages user authentication state, tokens, and workspace information across the application

### HTTP Client

#### Axios
- **Version:** ^1.6.2
- **Purpose:** HTTP client for making API requests
- **Where Used:** `frontend/src/api/axios.js`, `frontend/src/api/endpoints.js`
- **Details:** Configured with interceptors for JWT token management, base URL configuration, and error handling

### UI Libraries

#### Framer Motion
- **Version:** ^12.23.24
- **Purpose:** Animation library for React
- **Where Used:** All page components, layout components, animations directory
- **Details:** Provides page transitions, component animations, and interactive UI effects

#### Lucide React
- **Version:** ^0.294.0
- **Purpose:** Icon library for React
- **Where Used:** All components requiring icons (buttons, navigation, status indicators)
- **Details:** Provides consistent icon set across the application

#### React Hot Toast
- **Version:** ^2.4.1
- **Purpose:** Toast notification library
- **Where Used:** All components that need user feedback (success, error, warning messages)
- **Details:** Provides non-intrusive toast notifications for user actions

### Styling

#### Tailwind CSS
- **Version:** ^3.3.6
- **Purpose:** Utility-first CSS framework
- **Where Used:** All components and pages via utility classes
- **Details:** Provides rapid UI development with utility classes, configured in `tailwind.config.js`

#### PostCSS
- **Version:** ^8.4.32
- **Purpose:** CSS post-processor
- **Where Used:** `postcss.config.js` for processing Tailwind CSS
- **Details:** Transforms Tailwind CSS classes into production-ready CSS

#### Autoprefixer
- **Version:** ^10.4.16
- **Purpose:** CSS vendor prefixing tool
- **Where Used:** PostCSS configuration
- **Details:** Automatically adds vendor prefixes for browser compatibility

### Build Tools

#### Vite
- **Version:** ^5.0.8
- **Purpose:** Next-generation frontend build tool
- **Where Used:** `vite.config.js`, build and development scripts
- **Details:** Provides fast development server, HMR (Hot Module Replacement), and optimized production builds

#### @vitejs/plugin-react
- **Version:** ^4.2.1
- **Purpose:** Vite plugin for React support
- **Where Used:** `vite.config.js`
- **Details:** Enables React Fast Refresh and JSX transformation in Vite

### Development Tools

#### ESLint
- **Version:** ^8.55.0
- **Purpose:** JavaScript/JSX linter
- **Where Used:** All JavaScript/JSX files, configured in ESLint config
- **Details:** Enforces code quality and catches potential errors

#### eslint-plugin-react
- **Version:** ^7.33.2
- **Purpose:** ESLint plugin for React-specific linting rules
- **Where Used:** React component files
- **Details:** Validates React best practices and patterns

#### eslint-plugin-react-hooks
- **Version:** ^4.6.0
- **Purpose:** ESLint plugin for React Hooks rules
- **Where Used:** Components using React Hooks
- **Details:** Ensures correct usage of React Hooks (useState, useEffect, etc.)

#### eslint-plugin-react-refresh
- **Version:** ^0.4.5
- **Purpose:** ESLint plugin for React Fast Refresh
- **Where Used:** All React components
- **Details:** Validates React Fast Refresh compatibility

#### @types/react
- **Version:** ^18.43
- **Purpose:** TypeScript type definitions for React
- **Where Used:** TypeScript/JSX development
- **Details:** Provides type checking and IntelliSense support

#### @types/react-dom
- **Version:** ^18.17
- **Purpose:** TypeScript type definitions for React DOM
- **Where Used:** TypeScript/JSX development
- **Details:** Provides type checking for React DOM APIs

---

## Backend

### Programming Language

#### Python
- **Version:** 3.x (compatible with Django 4.2.7)
- **Purpose:** Primary backend programming language
- **Where Used:** All backend services, ETL pipeline, AI modules
- **Details:** Used for Django applications, data processing, AI/ML pipelines, and ETL services

### Web Framework

#### Django
- **Version:** 4.2.7 (Main backend), >=4.2 (Small Whisper), Latest (ETL services)
- **Purpose:** High-level Python web framework
- **Where Used:** 
  - Main BI backend (`config/settings.py`)
  - Small Whisper backend (`Small Whisper/backend/`)
  - All ETL services (`etl-final/*/`)
- **Details:** Provides MVC architecture, ORM, admin interface, authentication, and URL routing

#### Django REST Framework
- **Version:** 3.14.0 (Main backend), Latest (ETL services)
- **Purpose:** RESTful API framework for Django
- **Where Used:** All API views (`users/views.py`, `workspace/views.py`, `voice_reports/views.py`, etc.)
- **Details:** Provides APIView classes, serializers, authentication, permissions, and API documentation

### Authentication & Security

#### djangorestframework-simplejwt
- **Version:** 5.3.0
- **Purpose:** JWT authentication for Django REST Framework
- **Where Used:** `config/settings.py`, `users/views.py`, `users/serializers.py`
- **Details:** Provides JWT token generation, refresh tokens, token blacklisting, and authentication middleware

#### django-cors-headers
- **Version:** 4.3.1 (Main backend), Latest (Small Whisper)
- **Purpose:** CORS (Cross-Origin Resource Sharing) middleware
- **Where Used:** `config/settings.py`, `Small Whisper/backend/backend/settings.py`
- **Details:** Enables frontend (running on different port) to make API requests to backend

#### PyJWT (via djangorestframework-simplejwt)
- **Purpose:** JWT token encoding/decoding
- **Where Used:** `voice_reports/services/jwt_embedding.py`
- **Details:** Used for generating secure JWT tokens for Metabase embedding

### Database

#### PostgreSQL
- **Purpose:** Primary relational database
- **Where Used:** Main Django backend (`config/settings.py`)
- **Details:** Stores user data, workspaces, voice reports, database metadata, and all application data

#### psycopg2-binary
- **Version:** 2.9.9
- **Purpose:** PostgreSQL database adapter for Python
- **Where Used:** Main Django backend database connections
- **Details:** Provides database connectivity for Django ORM to PostgreSQL

#### ClickHouse
- **Purpose:** Column-oriented database for analytics and data warehousing
- **Where Used:** 
  - ETL pipeline final destination (`etl-final/loader-service/`)
  - Voice reports query execution (`voice_reports/services/clickhouse_executor.py`)
  - Database preview (`database/utils.py`)
- **Details:** Stores processed data from ETL pipeline, used for analytical queries

#### clickhouse-connect
- **Version:** Latest
- **Purpose:** ClickHouse HTTP client library
- **Where Used:** `voice_reports/services/clickhouse_executor.py`
- **Details:** Executes queries via HTTP protocol (port 8123) for voice reports

#### clickhouse-driver
- **Version:** Latest
- **Purpose:** ClickHouse native protocol client library
- **Where Used:** `etl-final/loader-service/loader/engine/clickhouse_client.py`
- **Details:** Executes batch inserts via native TCP protocol (port 9000) for ETL pipeline

### HTTP Requests

#### Requests
- **Version:** 2.31.0 (Main backend), Latest (ETL services, Small Whisper)
- **Purpose:** HTTP library for making API requests
- **Where Used:** 
  - Small Whisper client (`voice_reports/services/small_whisper_client.py`)
  - Metabase service (`voice_reports/services/metabase_service.py`)
  - ETL service communication (`database/views.py`)
  - SurrealDB client (`etl-final/shared/utils/surreal_client.py`)
- **Details:** Used for inter-service communication and external API calls

### Configuration Management

#### python-dotenv
- **Version:** 1.0.0 (Main backend), Latest (ETL services, Small Whisper)
- **Purpose:** Load environment variables from .env files
- **Where Used:** All Django settings files
- **Details:** Manages configuration via environment variables (database credentials, API keys, service URLs)

### Email

#### Django Email Backend (SMTP)
- **Purpose:** Email sending functionality
- **Where Used:** `users/utils.py` for verification and invitation emails
- **Details:** Configured with Gmail SMTP for sending verification and invitation emails

### Testing

#### pytest
- **Version:** 7.4.3
- **Purpose:** Python testing framework
- **Where Used:** Test files across the project
- **Details:** Provides test discovery, fixtures, and assertion framework

#### pytest-django
- **Version:** 4.7.0
- **Purpose:** Pytest plugin for Django
- **Where Used:** Django test files
- **Details:** Provides Django-specific test utilities and database management

### Development Tools

#### IPython
- **Version:** 8.17.2
- **Purpose:** Enhanced interactive Python shell
- **Where Used:** Development environment
- **Details:** Provides better debugging and exploration capabilities

---

## ETL Pipeline

### Message Broker

#### Apache Kafka
- **Purpose:** Distributed event streaming platform
- **Where Used:** All ETL services for inter-service communication
- **Details:** 
  - Topics: `connection_topic`, `schema_topic`, `extracted_rows_topic`, `clean_rows_topic`, `load_rows_topic`, `metadata_topic`
  - Used for asynchronous communication between ETL stages
  - Configured in `etl-final/docker-compose.yml`

#### kafka-python
- **Version:** Latest
- **Purpose:** Python client for Apache Kafka
- **Where Used:** 
  - `etl-final/shared/utils/kafka_consumer.py`
  - `etl-final/shared/utils/kafka_producer.py`
  - All ETL service Kafka listeners
- **Details:** Provides producer and consumer APIs for Kafka messaging

### Data Processing

#### Pandas
- **Version:** Latest
- **Purpose:** Data manipulation and analysis library
- **Where Used:** `etl-final/extractor-service/` for data extraction and transformation
- **Details:** Handles CSV/Excel file parsing, data cleaning, and transformation

#### openpyxl
- **Version:** Latest
- **Purpose:** Excel file reader/writer
- **Where Used:** `etl-final/extractor-service/` for Excel file processing
- **Details:** Reads and writes Excel files (.xlsx, .xlsm)

### Database Connectors

#### PyMySQL
- **Version:** Latest
- **Purpose:** MySQL database connector
- **Where Used:** `etl-final/extractor-service/extractor/engine/db_connector.py`
- **Details:** Connects to MySQL databases for data extraction

#### psycopg2-binary
- **Version:** Latest
- **Purpose:** PostgreSQL database connector
- **Where Used:** `etl-final/extractor-service/extractor/engine/db_connector.py`
- **Details:** Connects to PostgreSQL databases for data extraction

### Metadata Storage

#### SurrealDB
- **Purpose:** Cloud-native database for metadata and logging
- **Where Used:** `etl-final/metadata-service/` and all ETL services for logging
- **Details:** 
  - Stores ETL pipeline metadata, logs, and audit trails
  - Configured in `etl-final/docker-compose.yml`
  - Accessed via HTTP API (`etl-final/shared/utils/surreal_client.py`)

### Data Storage

#### ClickHouse
- **Purpose:** Final destination for processed data
- **Where Used:** `etl-final/loader-service/` for batch loading
- **Details:** 
  - Receives cleaned and transformed data from ETL pipeline
  - Used for analytical queries in voice reports
  - Configured with native protocol (port 9000) for batch inserts

---

## AI / Intelligence Module

### Speech-to-Text

#### OpenAI Whisper
- **Version:** Latest (via openai-whisper package)
- **Purpose:** Automatic speech recognition (ASR) model
- **Where Used:** 
  - `Small Whisper/backend/whisper_app/views.py`
  - `Small Whisper/backend/whisper_app/transcription_task.py`
- **Details:** 
  - Model: `large-v3`
  - Transcribes audio files to text
  - Supports multiple languages and translation

#### torch (PyTorch)
- **Version:** Latest
- **Purpose:** Deep learning framework (required by Whisper)
- **Where Used:** Whisper model loading and inference
- **Details:** Provides tensor operations and neural network support

#### torchaudio
- **Version:** Latest
- **Purpose:** Audio processing library for PyTorch
- **Where Used:** Audio preprocessing for Whisper
- **Details:** Handles audio file loading and preprocessing

#### numpy
- **Version:** Latest
- **Purpose:** Numerical computing library
- **Where Used:** Audio processing, data manipulation in AI pipeline
- **Details:** Provides array operations and mathematical functions

#### scipy
- **Version:** Latest
- **Purpose:** Scientific computing library
- **Where Used:** Signal processing for audio
- **Details:** Provides advanced mathematical functions and signal processing

#### ffmpeg-python
- **Version:** Latest
- **Purpose:** Python bindings for FFmpeg
- **Where Used:** Audio file format conversion and processing
- **Details:** Handles audio format conversion (WAV, MP3, etc.)

### Large Language Models

#### OpenAI API (via OpenRouter)
- **Purpose:** LLM API access through OpenRouter
- **Where Used:** `Small Whisper/backend/llm_app/llm_client.py`
- **Details:** 
  - Model: `google/gemma-3n-e4b-it:free` (configurable)
  - Used for intent extraction and SQL generation
  - Stateless API calls (no user context)

#### openai (Python SDK)
- **Version:** Latest
- **Purpose:** OpenAI Python SDK (used with OpenRouter)
- **Where Used:** `Small Whisper/backend/llm_app/llm_client.py`
- **Details:** Provides client interface for OpenRouter API

#### tiktoken
- **Version:** Latest
- **Purpose:** Token counting library for LLMs
- **Where Used:** LLM prompt processing
- **Details:** Counts tokens in prompts for API limits

### NLP & ML Frameworks

#### LangChain
- **Version:** Latest
- **Purpose:** Framework for building LLM applications
- **Where Used:** `Small Whisper/backend/` for intent extraction pipeline
- **Details:** Provides prompt templates, chains, and LLM integration

#### langchain-community
- **Version:** Latest
- **Purpose:** Community integrations for LangChain
- **Where Used:** LLM pipeline integrations
- **Details:** Provides additional LLM providers and tools

#### langchain-core
- **Version:** Latest
- **Purpose:** Core LangChain functionality
- **Where Used:** Base classes and utilities for LangChain
- **Details:** Provides base abstractions for chains and agents

#### LangGraph
- **Version:** Latest
- **Purpose:** Graph-based workflow for LLM applications
- **Where Used:** `Small Whisper/backend/reasoning_app/graph.py`
- **Details:** 
  - Builds state graphs for reasoning pipeline
  - Routes between analytical and conversational flows
  - Manages question classification workflow

### Data Validation

#### Pydantic
- **Version:** Latest
- **Purpose:** Data validation using Python type annotations
- **Where Used:** 
  - `Small Whisper/backend/shared/intent_schema.py` (Intent, Metric, Filter models)
  - ETL message validation
- **Details:** Validates intent structures, message schemas, and data types

### Vector Databases
- **Status:** Not currently used
- **Note:** System uses structured SQL queries rather than vector similarity search

### Inference Tools
- **OpenRouter API:** Primary inference endpoint for LLM calls
- **Local Whisper Model:** On-device inference for speech-to-text

---

## Infrastructure & DevOps

### Containers

#### Docker
- **Purpose:** Containerization platform
- **Where Used:** All ETL services (`etl-final/docker-compose.yml`)
- **Details:** 
  - Containerizes ETL services (connector, detector, extractor, transformer, loader, metadata)
  - Includes Kafka, ClickHouse, and SurrealDB containers
  - Defined in Dockerfiles and docker-compose.yml

#### Docker Compose
- **Purpose:** Multi-container Docker application orchestration
- **Where Used:** `etl-final/docker-compose.yml`
- **Details:** 
  - Orchestrates all ETL services
  - Manages Kafka, ClickHouse, and SurrealDB containers
  - Handles networking and volume management

### Orchestration
- **Status:** Docker Compose for local development
- **Note:** Production deployment strategy not specified in codebase

### Environment Variables

#### Configuration via .env files
- **Purpose:** Environment-based configuration
- **Where Used:** All services
- **Details:** 
  - Database credentials (PostgreSQL, ClickHouse)
  - API keys (OpenRouter, Metabase)
  - Service URLs (ETL, Small Whisper, Metabase)
  - SMTP settings (Gmail)
  - JWT secrets

### Deployment Strategy
- **Development:** 
  - Django development server (runserver)
  - Vite development server for frontend
  - Docker Compose for ETL services
- **Production:** 
  - Not fully specified in codebase
  - Likely uses WSGI/ASGI servers (Gunicorn, uvicorn)
  - Static file serving (nginx recommended)

---

## Other Tools

### Logging

#### Python logging (Standard Library)
- **Purpose:** Application logging
- **Where Used:** All Python modules
- **Details:** 
  - Configured in `config/settings.py` with console and file handlers
  - Used throughout backend, ETL, and AI modules
  - Provides structured logging with levels (INFO, WARNING, ERROR)

### Monitoring
- **Status:** Basic logging implemented
- **Note:** No dedicated monitoring tools (Prometheus, Grafana) specified

### Security

#### Django Security Middleware
- **Purpose:** Built-in Django security features
- **Where Used:** `config/settings.py`
- **Details:** 
  - CSRF protection
  - XSS protection
  - Clickjacking protection
  - Security headers

#### SQL Injection Prevention
- **Purpose:** SQL security
- **Where Used:** `voice_reports/services/sql_guard.py`
- **Details:** 
  - Read-only query enforcement (SELECT only)
  - Dangerous keyword blocking
  - Pattern-based injection detection
  - Workspace database isolation

#### JWT Token Security
- **Purpose:** Secure authentication tokens
- **Where Used:** 
  - `users/serializers.py` (login)
  - `voice_reports/services/jwt_embedding.py` (Metabase embedding)
- **Details:** 
  - Short-lived tokens (10 minutes for embedding, 1 hour for access)
  - Token blacklisting on logout
  - HS256 algorithm
  - Server-side signing only

### Testing Tools

#### pytest
- **Version:** 7.4.3
- **Purpose:** Python testing framework
- **Where Used:** Test files across the project
- **Details:** Provides test discovery, fixtures, parametrization

#### pytest-django
- **Version:** 4.7.0
- **Purpose:** Django integration for pytest
- **Where Used:** Django test files
- **Details:** Provides database management, test client, and Django-specific fixtures

### Code Quality

#### ESLint (Frontend)
- **Version:** ^8.55.0
- **Purpose:** JavaScript/JSX linting
- **Where Used:** All frontend JavaScript/JSX files
- **Details:** Enforces code style and catches errors

### File Processing

#### Python Standard Library (tempfile, os, pathlib)
- **Purpose:** File handling and temporary file management
- **Where Used:** 
  - Audio file processing (`Small Whisper/backend/whisper_app/`)
  - Database file uploads (`database/views.py`)
  - ETL file processing
- **Details:** Handles file uploads, temporary storage, and file operations

### Data Serialization

#### JSON (Standard Library)
- **Purpose:** Data serialization
- **Where Used:** 
  - API responses (Django REST Framework)
  - Kafka message serialization
  - Intent and metadata storage
- **Details:** Primary format for data exchange

#### Django JSONField
- **Purpose:** JSON field storage in PostgreSQL
- **Where Used:** 
  - `voice_reports/models.py` (intent_json, query_result, chart_config)
  - `database/models.py` (columns_schema)
- **Details:** Stores structured JSON data in database

### Time & Date

#### Python datetime (Standard Library)
- **Purpose:** Date and time handling
- **Where Used:** All modules requiring timestamps
- **Details:** Used for created_at, updated_at, expiration dates, etc.

#### Django timezone utilities
- **Purpose:** Timezone-aware datetime handling
- **Where Used:** All Django models with DateTimeField
- **Details:** Ensures consistent timezone handling across the application

### Email Templates
- **Purpose:** HTML email generation
- **Where Used:** `users/utils.py`
- **Details:** 
  - Verification emails (HTML with styling)
  - Invitation emails (HTML with styling)
  - Uses Django EmailMessage with HTML content

### Validation

#### Django Form Validation
- **Purpose:** Form and serializer validation
- **Where Used:** All Django serializers
- **Details:** Provides field validation, custom validators, and error handling

#### Pydantic Validation
- **Purpose:** Data model validation
- **Where Used:** 
  - Intent schema (`Small Whisper/backend/shared/intent_schema.py`)
  - ETL message validation
- **Details:** Type-safe validation with automatic error messages

---

## Technology Summary by Category

### Frontend Technologies (11)
1. React ^18.2.0
2. React DOM ^18.2.0
3. React Router DOM ^6.20.0
4. Zustand ^4.4.7
5. Axios ^1.6.2
6. Framer Motion ^12.23.24
7. Lucide React ^0.294.0
8. React Hot Toast ^2.4.1
9. Tailwind CSS ^3.3.6
10. PostCSS ^8.4.32
11. Vite ^5.0.8

### Backend Technologies (15)
1. Python 3.x
2. Django 4.2.7+
3. Django REST Framework 3.14.0+
4. djangorestframework-simplejwt 5.3.0
5. django-cors-headers 4.3.1+
6. PostgreSQL
7. psycopg2-binary 2.9.9+
8. ClickHouse
9. clickhouse-connect (Latest)
10. clickhouse-driver (Latest)
11. Requests 2.31.0+
12. python-dotenv 1.0.0+
13. pytest 7.4.3
14. pytest-django 4.7.0
15. IPython 8.17.2

### ETL Technologies (10)
1. Apache Kafka
2. kafka-python (Latest)
3. Pandas (Latest)
4. openpyxl (Latest)
5. PyMySQL (Latest)
6. psycopg2-binary (Latest)
7. SurrealDB
8. ClickHouse
9. clickhouse-driver (Latest)
10. Requests (Latest)

### AI/ML Technologies (15)
1. OpenAI Whisper (Latest)
2. PyTorch (torch) (Latest)
3. torchaudio (Latest)
4. NumPy (Latest)
5. SciPy (Latest)
6. ffmpeg-python (Latest)
7. OpenAI API (via OpenRouter)
8. openai Python SDK (Latest)
9. tiktoken (Latest)
10. LangChain (Latest)
11. langchain-community (Latest)
12. langchain-core (Latest)
13. LangGraph (Latest)
14. Pydantic (Latest)
15. Python Standard Library (math, re, json)

### Infrastructure Technologies (3)
1. Docker
2. Docker Compose
3. Environment Variables (.env)

### Development & Testing Tools (8)
1. ESLint ^8.55.0
2. eslint-plugin-react ^7.33.2
3. eslint-plugin-react-hooks ^4.6.0
4. eslint-plugin-react-refresh ^0.4.5
5. @types/react ^18.43
6. @types/react-dom ^18.17
7. pytest 7.4.3
8. pytest-django 4.7.0

---

## Technology Integration Points

### Frontend ↔ Backend
- **Protocol:** HTTP/HTTPS
- **Format:** JSON
- **Authentication:** JWT tokens (Bearer token in Authorization header)
- **CORS:** Enabled via django-cors-headers
- **Base URL:** Configurable via environment variables

### Backend ↔ Small Whisper
- **Protocol:** HTTP
- **Format:** Multipart form data (audio files), JSON (responses)
- **Authentication:** None (stateless AI worker)
- **Endpoint:** `/api/transcribe/`

### Backend ↔ ClickHouse
- **Protocol:** HTTP (port 8123) for queries, Native TCP (port 9000) for batch inserts
- **Format:** SQL queries, JSON responses
- **Authentication:** Username/password
- **Libraries:** clickhouse-connect (HTTP), clickhouse-driver (Native)

### Backend ↔ Metabase
- **Protocol:** HTTP
- **Format:** JSON
- **Authentication:** Session token (X-Metabase-Session header)
- **Embedding:** JWT-signed embed URLs

### ETL Services ↔ Kafka
- **Protocol:** Kafka protocol
- **Format:** JSON messages
- **Authentication:** None (internal network)
- **Topics:** connection_topic, schema_topic, extracted_rows_topic, clean_rows_topic, load_rows_topic, metadata_topic

### ETL Services ↔ SurrealDB
- **Protocol:** HTTP
- **Format:** SQL queries, JSON responses
- **Authentication:** Username/password
- **Purpose:** Metadata and logging storage

### ETL Services ↔ ClickHouse
- **Protocol:** Native TCP (port 9000)
- **Format:** Batch inserts
- **Authentication:** Username/password
- **Library:** clickhouse-driver

### Small Whisper ↔ OpenRouter
- **Protocol:** HTTPS
- **Format:** JSON (OpenAI API format)
- **Authentication:** API key
- **Model:** google/gemma-3n-e4b-it:free (configurable)

---

## Version Compatibility Notes

- **Django 4.2.7** requires Python 3.8+
- **React 18.2.0** requires Node.js 14+
- **Vite 5.0.8** requires Node.js 18+
- **ClickHouse** supports both HTTP (8123) and Native (9000) protocols
- **Kafka** requires Java runtime (handled by Docker)
- **Whisper large-v3** requires significant memory (~10GB+)

---

## Production Considerations

### Recommended Additions
1. **Web Server:** Nginx or Apache for reverse proxy
2. **WSGI Server:** Gunicorn or uWSGI for Django
3. **ASGI Server:** Uvicorn for async Django (if needed)
4. **Process Manager:** Supervisor or systemd
5. **Monitoring:** Prometheus + Grafana
6. **Logging:** ELK Stack or similar
7. **Caching:** Redis (for session storage, if needed)
8. **CDN:** For static files (if applicable)
9. **SSL/TLS:** Certificates for HTTPS
10. **Database Backup:** Automated backup solution for PostgreSQL

---

## Summary

This system uses:
- **62+ distinct technologies** across all layers
- **Modern web stack** (React + Django)
- **Microservices architecture** (ETL pipeline)
- **AI/ML capabilities** (Whisper + LLM)
- **Event-driven architecture** (Kafka)
- **Analytical database** (ClickHouse)
- **Containerization** (Docker)

All technologies are actively used and integrated into the system architecture.
