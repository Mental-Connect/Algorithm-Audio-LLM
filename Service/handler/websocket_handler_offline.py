import asyncio
import json
import websockets
import io
from Service.services.offline_services import OfflineService
from Service.common.processing import offline_processing
from Service.common.audio_saving import save_audio_to_wav
from Service.logging.logging import get_logger

# Configure logger
logger = get_logger()

# 心跳间隔时间（5秒）
HEARTBEAT_INTERVAL = 5

async def send_heartbeat(websocket):
    while True:
        try:
            # 发送心跳消息
            # 创建心跳消息
            heartbeat_message = {
                "type": "HEARTBEAT",
                "text": "",
                "start_time": -1,
                "end_time": -1,
                "err": "OK"
            }
            message = json.dumps(heartbeat_message)
            await websocket.send(message)

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed.")
            break
        await asyncio.sleep(HEARTBEAT_INTERVAL)

async def handle_websocket_connection(websocket):

    # 启动心跳发送任务
    asyncio.create_task(send_heartbeat(websocket))

    """
    Handles the WebSocket connection from the client and communicates with the offline service.
    
    :param websocket: The WebSocket connection object for the client.
    :param path: The WebSocket request path.
    """
    logger.info(f"New client connected: {websocket.remote_address}")

    # Create an instance of the offlineService class
    service = OfflineService()
    audio_data_buffer = io.BytesIO()
    message_queue = asyncio.Queue()  # Queue to handle messages specific to this WebSocket
    
    # Start heartbeat and message processing tasks for this connection
    asyncio.create_task(send_heartbeat(websocket, message_queue))
    asyncio.create_task(process_and_send_messages(websocket, message_queue)) 
    
    try:
        async for message in websocket:
            logger.info(f"Received audio data from client, length: {len(message)}")

            # Send the audio data received from the client to the offline service
            service.send_audio(message)
            audio_data_buffer.write(message)

            # Retrieve response from the offline service
            response = service.fetch_messages_from_queue()
            if response:
                for res in response:
                    formatted_response = await offline_processing(res)
                    if formatted_response:
                        await message_queue.put(formatted_response)  # Add formatted response to the queue
                        logger.info(f"Formatted response is: {formatted_response}")
                    else:
                        logger.info("No response received from model")

    except websockets.ConnectionClosed:
        logger.info(f"Connection with {websocket.remote_address} closed.")
        service.send_finish()

    finally:
        audio_data_buffer.seek(0)  # Reset the buffer pointer to the beginning
        save_audio_to_wav(audio_data_buffer)

