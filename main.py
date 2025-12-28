import threading
import queue
import json
import asyncio
import random
from devices import SmartBulb, SmartThermostat, SmartCamera


data_queue = queue.Queue()

def file_writer_worker():
    """
    This thread pulls live dictionaries from the queue  and serializes them into strings for the log.
    """
    print("Storage Thread Started...")
    while True:
        # 1. Pull the dictionary from the queue
        data = data_queue.get()

        # 2. Serialize: Convert dict to JSON string
        serialized_data = json.dumps(data)

        # 3. Save to disk [cite: 103, 115]
        with open("history.log", "a") as f:
            f.write(serialized_data + "\n")  # New line for each update

        # 4. Mark task as done (optional but good practice)
        data_queue.task_done()



async def device_task(device):
    """
    Simulates a single device on the network.
    """
    device.connect()  # requirement: is_connected becomes True [cite: 98]
    while True:
        # sleep for a few seconds
        await asyncio.sleep(random.uniform(1, 5))

        # get the state as a dictionary [cite: 100]
        update = device.send_update()

        # pipe it to the storage queue
        data_queue.put(update)


async def main():
    # 1. Instantiate devices
    bulb = SmartBulb("bulb_01", "Living Room Light", "Living Room", 80)
    thermostat=SmartThermostat("term_01", "Thermostat", "Bedroom",23,22,40.0)

    # ... create others ...

    # 2. Create tasks
    tasks = [
        asyncio.create_task(device_task(bulb)),
        # ... add others ...
    ]

    # 3. Keep the loop running
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Start the storage thread [cite: 105]
    # Then run the async main
    asyncio.run(main())