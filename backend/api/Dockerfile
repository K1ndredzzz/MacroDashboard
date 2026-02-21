FROM python:3.11-slim

WORKDIR /app

# Use Tsinghua PyPI mirror for faster downloads in China
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Cloud Run uses PORT environment variable
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
