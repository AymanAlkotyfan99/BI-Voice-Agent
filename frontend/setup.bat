@echo off
REM BI Voice Agent Frontend - Setup Script (Windows)
REM This script automates the setup process

echo ==================================
echo BI Voice Agent Frontend Setup
echo ==================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed!
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js version:
node --version
echo ✅ npm version:
npm --version
echo.

REM Install dependencies
echo 📦 Installing dependencies...
call npm install

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # Backend API Base URL
        echo VITE_API_BASE_URL=http://127.0.0.1:8000
        echo.
        echo # Frontend Base URL ^(for email verification links^)
        echo VITE_FRONTEND_URL=http://localhost:5173
    ) > .env
    echo ✅ .env file created!
) else (
    echo ℹ️  .env file already exists
)

echo.
echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo 🚀 To start the development server, run:
echo    npm run dev
echo.
echo 📱 The app will be available at:
echo    http://localhost:5173
echo.
echo ⚠️  Make sure the backend is running on:
echo    http://127.0.0.1:8000
echo.
echo 📚 For more information, see:
echo    - QUICK_START.md
echo    - FRONTEND_README.md
echo.
pause

