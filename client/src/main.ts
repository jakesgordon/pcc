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

type DebugFrameMessage = {
  type: "debug-frame",
  payload: {
    frame: string,
    details: any,
    dir: string,
  }
}

type ServerMessage =
  | DebugFrameMessage

function onServerMessage(message: ServerMessage) {
  if (message.type === "debug-frame") {
    console.log(message.payload.frame, message.payload.dir, message.payload.details)
  } else {
    console.log("unknown message", message)
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
