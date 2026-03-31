FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl

# Copy requirements and install
COPY DataProcessingService/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code
COPY DataProcessingService/ /app/

# Default command to run the FastAPI server
CMD ["python", "main.py"]