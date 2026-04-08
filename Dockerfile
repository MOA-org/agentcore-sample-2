# App Management backend runs: docker build -f <dockerfile_path> -t <ecr_uri:tag> .
# CodeBuild hosts are often x86_64 — if AgentCore requires arm64, use linux/arm64 + ARM CodeBuild.
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=25s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/ping', timeout=5)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
