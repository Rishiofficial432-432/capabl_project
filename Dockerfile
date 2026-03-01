# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# Stage 2: Build the FastAPI backend and serve everything
FROM python:3.11-slim
WORKDIR /app

# System dependencies (for potential binary packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code including tools
COPY agent.py database.py main.py utils.py ./
COPY tools ./tools

# Copy the built React app from the first stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the standard HF Spaces Port
EXPOSE 7860

# Run FastAPI server
# Since this is a container, we bind to 0.0.0.0 and port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
