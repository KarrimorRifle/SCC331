from umqtt.simple import MQTTClient
from lib.ubeacon.ibeacon import IBeacon
import network
import bluetooth

beacon = IBeacon(uuid="12345678-1234-5678-1234-567812345678", major=1, minor=1)

ble = bluetooth.BLE()
ble.active(True)
ble.gap_advertise(250_000, adv_data=beacon.adv_data, resp_data=beacon.resp_bytes, connectable=False)

ssid = "grp3"
password = "eqdf2376"

mqtt_server = "185.213.2.121"
mqtt_user = "czW0b0Vb6JToFwfMvl2BsAveeJ6Iwx9L0zJxe8AsWQrgsbj8kO5Vsf8Hur9rfyc7"
mqtt_password = ""

client_uid = "1"
topic_to_publish = "feeds/hardware-data/" + client_uid


station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    print("connecting to:")
    print(ssid)
    print(password)
    pass

client = MQTTClient(client_uid, mqtt_server, user = mqtt_user, password = mqtt_password)
client.connect()


while (True):
    client.publish(topic_to_publish, "hello world!")
    print("published")
    print("")
