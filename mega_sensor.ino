#include <Wire.h>
#include "MLX90641_API.h"
#include "MLX90641_I2C_Driver.h"

/* 
 * Temperature Sensor Setup 
 */
#define TA_SHIFT 8 //Default shift for MLX90641 in open air, alternative: 8

const byte MLX90641_address = 0x33; //Default 7-bit unshifted address of the MLX90641
static float mlx90641To[192];   // object temp array
paramsMLX90641 mlx90641;
unsigned long myTime;
int minIdx; // no longer in use

void setup() {
  
  Wire.begin();
  Wire.setClock(400000); //Increase I2C clock speed to 400kHz
  Serial.begin(115200); // alternative 9600 baud rate
  while(!Serial.available()){
    Serial.println("MEGA");
    delay(500);
  }
  String cmd = Serial.readString();
  if(cmd != "connected"){
    Serial.print("ERROR00S"); //not connected to RPI 
  }
  /*debug.begin(9600);
  while (!debug); //Wait for user to open terminal
  debug.println("MLX90641 IR Array Example");
  */
  
  if (sensorConnected() == false) {
    //debug.println("MLX90641 not detected at default I2C address. Please check wiring. Freezing.");
    Serial.print("ERROR01S");
    while (1);
  }

  int status;
  uint16_t eeMLX90641[832];
  status = MLX90641_DumpEE(MLX90641_address, eeMLX90641);
  if (status != 0) {
    //debug.println("Failed to load system parameters");
    Serial.println("ERROR02S");
  }
  //debug.println("load parameters success");
  status = MLX90641_ExtractParameters(eeMLX90641, &mlx90641);
  if (status != 0) {
    //debug.println("Parameter extraction failed");
    Serial.println("ERROR03S");
  }
  //debug.println("parameter extraction success");

  /*
   * 0x05-0.5Hz; 0x01-1Hz; 0x02-2Hz; 0x03-4Hz; 0x04-8Hz(DEFAULT); 0x05-16Hz; 0x06-32Hz;0x07-64Hz 
  */
  MLX90641_SetRefreshRate(MLX90641_address, 0x03); // Default: 0x04 | 8Hz
}

void loop() {

  if(Serial.available()){
    String cmd = Serial.readString();
    if(cmd.length()>0){
      switch(cmd.charAt(0)){
        case 'R': // change refresh rate
          updateRefreshRate(cmd.charAt(1));
          break;
        case 'Y':
          break;
        case 'P':
          break;
      }  
    } 
  }
  
  for (byte x = 0 ; x < 2 ; x++) { // both subpages
    uint16_t mlx90641Frame[242]; 
    int status = MLX90641_GetFrameData(MLX90641_address, mlx90641Frame);
    // DEBUG 0/1 SUCCESS debug.println("GetFrameData" + String(status));
    if (status < 0) {
      //Serial.print("GetFrame Error: ");
      //Serial.println(status);
      Serial.println("ERROR04S");
    }

    float vdd = MLX90641_GetVdd(mlx90641Frame, &mlx90641);
    float Ta = MLX90641_GetTa(mlx90641Frame, &mlx90641);
    
    if (x==0){
      /*Serial.print("Time: ");
      myTime = millis();
      Serial.println(myTime);*/
      Serial.print("V");
      Serial.print(vdd);
      Serial.print("T");
      Serial.println(Ta);
    }
    float tr = Ta - TA_SHIFT; //Reflected temperature based on the sensor ambient temperature
    float emissivity = 0.95;  //0.95 skin

    minIdx = MLX90641_CalculateTo(mlx90641Frame, &mlx90641, emissivity, tr, mlx90641To);
  }
 
    for (int x = 0 ; x < 192 ; x++) {
        Serial.print(mlx90641To[x], 2); // Adjust sig figs for temperature
        Serial.print(",");
    }
  
    /*Serial.print("End time: ");
    myTime = millis();
    Serial.println(myTime); */

  // DEBUG
  delay(1500);
}

//Returns true if the MLX90641 is detected on the I2C bus
boolean sensorConnected() {
  Wire.beginTransmission((uint8_t)MLX90641_address);
  if (Wire.endTransmission() != 0) {
    return (false);    //Sensor NACK
  }
  return (true);
}

void updateRefreshRate(char rate){
  uint8_t new_rate;
  switch(rate){
    case '0':
      new_rate = 0x00;  // 0.5 Hz
      break;
    case '1':
      new_rate = 0x01;  // 1Hz
      break;
    case '2':
      new_rate = 0x02;  // 2Hz
      break;
    case '3':
      new_rate = 0x03;  // 4Hz
      break;
    case '4':
      new_rate = 0x04;  // 8Hz default
      break;
    case '5':
      new_rate = 0x05;  // 16Hz
      break;
    case '6':
      new_rate = 0x06;  // 32Hz
      break;
    case '7':
      new_rate = 0x07;  // 64Hz
      break;
    default:
      new_rate = 0x04;  // default
      break;
  }
  MLX90641_SetRefreshRate(MLX90641_address, new_rate); //0x00-0.5Hz; 0x01-1Hz; 0x02-2Hz; 0x03-4Hz; 0x04-8Hz(DEFAULT); 0x05-16Hz; 0x06-32Hz;0x07-64Hz 
}
  
