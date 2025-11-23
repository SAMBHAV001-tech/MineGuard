# app/services/sensors_mqtt.py
import asyncio
import random
import threading
from typing import Dict

# Shared in-memory state
_sensor_state: Dict[str, float] = {"vibration": 0.0}


def get_latest_sensor_state() -> Dict[str, float]:
    """Return the latest sensor state."""
    return dict(_sensor_state)


async def simulate_vibration():
    """Continuously generate simulated vibration values every 5 seconds."""
    global _sensor_state
    while True:
        # Simulated vibration between 0.0 - 1.0 (adjust range if needed)
        _sensor_state["vibration"] = round(random.uniform(0.0, 1.0), 2)
        print(f"[SIM] Vibration updated: {_sensor_state['vibration']}")
        await asyncio.sleep(5)


def start_mqtt_client():
    """
    Instead of connecting to a real MQTT broker,
    this starts a background thread running the vibration simulator.
    """
    loop = asyncio.new_event_loop()

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(simulate_vibration())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("✅ Vibration simulation started...")
