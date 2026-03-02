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
#include <SPI.h>              // include libraries
#include <LoRa.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define BUTTON_A  9
  #define BUTTON_B  6
  #define BUTTON_C  5
  #define WIRE Wire
  
   // Data wire is connected to pin 2 on the Arduino
#define ONE_WIRE_BUS 17  //pin A3

const int csPin = 8;          // LoRa radio chip select
const int resetPin = 4;       // LoRa radio reset
const int irqPin = 3;         // change for your board; must be a hardware interrupt pin
const int powerPin = 13;

String outgoing;              // outgoing message

byte msgCount = 0;            // count of outgoing messages
byte localAddress = 8;     // address of this device
byte destination = 0x02;      // destination to send to
long lastSendTime = 0;        // last send time
const unsigned long interval = 3600000;          // interval 1hours


// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor
DallasTemperature sensors(&oneWire);

void setup() {

  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  pinMode(BUTTON_C, INPUT_PULLUP);
  pinMode(powerPin, OUTPUT); 

  Serial.begin(9600);                   // initialize serial
  //while (!Serial);
sensors.begin();
  Serial.println("LoRa Duplex");

  // override the default CS, reset, and IRQ pins (optional)
  LoRa.setPins(csPin, resetPin, irqPin);// set CS, reset, IRQ pin

  if (!LoRa.begin(915E6)) {             // initialize ratio at 915 MHz
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }

  Serial.println("LoRa init succeeded.");
  LoRa.setSpreadingFactor(12);
  //LoRa.dumpRegisters(Serial);

}

void loop() {
	int n=0;  //number of timez to run 1hours
  while (n<4 ) 
  {
	 sendTemp();
	  int m=1;
	  long lastSendTime2 = millis();
  	while(m==1)
	  { 
		 onReceive(LoRa.parsePacket());
		   
	  	if(millis() - lastSendTime2 > interval) //wait 1 hours
	  	{
	  		sendTemp();
	  		lastSendTime2 = millis();
	  		m=0;
	  	}
	  }
   n++;
  } 

  lastSendTime2 = millis();
  int k=1;
  while(k==1)
{ 
	onReceive(LoRa.parsePacket());
	   
  	if(millis() - lastSendTime2 > interval*12) //wait 12 hours
  	{
  		lastSendTime2 = millis();
  		k=0;
  	}
}
  
  
/*
  if (!digitalRead(BUTTON_A) || !digitalRead(BUTTON_B) || !digitalRead(BUTTON_C)) {
    Serial.println("Button pressed!");
    char radiopacket[20] = "Button #";
    char radiopackett[20] = "";
    if (!digitalRead(BUTTON_A)) radiopacket[8] = 'A';
    if (!digitalRead(BUTTON_B)) strcpy(radiopacket + 0, "Hey Captain!");;
    if (!digitalRead(BUTTON_C)) {}
     
      
  }
  */
  
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


void sendTemp()
{
	sensors.requestTemperatures();
  // Fetch the temperature in Celsius
  float temperatureC = sensors.getTempCByIndex(0);
  float temperatureF = (temperatureC * 9.0 / 5.0) + 32.0;
  // Print the temperature to the serial monitor
 
  int temperatureFInt = int(temperatureF);
  String message = String(temperatureFInt);
  Serial.print("Temperature: ");
  Serial.print(temperatureFInt);
  Serial.println(" °F");
  String preamble = "!!!!zy";
  message = preamble + message;
  sendMessage(message);
    Serial.println(" sent");

}


void onReceive(int packetSize) {
  if (packetSize == 0) return;          // if there's no packet, return

  //read packet header bytes:
  int recipient = LoRa.read();          // recipient address
  byte sender = LoRa.read();            // sender address
  byte incomingMsgId = LoRa.read();     // incoming msg ID
  byte incomingLength = LoRa.read();    // incoming msg length

  String incoming = "";

  while (LoRa.available()) {
    incoming += (char)LoRa.read();
  }

  //if (incomingLength != incoming.length()) {   // check length for error
  //  Serial.println("error: message length does not match length");
  //  return;                             // skip rest of function
  //}

  // if the recipient isn't this device or broadcast,
  //if (recipient != localAddress && recipient != 0xFF) {
  //  Serial.println("This message is not for me.");
  //  return;                             // skip rest of function
  //}

  // if message is for this device, or broadcast, print details:
  //Serial.println("Received from: 0x" + String(sender, HEX));
  //Serial.println("Sent to: 0x" + String(recipient, HEX));
  //Serial.println("Message ID: " + String(incomingMsgId));
  //Serial.println("Message length: " + String(incomingLength));
  Serial.println("Message: " + incoming);
  
  if (incoming.indexOf("!!!!sendtemp") != -1) {
  // The string contains "!!!!sendtemp"
  // Add your code here to handle the case where the condition is true
  Serial.println("Command to send temperature received!");
  
 	 sendTemp();

	}


  
  //Serial.println("RSSI: " + String(LoRa.packetRssi()));
  //Serial.println("Snr: " + String(LoRa.packetSnr()));
  //Serial.println();
}

  /*
  if (millis() - lastSendTime > interval) {
  String message = "  Hello LoRa World1";   // send a message
    sendMessage(message);
    //Serial.println("Sending " + message);
    lastSendTime = millis();            // timestamp the message
    interval = random(5000) + 1000;    // 2-3 seconds
    //LoRa.dumpRegisters(Serial);
  }
    */ 
