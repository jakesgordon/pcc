/// <reference types="vite/client" />

import { PipecatClient, Participant } from "@pipecat-ai/client-js"
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport"

function handleBotAudio(track: MediaStreamTrack, participant?: Participant) {
  if (participant?.local || track.kind !== "audio") return;
  const audioElement = document.createElement("audio");
  audioElement.srcObject = new MediaStream([track]);
  document.body.appendChild(audioElement);
  audioElement.play();
}

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
