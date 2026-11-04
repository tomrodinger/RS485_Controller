#include <Servomotor.h>

// RS485 Pins for ESP32-S3 RS485 Controller
#define RS485_TXD 4
#define RS485_RXD 5

#define N_DETECT_DEVICES 3
#define MAX_N_DEVICES 48

// Global objects
Servomotor device255(255, Serial1); // Broadcast address 255

typedef struct {
  uint64_t unique_id;
  uint8_t alias;
  Servomotor *motor;
} device_data_t;

device_data_t device_list[MAX_N_DEVICES];
uint8_t n_devices = 0;

void reset_all_devices(void)
{
  Serial.println("Resetting all devices...");
  device255.systemReset();
  delay(1500); // wait for the reset to happen and the bootloader to pass execution to the main firmware
  Serial1.flush(); // Flush any outgoing data
  while (Serial1.available()) {
      Serial1.read(); // Clear any incoming data
  }
}

void detect_all_devices_once()
{
  detectDevicesResponse response;
  bool command_sent = false;

  reset_all_devices();
  
  while (1) {
    if (!command_sent) {
      response = device255.detectDevices();
      command_sent = true;
    }
    else {
      response = device255.detectDevicesGetAnotherResponse();
    }
    
    if (device255.getError() == COMMUNICATION_SUCCESS) {
      bool device_already_in_list = false;
      for (uint32_t n = 0; n < n_devices; n++) {
        if (response.uniqueId == device_list[n].unique_id) {
          device_already_in_list = true;
          break;
        }
      }
      if (!device_already_in_list) {
        if (n_devices >= MAX_N_DEVICES) {
          Serial.println("Error: too many devices");
          return;
        }
        device_list[n_devices].unique_id = response.uniqueId;
        device_list[n_devices].alias = response.alias;
        device_list[n_devices].motor = new Servomotor(response.alias, Serial1);
        n_devices++;
        Serial.printf("Found New Device - Unique ID: %016llX, Alias: %d\n", response.uniqueId, response.alias);
      }
    }
    else if (device255.getError() == COMMUNICATION_ERROR_TIMEOUT) {
      Serial.println("No more responses from the detectDevices command");
      break;
    }
    else {
      Serial.println("Corrupt data detected on the line");
      delay(1500);
      break;
    }
  }
}

void detect_all_devices()
{
  for (uint32_t i = 0; i < N_DETECT_DEVICES; i++) {
    Serial.printf("Starting detection of devices cycle number %u\n", i + 1);
    detect_all_devices_once();
  }
  Serial.printf("Total devices detected: %d\n", n_devices);
  Serial.println("------------------------------------------------");
}

void wait_for_queue_empty(Servomotor *motor)
{
  while (1) {
    if (motor->getNQueuedItems() == 0) {
      break;
    }
    delay(10);
  }
}

void setup() {
  // Initialize the main serial port for debugging
  Serial.begin(230400);
  while (!Serial);
  
  Serial.println("Starting Motor Control Demo");
  
  // Initialize Serial1 for RS485 communication
  Serial1.begin(230400, SERIAL_8N1, RS485_RXD, RS485_TXD);
  while (!Serial1);
  
  device255.openSerialPort();
  delay(100);
  
  detect_all_devices();
}

void loop() {
  if (n_devices == 0) {
    Serial.println("No devices found. Retrying detection in 5 seconds...");
    delay(5000);
    detect_all_devices();
    return;
  }

  for (int i = 0; i < n_devices; i++) {
    Servomotor* motor = device_list[i].motor;
    uint8_t alias = device_list[i].alias;
    
    Serial.printf("Testing motor with alias %d\n", alias);
    
    // Configure units
    motor->setPositionUnit(PositionUnit::SHAFT_ROTATIONS);
    motor->setTimeUnit(TimeUnit::SECONDS);
    motor->setVelocityUnit(VelocityUnit::ROTATIONS_PER_SECOND);
    motor->setAccelerationUnit(AccelerationUnit::ROTATIONS_PER_SECOND_SQUARED);
    
    // (1) Go to closed loop mode (which at the same time enables the MOSFETs)
    Serial.println("  Enabling MOSFETs and going to closed loop...");
    motor->enableMosfets();
    motor->goToClosedLoop();
    delay(100); // Short delay to ensure state change
    
    // (2) Queue up two trapezoid moves
    // Rotate half a rotation couterclockwise (0.5)
    // Rotate back (-0.5)
    // Time: 0.5s each
    Serial.println("  Queuing moves: +0.5 rotations (0.5s) and -0.5 rotations (0.5s)");
    motor->trapezoidMove(0.5, 0.5);
    motor->trapezoidMove(-0.5, 0.5);
    
    // Wait for moves to finish before resetting
    Serial.println("  Waiting for moves to complete...");
    wait_for_queue_empty(motor);
    
    // (3) Reset the motor
    Serial.println("  Resetting motor...");
    motor->systemReset();
    
    // Wait a bit for the reset to complete before moving to the next motor
    delay(1500); 
    Serial.println("  Motor reset complete.");
    Serial.println("------------------------------------------------");
  }
  
  Serial.println("Cycle complete. Restarting cycle in 2 seconds...");
  delay(2000);
}