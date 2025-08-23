import { PipecatClient, Participant } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";

function handleBotAudio(track: MediaStreamTrack, participant?: Participant) {
  if (participant?.local || track.kind !== "audio") return;
  const audioElement = document.createElement("audio");
  audioElement.srcObject = new MediaStream([track]);
  document.body.appendChild(audioElement);
  audioElement.play();
}

const pcClient = new PipecatClient({
  transport: new SmallWebRTCTransport(),
  enableCam: false, // Default camera off
  enableMic: true, // Default microphone on
  callbacks: {
    onTrackStarted: handleBotAudio
  },
});

await pcClient.connect({
  connectionUrl: "/api/offer"
})
