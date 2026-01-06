#include <Wire.h>
#include <SPI.h>

/* TODO: double check the pin ordering. */
// #define DATAOUT 12 // 1 // 14 // 11 // MISO
// #define DATAIN  11 // 4 // 16 // 10 // MOSI
// #define SPICLOCK  13 // 3 // 15 // 9 // sck
// #define CHIPSELECT 8 // ss

volatile byte receivedData = 0;

/* SPI interrupt routine */
ISR(SPI_STC_vect) {
  receivedData = SPDR;
  SPDR = 10;
  Serial.println("here");
}

void setupSPI(void) {
  // SPI.begin();
  SPI.beginTransaction(SPISettings(5000, MSBFIRST, SPI_MODE0));

  SPCR |= _BV(SPE); // turn on SPI in slave mode
  pinMode(MISO, OUTPUT);
  pinMode(MOSI, INPUT);
  pinMode(SCK, INPUT);
  SPI.attachInterrupt(); // turn on interrupt

  // pinMode(DATAOUT, OUTPUT);
  // pinMode(DATAIN, INPUT);
  // pinMode(SPICLOCK, OUTPUT);
  pinMode(SS, INPUT);

  // digitalWrite(SS, LOW);  // enable device
}

void setup(void) {
  #ifndef ESP8266
    while (!Serial)
      ; // will pause Zero, Leonardo, etc until serial console opens
  #endif

  Serial.begin(9600);
  
  setupSPI();
}

void loop(void) {
  //Byte Received!
  if (receivedData) {
    Serial.print("Received: ");
    Serial.println(receivedData);
    receivedData = 0;
    // SPDR = 10;
  }
}
