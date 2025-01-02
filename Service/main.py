import os
import sys
import asyncio
import websockets
import uvicorn
from fastapi import FastAPI


# Dynamically add the parent directory of the Service to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# from Service.handler.websocket_handler_baidu import handle_websocket_connection
from Service.logging.logging import get_logger
from Service.handler.websocket_handler_offline import handle_websocket_connection
from fastapi.middleware.cors import CORSMiddleware
from Service.config import *
from Service.routers import chatbot

logger = get_logger()

# Initialize FastAPI app and include router
app = FastAPI()
# Allow connections from any origin (or adjust to allow specific ones)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chatbot.router)

# WebSocket service startup function
async def start_websocket_service():
    """Start the WebSocket service."""
    try:

        server = await websockets.serve(handle_websocket_connection, "0.0.0.0", 8001)
        logger.info("WebSocket Service is running!")
        await server.wait_closed()
    except Exception as e:
        logger.error(f"Error starting WebSocket service: {e}")

# Start the Uvicorn server in an asynchronous task
async def start_fastapi_service():
    """Start the FastAPI server."""
    try:
        config = uvicorn.Config(app, host="0.0.0.0", port=8000)
        server = uvicorn.Server(config)
        logger.info("FastAPI Service is running!")
        await server.serve()
    except Exception as e:
        logger.error(f"Error starting FastAPI service: {e}")

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

