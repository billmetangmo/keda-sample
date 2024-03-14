FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY apps/utils ./utils
ARG APP_ROLE
COPY apps/${APP_ROLE} .
CMD ["python", "main.py"]