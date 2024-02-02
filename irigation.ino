// Pin definition 
# define sensor_pin_1 A0
# define sensor_pin_2 A1
# define sensor_pin_3 A2
# define SENSOR_COUNT 3
# define WATERING_TRESHOLD 600
# define TIME_TO_WATER 5

// Watering state
bool waterPlants = false;

// Precentages
float percentage[] = {0,0,0};
float averagePercentage = 0; 

// other
const int maximum = 365;
const int threshold = 41; // Percentage
const int minimum = 666;
const int sensor_power_pins[] = {6, 7, 8};

int fluidControlValue = 3;
int pins_a_out[] = {0, 0, 0};

void setup() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    pinMode(sensor_power_pins[i], OUTPUT);
    digitalWrite(sensor_power_pins[i], HIGH);
  }
  pinMode(fluidControlValue, OUTPUT);
  digitalWrite(fluidControlValue, HIGH);
  Serial.begin(9600);
}

void loop() {
  readSensor();
  checkWatering();
  giveWater();
  printMoisture();
  averagePercentage = 0;
  delay(10000);// Each second check for moisture
}

void readSensor(){
  // Reads sensor output (analog) // calculates percentage // 
  pins_a_out[0] = analogRead(sensor_pin_1);
  pins_a_out[1] = analogRead(sensor_pin_2);
  pins_a_out[2] = analogRead(sensor_pin_3);
  for (int i = 0; i < SENSOR_COUNT; i++) {
    percentage[i] = ((pins_a_out[i] - minimum) * 100) / (maximum - minimum);
    averagePercentage += percentage[i];
  }
  averagePercentage /= 3;
}

void checkWatering(){
  waterPlants =  averagePercentage < threshold;
}

void giveWater() {
  if (waterPlants) {
    digitalWrite(fluidControlValue, LOW);
    delay(TIME_TO_WATER * 1000);
    digitalWrite(fluidControlValue, HIGH);
    Serial.println("Watering plants");
  }
  else {
    digitalWrite(fluidControlValue, HIGH);
  }
}

void printMoisture() {
  for (int i = 0; i < SENSOR_COUNT; i++) {
    Serial.print("Plant ");
    Serial.println(i);
    Serial.print("Moisture level: ");
    Serial.print(round(percentage[i]));
    Serial.println("%");
  }
  Serial.println(averagePercentage);
}
