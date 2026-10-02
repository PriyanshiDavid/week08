FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --root-user-action=ignore \
    -r requirements.txt

COPY . .

RUN useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser

# Set only for the deliberately faulty demo image
ARG FAULT_RATE=0
ENV FAULT_RATE=${FAULT_RATE}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]