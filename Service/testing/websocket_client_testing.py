import asyncio
import websockets
import pyaudio
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket 服务器地址
SERVER_URL = "ws://localhost:8001"

# SERVER_URL = "ws://121.41.3.58:8001"

# 音频相关设置
SAMPLE_RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK_MS = 2500 # 每帧音频时长 (ms)
CHUNK_SIZE = int(SAMPLE_RATE * 1 / 1000 * CHUNK_MS)  # 16000Hz采样率下每帧160ms的音频数据量

async def send_audio_data(websocket, stream):
    while True:
        # 从麦克风读取音频数据
        audio_data = stream.read(CHUNK_SIZE)
        logger.debug(f"Sent audio frame of size: {len(audio_data)}")
        
        # 发送音频数据给服务器
        await websocket.send(audio_data)

        # 每隔一定时间发送一个小的间隔，模拟实际音频传输过程
        await asyncio.sleep(CHUNK_MS / 1000.0)

async def receive_server_data(websocket):
    while True:
        try:
            # 等待服务器的响应
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            response = json.loads(response)
            print(f"Received from server: {response}")
        except asyncio.TimeoutError:
            # 超时处理
            logger.warning("No response from server.")

async def send_audio_data_to_server():
    async with websockets.connect(SERVER_URL) as websocket:
        logger.info("Connected to WebSocket server")

        # 初始化 PyAudio
        p = pyaudio.PyAudio()

        # 打开麦克风流
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)

        logger.info("Start sending audio data...")

        # 并发运行发送音频数据和接收服务器数据
        task_send = asyncio.create_task(send_audio_data(websocket, stream))
        task_receive = asyncio.create_task(receive_server_data(websocket))

        # 等待任务完成
        await asyncio.gather(task_send, task_receive)

        # 停止音频流
        stream.stop_stream()
        stream.close()
        p.terminate()

        # 发送结束信号到服务器
        finish_params = {"type": "FINISH"}
        await websocket.send(json.dumps(finish_params))
        logger.info("Sent FINISH frame")

# 运行 WebSocket 客户端
if __name__ == "__main__":
    asyncio.run(send_audio_data_to_server())