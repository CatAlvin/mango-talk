import asyncio
import json
import sys
import websockets

if len(sys.argv) < 4:
    print("Usage: python ws_send.py <room_id> <token> <content>")
    sys.exit(1)

room_id = sys.argv[1]
token = sys.argv[2]
content = " ".join(sys.argv[3:])

url = f"ws://127.0.0.1:8000/ws/rooms/{room_id}?token={token}"

async def main():
    async with websockets.connect(url) as ws:
        print(f"Connected to {url}")

        first_msg = await ws.recv()
        print("Server:", first_msg)

        payload = {
            "action": "send_message",
            "data": {
                "content": content,
                "reply_to_message_id": None
            }
        }

        await ws.send(json.dumps(payload, ensure_ascii=False))
        print("Sent:", json.dumps(payload, ensure_ascii=False))

        echo = await ws.recv()
        print("Received:", echo)

asyncio.run(main())
