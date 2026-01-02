import threading
import queue
import json
import asyncio
import random
from devices import SmartBulb, SmartThermostat, SmartCamera, SmartDevice
import time
from typing import Dict, Any, List, Optional

from dataclasses import dataclass
from functools import reduce

@dataclass(frozen=True)
class DeviceStatus:
    """Immutable Dataclass to represent a snapshot of device state."""
    device_id: str
    type: str
    timestamp: float
    payload: dict

data_queue = queue.Queue()

def file_writer_worker()->None:
    """
    Daemon thread for non-blocking I/O.
    Serializes data from the queue to history.log using a context manager.
    """
    print("Storage Thread Started...")
    while True:
        #Pull the dictionary from the queue
        data: Dict[str,Any] = data_queue.get()

        try:
            with open("history.log", "a") as f:
                f.write(json.dumps(data) + "\n")
        except IOError as e:
            print(f"File Error: {e}")
        finally:
            data_queue.task_done() # Mark task as done


def analytic_engine(status: DeviceStatus) -> Optional[str]:
    """
    Returns a command string based on the status, with no side effects.
    """
    p = status.payload

    if status.type == "THERMOSTAT":
        if p.get('current_temp', 0) > p.get('target_temp', 0):
            return "TRIGGER_COOLING"
        if p.get('current_temp', 0) < p.get('target_temp', 0):
            return "TRIGGER_HEATING"

    elif status.type == "CAMERA":
        if p.get('battery_level', 100) < 10:
            return "LOW_BATTERY_WARNING"
        if p.get('motion_detected'):
            return "TAKE_SNAPSHOT"

    elif status.type == "BULB" and random.random() < 0.05:
        return "TOGGLE"

    return None

def run_analytics_pipeline(devices: List[SmartDevice]):
    """Functional Processing Pipeline.
    Uses Map, Filter, and Reduce to process data and trigger actions."""

    statuses = list(map(lambda d: DeviceStatus(**d.send_update()), devices))

    def get_decision(status):
        # find the object that matches the ID
        target_device = next(d for d in devices if d.device_id == status.device_id)
        return (target_device, analytic_engine(status))

    decisions = list(map(get_decision, statuses))

    actions = list(filter(lambda item: item[1] is not None, decisions))

    for device, command in actions:
        if "COOLING" in command or "HEATING" in command:
            print(f"ALERT: Temperature threshold hit for {device.name}!")
        elif command == "LOW_BATTERY_WARNING":
            print(f"ALERT: {device.name} battery is below 10%!")

        device.execute_command(command)

    # Metrics calculation
    thermos = list(filter(lambda s: s.type == "THERMOSTAT", statuses))
    if thermos:
        avg = reduce(lambda acc, s: acc + s.payload['current_temp'], thermos, 0) / len(thermos)
        print(f"Average Temp: {avg:.2f} \n")




async def device_task(device: SmartDevice)->None:
    """
    Asynchronous task simulating a single IoT device on the network.

    :param device: The device instance to simulate.

    """
    # Simulate connection time as seen in requirements
    connection_time = random.uniform(0.5, 1.5)
    await asyncio.sleep(connection_time)

    print(f"{device.name} connected successfully in {connection_time:.2f}s.")

    device.connect()
    while True:
        await asyncio.sleep(random.uniform(1, 9)) #sleep a few seconds

        if device.device_type == "CAMERA":
            # randomise motion_detected
            if random.random() < 0.2:
                device.detect_motion()
                device.battery_level -= random.randint(1, 3) #detecting motion decreases battery faster
            else:
                device.motion_detected = False

            device.battery_level -= random.randint(0, 5) #decreasing the battery normaly

            if device.battery_level < 10:
                await asyncio.sleep(4)

        if device.device_type == "THERMOSTAT":
            #simulate the temp changing naturally
            device.current_temp += random.uniform(-2, 2)

        data_queue.put(device.send_update())




async def main()->None:
    """
       Instantiate devices - list of devices to make it easyer to loop through them
       Manages the async event loop
       """
    devices = [
        SmartBulb("bulb_01", "Living Room Light", "Living Room", 80),
        SmartThermostat("term_01", "Bedroom Thermostat", "Bedroom", 23, 22, 40.0),
        SmartThermostat("term_02", "Living Room Thermostat", "Living Room", 20, 22, 60.2),
        SmartCamera("camera_01", "Front Gate Camera", "Front Gate", 78,True),
        SmartCamera("camera_02", "Patio Camera", "Patio", 100),
        SmartCamera("camera_03", "Garden Camera", "Back Garden", 99),
        SmartCamera("camera_04", "Second Garden Camera", "Back Garden", 9),
        SmartThermostat("term_03","Second Floor Thermostat","Hallway",21,24,35.2),
        SmartBulb("bulb_02","Bedroom 1 Light","Bedroom 1",80),
        SmartBulb("bulb_03", "Bedroom 2 Light", "Bedroom 2", 50),
        SmartBulb("bulb_04", "Bathroom light", "Bathroom", 90),
        SmartBulb("bulb_05", "Patio light", "Patio", 0),
        SmartBulb("bulb_06", "Kitchen light", "Kitchen", 80)
    ]

    # Create asynchronous tasks
    tasks = [asyncio.create_task(device_task(dev)) for dev in devices]
    print("\nConnecting devices\n")

    for dev in devices:
        print(f"{dev} is connecting...\n")

    async def analytics_loop():
        while True:
            await asyncio.sleep(12)
            print("\nRunning Functional Analytics Pipeline")
            run_analytics_pipeline(devices)

    # Run tasks concurrently
    await asyncio.gather(*tasks, analytics_loop())


if __name__ == "__main__":
    # Start the background storage thread
    writer_thread = threading.Thread(target=file_writer_worker, daemon=True)
    writer_thread.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # exit
        print("\nSystem shutting down safely\n")
        print("All logs saved to history.log. Goodbye!")
