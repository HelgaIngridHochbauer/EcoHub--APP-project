from abc import ABC, abstractmethod
import time

from typing import Dict, Any, Optional, Union



class SmartDevice(ABC):
    """
    Abstract Base Class for all IoT devices in the EcoHub system.
    """

    def __init__(self, device_id: str, name: str, location: str)->None:
        """
        Initialize the core properties of a smart device.

        :param device_id: The unique ID of the device
        :param name: The name of the device used for identification
        :param location: The room/area where the device is installed
        """
        self.device_id = device_id
        self.name = name
        self.location = location
        self.device_type = "GENERIC"
        self.is_connected = False


    def __str__(self) -> str:
        return f"{self.device_type}: {self.name} ({self.location})"

    def __repr__(self) -> str:
        return f"Device(id={self.device_id}, type={self.device_type})"

    def connect(self)->None:
        """
        Connect the device to the EcoHub system.
        """
        self.is_connected = True

    def disconnect(self)->None:
        """
        Disconnect the device from the EcoHub system.
        :param self:
        :return:
        """
        self.is_connected = False

    def send_update(self) -> dict:
        """
        Creates the dictionary for the log using the __dict__ attribute.
        We strip the leading underscores so '_target_temp' becomes 'target_temp'.
        """
        clean_payload = {
            k.lstrip('_'): v for k, v in self.__dict__.items()
            if k not in ['device_id', 'device_type', 'is_connected', 'name', 'location']
        }
        log_entry = {
            'device_id': self.device_id,
            'type': self.device_type,
            'timestamp': time.time(),
            'payload': clean_payload
        }
        return log_entry

    @abstractmethod
    def execute_command(self, command: str) -> None:
        """
        Abstract method to handle device-specific commands.
        :param command: The string command to execute.
        """
        pass



class SmartBulb(SmartDevice):
    """
    The core properties of a smart bulb.
    """
    def __init__(self, device_id, name, location, brightness)->None:
        """
        :param brightness: The brightness of the bulb
        """
        print("SmartBulb constructor called\n")
        super().__init__(device_id,name,location)
        self._brightness = brightness
        self.device_type = "BULB"
        self.is_on=False

    @property
    def brightness(self)->int:
        """
        :return: the current brightness value
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value: int)->None:
        """
        validation logic for brightness
        :param value: the new brightness to set, value between 0 and 100
        :return: None
        """
        if not isinstance(value, int):
            print("brightness value must be an integer \n")
            self._brightness = int(value)

        if 0 <= value <= 100:
            self._brightness = value
        else:
            print("Brightness must be between 0 and 100! \n The value will be transformed accordingly\n")
            if value > 100:
                self._brightness = 100
            else:
                if value < 0:
                    self._brightness = 0

    def execute_command(self, command: str)->None:
        """ Handles bulb commands like switching on/off  """
        if command == "TOGGLE":
            self.is_on = not self.is_on
            print(f"{self.name} toggled.")

class SmartThermostat(SmartDevice):
    """
    The core properties of a smart thermostat for climate control.

    """
    def __init__(self, device_id: str, name: str, location: str, current_temp:float =20.0, target_temp: float =22.0, humidity:float =40.0)->None:
        """
        :param current_temp: current temperature
        :param target_temp: the target temperature must be between 15 and 30 degrees
        :param humidity: the current humidity
        """
        print("SmartThermostat constructor called \n")
        super().__init__(device_id,name,location)
        self.device_type = "THERMOSTAT"
        self.current_temp = current_temp
        self._target_temp = target_temp
        self.humidity = humidity

    @property
    def target_temp(self)->float:
        """getter for the target temperature"""
        return self._target_temp

    @target_temp.setter
    def target_temp(self, value)->None:
        """Protecting internal state: keep house between 15 and 30 degrees
        :param value: Float temperature value.
        """
        if 15 <= value <= 30:
            self._target_temp = value
        else:
            print(f"{self.name}: Target temperature {value} is out of safe range.\n")


    def execute_command(self, command:str)->None:
        """ Handles thermostat commands like cooling down/warming up  """
        if command == "TRIGGER_COOLING":
            self.current_temp -= 1.0
            print(f"{self.name}: command executed: Cooling Down (-1) \n")
        elif command == "TRIGGER_HEATING":
            self.current_temp += 1.0
            print(f"{self.name}: command executed: Warming Up! (-1) \n")

class SmartCamera(SmartDevice):
    """
    The core properties of a smart security camera.
    """
    def __init__(self, device_id:str, name:str, location:str, battery_level:int, motion_detected:bool=False, last_snapshot:Optional[float]=None)->None:
        """
        :param battery_level: the battery level
        :param motion_detected: if the camera is motion detected
        """
        print("SmartCamera constructor called \n")
        super().__init__(device_id,name,location)
        self.device_type = "CAMERA"
        self._battery_level = battery_level
        if last_snapshot is None:
            self.last_snapshot = time.time()
        else: self.last_snapshot=last_snapshot
        self.motion_detected = motion_detected


    @property
    def battery_level(self)->int:
        """return battery precentage"""
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value:int)->None:
        """battery can't be >100 or <0"""
        if 0 <= value <= 100:
            self._battery_level = value
        else:
            print("Battery level must be between 0 and 100! \n The value will be transformed accordingly\n")
            if value > 100:
                self._battery_level = 100
            else:
                if value < 0:
                    self._battery_level = 0


    def execute_command(self, command:str)->None:
        """triggers camera actions"""
        if command == "TAKE_SNAPSHOT":
            self.last_snapshot = time.time()
            print(f"Snapshot taken at {self.last_snapshot} \n")
        elif command == "LOW_BATTERY_WARNING":
            print(f"Charging {self.name} \n")
            self.battery_level = 100

    def detect_motion(self)->None:
        self.motion_detected = True