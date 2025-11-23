# Simulated IoT Sensor Publisher for MineGuard AI
# Publishes random displacement/vibration/pore_pressure values to HiveMQ public broker

import time
import random
import json
import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            payload = {
                "displacement": round(random.uniform(0.0, 0.2), 4),   # meters per hour
                "vibration": round(random.uniform(0.0, 3.0), 3),      # m/s²
                "pore_pressure": round(random.uniform(10, 80), 2),    # kPa
                "timestamp": time.time()
            }
            client.publish(MQTT_TOPIC, json.dumps(payload))
            print("Published:", payload)
            time.sleep(5)  # send every 5 seconds
    except KeyboardInterrupt:
        print("Publisher stopped by user.")
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
