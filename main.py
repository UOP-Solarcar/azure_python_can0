import os
import time
import can
from subprocess import run
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = f"HostName=uopsolarcartest001.azure-devices.net;DeviceId=raspberry-pi-solarcar;SharedAccessKey={os.getenv('sharedaccesskey')}"
DEVICE_ID = os.getenv("deviceid")

def run_rust_script():
    try:
        # Run the Rust script command in the ~/rpi_can directory
        rust_script_command = "cd ~/rpi_can/ && cargo run --release -- can0"
        result = run(
            rust_script_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.expanduser("~")
        )

        if result.returncode == 0:
            # Successfully executed the Rust script
            return result.stdout.strip()
        else:
            print(f"Rust script returned an error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running Rust script: {e}")
        return None

def send_sensor_data(data):
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    try:
        client.connect()
        message = Message(data)
        client.send_message(message)
        print(f"Sent: {data}")
    except Exception as e:
        print(f"Error sending data: {e}")
    finally:
        client.disconnect()

def main():
    bus = None  # Initialize bus outside the try block

    try:
        # Create a SocketCAN bus interface
        bus = can.interface.Bus(channel="can0", bustype="socketcan")

        while True:
            # Run the Rust script to get sensor data
            sensor_data = run_rust_script()

            if sensor_data is not None:
                send_sensor_data(sensor_data)
            time.sleep(5)  # Send data every 5 seconds

    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if bus is not None:
            bus.shutdown()  # Properly shut down the CAN bus interface

if __name__ == "__main__":
    main()
