# Technology Stack and Dependencies: Langflow

## Core Technology Stack

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Flow Editor**: ReactFlow
- **State Management**: Zustand
- **Styling**: Tailwind CSS, shadcn/ui components
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **Data Visualization**: D3.js
- **Code Highlighting**: React Syntax Highlighter
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **API Documentation**: Swagger UI (via FastAPI)
- **Data Validation**: Pydantic
- **ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery (for background tasks)
- **WebSockets**: FastAPI WebSockets

### Database
- **Development**: SQLite
- **Production**: PostgreSQL (supported)
- **Caching**: Redis (optional)

### LLM Integration
- **Primary Framework**: LangChain
- **Supported LLM Providers**:
  - OpenAI
  - Anthropic
  - Google AI
  - Hugging Face
  - Ollama
  - Azure OpenAI
  - And others via LangChain integrations

### Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Hosting Options**: Self-hosted, Cloud (AWS, GCP, Azure)

## Development Tools

### Package Management
- **Backend**: uv (Python package manager)
- **Frontend**: npm

### Testing
- **Backend**: pytest
- **Frontend**: Playwright
- **Load Testing**: Locust

### Code Quality
- **Linting**: 
  - Backend: ruff
  - Frontend: ESLint
- **Formatting**: 
  - Backend: ruff format
  - Frontend: Prettier
- **Type Checking**: 
  - Backend: mypy
  - Frontend: TypeScript

### Build System
- **Task Runner**: Makefile
- **Frontend Build**: Vite
- **Backend Build**: uv build

## Key Dependencies

### Backend Dependencies
```
fastapi
uvicorn
sqlalchemy
alembic
pydantic
langchain
langchain-community
langchain-core
python-multipart
python-jose[cryptography]
passlib[bcrypt]
celery
redis
psycopg2-binary (for PostgreSQL)
```

### Frontend Dependencies
```
react
react-dom
@reactflow/core
@reactflow/node-resizer
@reactflow/background
zustand
axios
tailwindcss
@headlessui/react
@radix-ui/react-*
react-hook-form
zod
lucide-react
react-syntax-highlighter
d3
```

## Environment Configuration

### Environment Variables
- **Database Configuration**: 
  - `LANGFLOW_DATABASE_URL`
  - `LANGFLOW_DATABASE_CONNECTION_RETRY`
- **Server Configuration**:
  - `LANGFLOW_HOST`
  - `LANGFLOW_PORT`
  - `LANGFLOW_WORKERS`
- **Authentication**:
  - `LANGFLOW_AUTO_LOGIN`
  - `LANGFLOW_SUPERUSER`
  - `LANGFLOW_SUPERUSER_PASSWORD`
- **Frontend Configuration**:
  - `LANGFLOW_FRONTEND_PATH`
  - `BACKEND_URL`
- **Logging**:
  - `LANGFLOW_LOG_LEVEL`
  - `LANGFLOW_LOG_FILE`
- **Caching**:
  - `LANGFLOW_CACHE_TYPE`
  - `LANGFLOW_LANGCHAIN_CACHE`

### Configuration Files
- `.env`: Environment variables
- `pyproject.toml`: Python project configuration
- `package.json`: Frontend dependencies
- `tsconfig.json`: TypeScript configuration
- `tailwind.config.mjs`: Tailwind CSS configuration
- `vite.config.mts`: Vite configuration

## Development Environment Setup

### Local Development
1. **Clone Repository**:
   ```bash
   git clone https://github.com/langflow-ai/langflow.git
   cd langflow
   ```

2. **Backend Setup**:
   ```bash
   make install_backend
   ```

3. **Frontend Setup**:
   ```bash
   make install_frontend
   ```

4. **Run Development Servers**:
   ```bash
   # Backend
   make backend
   
   # Frontend
   make frontend
   ```

### Docker Development
```bash
# Build and run with Docker Compose
make docker_compose_up
```

## Deployment Options

### Self-Hosted Deployment
1. **Build the Application**:
   ```bash
   make build
   ```

2. **Run with Python**:
   ```bash
   langflow run
   ```

### Docker Deployment
```bash
# Pull the Docker image
docker pull langflow/langflow

# Run the container
docker run -p 7860:7860 langflow/langflow
```

### Cloud Deployment
- **AWS**: EC2, ECS, or EKS
- **GCP**: Compute Engine, GKE
- **Azure**: AKS, VM instances

## Integration Points

### External APIs
- **LLM Provider APIs**: OpenAI, Anthropic, etc.
- **Vector Databases**: Pinecone, Weaviate, Chroma, etc.
- **Document Processing**: Unstructured, etc.

### Authentication Systems
- **Built-in JWT**: Default authentication
- **OAuth**: Supported through custom integrations

### Storage Systems
- **Database**: SQLite/PostgreSQL for flow storage
- **File Storage**: Local filesystem or cloud storage (S3, etc.)

## Performance Considerations

### Scalability
- **Horizontal Scaling**: Multiple backend instances behind load balancer
- **Database Scaling**: PostgreSQL with connection pooling

### Resource Requirements
- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4+ CPU cores, 8GB+ RAM
- **Storage**: Depends on number of flows and usage patterns
