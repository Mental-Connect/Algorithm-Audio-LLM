import logging
import wave
import datetime

logger = logging.getLogger(__name__)

def save_audio_to_wav(audio_data_buffer):
    """
    Saves the audio data stored in the buffer as a .wav file.
    
    :param audio_data_buffer: A buffer containing the audio data.
    :param websocket: The WebSocket connection object.
    """
    try:
        # Generate a timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create the filename using the timestamp
        filename = f"{timestamp}.wav"

        with wave.open(filename, 'wb') as wave_file:
            # Set the audio file parameters
            wave_file.setnchannels(1)  # Mono channel
            wave_file.setsampwidth(2)  # Sample width in bytes (16-bit audio)
            wave_file.setframerate(16000)  # Sample rate (16000 Hz)

            # Write the audio data to the file
            wave_file.writeframes(audio_data_buffer.read())

        logger.info(f"Audio successfully saved to {filename}")

    except Exception as e:
        logger.error(f"Error saving audio to .wav file: {e}")
