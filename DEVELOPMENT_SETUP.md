# Langflow Development Setup Guide

This guide provides a robust, automated solution for setting up and running Langflow in development mode. The setup addresses common issues with frontend-backend connections, database migrations, and provides reliable startup procedures.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Start both frontend and backend with proper configuration
./scripts/dev-start.sh
```

### Option 2: Manual Setup

```bash
# Terminal 1: Start Backend
python -m langflow run --backend-only --host 127.0.0.1 --port 7860

# Terminal 2: Start Frontend
cd src/frontend
VITE_BACKEND_URL=http://127.0.0.1:7860 npm start
```

### Option 3: Using NPM Scripts

```bash
cd src/frontend

# Start frontend with correct backend URL
npm run dev

# Or start both frontend and backend (requires concurrently)
npm run dev:full
```

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database (Supabase configured)
- Git

## 🔧 Configuration

### Environment Variables

The development setup uses standardized environment variables defined in `.env.development`:

```bash
# Backend Configuration
LANGFLOW_HOST=127.0.0.1
LANGFLOW_PORT=7860
LANGFLOW_WORKERS=1
LANGFLOW_LOG_LEVEL=info

# Database Configuration
LANGFLOW_DATABASE_URL=postgresql://postgres:MPStander999@db.tesimbcfpfgrazocngof.supabase.co:5432/postgres
LANGFLOW_DATABASE_CONNECTION_RETRY=true

# Frontend Configuration
VITE_BACKEND_URL=http://127.0.0.1:7860
VITE_PORT=3000
```

### Port Configuration

- **Backend**: `127.0.0.1:7860`
- **Frontend**: `127.0.0.1:3000`

These ports are standardized across all configuration files to prevent connection issues.

## 🛠️ Features

### 1. Standardized Connection Configuration

- Frontend automatically connects to the correct backend port
- Environment variables override hardcoded values
- Consistent configuration across all files

### 2. Robust Database Migration System

- Automatic retry logic for migration lock timeouts
- Graceful handling of concurrent connections
- Fallback to legacy migration system if needed
- PostgreSQL advisory lock management

### 3. Improved Error Handling

- Connection timeout detection and reporting
- Graceful degradation when backend is unavailable
- Clear error messages with actionable guidance

### 4. Automated Startup Scripts

- Health checks for database connectivity
- Proper service startup sequence
- Process management and cleanup
- Detailed logging and status reporting

## 📁 File Structure

```
langflow/
├── .env.development              # Development environment variables
├── scripts/
│   ├── dev-start.sh             # Automated startup script
│   └── dev-stop.sh              # Cleanup script
├── src/
│   ├── backend/
│   │   └── base/langflow/
│   │       ├── services/database/service.py  # Enhanced migration handling
│   │       └── utils/migration_utils.py      # New migration utilities
│   └── frontend/
│       ├── vite.config.mts      # Enhanced proxy configuration
│       ├── package.json         # New development scripts
│       └── src/customization/
│           └── config-constants.ts  # Dynamic backend URL
└── DEVELOPMENT_SETUP.md         # This documentation
```

## 🔄 Migration System

### New Migration Features

1. **Lock Timeout Handling**: Automatically detects and handles PostgreSQL advisory lock timeouts
2. **Retry Logic**: Exponential backoff for failed migrations
3. **Force Lock Release**: Ability to clear stuck migration locks
4. **Health Checks**: Verify migration status before attempting changes
5. **Fallback System**: Falls back to legacy migration system if new system fails

### Migration Commands

```bash
# Check migration status
python -c "
from langflow.utils.migration_utils import DatabaseMigrationManager
import asyncio
# ... check migration status
"

# Force release stuck locks (if needed)
python -c "
from langflow.services.deps import get_db_service
import asyncio
# ... force release locks
"
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Frontend Cannot Connect to Backend

**Symptoms**: 
- `ETIMEDOUT` errors in frontend console
- "Backend service unavailable" messages

**Solutions**:
```bash
# Check if backend is running
curl http://127.0.0.1:7860/health

# Restart with correct configuration
./scripts/dev-stop.sh
./scripts/dev-start.sh
```

#### 2. Database Migration Lock Timeout

**Symptoms**:
- `psycopg.errors.LockNotAvailable` errors
- Backend stuck at "Running DB migrations"

**Solutions**:
```bash
# Stop all services
./scripts/dev-stop.sh

# Check for stuck processes
ps aux | grep langflow

# Force kill if necessary
pkill -f langflow

# Restart
./scripts/dev-start.sh
```

#### 3. Port Already in Use

**Symptoms**:
- `EADDRINUSE` errors
- Services fail to start

**Solutions**:
```bash
# Check what's using the ports
lsof -i :7860
lsof -i :3000

# Kill processes on ports
lsof -ti:7860 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Or use the stop script
./scripts/dev-stop.sh
```

#### 4. Database Connection Issues

**Symptoms**:
- Database connection errors
- Migration failures

**Solutions**:
```bash
# Test database connectivity
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('postgresql+asyncpg://postgres:MPStander999@db.tesimbcfpfgrazocngof.supabase.co:5432/postgres')
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('Database connection successful')
    await engine.dispose()

asyncio.run(test())
"
```

## 📊 Monitoring and Logs

### Log Files

- **Backend**: `logs/backend.log`
- **Frontend**: `logs/frontend.log`
- **Alembic**: `src/backend/base/langflow/alembic/alembic.log`

### Health Checks

```bash
# Backend health
curl http://127.0.0.1:7860/health

# Frontend health
curl http://127.0.0.1:3000

# Database health
npm run health-check  # (from frontend directory)
```

## 🔄 Development Workflow

### Standard Development Process

1. **Start Development Environment**:
   ```bash
   ./scripts/dev-start.sh
   ```

2. **Make Changes**: Edit code as needed

3. **Test Changes**: 
   - Frontend hot-reloads automatically
   - Backend requires restart for most changes

4. **Stop Environment**:
   ```bash
   ./scripts/dev-stop.sh
   ```

### Database Schema Changes

1. **Create Migration**:
   ```bash
   cd src/backend/base
   python -m alembic revision --autogenerate -m "Description of changes"
   ```

2. **Review Migration**: Check the generated migration file

3. **Test Migration**: Restart development environment to apply

4. **Verify Changes**: Check that tables/columns are created correctly

## 🎯 Best Practices

1. **Always use the startup scripts** for consistent environment setup
2. **Check logs** when issues occur - they provide detailed error information
3. **Use environment variables** instead of hardcoding URLs or ports
4. **Test database connectivity** before starting development
5. **Clean up processes** when switching between different development setups

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. Check the log files for detailed error messages
2. Verify all prerequisites are installed and configured
3. Ensure database connectivity
4. Try the automated startup script first
5. Use the troubleshooting section for common issues

For persistent issues, the automated scripts provide detailed error reporting and suggested solutions.
