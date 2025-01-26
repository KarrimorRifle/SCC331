#include <Arduino.h>
#include <PDM.h>
#include <WiFi.h>
#include <Adafruit_GFX.h> 
#include "bme68xLibrary.h"  //environmental
#include "Wire.h"
#include "BH1745NUC.h"      //light level
#include <Adafruit_GFX.h>       //OLED display support library
#include <Adafruit_SSD1306.h>   //OLED display library

//--- defines OLED screen dimensions ---
#define SCREEN_WIDTH 128        // OLED display width, in pixels
#define SCREEN_HEIGHT 64        // OLED display height, in pixels
#define OLED_RESET    -1        // Reset pin # 
#define SCREEN_ADDRESS 0x3C     //OLED I2C address

//creates OLED display object "display"
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define REDButton 12
#define BLACKButton 13

//for future connection stuffs
#define REMOTE_IP       ""
#define REMOTE_PORT      ""

const char* ssid = "";
const char* password = "";

WiFiClient client;

int room = 1;       //expect to be changed when location sorted
#define MAX_ROOM 5

//climate sensor 
Bme68x bme;

//microphone measurement sensor parameters
short sampleBuffer[512];
volatile int samplesRead;

#define BH1745NUC_DEVICE_ADDRESS_38 0x38    //light measurement sensor I2C address
BH1745NUC bh1745nuc = BH1745NUC();


// put function declarations here:
// void redButtonPress();
void blkButtonPress();
void enivronmentalData();
void onPDMdata();
float readSoundSamples();
float calculateDecibels();

void setup() {
  Wire.begin();
  Serial.begin(115200);

  bme.begin(0x76, Wire);

  //error catch the OLED display 
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)){
    display.println(F("SSD1306 allocation failed"));
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); //loops forever
  }


  display.display();   

  // clears the display buffer
  display.clearDisplay();                 //clears OLED screen
  display.setTextSize(1);                 //Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);    //Draw white text
  display.setCursor(0,0);
  delay(6);//added because this is the minimum time I found that gets all serial message to print


  bme.begin(0x76, Wire);

  //error catch the sensor
  if (bme.checkStatus()){
    if (bme.checkStatus() == BME68X_ERROR){
      Serial.println("Sensor error:" + bme.statusString());
      return;
      }
    else if (bme.checkStatus() == BME68X_WARNING){
      Serial.println("Sensor Warning:" + bme.statusString());
    }
  }

  bme.setTPH();

  uint16_t temperatureProfile[10] = {100, 200, 320};
  uint16_t durationProfile[10] = {150, 150, 150};

  //environmental
  bme.setSeqSleep(BME68X_ODR_250_MS);
  bme.setHeaterProf(temperatureProfile, durationProfile, 3);
  bme.setOpMode(BME68X_SEQUENTIAL_MODE);

  //light
  bh1745nuc.begin(BH1745NUC_DEVICE_ADDRESS_38);
  bh1745nuc.startMeasurement();

  //noise
    PDM.onReceive(onPDMdata);
    PDM.setCLK(3);
    PDM.setDIN(2);
    if(!PDM.begin(1, 16000)){
      display.clearDisplay();
      display.setCursor(0,0);
      display.write("Failed to start PDM");
      display.display();
      while(1);
    }


  // pinMode(REDButton, INPUT);
  pinMode(BLACKButton, INPUT);

  // attachInterrupt(REDButton, redButtonPress, FALLING);
  attachInterrupt(BLACKButton, blkButtonPress, FALLING);
}

void loop() {
  // put your main code here, to run repeatedly:
  display.clearDisplay();               
  display.setCursor(0,0);

  enivronmentalData();
}

void enivronmentalData(){
  bme68xData data;
  bme.fetchData();
  while(bme.getData(data));
  bh1745nuc.read();
  float sound = readSoundSamples();

  //csv json file
  String dataLine = "Enivronmental Data:\n\tRoom " + String(room) + ", \n\tlight: " + bh1745nuc.clear + ", \n\tsound: " + sound + ", \n\ttemp: " + String(data.temperature-4.49);     
  
  display.clearDisplay();
  display.setCursor(0,0);
  display.println(dataLine);
  Serial.println(dataLine);
  display.display();
}

float readSoundSamples(){
  if (samplesRead > 0) {
    float decibels = calculateDecibels();
    samplesRead = 0; // Reset the sample count after processing
    return decibels;
  }
  return -1; 
}

float calculateDecibels(){
  float sum = 0;
  for (int i = 0; i < samplesRead; i++) {
    sum += abs(sampleBuffer[i]);
  }
  float average = sum / samplesRead;
  return -20.0f * log10(average / 32767.0f); // Convert average value to decibels
}

void onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);
  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}

// void redButtonPress(){

// }

//use to set which room the sensor is in
  //could be changed to external trigger if desired
void blkButtonPress(){
  room++;
  if(room > MAX_ROOM){
    room = 1;
  }
}
