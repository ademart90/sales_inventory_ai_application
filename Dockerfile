FROM python:3.11-slim

# Set working directory to root so relative paths (data/, sales_inventory.db) work
WORKDIR /app

# Ensure Python finds modules inside src/ cleanly
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project into the container
COPY . .

# Expose both FastAPI (8000) and Streamlit (8501) ports
EXPOSE 8000 8501
