import asyncio
import websockets
import json
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import ChatRoom
from django.contrib.sessions.backends.db import SessionStore
from asgiref.sync import sync_to_async

User = get_user_model()

async def test_websocket():
    # Connect to WebSocket
    uri = "ws://localhost:8000/ws/chat/test_room/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Send a test message
            message = {
                "type": "chat_message",
                "message": "Hello, this is a test message!",
                "username": "testuser1"
            }
            await websocket.send(json.dumps(message))
            print("Sent message:", message)
            
            # Wait for response
            response = await websocket.recv()
            print("Received response:", response)
            
            # Keep connection open for a few seconds
            await asyncio.sleep(5)
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed unexpectedly: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 