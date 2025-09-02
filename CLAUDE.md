# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pipecat client/server voice AI application that demonstrates real-time voice communication between a web client and a Python server running Pipecat AI pipelines. The application uses WebRTC for real-time communication and integrates with Deepgram (STT), OpenAI (LLM), and ElevenLabs (TTS) services.

## Architecture

**Client/Server Separation**: The project follows Pipecat's recommended client/server architecture:
- **Client** (`/client`): TypeScript/Vite frontend using Pipecat Client SDK
- **Server** (`/server`): Python backend using Pipecat AI framework with voice processing pipeline

**Key Components**:
- **Transport Layer**: Uses SmallWebRTCTransport for development, Daily transport for production
- **Pipeline**: STT → Context Aggregator → LLM → TTS flow with RTVI processor
- **Voice Activity Detection**: Silero VAD analyzer with configurable parameters
- **Smart Turn Management**: FAL Smart Turn analyzer for conversation flow

## Development Commands

Use the `justfile` for common tasks:

```bash
# Install dependencies for both client and server
just install

# Run client development server (http://localhost:5173)
just client

# Run server bot
just server

# Build Docker image
just docker-build
```

**Manual Commands**:
- Client: `cd client && npm run dev` (development), `npm run build` (production)
- Server: `cd server && poetry run python bot.py`

## Environment Configuration

Required environment variables in `server/.env`:
- `DEEPGRAM_API_KEY`: For speech-to-text
- `OPENAI_API_KEY`: For LLM responses  
- `ELEVENLABS_API_KEY`: For text-to-speech
- `FAL_API_KEY`: For smart turn analysis

## Key Files

**Server**:
- `server/bot.py`: Main bot implementation with pipeline configuration
- `server/pyproject.toml`: Poetry dependencies including pipecat-ai with extensions

**Client**:
- `client/src/main.ts`: Client-side Pipecat integration
- `client/package.json`: Contains Pipecat client SDK dependencies

## Pipeline Configuration

The server implements a configurable pipeline with:
- VAD parameters: confidence=0.7, start_secs=0.2, stop_secs=2
- Smart turn parameters: stop_secs=3.0, max_duration_secs=8.0  
- Transport switching between WebRTC (development) and Daily (production)
- RTVI processor for real-time voice interface

## Development Notes

- Server uses Poetry for dependency management
- Client uses npm with Vite for development
- Both client and server must run simultaneously for full functionality
- WebRTC requires microphone permissions and UDP connectivity
