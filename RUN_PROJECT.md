# 🚀 BI Voice Agent - Complete Project Setup Guide

This guide will walk you through setting up and running the entire Django + ETL + BI Voice Agent system from scratch.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Architecture Overview](#project-architecture-overview)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [ClickHouse & ETL Services](#clickhouse--etl-services)
6. [Small Whisper Backend](#small-whisper-backend)
7. [Django Backend](#django-backend)
8. [Frontend Setup](#frontend-setup)
9. [Testing the Complete System](#testing-the-complete-system)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python**: 3.9 or higher (3.10 recommended)
- **Node.js**: 16.x or higher (for frontend)
- **Docker & Docker Compose**: Latest version
- **PostgreSQL**: 14 or higher (or use Docker)
- **Git**: For version control

### Check Your Versions

```bash
python --version
node --version
docker --version
docker-compose --version
psql --version
```

---

## Project Architecture Overview

```
BI Voice Agent System
├── Django Backend (Main API)
│   ├── PostgreSQL (User data, workspaces)
│   ├── Voice Reports Module
│   └── User Authentication
│
├── Small Whisper Backend (NLP Pipeline)
│   ├── Audio Transcription (Whisper)
│   ├── Intent Extraction (LLM)
│   └── SQL Generation
│
├── ETL Pipeline (Data Ingestion)
│   ├── ClickHouse (Data Warehouse)
│   ├── Kafka (Message Queue)
│   ├── Connector → Detector → Extractor → Transformer → Loader
│   └── Metadata Service
│
└── React Frontend (UI)
    ├── Voice Upload Interface
    ├── SQL Editor
    └── Dashboard Visualization
```

---

## Environment Setup

### 1. Clone the Repository

```bash
cd "C:\Users\Ayman\Desktop\BI coding (3)\BI coding"
# Or wherever your project is located
```

### 2. Create Virtual Environment (Django Backend)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Django Backend Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected packages:
- Django 4.2.7
- djangorestframework
- psycopg2-binary (PostgreSQL adapter)
- clickhouse-connect (HTTP ClickHouse client)
- requests
- python-dotenv

### 4. Create Environment Variables File

Create a `.env` file in the project root:

```bash
# Database Configuration
DB_NAME=bi_voice_agent
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ClickHouse Configuration (HTTP for Queries)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_HTTP_PORT=8123
CLICKHOUSE_USER=etl_user
CLICKHOUSE_PASSWORD=etl_pass123
CLICKHOUSE_QUERY_USER=etl_user
CLICKHOUSE_QUERY_PASSWORD=etl_pass123
CLICKHOUSE_DATABASE=etl

# ClickHouse Native (for ETL only - DO NOT MODIFY)
CLICKHOUSE_NATIVE_PORT=9000

# Small Whisper Backend
SMALL_WHISPER_BASE_URL=http://localhost:8001
SMALL_WHISPER_TIMEOUT=60

# OpenAI API (for LLM)
OPENAI_API_KEY=your-openai-api-key-here

# Metabase Self-Hosted (Session Auth; no Cloud, no API keys)
METABASE_URL=http://127.0.0.1:3000
METABASE_USERNAME=your_metabase_email
METABASE_PASSWORD=your_metabase_password
METABASE_DATABASE_ID=1
# Optional: for JWT embedding (must match Metabase Admin > Embedding secret)
# METABASE_SECRET_KEY=your-embedding-secret

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
```

**⚠️ Important:** Replace placeholder values with your actual credentials.

---

## Database Setup

### 1. Create PostgreSQL Database

```bash
# Windows (PowerShell)
psql -U postgres

# Create database
CREATE DATABASE bi_voice_agent;

# Create user (optional)
CREATE USER bi_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bi_voice_agent TO bi_admin;

# Exit
\q
```

### 2. Run Django Migrations

```bash
# Make sure virtual environment is activated
python manage.py makemigrations
python manage.py migrate
```

This will create tables for:
- Users (authentication)
- Workspaces
- Voice Reports
- SQL Edit History

### 3. Create Django Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## ClickHouse & ETL Services

### 1. Navigate to ETL Directory

```bash
cd etl-final
```

### 2. Start All Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- **ClickHouse** (Ports 8123 HTTP, 9000 Native)
- **Kafka** (Port 9092)
- **Zookeeper** (Port 2181)
- **Connector Service** (Port 5001)
- **Detector Service** (Port 5002)
- **Extractor Service** (Port 5003)
- **Transformer Service** (Port 5004)
- **Loader Service** (Port 5005)
- **Metadata Service** (Port 5006)

### 3. Verify Services Are Running

```bash
docker-compose ps
```

All services should show status "Up".

### 4. Check ClickHouse Connection

```bash
# Windows PowerShell
curl http://localhost:8123/ping

# Expected output: Ok.
```

### 5. Create ClickHouse Database (if not exists)

```bash
# Using ClickHouse client
docker exec -it etl-final_clickhouse_1 clickhouse-client

# Inside ClickHouse client
CREATE DATABASE IF NOT EXISTS etl;
USE etl;
SHOW TABLES;
exit;
```

### 6. Test ETL Pipeline (Optional)

```bash
# From etl-final directory
python test_full_pipeline.py
```

This uploads a test CSV and validates the entire ETL flow.

---

## Small Whisper Backend

The Small Whisper backend handles NLP, intent extraction, and SQL generation.

### 1. Navigate to Small Whisper Directory

```bash
cd "Small Whisper/backend"
```

### 2. Create Virtual Environment (Separate from Django)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected packages:
- Django
- openai-whisper (audio transcription)
- torch, torchaudio (ML models)
- langchain, langgraph (LLM orchestration)
- openai (GPT API)
- clickhouse-driver (schema loading)
- clickhouse-connect (query execution)

**Note:** Installing Whisper may take 10-15 minutes due to large ML models.

### 4. Configure Environment

Create `.env` in `Small Whisper/backend/`:

```bash
# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here

# ClickHouse (for schema loading via HTTP)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_HTTP_PORT=8123
CLICKHOUSE_USER=etl_user
CLICKHOUSE_PASSWORD=etl_pass123
CLICKHOUSE_DATABASE=etl

# Django Settings
SECRET_KEY=small-whisper-secret-key
DEBUG=True
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Start Small Whisper Server

```bash
python manage.py runserver 8001
```

**Port 8001** is critical - Django backend expects Small Whisper on this port.

### 7. Test Small Whisper Health

Open browser or curl:
```bash
curl http://localhost:8001/api/whisper/health/
```

Expected response:
```json
{
  "status": "healthy",
  "whisper_model": "loaded",
  "clickhouse": "connected"
}
```

---

## Django Backend

### 1. Return to Project Root

```bash
cd ../..
# Should be in: C:\Users\Ayman\Desktop\BI coding (3)\BI coding
```

### 2. Activate Django Virtual Environment

```bash
# Windows
venv\Scripts\activate
```

### 3. Start Django Development Server

```bash
python manage.py runserver 8000
```

**Port 8000** is the main API server.

### 4. Verify Django is Running

Open browser:
```
http://localhost:8000/admin/
```

You should see the Django admin login page.

### 5. Test API Health Check

```bash
curl http://localhost:8000/api/voice-reports/health/
```

Expected response includes:
```json
{
  "status": "healthy",
  "database": true,
  "clickhouse": true,
  "small_whisper": true
}
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

This installs:
- React
- React Router
- Tailwind CSS
- Axios (API client)
- Chart.js (visualizations)

### 3. Configure API Endpoint

Check `src/api/axios.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### 4. Start Development Server

```bash
npm run dev
```

Frontend will start on **http://localhost:5173**

### 5. Open in Browser

```
http://localhost:5173
```

You should see the login/signup page.

---

## Testing the Complete System

### End-to-End Voice Query Flow

#### 1. Create User Account

1. Open frontend: http://localhost:5173
2. Click "Sign Up"
3. Register as Manager role
4. Verify email (check console logs in development)

#### 2. Upload Data via ETL

```bash
cd etl-final

# Create test CSV
echo "year,revenue,students
2020,100000,500
2021,150000,600
2022,200000,700" > test_data.csv

# Upload via connector service
curl -X POST http://localhost:5001/upload \
  -F "file=@test_data.csv" \
  -F "source_name=test_data"
```

#### 3. Verify Data in ClickHouse

```bash
docker exec -it etl-final_clickhouse_1 clickhouse-client

# Inside ClickHouse
SELECT * FROM etl.test_data LIMIT 10;
exit;
```

#### 4. Test Voice Query (via API)

Create a test audio file with the question: **"Show total revenue by year"**

```bash
# Using curl to upload audio
curl -X POST http://localhost:8000/api/voice-reports/upload/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "audio_file=@test_audio.m4a"
```

**Expected Flow:**
1. ✅ Django receives audio
2. ✅ Forwards to Small Whisper (port 8001)
3. ✅ Small Whisper transcribes audio
4. ✅ Extracts intent
5. ✅ Generates SQL: `SELECT year, SUM(revenue) AS total_revenue FROM etl.test_data GROUP BY year`
6. ✅ Django validates SQL
7. ✅ Executes on ClickHouse (HTTP port 8123)
8. ✅ Returns results to frontend

#### 5. Execute Query and View Results

In the frontend:
1. Navigate to Voice Reports
2. Select your uploaded report
3. Click "Execute Query"
4. View results in table/chart

---

## Service Port Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Django Backend | 8000 | HTTP | Main API |
| Small Whisper | 8001 | HTTP | NLP Pipeline |
| ClickHouse HTTP | 8123 | HTTP | **Query Execution** |
| ClickHouse Native | 9000 | TCP | **ETL Ingestion Only** |
| Frontend | 5173 | HTTP | React UI |
| Metabase | 3000 | HTTP | BI Dashboards |
| Kafka | 9092 | TCP | Message Queue |
| Connector Service | 5001 | HTTP | CSV Upload |
| Detector Service | 5002 | HTTP | Schema Detection |
| Extractor Service | 5003 | HTTP | Data Extraction |
| Transformer Service | 5004 | HTTP | Data Transform |
| Loader Service | 5005 | HTTP | ClickHouse Load |
| Metadata Service | 5006 | HTTP | Schema Registry |

---

## Troubleshooting

### ClickHouse Connection Issues

**Problem:** `Connection refused` to ClickHouse

**Solution:**
```bash
# Check if ClickHouse is running
docker ps | grep clickhouse

# Check logs
docker logs etl-final_clickhouse_1

# Restart ClickHouse
docker-compose restart clickhouse
```

**Problem:** Port 9000 error in query execution

**Solution:** 
Ensure `.env` has:
```
CLICKHOUSE_PORT=8123
CLICKHOUSE_HTTP_PORT=8123
```

### Small Whisper Not Responding

**Problem:** Small Whisper health check fails

**Solution:**
```bash
cd "Small Whisper/backend"
venv\Scripts\activate

# Check if running
curl http://localhost:8001/api/whisper/health/

# Check logs
python manage.py runserver 8001 --noreload
```

**Problem:** OpenAI API errors

**Solution:**
- Verify `OPENAI_API_KEY` in `.env`
- Check API quota: https://platform.openai.com/usage

### ETL Pipeline Issues

**Problem:** CSV upload fails

**Solution:**
```bash
# Check all services are up
docker-compose ps

# Restart all services
docker-compose down
docker-compose up -d

# Check connector logs
docker logs etl-final_connector-service_1
```

### Database Migration Errors

**Problem:** `relation does not exist`

**Solution:**
```bash
# Delete migrations (caution in production!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Frontend Can't Connect to Backend

**Problem:** CORS errors

**Solution:**
In `config/settings.py`, verify:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

---

## Quick Start Commands (After Initial Setup)

### Start Everything

```bash
# Terminal 1 - ClickHouse & ETL
cd etl-final
docker-compose up -d

# Terminal 2 - Small Whisper
cd "Small Whisper/backend"
venv\Scripts\activate
python manage.py runserver 8001

# Terminal 3 - Django Backend
cd ../..
venv\Scripts\activate
python manage.py runserver 8000

# Terminal 4 - Frontend
cd frontend
npm run dev
```

### Stop Everything

```bash
# Stop Django & Small Whisper
Ctrl+C in each terminal

# Stop Docker services
cd etl-final
docker-compose down
```

---

## Next Steps

1. **Load Production Data**: Upload your CSV files via the connector service
2. **Configure Metabase**: Set up dashboards for visualization
3. **Train Custom Models**: Fine-tune Whisper for your domain
4. **Security Hardening**: 
   - Change all default passwords
   - Use environment-specific `.env` files
   - Enable HTTPS
   - Configure firewall rules

---

## Support & Documentation

- **Django Docs**: https://docs.djangoproject.com/
- **ClickHouse Docs**: https://clickhouse.com/docs/
- **Whisper Model**: https://github.com/openai/whisper
- **React Docs**: https://react.dev/

---

## Summary

✅ **Backend Services**: Django (8000) + Small Whisper (8001)  
✅ **Data Layer**: PostgreSQL + ClickHouse (8123 HTTP, 9000 Native)  
✅ **ETL Pipeline**: 6 microservices + Kafka  
✅ **Frontend**: React on Vite (5173)  

**Total Services Running**: 12+

You're now ready to process voice queries and generate SQL-based insights! 🎉

