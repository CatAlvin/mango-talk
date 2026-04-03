import asyncio
import json
import sys
import websockets

if len(sys.argv) != 3:
    print("Usage: python ws_listen.py <room_id> <token>")
    sys.exit(1)

room_id = sys.argv[1]
token = sys.argv[2]

url = f"ws://127.0.0.1:8000/ws/rooms/{room_id}?token={token}"

async def main():
    async with websockets.connect(url) as ws:
        print(f"Connected to {url}")
        while True:
            message = await ws.recv()
            try:
                data = json.loads(message)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception:
                print(message)

asyncio.run(main())
