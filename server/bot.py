import os
import aiohttp
import sys

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.audio.turn.smart_turn.fal_smart_turn import FalSmartTurnAnalyzer
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.observers.base_observer import BaseObserver, FramePushed
from pipecat.pipeline.pipeline import Pipeline, PipelineSink
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext, OpenAILLMContextFrame
from pipecat.processors.frame_processor import Frame, FrameProcessor, FrameDirection
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor, RTVIServerMessageFrame
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.services.daily import DailyParams

from pipecat.frames.frames import (
    BotSpeakingFrame,
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    InputAudioRawFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMMessagesAppendFrame,
    LLMMessagesFrame,
    LLMMessagesUpdateFrame,
    LLMRunFrame,
    LLMTextFrame,
    MetricsFrame,
    OutputTransportReadyFrame,
    SpeechControlParamsFrame,
    StartFrame,
    StartInterruptionFrame,
    StopInterruptionFrame,
    TTSAudioRawFrame,
    TTSStartedFrame,
    TTSTextFrame,
    TTSUpdateSettingsFrame,
    TextFrame,
    TranscriptionFrame,
    TranscriptionUpdateFrame,
    TransportMessageUrgentFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)

load_dotenv(override=True)

#==================================================================================================

def tune_logger():
    logger.remove()
    logger.add(sys.stderr, format="<level>{level}</level> | <cyan>{message}</cyan>", level="INFO")

NEVER_TRACE = (
    BotSpeakingFrame,
    InputAudioRawFrame,
    MetricsFrame,
    OutputTransportReadyFrame,
    RTVIServerMessageFrame,
    SpeechControlParamsFrame,
    TTSAudioRawFrame,
    TransportMessageUrgentFrame,
)

WOMAN="21m00Tcm4TlvDq8ikWAM" # Rachel
MAN="2EiwWnXFnvU5JabPnv8n" # Clyde

#==================================================================================================

class ExperienceObserver(BaseObserver):
    def __init__(self, rtvi):
        super().__init__()
        self.rtvi = rtvi

    async def on_push_frame(self, data: FramePushed):
        frame = data.frame
        src  = data.source
        dst  = data.destination
        dir  = f"{src.__class__.__name__} -> {dst.__class__.__name__}"
        if isinstance(frame, OpenAILLMContextFrame):
            await self.trace(frame, dir, [f"{m["role"]}> {m["content"]}" for m in frame.context.messages])
        elif isinstance(frame, TextFrame):
            await self.trace(frame, dir, frame.text)
        elif not isinstance(frame, NEVER_TRACE):
            await self.trace(frame, dir)

    async def trace(self, frame, dir, details = None):
        name = frame.__class__.__name__
        if details is None:
            logger.info(f"{name} : {dir}")
        else:
            logger.info(f"{name} : {dir} : {details}")

        await self.rtvi.push_frame(RTVIServerMessageFrame(
            data={
                "type": "debug-frame",
                "payload": {
                    "frame": name,
                    "details": details,
                    "dir": f"{dir}",
                },
            }
        ))

#==================================================================================================

class ExperienceProcessor(FrameProcessor):
    def __init__(self, rtvi):
        super().__init__()
        self.rtvi = rtvi

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            if "woman" in frame.text.lower():
                await self.trace(frame, "SWITCH TO WOMAN")
                await self.push_frame(
                    TTSUpdateSettingsFrame(settings={
                      "voice": WOMAN
                    })
                )
            elif "man" in frame.text.lower():
                await self.trace(frame, "SWITCH TO MAN")
                await self.push_frame(
                    TTSUpdateSettingsFrame(settings={
                      "voice": MAN
                    })
                )

        elif isinstance(frame, OpenAILLMContextFrame):
            await self.trace(frame, [f"{m["role"]}> {m["content"]}" for m in frame.context.messages])
        elif isinstance(frame, TextFrame):
            await self.trace(frame, frame.text)
        elif not isinstance(frame, NEVER_TRACE):
            await self.trace(frame)

        await self.push_frame(frame, direction)

    async def trace(self, frame, details = None):
        name = frame.__class__.__name__
        if details is None:
            logger.info(f"{name}")
        else:
            logger.info(f"{name}: {details}")

        await self.rtvi.push_frame(RTVIServerMessageFrame(
            data={
                "type": "debug-frame",
                "payload": {
                    "frame": name,
                    "details": details,
                },
            }
        ))

#==================================================================================================

async def run_bot(transport: BaseTransport):
    tune_logger()
    logger.info("STARTING BOT")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        model=os.getenv("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5"),
        voice_id=WOMAN,
    )
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant. Respond naturally and keep your answers conversational, but brief.",
        },
        {
            "role": "system",
            "content": "Say hello and briefly introduce yourself."
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))
    experience = ExperienceProcessor(rtvi)

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            experience, # OUR EXPERIENCE
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
            allow_interruptions=True,
        ),
        observers=[
            RTVIObserver(rtvi),
            # ExperienceObserver(rtvi),
        ],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("CLIENT CONNECTED")
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("CLIENT DISCONNECTED")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)

#==================================================================================================

async def bot(runner_args: RunnerArguments):

    async with aiohttp.ClientSession() as session:

        vad_analyzer = SileroVADAnalyzer(
            params=VADParams(
                confidence=0.7,
                start_secs=0.2,
                stop_secs=2,
                min_volume=0.6,
            ),
        )

        smart_turn_analyzer = FalSmartTurnAnalyzer(
            api_key = os.getenv("FAL_API_KEY"),
            aiohttp_session=session,
            params=SmartTurnParams(
                stop_secs=3.0,
                pre_speech_ms=0.0,
                max_duration_secs=8.0,
            ),
        )

        transport_params = {
            # DEVELOPMENT
            "webrtc": lambda: TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad_analyzer,
                smart_turn_analyzer=smart_turn_analyzer,
            ),

            # PRODUCTION
            "daily": lambda: DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad_analyzer,
                smart_turn_analyzer=smart_turn_analyzer,
            ),
        }

        transport = await create_transport(runner_args, transport_params)

        await run_bot(transport)

#==================================================================================================

if __name__ == "__main__":
    from pipecat.runner.run import main
    main()
