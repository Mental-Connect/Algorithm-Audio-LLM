import json
import logging
import queue
import threading
import uuid

import websocket

logger = logging.getLogger(__name__)

# WebSocket URI for Baidu Real-Time ASR Service
uri = "ws://vop.baidu.com/realtime_asr" + "?sn=" + str(uuid.uuid1())

# Baidu WebSocket connection management class
class BaiduService:
    def __init__(self):
        """Initialize the BaiduService with WebSocket and message queue"""
        self.ws = None
        self.message_queue = queue.Queue()  # Queue to receive and pass messages from Baidu

    def connect(self):
        """Establish a WebSocket connection to the Baidu service"""
        # Initialize a WebSocketApp with provided URI and event handlers
        self.ws = websocket.WebSocketApp(
            uri,
            on_open = self.on_open,
            on_message=self.on_message,  # Handle incoming messages
            on_error=self.on_error,      # Handle any errors
            on_close=self.on_close       # Handle WebSocket closure
        )
        threading.Thread(target=self.ws.run_forever).start()  # Run WebSocket in a separate thread


    def send_audio(self, audio_data):
        """Send audio data frames to Baidu service via WebSocket"""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            # If WebSocket connection is established, send audio data
            print("Send data to Baidu service. Data length: ", len(audio_data))
            self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)  # Send audio data in binary format
            logger.debug(f"Sent audio data, length: {len(audio_data)}")
        else:
            logger.error("Baidu WebSocket connection not established.")  # If no WebSocket connection, log error


    def send_finish(self):
        """Send a finish frame to Baidu service indicating the end of the audio stream"""
        req = {"type": "FINISH"}  # Prepare finish request payload
        body = json.dumps(req)  # Convert request to JSON format
        self.ws.send(body, websocket.ABNF.OPCODE_TEXT)  # Send the finish request as a text frame


    def send_start_params(self):
        """Send start parameters to Baidu service to begin processing"""
        req = {
            "type": "START",  # Frame type is START
            "data": {
                "appid": 116386783,  # Application ID for authentication
                "appkey": "u2vZBUqEDbl8u22HxWLZAksQ",  # API key for authentication
                "dev_pid": 15372,  # Device language model ID
                "cuid": "yourself_defined_user_id",  # Custom user ID
                "sample": 16000,  # Sample rate (16kHz for speech recognition)
                "format": "pcm"  # Audio format (pcm)
            }
        }
        body = json.dumps(req)  # Convert parameters to JSON format
        self.ws.send(body, websocket.ABNF.OPCODE_TEXT)  # Send start parameters as a text frame


    def fetch_messages_from_queue(self):
        """Fetch all available messages from the message queue"""
        items = []
        while True:
            try:
                # Attempt to get items from the queue without blocking
                item = self.message_queue.get_nowait()
                items.append(item)  # Add item to list if available
            except queue.Empty:
                break  # Break if the queue is empty
        return items  # Return all items received from the queue

    def on_message(self, ws, message):
        """Handle incoming messages from Baidu WebSocket"""
        self.message_queue.put(message)  # Put the received message into the queue for processing

    def on_error(self, ws, error):
        """Handle errors that occur during WebSocket communication"""
        logger.error(f"Error from Baidu WebSocket: {error}")  # Log any errors encountered

    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure event"""
        logger.info(f"Baidu WebSocket closed with status {close_status_code}")  # Log WebSocket closure

    def on_open(self, ws):
        """Handle WebSocket connection establishment"""
        self.send_start_params()  # Send the start parameters when the connection is open
        logger.info("Baidu WebSocket connected.")  # Log successful connection
