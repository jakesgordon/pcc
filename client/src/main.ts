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
  }
}

type ServerMessage =
  | DebugFrameMessage

function onServerMessage(message: ServerMessage) {
  if (message.type === "debug-frame") {
    if (message.payload.details) {
      console.log(`${message.payload.frame} > ${message.payload.details}`)
    } else {
      console.log(message.payload.frame)
    }
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
