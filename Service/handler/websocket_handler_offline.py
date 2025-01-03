import json
import websockets

import io
from Service.services.offline_services import OfflineService
from Service.common.processing import offline_processing
from Service.common.audio_saving import save_audio_to_wav
from Service.logging.logging import get_logger

# Configure logger
logger = get_logger()

async def handle_websocket_connection(websocket):
    """
    Handles the WebSocket connection from the client and communicates with the offline service.
    
    :param websocket: The WebSocket connection object for the client.
    :param path: The WebSocket request path.
    """
    print(f"New client connected: {websocket.remote_address}")

    # Create an instance of the offlineService class
    service = OfflineService()
    audio_data_buffer = io.BytesIO()


    try:
        async for message in websocket:
            logger.info(f"received audio data from client, length: {len(message)}")

            # Send the audio data received from the client to the offline service
            audio_data_buffer.write(message)
            service.send_audio(message)

            # Retrieve response from the offline service (in this case, from the queue)
            response = service.fetch_messages_from_queue()
            if response:
                for res in response:
                    formatted_response = await offline_processing(res)
                    if formatted_response:
                        await websocket.send(json.dumps(formatted_response))
                        logger.info(f"formatted response is:  {formatted_response}")
                    else:
                        logger.info("No response received from model")

        audio_data_buffer.seek(0)  # Reset the buffer pointer to the beginning
        save_audio_to_wav(audio_data_buffer,websocket)

    except websockets.ConnectionClosed:
        logger.info(f"Connection with {websocket.remote_address} closed.")
        service.send_finish()
        # Log if the WebSocket connection with the client is closed

