FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app
COPY requirements.txt .
COPY imap.py .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./src

CMD ["python3", "imap.py"]