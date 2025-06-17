import asyncio
import json
import websockets

async def listen_alerts():
    uri = "ws://localhost:8000/ws/alerts"
    async with websockets.connect(uri) as websocket:
        print("Connected to the alerts WebSocket. Awaiting messages...")
        async for message in websocket:
            data = json.loads(message)
            event = data.get("event")
            ticket_id = data.get("ticket_id")
            remaining = data.get("remaining_percent")
            print(f"[{event}] Ticket {ticket_id} — {remaining:.2f}% remaining")

if __name__ == "__main__":
    try:
        asyncio.run(listen_alerts())
    except KeyboardInterrupt:
        print("\nClosing client WebSocket.")
