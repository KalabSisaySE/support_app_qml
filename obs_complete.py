import threading
import time
from obswebsocket import obsws, requests
from obswebsocket.exceptions import ConnectionFailure

# Configuration - Update these values according to your OBS setup
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "1JsPjODRVHB57h6e"
RTMP_SERVER = "rtmp://live.restream.io/live/re_9442228_eventa8eb3240beee4cdda527ff4731922248"


class OBSController:
    def __init__(self):
        self.ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        self.stop_flag = False
        self.recording_active = False
        self.streaming_active = False

    def connect(self):
        try:
            self.ws.connect()
            print("Successfully connected to OBS WebSocket")
        except ConnectionFailure:
            print("Failed to connect to OBS. Make sure OBS is running and WebSocket server is enabled.")
            raise

    def start_recording_streaming(self):
        try:
            # Start recording
            self.ws.call(requests.StartRecording())
            print("Recording started")

            # Start streaming
            self.ws.call(requests.StartStream())
            print("Streaming started")

        except Exception as e:
            print(f"Error starting recording/streaming: {e}")
            raise

    def stop_recording_streaming(self):
        try:
            # Stop recording
            self.ws.call(requests.StopRecording())
            print("Stopping recording...")

            # Stop streaming
            self.ws.call(requests.StopStream())
            print("Stopping streaming...")

        except Exception as e:
            print(f"Error stopping recording/streaming: {e}")
            raise

    def monitor_status(self):
        try:
            while not self.stop_flag:
                # Get recording status
                recording_status = self.ws.call(requests.GetRecordingStatus())
                new_recording_state = recording_status.datain['isRecording']

                # Get streaming status
                streaming_status = self.ws.call(requests.GetStreamStatus())
                new_streaming_state = streaming_status.datain['streaming']

                # Print status changes
                if new_recording_state != self.recording_active:
                    self.recording_active = new_recording_state
                    print(f"Recording status changed to: {'Active' if self.recording_active else 'Inactive'}")

                if new_streaming_state != self.streaming_active:
                    self.streaming_active = new_streaming_state
                    print(f"Streaming status changed to: {'Active' if self.streaming_active else 'Inactive'}")

                time.sleep(1)

        except KeyboardInterrupt:
            self.stop_flag = True
            print("\nInterrupt received, stopping...")
        except Exception as e:
            print(f"Monitoring error: {e}")
            self.stop_flag = True

    def wait_for_stop(self):
        input("Press Enter to stop recording and streaming...\n")
        self.stop_flag = True

    def run(self):
        try:
            self.connect()
            self.start_recording_streaming()

            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_status)
            monitor_thread.start()

            # Wait for user input to stop
            self.wait_for_stop()

            # Stop operations
            self.stop_recording_streaming()

            # Wait for final status updates
            monitor_thread.join(timeout=10)

        finally:
            self.ws.disconnect()
            print("Disconnected from OBS WebSocket")


if __name__ == "__main__":
    controller = OBSController()
    controller.run()


    # request for setting rtmp
    rtmp_data = {
        "op": 6,
        "d": {
            "requestType": "SetStreamServiceSettings",
            "requestId": "2",
            "requestData": {
                "streamServiceType": "rtmp_custom",
                "streamServiceSettings": {
                    "server": "rtmp://live.restream.io/live",
                    "key": "re_9442228_eventa8eb3240beee4cdda527ff4731922248"
                }
            }
        }
    }