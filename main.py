import threading
import queue
import json
import asyncio
import random
from devices import SmartBulb, SmartThermostat, SmartCamera


data_queue = queue.Queue()

def file_writer_worker():
    """
    This thread pulls live dictionaries from the queue and serializes them into strings for the log.
    """
    print("Storage Thread Started...")
    while True:
        #Pull the dictionary from the queue
        data = data_queue.get()
        # Convert dict to JSON string
        serialized_data = json.dumps(data)
        # Save to disk
        with open("history.log", "a") as f:
            f.write(serialized_data + "\n")
        # Mark task as done
        data_queue.task_done()



async def device_task(device):
    """
    Simulates a single device on the network.
    """
    device.connect()
    while True:
        await asyncio.sleep(random.uniform(1, 5)) #sleep a few seconds

        update = device.send_update()
        data_queue.put(update)


async def main():
    # Instantiate devices - list of devices to make it easyer to loop through them
    devices = [
        SmartBulb("bulb_01", "Living Room Light", "Living Room", 80),
        SmartThermostat("term_01", "Bedroom Thermostat", "Bedroom", 23, 22, 40.0),
        SmartThermostat("term_02", "Living Room Thermostat", "Living Room", 20, 22, 60.2),
        SmartCamera("camera_01", "Front Gate Camera", "Front Gate", 78,True),
        SmartCamera("camera_02", "Patio Camera", "Patio", 100),
        SmartCamera("camera_03", "Garden Camera", "Back Garden", 99),
        SmartThermostat("term_03","Second Floor Thermostat","Hallway",21,24,35.2),
        SmartBulb("bulb_02","Bedroom 1 Light","Bedroom 1",80),
        SmartBulb("bulb_03", "Bedroom 2 Light", "Bedroom 2", 50),
        SmartBulb("bulb_04", "Bathroom light", "Bathroom", 90),
        SmartBulb("bulb_05", "Patio light", "Patio", 0),
        SmartBulb("bulb_06", "Kitchen light", "Kitchen", 80)
    ]

    # Create tasks
    tasks = [asyncio.create_task(device_task(d)) for d in devices]
    print("Connecting devices...")

    # Keep the loop running
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

    #to do: 1. Check the ascio logic, start phase 2, open main.py and start Phase 2 by setting up the Threaded Storage Worker to handle writing to history.log
    #see device task? do we have to add something more there?