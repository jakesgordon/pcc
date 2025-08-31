/// <reference types="vite/client" />

import { PipecatClient, Participant } from "@pipecat-ai/client-js"
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport"

function onTrackStarted(track: MediaStreamTrack, participant?: Participant) {
  if (participant?.local || track.kind !== "audio") return;
  const audioElement = document.createElement("audio");
  audioElement.srcObject = new MediaStream([track]);
  document.body.appendChild(audioElement);
  audioElement.play();
}


type BotStartedSpeakingMessage = {
  type: "bot-started-speaking",
  payload: {
    yolo: string
  }
}

type BotStoppedSpeakingMessage = {
  type: "bot-stopped-speaking",
  payload: {
    yolo: string
  }
}

type ServerMessage =
  | BotStartedSpeakingMessage
  | BotStoppedSpeakingMessage

function onServerMessage(message: ServerMessage) {
  if (message.type === "bot-started-speaking") {
    console.log("🤖 Bot started speaking", message.payload.yolo)
  } else if (message.type === "bot-stopped-speaking") {
    console.log("🤖 Bot stopped speaking", message.payload.yolo)
  } else {
    console.error("unexpected server message", message)
  }
}

const pcc = new PipecatClient({
  transport: new SmallWebRTCTransport(),
  enableCam: false,
  enableMic: true,
  callbacks: {
    onTrackStarted: onTrackStarted,
    onServerMessage: onServerMessage
  },
});

await pcc.connect({
  connectionUrl: "/api/offer"
})
