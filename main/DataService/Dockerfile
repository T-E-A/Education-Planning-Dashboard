# using python 3.11 slim as the base image to keep the container lightweight
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install curl for health checks / debugging inside the container
RUN apt-get update && apt-get install -y curl

# set the working directory inside the container
WORKDIR /db_app

# copy and install dependencies first 
COPY DataService/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the container
COPY DataService/ /db_app/

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]