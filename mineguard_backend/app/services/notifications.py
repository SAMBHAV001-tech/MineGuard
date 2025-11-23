import time
import queue
from typing import Generator

# simple in-memory queue for SSE messages
SSE_QUEUE = queue.Queue()


def push_event(event: str, data: str):
    # payload must be indented inside function
    payload = {
        "time": time.time(),
        "event": event,
        "data": data
    }
    SSE_QUEUE.put(payload)


def event_generator() -> Generator[str, None, None]:
    # yields Server-Sent Events (text/event-stream) strings
    while True:
        payload = SSE_QUEUE.get()
        # event name and data
        # SSE format: event: <name>\ndata: <json>\n\n
        yield f"event: {payload['event']}\n"
        # guarantee data is single-line or replace newlines
        data_line = payload['data'].replace('\n', ' ')
        yield f"data: {data_line}\n\n"
