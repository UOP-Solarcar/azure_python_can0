import os
import time
from azure.iot.device import IoTHubDeviceClient, Message
import can

CONNECTION_STRING = f"HostName=uopsolarcartest001.azure-devices.net;DeviceId=raspberry-pi-solarcar;SharedAccessKey={os.getenv('sharedaccesskey')}"
DEVICE_ID = os.getenv('deviceid')

def send_sensor_data(data):
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    try:
        client.connect()
        message = Message(data)
        client.send_message(message)
        print(f"Sent: {data}")
    except Exception as e:
        print(f"Error sending data: {str(e)}")
    finally:
        client.disconnect()

def read_data_from_can_bus():
    bus = can.interface.Bus(channel='can0', bustype='socketcan')

    try:
        message = bus.recv(timeout=1)  # Adjust the timeout as needed
        if message is not None:

            sensor_data = message.data  # WIP, will change based on sensor data format
            return sensor_data
    except can.CanError:
        print("Error reading from CAN bus")

    return None

while True:
    # Read data from Arduino over CAN bus
    arduino_data = read_data_from_can_bus()
    if arduino_data is not None:
        send_sensor_data(arduino_data)
    time.sleep(5)  # Send data every 5 seconds
