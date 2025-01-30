import bluetooth
from lib.ubeacon.ibeacon import IBeacon

from backend_connection import BackendConnection

import time

# Bluetooth advertising code, commented out but left here for others to see and work with in future
#beacon = IBeacon(uuid="12345678-1234-5678-1234-567812345678", major=1, minor=1)

#ble = bluetooth.BLE()
#ble.active(True)
#ble.gap_advertise(250_000, adv_data=beacon.adv_data, resp_data=beacon.resp_bytes, connectable=False)

#Create a connection to the backend through MQTT
backendConnection = BackendConnection()

#publish "hello world" every 30 seconds, primarily for testing purposes
while (True):
    backendConnection.publishMessage("hello world!")
    print("published")
    print("")
    time.sleep(30)
