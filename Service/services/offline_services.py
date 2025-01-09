import queue

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
        self.base_audio_cache = bytes()

        self.audio_sample_rate = 16000
        
        self.last_text = ""
        self.same_with_last_text_cnt = 0

    def __is_complete_sentence(self, sentence: str) -> bool:
        sentence = sentence.strip()
        return sentence.endswith(('.', '。', '?', '？'))


    def send_audio(self, audio_new_data: bytes):
        """Process the audio sample using the offline model"""
        
        try:
            logger.info(f"Processing audio sample of length: {len(audio_new_data)}")
            audio_cache = self.base_audio_cache + audio_new_data
            # print("audio_cache length: ", len(audio_cache))
            # The audio data can not be too small, otherwise it will generate issue.
            if(len(audio_cache) < 1000):
                self.base_audio_cache = audio_cache
                return
            
            result = offline_model(audio_cache, model)

            if len(result) == 0 or result[0]['text'] == '':
                return
            
            text = result[0]['text']  
            sentence_info_list = result[0]['sentence_info']

            base_time = self.base_time
            # 如果有多个语句，根据问号以及句号进行拆分
            if len(sentence_info_list) > 1:
                res_text = ''

                exist_complete_sentence = False
                for idx, sentence_info in enumerate(sentence_info_list[0:-1]):   # 或略最后一个text
                    
                    tmp_text = sentence_info['text']                
                    tmp_text_start_time = sentence_info['start']
    
                    res_text += tmp_text
                    if self.__is_complete_sentence(res_text):
                        exist_complete_sentence = True
                        res_start_time = self.base_time
                        res_end_time = base_time + tmp_text_start_time
                        self.__send_message(res_text, res_start_time, res_end_time)

                        res_text = ''
                        next_sentence_start = sentence_info_list[idx+1]['timestamp'][0][0]
                        byte_to_skip = int(next_sentence_start / 1000 * self.audio_sample_rate * 2)   # each value contains 2 bytes, 16 bit.
                        self.base_audio_cache = audio_cache[byte_to_skip::]
                        self.base_time = res_end_time
                
                if not exist_complete_sentence:
                    res_text = text
                    res_start_time = self.base_time
                    res_end_time = self.base_time + int(len(audio_cache) / self.audio_sample_rate * 1000)
                    self.base_audio_cache = audio_cache
                    self.__send_message(res_text, res_start_time, res_end_time)

            else:
                res_text = text
                res_start_time = self.base_time
                res_end_time = self.base_time + int(len(audio_cache) / self.audio_sample_rate * 1000)
                # self.base_time = self.base_time + int(len(self.base_audio_cache) / self.audio_sample_rate * 1000)

                self.base_audio_cache = audio_cache
                self.__send_message(res_text, res_start_time, res_end_time)

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
            print(f"Error processing audio sample: {e}")
            logger.error(f"Error processing audio sample: {e}")
            raise

    # Send message to the queue
    def __send_message(self, text, start_time, end_time):
        if text != self.last_text:
            self.message_queue.put({
                    "type": "TRANSCRIPT",  # Tag this message as transcribed text
                    "text": text,
                    "start_time": start_time,
                    "end_time": end_time,
                    "err": "OK"
                })
            self.last_text = text

            
        
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