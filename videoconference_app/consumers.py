# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RandomCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'randomcall_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify others in the group to leave
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'message': 'User has left the room'
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message']
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def user_left(self, event):
        message = event['message']

        # Notify user to redirect to dashboard
        await self.send(text_data=json.dumps({
            'leave': True,
            'message': message
        }))

// Same variables like in the earlier example:
// - `localStream`: your local media stream (obtained from WebRTC)
// - `peerConnections`: a map of PeerConnection objects by their user ID

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

// Function to initiate recording
async function startRecording() {
    recordedChunks = [];
  // Create a MediaRecorder
    mediaRecorder = new MediaRecorder(localStream, {
    mimeType: 'video/webm;codecs=vp9,opus' // Or 'video/mp4;codecs=avc1,mp4a' etc
  });
    
  // Event handler to append data
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    }

  mediaRecorder.onstop = async() => {
        console.log('Recording stopped')

       let blob = new Blob(recordedChunks, { type: 'video/webm' })
       const fileName = `recording-${Date.now()}.webm`;
        const file = new File([blob],fileName,{type:"video/webm"})

        const formData = new FormData()
        formData.append("file", file)


        try {
             const res = await fetch('/save-recording/', {  // Update this url
            method: 'POST',
           body: formData
            });

             if(res.ok){
               console.log("recording uploaded successfully");
            }
            
        } catch (e) {
             console.log(e);
        }

  }
    mediaRecorder.start();
    isRecording = true;
    console.log('Recording started');

}

// Function to stop recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        isRecording = false;
        console.log('Stopping recording');
    }
}

// Example UI button event handler
document.getElementById('startRecordingBtn').addEventListener('click', () => {
  if(isRecording){
      stopRecording();
  }else{
    startRecording();
  }
    
});

