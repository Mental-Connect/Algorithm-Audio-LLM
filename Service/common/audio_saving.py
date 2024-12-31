import re
import wave
import logging

# Configure logger
logger = logging.getLogger(__name__)

def save_audio_to_wav(audio_data_buffer, websocket):
    """
    Saves the audio data stored in the buffer as a .wav file.
    
    :param audio_data_buffer: A buffer containing the audio data.
    """
    try:
         # Sanitize the WebSocket remote address to create a valid filename
        client_ip = websocket.remote_address[0]
        client_port = websocket.remote_address[1]

        # Sanitize the client_ip to be valid for filenames (e.g., ::1 -> ipv6_localhost)
        sanitized_ip = re.sub(r'[^\w\s-]', '_', client_ip)  # Replace invalid characters with '_'
        client_id = f"{sanitized_ip}_{client_port}"

        filename = f"output_audio_{client_id}.wav"
        with wave.open(filename, 'wb') as wave_file:
            # Set the audio file parameters
            wave_file.setnchannels(1)  # Mono channel
            wave_file.setsampwidth(2)  # Sample width in bytes (16-bit audio)
            wave_file.setframerate(16000)  # Sample rate (16000 Hz)

            # Write the audio data to the file
            wave_file.writeframes(audio_data_buffer.read())

        print("Audio successfully saved to output_audio.wav")

    except Exception as e:
        logger.error(f"Error saving audio to .wav file: {e}")