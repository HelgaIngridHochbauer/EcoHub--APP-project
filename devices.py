from abc import ABC, abstractmethod
import time
class SmartDevice(ABC):
    """
    Abstract Base Class for all IoT devices in the EcoHub system.
    """

    def __init__(self, device_id, name, location):
        """
        Initialize the core properties of a smart device.

        :param device_id: The unique ID of the device
        :param name: The name of the device used for identification
        :param location: The room or area where the device is installed
        """
        self.device_id = device_id
        self.name = name
        self.location = location
        self.device_type = "GENERIC"
        self.is_connected = False

    def connect(self):
        """
        Connect the device to the EcoHub system.
        """
        self.is_connected = True

    def send_update(self):
        """
        Creates a dictionary representing the current state of the device.

        :return: A dictionary containing device_id, type, timestamp, and payload
        """
        pass

    def disconnect(self):
        """
        Disconnect the device from the EcoHub system.
        :param self:
        :return:
        """
        self.is_connected = False

    @abstractmethod
    def execute_command(self, command):
        pass

class SmartBulb(SmartDevice):
    """
    The core properties of a smart bulb. Based on SmartDevice.

    :param self.brightness: the brightness of the bulb, must be between 0 and 100
    :param self.is_on: is the bulb on or off
    :return:

    """
    def __init__(self, device_id, name, location, brightness):
        print("SmartBulb constructor called\n")
        super().__init__(device_id,name,location)
        self._brightness = brightness
        self.device_type = "BULB"
        self.is_on=False

    @property
    def brightness(self):
        """
        :return: the current brightness value
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        """
        :param value: the new brightness to set
        :return: None
        """
        if 0 <= value <= 100:
            self._brightness = value
        else:
            print("Brightness must be between 0 and 100! \n The value will be transformed accordingly\n")
            if value > 100:
                self._brightness = 100
            else:
                if value < 0:
                    self._brightness = 0


    def send_update(self):
        """ Returns the state in the format required by the log """
        return {
            'device_id': self.device_id,
            'type': self.device_type,
            'timestamp': time.time(),
            'payload': {
                'is_on': self.is_on,
                'brightness': self.brightness
            }
        }


    def execute_command(self, command):
        """ Handles bulb commands like switching on/off  """
        if command == "TOGGLE":
            self.is_on = not self.is_on
            print(f"{self.name} toggled.")

class SmartThermostat(SmartDevice):
    """
    The core properties of a smart thermostat. Based on SmartDevice.

    :param current_temp: current temperature
    :param target_temp: the target temperature must be between 15 and 30 degrees
    :param humidity: the current humidity

    :return:

    """
    def __init__(self, device_id, name, location, current_temp=20.0, target_temp=22.0, humidity=40.0):
        print("SmartThermostat constructor called \n")
        super().__init__(device_id,name,location)
        self.device_type = "THERMOSTAT"
        self.current_temp = current_temp
        self._target_temp = target_temp
        self.humidity = humidity

    @property
    def target_temp(self):
        return self._target_temp

    @target_temp.setter
    def target_temp(self, value):
        # Protecting internal state: keep house between 15 and 30 degrees
        if 15 <= value <= 30:
            self._target_temp = value
        else:
            print(f"Target temperature {value} is out of safe range.\n")

    def send_update(self):
        return {
            'device_id': self.device_id,
            'type': self.device_type,
            'timestamp': time.time(),
            'payload': {
                'current_temp': self.current_temp,
                'target_temp': self.target_temp,
                'humidity': self.humidity
            }
        }


    def execute_command(self, command):
        """ Handles thermostat commands like cooling down/warming up  """
        if command == "TRIGGER_COOLING":
            self.current_temp -= 1.0
            print("Smart Thermostat command executed: Cooling Down (-1) \n")
        elif command == "TRIGGER_HEATING":
            self.current_temp += 1.0
            print("Smart Thermostat command executed: Warming Up! (-1) \n")

class SmartCamera(SmartDevice):
    """
    The core properties of a smart thermostat. Based on SmartDevice.

    :param battery_level: the level of the battery, values in [0,100]
    :param motion_detected


    :return:

    """
    def __init__(self, device_id, name, location, battery_level, motion_detected=False, last_snapshot=None):
        print("SmartCamera constructor called \n")
        super().__init__(device_id,name,location)
        self.device_type = "CAMERA"
        self._battery_level = battery_level
        if last_snapshot is None:
            self.last_snapshot = time.time()
        else: self.last_snapshot=last_snapshot
        self.motion_detected = motion_detected


    @property
    def battery_level(self):
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value):
        # battery can't be >100 or <0
        if 0 <= value <= 100:
            self._battery_level = value
        else:
            print("Battery level must be between 0 and 100! \n The value will be transformed accordingly\n")
            if value > 100:
                self._battery_level = 100
            else:
                if value < 0:
                    self._battery_level = 0

    def send_update(self):
        return {
            'device_id': self.device_id,
            'type': self.device_type,
            'timestamp': time.time(),
            'payload': {
                'battery_level': self.battery_level,
                'motion_detected': self.motion_detected,
                'last_snapshot': self.last_snapshot
            }
        }


    def execute_command(self, command):
        if command == "TAKE_SNAPSHOT":
            self.last_snapshot = time.time()
            print(f"Snapshot taken at {self.last_snapshot}")

    def detect_motion(self):
        self.motion_detected = True