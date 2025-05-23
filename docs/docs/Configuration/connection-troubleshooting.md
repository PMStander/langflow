# Connection Troubleshooting

If you're experiencing connection issues between the frontend and backend of Langflow, follow these steps to resolve them.

## Common Connection Errors

You might see errors like these in your console:

```
http proxy error: /api/v1/config
AggregateError [ECONNREFUSED]: 
    at internalConnectMultiple (node:net:1139:18)
    at afterConnectMultiple (node:net:1714:7)
```

These errors indicate that the frontend is trying to connect to the backend API server, but the connection is being refused.

## Solution: Set Up Environment Variables

### 1. Create a `.env` file in the project root

Create a file named `.env` in the root directory of your project with the following content:

```
# Backend configuration
LANGFLOW_HOST=localhost
LANGFLOW_PORT=7860
LANGFLOW_AUTO_LOGIN=true
LANGFLOW_DATABASE_URL=sqlite:///./langflow.db
BACKEND_URL=http://localhost:7860/
```

### 2. Create a `.env` file in the frontend directory

Create a file named `.env` in the `src/frontend` directory with the following content:

```
# Frontend environment variables
VITE_PROXY_TARGET=http://localhost:7860
VITE_PORT=3000
```

## Starting the Application

1. **Start the backend server first**:
   ```bash
   # From the project root
   make backend
   # Or directly with uvicorn
   uvicorn --factory langflow.main:create_app --host localhost --port 7860 --loop asyncio
   ```

2. **Then start the frontend in a separate terminal**:
   ```bash
   # Navigate to the frontend directory
   cd src/frontend
   # Start the frontend
   npm run dev
   ```

## Additional Troubleshooting

If you still encounter connection issues:

1. **Check if the backend is running**: Make sure the backend server is actually running and listening on port 7860. You can check this with:
   ```bash
   lsof -i :7860
   ```

2. **Check for firewall issues**: Make sure your firewall isn't blocking connections to port 7860.

3. **Try a different host**: If `localhost` doesn't work, try using `127.0.0.1` explicitly in both .env files.

4. **Check for port conflicts**: Make sure no other application is using port 7860. If there is, you can change the port in both .env files.

5. **Docker configuration**: If you're using Docker, make sure the ports are properly mapped and the containers can communicate with each other.
