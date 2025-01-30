import env
import network

#connects to a network in station mode with the ssid and password provided
def connectToWiFi(ssid, password):
    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)
    print("connecting to ", end=" ")
    print(env.WIFI_SSID, end=" ")
    print(" with password ", end=" ")
    print(env.WIFI_PASSWORD, end=" ")

    

    while station.isconnected() == False:
        print(".", end=" ")
        pass

    print("")
    print("Connected!")
    
#connect to the wifi provided in env before booting any later code
# comment this out if needed for testing
connectToWiFi(env.WIFI_SSID, env.WIFI_PASSWORD)
