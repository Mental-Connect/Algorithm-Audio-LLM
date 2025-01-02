import logging
import queue
import time

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from Service.logging.logging import get_logger

# Configure logger
logger = get_logger()

model = AutoModel(
            model='paraformer-zh',
            vad_model="fsmn-vad", vad_kwargs={"max_single_segment_time": 30000},
            spk_model="cam++", spk_model_revision="v2.0.2", punc_model="ct-punc"
        )

class OfflineService:
    def __init__(self):
        self.message_queue = queue.Queue()  # Queue to receive and process messages

    def send_audio(self, audio_sample: bytes):
        """Process the audio sample using the offline model"""
        try:
            logger.info(f"Processing audio sample of length: {len(audio_sample)}")
            # Call the offline model to process the audio and get the transcribed text
            text = offline_model(audio_sample, model)  # Call your offline model
            self.message_queue.put({
                "type": "TRANSCRIPT",  # Tag this message as transcribed text
                "data": text,
                "err": "OK"
            })  # Put the transcribed text into the message queue
            logger.info(f"Processed text: {text}")
        except Exception as e:
            # Update the message queue with the error message if an exception occurs
            error_message = str(e)  # Convert the exception to a string for logging
            self.message_queue.put({
                "type": "ERROR",  # Tag this message as transcribed text
                "data": "",
                "err": f"Error: {error_message}"  # Include the error message
            })
            logger.error(f"Error processing audio sample: {e}")
        
    def fetch_messages_from_queue(self):
        """Fetch all available messages from the message queue"""
        items = []
        while True:
            try:
                item = self.message_queue.get_nowait()
                items.append(item)
            except queue.Empty:
                break
        return items

    def send_finish(self):
        """Finish processing and clear any pending tasks"""
        logger.info("Finishing processing and clearing queue.")
        while not self.message_queue.empty():
            self.message_queue.get_nowait()  # Clear the queue if needed

    def send_heartbeat(self):
        """Send a heartbeat message every 1 second"""
        while True:
            time.sleep(1)  # Wait for 1 second
            heartbeat_message = {
                "type": "HEARTBEAT",  # Tag this message as a heartbeat
            }
            logger.info("Sending heartbeat message.")
            # Add heartbeat message to the queue
            self.message_queue.put(heartbeat_message)

# Function to call the offline model
def offline_model(audio_sample, model: AutoModel):
    """
    Process the audio sample with an offline ASR model and return the transcribed text.
    """
    text = model.generate(
        input=audio_sample,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=15
    )
    return text