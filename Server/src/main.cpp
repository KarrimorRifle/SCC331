#include <Arduino.h>
#include <WiFi.h>

const char* ssid = "iPhone (204)"; // CHANGE THIS FOR DIFFERENT NETWORKS (FIND ON ROUTERS) 
const char* password = "dobberz68"; // THIS TOO!

int port = 4242;
WiFiServer server(port);

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.setHostname("PicoW2");

  Serial.printf("Connecting to '%s' with '%s'\n", ssid, password);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting...");
    delay(1000);
  }

  Serial.printf("\nConnected to WiFi\n\nConnect to server at %s:%d\n", WiFi.localIP().toString().c_str(), port);

  server.begin();
}

void loop() {
  delay(1000);
  Serial.printf("."); // Just to show that the server is working
  delay(10);

  // Accept request to join server by a client:
  WiFiClient client = server.accept();
  if (!client) {
    return;
  }

  // Wait to receive the message:
  while (!client.available()) {
    delay(10);
  }
  
  // Read their message: 
  String message = client.readStringUntil('\n');
  Serial.println(message);

  // Get rid of the client to allow a new one to join if needed:
  client.flush();
}