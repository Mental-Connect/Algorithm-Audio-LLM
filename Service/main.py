import os
import sys
import asyncio
import websockets
import uvicorn
from fastapi import FastAPI

# Dynamically add the parent directory of the Service to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from Service.handler.websocket_handler_baidu import handle_websocket_connection
# from Service.handler.websocket_handler_offline import handle_websocket_connection
from Service.config import *
from Service.routers import chatbot

# Initialize FastAPI app and include router
app = FastAPI()
app.include_router(chatbot.router)

# WebSocket service startup function
async def start_websocket_service():
    """Start the WebSocket service."""
    server = await websockets.serve(handle_websocket_connection, "localhost", 8001)
    print("WebSocket Service is running!")
    await server.wait_closed()

# Start the Uvicorn server in an asynchronous task
async def start_fastapi_service():
    """Start the FastAPI server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    print("FastAPI Service is running!")
    await server.serve()

# Main function to start both FastAPI and WebSocket services
async def main():
    fastapi_task = asyncio.create_task(start_fastapi_service())
    # await fastapi_task
    websocket_task = asyncio.create_task(start_websocket_service())
    await asyncio.gather(fastapi_task, websocket_task)


# Program entry point
if __name__ == "__main__":
    # Run the event loop for the main function
    asyncio.run(main())

