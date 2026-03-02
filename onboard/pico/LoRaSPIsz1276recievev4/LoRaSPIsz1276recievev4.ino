/*
  LoRa Duplex communication

  Sends a message every half second, and polls continually
  for new incoming messages. Implements a one-byte addressing scheme,
  with 0xFF as the broadcast address.

  Uses readString() from Stream class to read payload. The Stream class'
  timeout may affect other functuons, like the radio's callback. For an

  created 28 April 2017
  by Tom Igoe
*/
#include <Arduino.h>
#include <SPI.h>              // include libraries
#include <LoRa.h>
#include <Wire.h>


// pin definition for the pico tft

const int    LoRa_MISO_Pin  = 16;
const int    LoRa_CS_Pin    = 17;
const int    LoRa_SCK_Pin   = 18;
const int    LoRa_MOSI_Pin  = 19;
const int    LoRa_G0_Pin    = 20; // DIO0_Pin
const int    LoRa_EN_Pin    = 21;
const int    LoRa_RST_Pin   = 21;
const int    SPI_CH         =  0;

String outgoing = "";   // outgoing message
String incomingRec[5] = {"", "", "", "", ""};
byte msgCount = 0;            // count of outgoing messages
byte localAddress = 2;     // address of this device
byte destination = 255;      // destination to send to 255 is all

int recipient = 0;      // recipient address
byte sender = 0;
byte incomingMsgId = 0; // incoming msg ID
byte incomingLength = 0; // incoming msg length
String incoming = "Recieving...";
String incoming2 = "Recieving...";
int SpreadingFactor = 12;

const unsigned long timerDuration = 10000;  //10 sec
unsigned long lasttime;
String isolated_part = "";
int isolated_number = 0;
const int blowerPin = 15;


void setup() {
  pinMode(LoRa_CS_Pin, OUTPUT);  //set pin high so lora is disabled
  pinMode(blowerPin, OUTPUT); // blower realy pin
  digitalWrite(blowerPin, LOW);


  Serial.begin(9600);                   // initialize serial
  //while (!Serial);
  Serial.println("LoRa Duplex");

  LoRa.setPins(LoRa_CS_Pin, LoRa_RST_Pin, LoRa_G0_Pin);// set CS, reset, IRQ pin
  if (!LoRa.begin(915E6)) {             // initialize ratio at 915 MHz
    Serial.println("LoRa init failed. Check your connections.");

    while (true);                       // if failed, do nothing
  }

  // override the default CS, reset, and IRQ pins (optional)


  Serial.println("LoRa init succeeded.");
  LoRa.setSpreadingFactor(12);
  //LoRa.dumpRegisters(Serial);



}

void loop() {

  onReceive(LoRa.parsePacket());



}

void sendMessage(String outgoing) {
  LoRa.beginPacket();                   // start packet
  LoRa.write(destination);              // add destination address
  LoRa.write(localAddress);             // add sender address
  LoRa.write(msgCount);                 // add message ID
  LoRa.write(outgoing.length());        // add payload length
  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();                     // finish packet and send it
  msgCount++;                           // increment message ID


}
void onReceive(int packetSize) {
  if (packetSize == 0) return;          // if there's no packet, return
  // read packet header bytes:
  recipient = LoRa.read();          // recipient address
  sender = LoRa.read();
  incomingMsgId = LoRa.read();     // incoming msg ID
  incomingLength = LoRa.read();    // incoming msg length
  incoming2 = "";
  while (LoRa.available()) {
    incoming2 += (char)LoRa.read();
  }
  Serial.println(recipient);
  Serial.println(sender);
  Serial.println(incomingMsgId);
  Serial.println(incomingLength);

  Serial.println(incoming2);

  if (recipient == localAddress || recipient == 255) {
    // incoming = incoming2;
    Serial.println(incoming2);
    
    if (incoming.indexOf("!!!!stop") != -1) {
      // The string contains "!!!!stop"
      // Add your code here to handle the case where the condition is true
      Serial.println("Command to STOP received!");
                digitalWrite(blowerPin, LOW);

    }

      int startIndex = incoming2.indexOf("!!!!zy");
      isolated_part = "";
      // If the substring is found, extract the following digits
      if (startIndex != -1) {
        startIndex += 6; // Move to the position after "!!!!zy"
        while (startIndex < incoming2.length() && isDigit(incoming2[startIndex])) {
          isolated_part += incoming2[startIndex];
          startIndex++;

        }
          Serial.print("Isolated part: ");
          Serial.println(isolated_part);
      }

      // Print the isolated number
      if (isolated_part.length() > 0) {
        Serial.print("Isolated part: ");
        Serial.println(isolated_part);
        isolated_number = isolated_part.toInt();

        if (isolated_number < 140) {

          digitalWrite(blowerPin, HIGH);
          Serial.println("15 on at ");
          lasttime = millis();
          while (millis() - lasttime < timerDuration)
          {
            //wait 1 duration
          }
          digitalWrite(blowerPin, LOW);
          Serial.println("15 off at ");

        } else {
          Serial.println("No match found.");
        }
      }


    }


  }
