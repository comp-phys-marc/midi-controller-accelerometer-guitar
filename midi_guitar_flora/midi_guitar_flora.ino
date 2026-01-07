#include <Adafruit_LSM303_Accel.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(54321);

/* Z should correspond to walking back and forth. X for bends and Y for changing fret positions. */

int NEGATIVE_Y_SENSITIVITY = 0;
int POSITIVE_Y_SENSITIVITY = 10;
int X_SENSITIVITY = 5;

int MULTIPLIER = 5;

int position = 0;
bool pos = true;
bool process = false;

void displaySensorDetails(void) {
  sensor_t sensor;
  accel.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print("Sensor:       ");
  Serial.println(sensor.name);
  Serial.print("Driver Ver:   ");
  Serial.println(sensor.version);
  Serial.print("Unique ID:    ");
  Serial.println(sensor.sensor_id);
  Serial.print("Max Value:    ");
  Serial.print(sensor.max_value);
  Serial.println(" m/s^2");
  Serial.print("Min Value:    ");
  Serial.print(sensor.min_value);
  Serial.println(" m/s^2");
  Serial.print("Resolution:   ");
  Serial.print(sensor.resolution);
  Serial.println(" m/s^2");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

void sensorTest(void) {
  Serial.println("Accelerometer Test");
  Serial.println("");

  /* Initialise the sensor */
  if (!accel.begin()) {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
    while (1)
      ;
  }

  /* Display some basic information on this sensor */
  displaySensorDetails();
}

void setupSensor(void) {
  sensorTest();

  accel.setRange(LSM303_RANGE_4G);
  Serial.print("Range set to: ");
  lsm303_accel_range_t new_range = accel.getRange();
  switch (new_range) {
  case LSM303_RANGE_2G:
    Serial.println("+- 2G");
    break;
  case LSM303_RANGE_4G:
    Serial.println("+- 4G");
    break;
  case LSM303_RANGE_8G:
    Serial.println("+- 8G");
    break;
  case LSM303_RANGE_16G:
    Serial.println("+- 16G");
    break;
  }

  accel.setMode(LSM303_MODE_NORMAL);
  Serial.print("Mode set to: ");
  lsm303_accel_mode_t new_mode = accel.getMode();
  switch (new_mode) {
    case LSM303_MODE_NORMAL:
      Serial.println("Normal");
      break;
    case LSM303_MODE_LOW_POWER:
      Serial.println("Low Power");
      break;
    case LSM303_MODE_HIGH_RESOLUTION:
      Serial.println("High Resolution");
      break;
  }
}

/* SPI interrupt routine */
ISR(SPI_STC_vect) { 
  pos = !pos;
  byte c = SPDR; // read byte from SPI Data Register
  process = true;
}

void setupSPI(void) {
  SPI.begin();
  // SPI.beginTransaction(SPISettings(5000, MSBFIRST, SPI_MODE0));

  SPCR |= _BV(SPE); // turn on SPI in slave mode
  pinMode(MISO, OUTPUT);
  pinMode(MOSI, INPUT);
  pinMode(SCK, INPUT);
  SPI.attachInterrupt(); // turn on interrupt

  pinMode(SS, INPUT);
}

void positionAndBend(float x, float y) {
  if (pos) {
    /* Negative y dimension increases fret position. */
    if (y > POSITIVE_Y_SENSITIVITY) {
      position = position - 1;
    } else if (y < - NEGATIVE_Y_SENSITIVITY) {
      position = position + 1;
    }

    /* Roughly five 4-fret positions on a guitar neck. */
    if (position > 5) {
      position = 5;
    } else if (position < 0) {
      position = 0;
    }
    SPDR = int(position);

  } else {
    int extent = 0;

    if ((x > X_SENSITIVITY) || (x < - X_SENSITIVITY)) {
      extent = x;
    }

    /* Scale the bend extent. */
    extent = extent * MULTIPLIER;
    
    /* No negative bends, as they don't exist on real guitars. */
    extent = abs(extent);
    if (extent > 100) {
      extent = 100;
    } else if (extent < 6) {
      extent = 6;
    }
    SPDR = int(extent);
  }
}

void setup(void) {
  #ifndef ESP8266
    while (!Serial)
      ; // will pause Zero, Leonardo, etc until serial console opens
  #endif

  Serial.begin(9600);
  
  setupSensor();
  setupSPI();
}

void printAccelData(float x, float y, float z) {
  Serial.print("X: ");
  Serial.print(x);
  Serial.print("  ");
  Serial.print("Y: ");
  Serial.print(y);
  Serial.print("  ");
  Serial.print("Z: ");
  Serial.print(z);
  Serial.print("  ");
  Serial.println("m/s^2");
}

void loop(void) {
  if (process) {
    process = false; // reset the process

    /* Get a new sensor event */
    sensors_event_t event;
    accel.getEvent(&event);

    /* Display the results (acceleration is measured in m/s^2) */
    printAccelData(event.acceleration.x, event.acceleration.y, event.acceleration.z);

    /* Calculate and communicate position, any bend extent. */
    positionAndBend(event.acceleration.x, event.acceleration.y);
  }

  /* Delay before the next sensor sample */
  delay(500);
}
