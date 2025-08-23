FROM dailyco/pipecat-base:latest

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry config installer.max_workers 10
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN poetry install --only main --no-interaction --no-ansi
RUN poetry run python -m s
