#include <Servomotor.h>

// This file is compiled as C++, so declarations are needed before first use.
void ping_test_all_aliases(void);

#define MIN_DISTANCE -20000000
#define MAX_DISTANCE 20000000
#define MOVE_TIME_SECONDS 1
#define RS485_TXD 4
#define RS485_RXD 5
#define N_PINGS 1
#define MAX_QUEUED_ITEMS 3
#define CLOSED_LOOP_TEST // uncomment this if you want to run in closed loop mode, otherwise it will be open loop mode (which uses more current and stresses the driver more)
#define OPEN_LOOP_DRIVER_CURRENT_SETTING 300
#define MAX_N_DEVICES 48
#define N_DETECT_DEVICES 3 // The number of times we should reset and try to detect all devices, so that we are more sure that we have found all of them
#define MIN_ALIAS 2   // If a device is detected and its alias is not between MIN_ALIAS and MAX_ALIAS (inclusive) then the alias will be reassigned
#define MAX_ALIAS 253
#define ALL_SAME_ALIAS 'X' // in the case of running the test_same_alias_RS485_bus_collision test, this will determine the alias that all devices will use
#define N_COLLIDING_PING_TESTS 100 // the number of ping tests to do where all devices have the same alias (responses will collide) in one cycle of device detection

// Define LED pins for Arduino Micro
//const int ledPin = LED_BUILTIN_RX; // on-board green LED
const int ledPinPositive = 25; // LED attached to pin 25 of the ESP32 Dev Kit C board
const int ledPinNegative = 26; // LED attached to pin 25 of the ESP32 Dev Kit C board
uint8_t all_is_well = 1;

Servomotor device255(255, Serial1);
Servomotor device_with_unique_id(255, Serial1);

typedef struct {
  uint64_t unique_id;
  uint8_t current_alias;
  uint8_t reassigned_alias;
  Servomotor *motor;
} device_data_t;
device_data_t device_list[MAX_N_DEVICES];
uint8_t n_devices = 0;


void fatal_error(char *message)
{
  Serial.printf("Fatal error: %s\n", message);
  while (1);
}


void print_data_buffer(uint8_t *buf, uint8_t n_bytes)
{
  for (uint32_t d = 0; d < n_bytes; d++) {
    Serial.print(" ");
    Serial.print(buf[d]);
  }
  Serial.println("");
}


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

void detect_all_devices_once(Servomotor *device255)
{
  detectDevicesResponse response;
  bool command_sent;

  reset_all_devices();
  command_sent = false;
  while (1) {
    if (!command_sent) {
      response = device255->detectDevices();
      command_sent = true;
    }
    else {
      response = device255->detectDevicesGetAnotherResponse();
    }
    if (device255->getError() == COMMUNICATION_SUCCESS) {
      bool device_already_in_list = false;
      for (uint32_t n = 0; n < n_devices; n++) {
        if (response.uniqueId == device_list[n].unique_id) {
          device_already_in_list = true;
          break;
        }
      }
      if (!device_already_in_list) {
        if (n_devices >= MAX_N_DEVICES) {
          fatal_error("too may devices");
        }
        device_list[n_devices].unique_id = response.uniqueId;
        device_list[n_devices].current_alias = response.alias;
        device_list[n_devices].reassigned_alias = 255;
        device_list[n_devices].motor = new Servomotor(response.alias, Serial1);
        n_devices++;
        Serial.printf("Unique ID: %016llX\n", response.uniqueId);
        Serial.println(response.alias);
      }
      else {
        Serial.printf("Unique ID: %016llX (this device is already in the list)\n", response.uniqueId);
      }
    }
    else if (device255->getError() == COMMUNICATION_ERROR_TIMEOUT) {
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


void detect_all_devices(Servomotor *device255)
{
  for (uint32_t detect_devices_cycles = 0; detect_devices_cycles < N_DETECT_DEVICES; detect_devices_cycles++) {
    Serial.printf("Starting detection of devices cycle number %u\n", detect_devices_cycles);
    detect_all_devices_once(device255);
  }
  if (n_devices == 0) {
    fatal_error("No devices found");
  }
  Serial.printf("n_devices = %hhu\n", n_devices);
  Serial.println("------------------------------------------------");
  reset_all_devices();
}


void assign_unique_aliases(Servomotor *device_with_unique_id)
{
  uint8_t valid_used_alias_list[MAX_ALIAS - MIN_ALIAS + 1];
  memset(valid_used_alias_list, 0, sizeof(valid_used_alias_list));
  for (uint32_t n = 0; n < n_devices; n++) {
    if ((device_list[n].current_alias >= MIN_ALIAS) && (device_list[n].current_alias <= MAX_ALIAS)) {
      if (valid_used_alias_list[device_list[n].current_alias - MIN_ALIAS] == 0) {
        valid_used_alias_list[device_list[n].current_alias - MIN_ALIAS] = 1;
      }
      else {
        device_list[n].current_alias = 255;
      }
    }
    else {
      device_list[n].current_alias = 255;
    }
  }
//  for (uint32_t i = 0; i < sizeof(valid_used_alias_list); i++) {
//    Serial.printf("%u: %hhu\n", i + MIN_ALIAS, valid_used_alias_list[i]);
//  }
  uint32_t unused_alias_counter = MIN_ALIAS;
  for (uint32_t n = 0; n < n_devices; n++) {
    if (device_list[n].current_alias == 255) {
      while (1) {
        if (valid_used_alias_list[unused_alias_counter - MIN_ALIAS] == 0) {
          device_list[n].reassigned_alias = unused_alias_counter;
          unused_alias_counter++;
          break;
        }
        unused_alias_counter++;
        if (unused_alias_counter > MAX_ALIAS) {
          fatal_error("not enough aliases to allocate to all devices");
        }
      }
    }
  }
  Serial.println("Here are the new alias assignments:");
  for (uint32_t n = 0; n < n_devices; n++) {
    Serial.printf("   Unique ID: %016llX\n", device_list[n].unique_id);
    Serial.printf("    ---> current_alias:    %hhu\n", device_list[n].current_alias);
    Serial.printf("    ---> reassigned alias: %hhu\n", device_list[n].reassigned_alias);
  }
  // And now finally let's reassign any aliases that need it
//  bool at_least_one_reassigned = false;
  for (uint32_t n = 0; n < n_devices; n++) {
    if (device_list[n].current_alias == 255) {
      device_with_unique_id->useUniqueId(device_list[n].unique_id);
      device_with_unique_id->setDeviceAlias(device_list[n].reassigned_alias);
      if (device_with_unique_id->getError() == 0) {
        Serial.printf("Alias successfully reassigned: %hhu -> %hhu\n", device_list[n].current_alias, device_list[n].reassigned_alias);
        delay(1500);
      }
      else {
        Serial1.printf("Error: failed to reassign alias for device with unique ID %016llX (%hhu -> %hhu)\n", device_list[n].unique_id, device_list[n].current_alias, device_list[n].reassigned_alias);
        fatal_error("alias reassignment error");
      }
      device_list[n].current_alias = device_list[n].reassigned_alias;
//      at_least_one_reassigned = true;
    }
    // Initialize the Servomotor object with the new alias and Serial1
    device_list[n].motor->useAlias(device_list[n].current_alias);
  }
//  if (at_least_one_reassigned) { // make sure reassignment completed (which causes a devive reset)
//    delay(1500);
//  }
}


void assign_all_same_aliases(Servomotor *device_with_unique_id)
{
  for (uint32_t n = 0; n < n_devices; n++) {
    if (device_list[n].current_alias != ALL_SAME_ALIAS) {
      device_list[n].current_alias = 255;
      device_list[n].reassigned_alias = ALL_SAME_ALIAS;
    }
  }
  Serial.println("Here are the new alias assignments:");
  for (uint32_t n = 0; n < n_devices; n++) {
    Serial.printf("   Unique ID: %016llX\n", device_list[n].unique_id);
    Serial.printf("    ---> current_alias:    %hhu\n", device_list[n].current_alias);
    Serial.printf("    ---> reassigned alias: %hhu\n", device_list[n].reassigned_alias);
  }
  // And now finally let's reassign any aliases that need it
  for (uint32_t n = 0; n < n_devices; n++) {
    if (device_list[n].current_alias == 255) {
      device_with_unique_id->useUniqueId(device_list[n].unique_id);
      device_with_unique_id->setDeviceAlias(device_list[n].reassigned_alias);
      if (device_with_unique_id->getError() == 0) {
        Serial.printf("Alias successfully reassigned: %hhu -> %hhu\n", device_list[n].current_alias, device_list[n].reassigned_alias);
        delay(1500);
      }
      else {
        Serial1.printf("Error: failed to reassign alias for device with unique ID %016llX (%hhu -> %hhu)\n", device_list[n].unique_id, device_list[n].current_alias, device_list[n].reassigned_alias);
        fatal_error("alias reassignment error");
      }
      device_list[n].current_alias = device_list[n].reassigned_alias;
    }
    // Initialize the Servomotor object with the new alias and Serial1
    device_list[n].motor->useAlias(device_list[n].current_alias);
  }
}


void delete_all_devices(void)
{
  for (uint32_t n = 0; n < n_devices; n++) {
    delete device_list[n].motor;
  }
  n_devices = 0;
}


void test_detect_all_devices_continuous(Servomotor *device255, Servomotor *device_with_unique_id)
{
  uint32_t detect_devices_cycles = 0;

  assign_unique_aliases(device_with_unique_id);
  ping_test_all_aliases();
  if (!all_is_well) {
    fatal_error("all was not well with the ping tests");
  }

  while (1) {
    Serial.printf("Starting detection of devices\n");
    reset_all_devices();
    delete_all_devices();
    detect_all_devices_once(device255);
    Serial.printf("Number of devices detected this time: %u\n", n_devices);
    detect_devices_cycles++;
    Serial.printf("=== Finished detection cycle %u ============================================\n", detect_devices_cycles);
  }
}


void ping_test_all_aliases(void)
{
  Serial.println("Starting the ping test");
  Serial.printf("We will ping %u times to each alias and there are %u aliases to ping\n", N_PINGS, n_devices);
  for (uint32_t i = 0; i < N_PINGS; i++) {
    for (uint32_t alias_index = 0; alias_index < n_devices; alias_index++) {
      pingPayload send_data;
      pingResponse receive_data;
      for (uint32_t d = 0; d < sizeof(send_data.pingData); d++) {
        send_data.pingData[d] = random(0, 255);
      }
      Servomotor *motor = device_list[alias_index].motor;
      Serial.printf("Pinging device with alias %hhu with this random data:", motor->usingThisAlias());
      print_data_buffer(send_data.pingData, sizeof(send_data.pingData));
      receive_data = motor->ping(send_data.pingData);
      Serial.print("Received some data from the ping:");
      print_data_buffer(receive_data.responsePayload, sizeof(receive_data.responsePayload));
      if (memcmp(receive_data.responsePayload, send_data.pingData, sizeof(send_data.pingData)) != 0) {
        Serial.print("Ping test failed. The offending device is at index: ");
        Serial.println(alias_index);
        all_is_well = 0;
      }
    }
    Serial.print("Finished pinging number ");
    Serial.println(i + 1);
  }
}

void setup() {
  // Initialize the main serial port for debugging
  Serial.begin(230400); // Initialize serial port that weill be used for debug output
  while (!Serial);

  // Initialize Serial1 with baud rate 230400
  Serial.println("Initializing Serial1");
  Serial1.begin(230400, SERIAL_8N1, RS485_RXD, RS485_TXD);
  while (!Serial1);
  Serial.println("Opening serial port for communicating to the motors");
  device255.openSerialPort();
  delay(100); // wait for the serial port to stabilize
  detect_all_devices(&device255);
}


int32_t generate_random_move(int32_t min_distance, int32_t max_distance) {
    return random(min_distance, max_distance);
}


void test_same_alias_RS485_bus_collision(Servomotor *device255, Servomotor *device_with_unique_id)
{
  detectDevicesResponse response;
  pingPayload send_data;
  pingResponse receive_data;

  assign_all_same_aliases(device_with_unique_id);

  for (uint32_t n_detections = 0; ; n_detections++) {
    delete_all_devices();
    delay(1000); // Let the bus stabilize after the corrupt communication
    detect_all_devices_once(device255);
    if (n_devices == 0) {
      continue;
    }
    for (uint32_t n_pings = 0; n_pings < N_COLLIDING_PING_TESTS; n_pings++) {
      reset_all_devices();
      Servomotor *motor = device_list[0].motor;
      for (uint32_t d = 0; d < sizeof(send_data.pingData); d++) {
        send_data.pingData[d] = random(0, 255);
      }
      Serial.printf("Pinging device with alias %hhu with this random data:", motor->usingThisAlias());
      print_data_buffer(send_data.pingData, sizeof(send_data.pingData));
      receive_data = motor->ping(send_data.pingData);
      Serial.println("Delay 3");
      delay(1000);
      int8_t _errno = motor->getError();
      if (_errno == 0) {
        Serial.print("Received some data from the ping:");
        print_data_buffer(receive_data.responsePayload, sizeof(receive_data.responsePayload));
        if (memcmp(receive_data.responsePayload, send_data.pingData, sizeof(send_data.pingData)) != 0) {
          Serial.println("Ping succeeded to return something but it is wrong");
        }
      }
      else {
        Serial.printf("The ping returned an error (%hhd). This is not unexpected since there should be a collision on the RS485 bus\n", _errno);
      }
      Serial.printf("---   n_detections = %u   n_pings = %u   n_devices = %hhu   ----------------------------------------\n", n_detections + 1, n_pings + 1, n_devices);
    }
  }
}


void test_trapezoid_move_continuous(Servomotor *device255, Servomotor *device_with_unique_id)
{
  assign_unique_aliases(device_with_unique_id);
  ping_test_all_aliases();
  if (!all_is_well) {
    fatal_error("all was not well with the ping tests");
  }

  Serial.println("Going into closed loop mode now (all motors)");
  for (uint32_t alias_index = 0; alias_index < n_devices; alias_index++) {
    Servomotor *motor = device_list[alias_index].motor;
    #ifdef CLOSED_LOOP_TEST
    motor->goToClosedLoop();
    if (motor->getError() == 0) {
  //    flashLED();  // Flash the UART LED
      Serial.println("Go to closed loop succeeded.");
    }
    else {
      Serial.print("Error: could not go to closed loop. Errno: ");
      Serial.print(motor->getError());
      Serial.print(". The offending device is at index: ");
      Serial.println(alias_index);
      getStatusResponse status = motor->getStatus();
      Serial.print("   Status Flags: ");
      Serial.println(status.statusFlags, BIN); // Print as binary to see individual bits
      Serial.print("   Fatal Error Code: ");
      Serial.println(status.fatalErrorCode);
      all_is_well = 0;
      while(1);
    }
    #else
    motor->enableMosfets();
    motor->setMaximumMotorCurrent(OPEN_LOOP_DRIVER_CURRENT_SETTING, OPEN_LOOP_DRIVER_CURRENT_SETTING);
    #endif
  }

  while(1) {
    for (uint32_t alias_index = 0; alias_index < n_devices; alias_index++) {
      if (all_is_well) {
        Serial.print("Alias index: ");
        Serial.println(alias_index);
        Servomotor *motor = device_list[alias_index].motor;
        uint8_t nQueuedItems = motor->getNQueuedItems();
        Serial.print("   Number of Queued Items: ");
        Serial.println(nQueuedItems);
        if (nQueuedItems < MAX_QUEUED_ITEMS) {
          int32_t new_random_distance = generate_random_move(MIN_DISTANCE, MAX_DISTANCE);
          Serial.println("   ----- Sending a Trapezoid Move command -----");
          Serial.print("   New commanded move distance: ");
          Serial.println(new_random_distance);
          motor->trapezoidMoveRaw(new_random_distance, MOVE_TIME_SECONDS * 31250); // Move to position
          if (motor->getError() == 0) {
      //      flashLED();  // Flash the UART LED
            Serial.println("   Movement command sent successfully.");
          } else {
            Serial.print("   Error sending movement command. Errno: ");
            Serial.println(motor->getError());
          }
  //      delay(MOVE_TIME_SECONDS * 1000 * 105 / 100); // Wait for 1 second before generating a new position
        }

        getComprehensivePositionResponse position = motor->getComprehensivePositionRaw();
        if (motor->getError() == 0) {
            Serial.print("   Commanded Position: ");
            Serial.println(position.commandedPosition);
            Serial.print("   Hall Sensor Position: ");
            Serial.println(position.hallSensorPosition);
            Serial.print("   The difference between these: ");
            Serial.println(position.hallSensorPosition - position.commandedPosition);
        } else {
            Serial.print("   Error getting position. Errno: ");
            Serial.println(motor->getError());
        }

    //      int32_t position = motor->getPosition();
    //      if (motor->getError() == 0) {
    //          Serial.print("Current Position: ");
    //          Serial.println(position);
    //      } else {
    //          Serial.print("Error getting position. Errno: ");
    //          Serial.println(motor->getError());
    //      }

        getStatusResponse status = motor->getStatus();
        Serial.print("   Status Flags: ");
        Serial.println(status.statusFlags, BIN); // Print as binary to see individual bits
        Serial.print("   Fatal Error Code: ");
        Serial.println(status.fatalErrorCode);
        if (status.fatalErrorCode != 0) {
          all_is_well = 0;
        }
        

        getDebugValuesResponse debugValues = motor->getDebugValues();
        Serial.print("   Debug values: ");
        Serial.print(debugValues.debugValue1);
        Serial.print("   ");
        Serial.print(debugValues.debugValue2);
        Serial.print("   ");
        Serial.print(debugValues.debugValue3);
        Serial.print("   ");
        Serial.println(debugValues.debugValue4);
      }
    }
  }
}

void loop()
{
  // Uncomment one of these tests that you want to run
//  test_detect_all_devices_continuous(&device255, &device_with_unique_id);
//  test_same_alias_RS485_bus_collision(&device255, &device_with_unique_id);
  test_trapezoid_move_continuous(&device255, &device_with_unique_id);
}
