import queue
import re

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
        
        self.base_time = 0  # The transcripe end time.        
        self.base_audio_data = bytes()

        self.audio_sample_rate = 16000
        
        self.last_text = ""
        self.same_with_last_text_cnt = 0

    def __get_period_count(self, text: str):
        return text.count('。') + text.count('.')


    def __get_valid_text(self, text: str):
        pattern = r'[。.]'
        matches = list(re.finditer(pattern, text))
        if len(matches) < 2:
            return "没有足够的句号"

        second_last_period_index = matches[-2].end()
        return text[:second_last_period_index]


    def __get_text_words(self, text: str):
        return re.findall(r"[a-zA-Z']+|[\u4e00-\u9fa5]", text)
        

    def send_audio(self, audio_sample: bytes):
        """Process the audio sample using the offline model"""
        
        try:
            logger.info(f"Processing audio sample of length: {len(audio_sample)}")
            audio_data = self.base_audio_data + audio_sample
            
            # The audio data can not be too small, otherwise it will generate issue.
            if(len(audio_data) < 1000):
                self.base_audio_data += audio_sample
                return
            
            result = offline_model(audio_data, model)

            if len(result) == 0 or result[0]['text'] == '':
                self.send_heartbeat()
                return
            
            text = result[0]['text']
            timestamp = result[0]['timestamp']

            words = self.__get_text_words(text)
            if (len(words) != len(timestamp)):
                print(f"error, words count not equal timestamp count!, text: {text}, words: {words}, timestamp: {timestamp}")
                raise

            # 如果句号的个数大于或等于2，则提取倒数第二个句号前的内容
            period_count = self.__get_period_count(text)
            if period_count >= 2:
                res_text = self.__get_valid_text(text)
                res_words = self.__get_text_words(res_text)

                res_start_time = self.base_time
                res_end_time = self.base_time + int(len(self.base_audio_data) / self.audio_sample_rate * 1000) + timestamp[len(res_words)-1][1]

                self.base_time = res_end_time
                byte_to_skip = int(timestamp[len(res_words)-1][1] / 1000 * self.audio_sample_rate) // 2 * 2
                self.base_audio_data = audio_sample[byte_to_skip::]
            else:
                res_text = text
                res_start_time = self.base_time
                res_end_time = self.base_time + int((len(self.base_audio_data) + len(audio_sample)) / self.audio_sample_rate * 1000)
                self.base_audio_data += audio_sample


            if res_text != self.last_text: 
                self.message_queue.put({
                    "type": "TRANSCRIPT",  # Tag this message as transcribed text
                    "text": res_text,
                    "start_time": res_start_time,
                    "end_time": res_end_time,
                    "err": "OK"
                })  # Put the transcribed text into the message queue
                logger.info(f"Processed text: {text}")
                print(f"Processed text: {text}")
            else:
                self.same_with_last_text_cnt += 1
                if self.same_with_last_text_cnt >= 5:
                    self.base_time = self.base_time + int(len(self.base_audio_data) / self.audio_sample_rate * 1000)
                    self.same_with_last_text_cnt = 0
                    self.base_audio_data = bytes()

                self.send_heartbeat()

            self.last_text = res_text

        except Exception as e:
            # Update the message queue with the error message if an exception occurs
            error_message = str(e)  # Convert the exception to a string for logging
            self.message_queue.put({
                "type": "ERROR",  # Tag this message as transcribed text
                "text": "",
                "start_time": -1,
                "end_time": -1,
                "err": f"Error: {error_message}"  # Include the error message
            })

            logger.error(f"Error processing audio sample: {e}")
            raise
            
        
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
        heartbeat_message = {
            "type": "HEARTBEAT",  # Tag this message as a heartbeat
            "text": "",
            "start_time": -1,
            "end_time": -1,
            "err": f"OK"  # Include the error message
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