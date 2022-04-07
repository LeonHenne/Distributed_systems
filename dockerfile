# loading the base image
FROM python:3.8-slim

# exposing the desired port which will be mapped
EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#creats the app directory and copies your current directory into the app folder on the container
WORKDIR /app
COPY . /app

# Install pip requirements
RUN python -m pip install -r requirements.txt

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "src/library_api.py"]
