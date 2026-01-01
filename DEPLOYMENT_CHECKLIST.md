# ✅ Deployment Checklist - Database Feature

## Pre-Deployment Verification

Run through this checklist before starting your system or demo:

---

## 1. Environment Setup

### ✅ Python Environment
```bash
# Verify Python version
python --version
# Expected: Python 3.10 or higher

# Verify virtual environment exists
cd "C:\Users\Ayman\Desktop\BI coding (3)\BI coding"
dir venv
# Should see venv directory

# Activate venv
venv\Scripts\activate
# Prompt should show (venv)

# Verify packages installed
pip list | findstr Django
pip list | findstr djangorestframework
pip list | findstr requests
```

### ✅ Node.js Environment
```bash
# Verify Node version
node --version
# Expected: v18.0.0 or higher

# Verify npm
npm --version
# Expected: 9.0.0 or higher

# Check frontend dependencies
cd frontend
dir node_modules
# Should see node_modules directory
```

### ✅ Docker Environment
```bash
# Verify Docker is running
docker --version
docker ps
# Should not error

# Verify Docker Compose
docker-compose --version
# Expected: 1.29.0 or higher
```

### ✅ PostgreSQL
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Verify database exists
psql -U bi_admin -d bi_voice_agent -c "\dt"
```

---

## 2. Backend Verification

### ✅ Django Settings
Check `config/settings.py`:
```python
# Verify these settings exist:
✓ 'database' in INSTALLED_APPS
✓ CLICKHOUSE_HOST = 'localhost'
✓ CLICKHOUSE_PORT = '8123'
✓ ETL_SERVICE_URL = 'http://127.0.0.1:8001'
✓ 'http://localhost:5173' in CORS_ALLOWED_ORIGINS
```

### ✅ Database Migrations
```bash
# Check migration files exist
dir database\migrations\
# Should see: __init__.py and 0001_initial.py

# Verify migration status
python manage.py showmigrations database
# Should show: [X] 0001_initial

# If not migrated:
python manage.py migrate database
```

### ✅ Database URL Configuration
Check `config/urls.py`:
```python
# Should include:
path('database/', include('database.urls')),
```

### ✅ Admin Registration
Check `database/admin.py`:
```python
# Should have:
@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    # ...
```

### ✅ Test Backend Server
```bash
# Start server
python manage.py runserver

# In another terminal:
curl http://127.0.0.1:8000/admin/
# Should return HTML (Django admin page)

# Test database endpoint (will fail auth, but endpoint should exist)
curl http://127.0.0.1:8000/database/
# Should return: {"detail":"Authentication credentials were not provided."}
```

---

## 3. Frontend Verification

### ✅ Package Dependencies
Check `frontend/package.json`:
```json
{
  "dependencies": {
    "axios": "^1.6.2",
    "framer-motion": "^12.23.24",  ✓
    "react": "^18.2.0",
    "react-hot-toast": "^2.4.1",  ✓
    // ...
  }
}
```

### ✅ Frontend Files Exist
```bash
cd frontend\src

# Check new files
dir pages\database\DatabaseManagement.jsx
# Should exist

# Check modified files
dir App.jsx
dir layouts\DashboardLayout.jsx
dir api\endpoints.js
```

### ✅ Frontend Configuration
Check `frontend/.env` (create if doesn't exist):
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### ✅ Test Frontend Build
```bash
cd frontend
npm run dev

# Should start without errors
# Open: http://localhost:5173
# Should see homepage
```

---

## 4. ETL System Verification

### ✅ Docker Compose File
Check `etl-final/docker-compose.yml`:
```yaml
# Verify services exist:
✓ kafka
✓ clickhouse
✓ surrealdb
✓ connector-service (port 8001)
✓ detector-service
✓ extractor-service
✓ transformer-service
✓ loader-service
✓ metadata-service
```

### ✅ Start ETL Services
```bash
cd etl-final
docker-compose up -d

# Wait 30 seconds for startup
timeout /t 30

# Check all services are running
docker-compose ps
# All should show "Up"
```

### ✅ Test ETL Connector
```bash
# Test connector endpoint
curl http://127.0.0.1:8001/api/upload/
# Should return error about missing file (that's OK)

# Check connector logs
docker-compose logs connector-service | tail -20
# Should not show errors
```

### ✅ Test ClickHouse
```bash
# Test ClickHouse HTTP interface
curl http://localhost:8123
# Should return: Ok.

# Test ClickHouse client
docker exec -it etl-final-clickhouse-1 clickhouse-client --query "SHOW DATABASES"
# Should list databases
```

### ✅ Test Kafka
```bash
# List Kafka topics
docker exec -it etl-final-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
# Should show: connection_topic, detection_topic, etc.
```

---

## 5. Database Feature Specific Checks

### ✅ Manager User Exists
```bash
python manage.py shell

from users.models import User
managers = User.objects.filter(role='manager')
print(f"Manager count: {managers.count()}")
for m in managers:
    print(f"  - {m.email}")

# If no managers, create one:
# exit()
# python manage.py createsuperuser
```

### ✅ Database Model Accessible
```bash
python manage.py shell

from database.models import Database
print(Database.objects.count())
# Should work without error (count may be 0)

# Check model fields
print(Database._meta.get_fields())
```

### ✅ API Endpoints Registered
```bash
python manage.py show_urls | findstr database
# Should show:
# /database/ [name='database-detail']
# /database/upload/ [name='database-upload']
# /database/preview/ [name='database-preview']
```

### ✅ ClickHouse Client Works
```bash
python manage.py shell

from database.utils import ClickHouseClient
ch = ClickHouseClient()
result = ch.execute_query("SELECT 1")
print(result)
# Should show: {'success': True, 'data': '1\n'}
```

---

## 6. Integration Test

### ✅ Full Flow Test

1. **Start all services** (3 terminals):
```bash
# Terminal 1: Backend
python manage.py runserver

# Terminal 2: ETL
cd etl-final
docker-compose up -d

# Terminal 3: Frontend
cd frontend
npm run dev
```

2. **Create test CSV**:
```csv
id,name,age
1,John,30
2,Jane,28
```
Save as `test_data.csv`

3. **Test upload flow**:
- Open http://localhost:5173
- Login as manager
- Click "Database" in sidebar
- Upload `test_data.csv`
- Wait for "Processing" → "Completed"
- Verify schema shows: id, name, age
- Verify preview shows 2 rows

4. **Test replace flow**:
- Upload different CSV
- Confirm in modal
- Verify new data appears

5. **Test delete flow**:
- Click "Delete Database"
- Confirm deletion
- Verify back to upload state

6. **Verify ClickHouse cleanup**:
```bash
docker exec -it etl-final-clickhouse-1 clickhouse-client --query "SHOW TABLES"
# After delete, table should be gone
```

---

## 7. Browser Verification

### ✅ Console Check
1. Open http://localhost:5173
2. Press F12 (DevTools)
3. Go to Console tab
4. Should see no errors
5. Should see no warnings

### ✅ Network Check
1. In DevTools, go to Network tab
2. Login and navigate to Database page
3. All requests should return 200 or 201
4. No 404 or 500 errors

### ✅ Responsive Check
1. In DevTools, toggle device toolbar (Ctrl+Shift+M)
2. Test on:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)
3. No layout breaks

---

## 8. Security Verification

### ✅ Manager Role Check
```bash
# Try accessing as non-manager
python manage.py shell

from users.models import User
# Create test analyst
analyst = User.objects.create_user(
    email='analyst@test.com',
    password='test123',
    name='Test Analyst',
    role='analyst',
    is_verified=True
)

# Login as analyst in frontend
# Navigate to /dashboard/database
# Should redirect to /dashboard
```

### ✅ JWT Token Required
```bash
# Try without token
curl http://127.0.0.1:8000/database/
# Should return: 401 Unauthorized
```

### ✅ CORS Configured
```bash
# Check settings.py
grep -A 10 "CORS_ALLOWED_ORIGINS" config/settings.py
# Should include: http://localhost:5173
```

---

## 9. Documentation Verification

### ✅ All Docs Exist
```bash
dir *.md

# Should see:
✓ RUN_FROM_SCRATCH.md
✓ QUICK_TEST_GUIDE.md
✓ DATABASE_FEATURE_COMPLETE.md
✓ ARCHITECTURE_DIAGRAM.md
✓ TROUBLESHOOTING.md
✓ README_DATABASE_FEATURE.md
✓ DEPLOYMENT_CHECKLIST.md (this file)
```

### ✅ Code Documentation
```bash
# Check docstrings exist
grep -r "\"\"\"" database/
# Should find multiple docstrings

# Check comments exist
grep -r "#" database/
# Should find many comments
```

---

## 10. Performance Check

### ✅ Load Times
- [ ] Frontend loads in < 2 seconds
- [ ] Backend API responds in < 500ms
- [ ] Database page loads in < 1 second
- [ ] Upload starts in < 1 second
- [ ] ETL completes in < 30 seconds (for small files)

### ✅ Resource Usage
```bash
# Check Docker resources
docker stats

# Should not exceed:
# - CPU: 50% per container
# - Memory: 500MB per container
```

---

## 11. Final Checklist

Before demo or production:

### System Status
- [ ] PostgreSQL running and accessible
- [ ] Django backend running (port 8000)
- [ ] ETL services running (all 'Up' status)
- [ ] Frontend running (port 5173)
- [ ] ClickHouse responding (port 8123)
- [ ] Kafka topics created

### Feature Status
- [ ] Manager user exists and can login
- [ ] Database page accessible to manager
- [ ] Upload works end-to-end
- [ ] ETL processes file successfully
- [ ] Preview displays data
- [ ] Replace flow works
- [ ] Delete flow works
- [ ] Non-managers cannot access

### Quality Status
- [ ] No console errors
- [ ] No linter warnings
- [ ] All migrations applied
- [ ] No broken imports
- [ ] Responsive design works
- [ ] Animations smooth

### Documentation Status
- [ ] All 6 docs created
- [ ] Code commented
- [ ] API documented
- [ ] Architecture explained

---

## 12. Quick Status Script

Save this as `check_status.ps1` (Windows):

```powershell
Write-Host "=== System Status Check ===" -ForegroundColor Green

# Backend
Write-Host "`n[Backend]" -ForegroundColor Yellow
$backend = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet
if ($backend) { Write-Host "✓ Django running" -ForegroundColor Green } 
else { Write-Host "✗ Django not running" -ForegroundColor Red }

# ETL
Write-Host "`n[ETL]" -ForegroundColor Yellow
$etl = Test-NetConnection -ComputerName 127.0.0.1 -Port 8001 -InformationLevel Quiet
if ($etl) { Write-Host "✓ ETL Connector running" -ForegroundColor Green } 
else { Write-Host "✗ ETL Connector not running" -ForegroundColor Red }

# Frontend
Write-Host "`n[Frontend]" -ForegroundColor Yellow
$frontend = Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -InformationLevel Quiet
if ($frontend) { Write-Host "✓ Frontend running" -ForegroundColor Green } 
else { Write-Host "✗ Frontend not running" -ForegroundColor Red }

# ClickHouse
Write-Host "`n[ClickHouse]" -ForegroundColor Yellow
$clickhouse = Test-NetConnection -ComputerName 127.0.0.1 -Port 8123 -InformationLevel Quiet
if ($clickhouse) { Write-Host "✓ ClickHouse running" -ForegroundColor Green } 
else { Write-Host "✗ ClickHouse not running" -ForegroundColor Red }

# Database Check
Write-Host "`n[Database]" -ForegroundColor Yellow
$dbCheck = python -c "from database.models import Database; print('OK')" 2>&1
if ($dbCheck -eq "OK") { Write-Host "✓ Database model accessible" -ForegroundColor Green }
else { Write-Host "✗ Database model error" -ForegroundColor Red }

Write-Host "`n=== Status Check Complete ===" -ForegroundColor Green
```

Run: `powershell .\check_status.ps1`

---

## 🎯 Ready for Demo?

If all items above are checked, you're ready to:
- ✅ Demonstrate to your advisor
- ✅ Present to evaluation committee
- ✅ Deploy to staging environment
- ✅ Showcase to stakeholders

---

## 🚨 If Something Fails

1. **Don't Panic** - Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. **Check Logs** - Backend, ETL, Frontend console
3. **Restart Services** - Often fixes transient issues
4. **Review Checklist** - Ensure all steps completed
5. **Emergency Reset** - See TROUBLESHOOTING.md final section

---

## 📞 Pre-Demo Support

### Day Before Demo
- [ ] Run full system check
- [ ] Test complete upload flow 3 times
- [ ] Verify all services start cleanly
- [ ] Check browser compatibility
- [ ] Prepare backup test data
- [ ] Review documentation

### Demo Day
- [ ] Start services 30 minutes early
- [ ] Verify all endpoints responding
- [ ] Clear browser cache
- [ ] Have backup CSV files ready
- [ ] Keep TROUBLESHOOTING.md open
- [ ] Stay calm and confident

---

**✅ You're all set! Good luck with your demo! 🎓🎉**

