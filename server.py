import asyncio
import websockets
import json
import cv2
from datetime import datetime
from VehicleDetectionTracker.VehicleDetectionTracker import VehicleDetectionTracker

# Create a global dictionary to keep track of active tasks for each connection
active_streams = {}

async def stream_video(websocket, video_url):
    vehicle_detection = VehicleDetectionTracker()
    cap = cv2.VideoCapture(video_url)
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                timestamp = datetime.now()
                response = vehicle_detection.process_frame(frame, timestamp)
                
                # Send detection results
                await websocket.send(json.dumps(response))
                total = len(response["detected_vehicles"])
                # Send annotated frame in base64 format
                if 'annotated_frame_base64' in response:
                    await websocket.send(json.dumps({"annotated_frame_base64": response['annotated_frame_base64'], "data" :{"timestamp": str(timestamp), "total":  response["detected_vehicles"][total-1]["vehicle_id"]}}))
            else:
                break
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    finally:
        cap.release()

async def handle_connection(websocket, path):
    global active_streams

    try:
        async for message in websocket:
            video_url = message.strip()
            print(f"Received video URL: {video_url}")

            if websocket in active_streams:
                active_streams[websocket].cancel()
                try:
                    await active_streams[websocket]
                except asyncio.CancelledError:
                    pass

            if video_url:
                stream_task = asyncio.create_task(stream_video(websocket, video_url))
                active_streams[websocket] = stream_task
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    finally:
        if websocket in active_streams:
            active_streams[websocket].cancel()
            try:
                await active_streams[websocket]
            except asyncio.CancelledError:
                pass
            del active_streams[websocket]

async def main():
    ws_host = 'localhost'
    ws_port = 8000

    async with websockets.serve(handle_connection, ws_host, ws_port):
        print(f"WebSocket server running at ws://{ws_host}:{ws_port}")
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
