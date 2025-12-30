import threading
import queue
import json
import asyncio
import random
from devices import SmartBulb, SmartThermostat, SmartCamera
import time


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
            f.flush()
        # Mark task as done
        data_queue.task_done()


def analytic_engine(update, device):
    """
    The Analytics Engine: uses the update data to decide if a device method should be called.
    """
    device_type = update.get('type')
    payload = update.get('payload')

    # Thermostat Logic
    if device_type == "THERMOSTAT":
        if payload['current_temp'] > payload['target_temp']:
            # Call your existing method!
            device.execute_command("TRIGGER_COOLING")
        elif payload['current_temp'] < payload['target_temp']:
            device.execute_command("TRIGGER_HEATING")

    # Camera Logic
    if device_type == "CAMERA":
        if payload['motion_detected']:
            print(f"Movement detected by {device.name}!")
            # Call your snapshot method
            device.execute_command("TAKE_SNAPSHOT")

    #Bulb Logic
    if device_type == "BULB":
        if random.random() < 0.05:
            device.execute_command("TOGGLE")

    # Return the potentially updated state for the log
    return device.send_update()

async def device_task(device):
    """
    Simulates a single device on the network.
    """
    device.connect()
    while True:
        await asyncio.sleep(random.uniform(1, 9)) #sleep a few seconds

        if device.device_type == "CAMERA":
            # randomise motion_detected
            if random.random() < 0.2:
                device.detect_motion()
            else:
                device.motion_detected = False

        if device.device_type == "THERMOSTAT":
            #simulate the temp changing naturally
            device.current_temp += random.uniform(-2, 2)

        #analytics and storage
        update = device.send_update()
        processed_update = analytic_engine(update, device)
        data_queue.put(processed_update)


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
    tasks = [asyncio.create_task(device_task(dev)) for dev in devices]
    print("\nConnecting devices\n")

    # Keep the loop running
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    writer_thread = threading.Thread(target=file_writer_worker, daemon=True)
    writer_thread.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # exit
        print("\nSystem shutting down safely\n")
        print("All logs saved to history.log. Goodbye!")
