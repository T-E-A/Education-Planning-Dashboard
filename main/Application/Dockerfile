FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl

# Copy requirements and install
COPY Application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Application/ /app/

EXPOSE 8519

#Command to Run Application
CMD ["python", "main.py"]