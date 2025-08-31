import os
import aiohttp
import sys

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.audio.turn.smart_turn.fal_smart_turn import FalSmartTurnAnalyzer
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.frames.frames import BotStartedSpeakingFrame, BotStoppedSpeakingFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor, RTVIServerMessageFrame
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.services.daily import DailyParams

load_dotenv(override=True)

#==================================================================================================

def tune_logger():
    logger.remove()
    logger.add(sys.stderr, level="INFO")

def trace(message):
    logger.success(f"[*** TRACE ***] {message}")

#==================================================================================================

class ExperienceProcessor(FrameProcessor):
    def __init__(self, rtvi):
        super().__init__()
        self.rtvi = rtvi

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            trace("BOT STARTED SPEAKING")
            await self.rtvi.push_frame(RTVIServerMessageFrame(
                data={
                    "type": "bot-started-speaking",
                    "payload": {"yolo": "hello"},
                }
            ))

        elif isinstance(frame, BotStoppedSpeakingFrame):
            trace("BOT STOPPED SPEAKING")
            await self.rtvi.push_frame(RTVIServerMessageFrame(
                data={
                    "type": "bot-stopped-speaking",
                    "payload": {"yolo": "goodbye"},
                }
            ))

        await self.push_frame(frame)

#==================================================================================================

async def run_bot(transport: BaseTransport):
    tune_logger()
    trace("STARTING BOT")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="71a7ad14-091c-4e8e-a314-022ece01c121",  # British Reading Lady
    )
    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": "You are a friendly AI assistant. Respond naturally and keep your answers conversational.",
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
            experience, # OUR CUSTOM EXPERIENCE
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
        ],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        trace("CLIENT CONNECTED")
        # Kick off the conversation.
        messages.append({"role": "system", "content": "Say hello and briefly introduce yourself."})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        trace("CLIENT DISCONNECTED")
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
