/// <reference types="vite/client" />

import { PipecatClient, Participant } from "@pipecat-ai/client-js"
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport"
import { DailyTransport } from "@pipecat-ai/daily-transport"

function handleBotAudio(track: MediaStreamTrack, participant?: Participant) {
  if (participant?.local || track.kind !== "audio") return;
  const audioElement = document.createElement("audio");
  audioElement.srcObject = new MediaStream([track]);
  document.body.appendChild(audioElement);
  audioElement.play();
}

const transport = import.meta.env.VITE_TRANSPORT ?? "webrtc"

if (transport === "webrtc") {
  const pcc = new PipecatClient({
    transport: new SmallWebRTCTransport(),
    enableCam: false,
    enableMic: true,
    callbacks: {
      onTrackStarted: handleBotAudio
    },
  });

  await pcc.connect({
    connectionUrl: "/api/offer"
  })

} else if (transport === "daily") {
  const pcc = new PipecatClient({
    transport: new DailyTransport(),
    enableCam: false,
    enableMic: true,
    callbacks: {
      onTrackStarted: handleBotAudio,
    },
  });

  pcc.connect({
    endpoint: "https://localhost:7860/api/connect",
    // url: "https://your-daily-room-url",
    // token: "your-daily-token",
  });
}
