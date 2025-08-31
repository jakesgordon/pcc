set dotenv-load := true

_default:
  just --list

@install:
  cd client && npm install
  cd server && poetry install

@client:
  cd client && npm run dev

@server:
  cd server && poetry run python bot.py

@docker-build:
  docker buildx build --platform=linux/arm64 -t "jakesgordon/jakes-test-bot:latest" --load server
