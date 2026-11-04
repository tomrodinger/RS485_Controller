// Minimal Arduino example: Trapezoid move using built‑in unit conversions
// Goal: spin the motor exactly 1 rotation in 1 second, then stop.
// Sequence:
//  enable MOSFETs -> trapezoidMove(1.0 rotations, 1.0 seconds) -> wait 1.1s -> disable MOSFETs.
//
// Notes:
// - This uses the library's unit conversion (no raw counts/timesteps).
// - Configure Serial1 pins for your board (ESP32 example pins below).
// - Motor is created AFTER Serial1.begin(...) so hardware UART pins are set first.

#include <Servomotor.h>

#define THROW_TIME_WHEN_THROWING_TO_SELF 0.08
#define THROW_TIME_WHEN_THROWING_TO_OTHER 0.5

//#define THROW_ANGLE1 20.0 // Use 13.0 for the demo on the first day of the fair, 20.5 for the white ball, throw to the left at the demo from the point of view behind the booth
//#define THROW_ANGLE2 21.3 // Use 13.0 for the demo on the first day of the fair, 20.5 for the white ball, throw right
//#define THROW_ANGLE1 15.0 // use for the juggling colourful ball, throw to the left at the demo from the point of view behind the booth
//#define THROW_ANGLE2 15.0 // use for the juggling colourful ball, throw right
//#define THROW_ANGLE3 15.0 // use for the juggling colourful ball, throw right
#define THROW_ANGLE_WHEN_THROWING_TO_SELF 15.0
#define THROW_ANGLE_WHEN_THROWING_TO_OTHER 120

#define MAX_HOMING_TIME 3.0
#define WIND_UP_ANGLE 15.0 // used to be 25 for the HK Electronics Fair
#define WIND_UP_ROTATIONS (WIND_UP_ANGLE / 360.0)
#define START_POSITION_ROTATIONS 0.25
#define WIND_UP_TIME 0.3
#define CATCH_ANGLE_WHEN_THROWING_TO_SELF 45.0
#define CATCH_ANGLE_WHEN_THROWING_TO_OTHER 80.0
#define PAUSE_AFTER_THROW_TIME 0.05
#define TO_CATCH_POSITION_TIME 0.15
#define CATCH_ANGLE 50.0
#define CATCH_TIME 0.2
#define GO_BACK_TO_START_TIME 1.0

#define VERBOSE 0

#define THROW_MOSFET_CURRENT 300.0
#define CATCH_CURRENT_WHEN_THROWING_TO_SELF 25.0
#define CATCH_CURRENT_WHEN_THROWING_TO_OTHER 45.0
#define SUSPEND_BALL_CURRENT 15

#define DROP_VELOCITY_THRESHOLD 0.005 // rotations per second. if the speed exceeds this then it means that the ball has landed on the arm and is moving it quickly
#define SLOW_DOWN_THRESHOLD 0.001

#define THROW_VELOCITY     4.0
#define THROW_ACCELERATION 100.0

#define ALIAS1 'X'                   // Device alias of first device
#define ALIAS2 'Y'                   // Device alias of second device
#define ALIAS3 'Z'                   // Device alias of third device
#define BAUD 230400                 // RS485 UART baud rate

// Example RS485 pins for ESP32 DevKit (change as needed for your board)
#if defined(ESP32)
#define RS485_TXD 4              // TX pin to RS485 transceiver
#define RS485_RXD 5              // RX pin from RS485 transceiver
#endif

  // Create the motor; serial port opens on first instantiation.
#if defined(ESP32)
  Servomotor motor1(ALIAS1, Serial1, RS485_RXD, RS485_TXD);
  Servomotor motor2(ALIAS2, Serial1, RS485_RXD, RS485_TXD);
  Servomotor motor3(ALIAS3, Serial1, RS485_RXD, RS485_TXD);
#else
  Servomotor motor1(ALIAS1, Serial1);
  Servomotor motor2(ALIAS2, Serial1);
  Servomotor motor3(ALIAS3, Serial1);
#endif

double full_range1 = 0;
double full_range2 = 0;
double full_range3 = 0;

void wait_for_queue_empty(Servomotor *motor)
{
  while (1) {   // wait for all these moves to finish, whish will be at the time when the arm is in the catch position
    if (motor->getNQueuedItems() == 0) {
      break;
    }
  }
}

int throw_a_ball(Servomotor *motor, double full_range, double direction, double throw_angle, double throw_time)
{
  double wind_up_position = -(START_POSITION_ROTATIONS + WIND_UP_ROTATIONS) * direction;
  double throw_rotations = throw_angle / 360.0;
  double end_of_throw_position = wind_up_position + (WIND_UP_ROTATIONS + throw_rotations) * direction;

  motor->setMaximumMotorCurrent(THROW_MOSFET_CURRENT, THROW_MOSFET_CURRENT); // set the MOSFET current
  motor->goToPosition(wind_up_position, 0.3); // wind up just before the throw
  wait_for_queue_empty(motor);
  motor->goToPosition(end_of_throw_position, throw_time); // throw the ball
  motor->trapezoidMove(0, PAUSE_AFTER_THROW_TIME); // pause for a short time without movement to wait for the ball to leave the arm
  return 0;
}

int catch_a_ball(Servomotor *motor, double full_range, double direction, double throw_angle, double catch_angle, uint16_t catch_current, bool do_special_catch_algorithm)
{
  double wind_up_position = -(START_POSITION_ROTATIONS + WIND_UP_ROTATIONS) * direction;
  double throw_rotations = throw_angle / 360.0;
  double end_of_throw_position = wind_up_position + (WIND_UP_ROTATIONS + throw_rotations) * direction;
  double catch_position = catch_angle / 360 * direction;

  motor->goToPosition(catch_position, TO_CATCH_POSITION_TIME); // move the motor very quickly to the catch position
  wait_for_queue_empty(motor);
  motor->setMaximumMotorCurrent(catch_current, catch_current);   // let's make the motor much more weak so that it has flex and causes the ball to be caught without bouncing out

  //============================================================================================================
  // Here we do an algorithm to detect that the motor is rotating because the ball landed on the arm as expected
  if (do_special_catch_algorithm) {
    double old_sensed_position = 1000000.0;
    bool down_movement_sensed = false;
    double max_velocity = 0;
    for(int count = 0; count < 50; count++) {
      getComprehensivePositionResponseConverted comprehensive_position_response = motor->getComprehensivePosition();  // get the position once more to make sure the motor is not moving
      double sensed_position = comprehensive_position_response.hallSensorPosition;
      if (old_sensed_position != 1000000.0) {
        double drop_velocity = fabs(sensed_position - old_sensed_position);
        if (drop_velocity > max_velocity) {
          max_velocity = drop_velocity;
        }
        if (down_movement_sensed && (drop_velocity < SLOW_DOWN_THRESHOLD)) {
          break;
        }
        if (drop_velocity > DROP_VELOCITY_THRESHOLD) {
          down_movement_sensed = true;
        }
      }
      old_sensed_position = sensed_position;
      delay(5);
    }
    Serial.print("max_volocity = "); 
    Serial.println(String(max_velocity, 6));  // 6 digits after decimal
//  char buf[48];
//  dtostrf(x, /*minWidth*/ 0, /*precision*/ 6, buf);  // AVR and many cores provide dtostrf
//  Serial.print("x = ");
//  Serial.println(buf);
//  Serial.printf("max_volocity = %f\n", max_velocity);
  }
  //============================================================================================================
  motor->setMaximumMotorCurrent(SUSPEND_BALL_CURRENT, SUSPEND_BALL_CURRENT);   // make the motor strength balance the weight of the ball so that the ball does not move when the motor is on
//  delay(3000);
  delay(0.5 * 1000);
  // let's determine if there is a ball there or not by seeing if the motor is moving when we disable the MOSFETs (ball will pull the motor by gravity if it is there)
  getComprehensivePositionResponseConverted comprehensive_position_response = motor->getComprehensivePosition();  // get the position once more to make sure the motor is not moving
  double sensed_before_disable = comprehensive_position_response.hallSensorPosition;
  motor->disableMosfets();                     // disable MOSFETs. if there is a ball there then the arm will drop
  delay(0.05 * 1000);
  comprehensive_position_response = motor->getComprehensivePosition();  // get the position once more to make sure the motor is not moving
  double sensed_after_disable = comprehensive_position_response.hallSensorPosition;
  motor->enableMosfets();                      // enable MOSFETs again   
  double distance_motor_moved_while_disabled = fabs(sensed_after_disable - sensed_before_disable);
//  print(f"The motor moved {distance_motor_moved_while_disabled} rotations while MOSFETs were disabled");
  if (distance_motor_moved_while_disabled < 0.008) {
//      print("DID NOT CATCH IT. WILL WAIT FOR THE BALL TO BE PLACED BY THE HUMAN");
    while (1) {
      comprehensive_position_response = motor->getComprehensivePosition();
      double sensed = comprehensive_position_response.hallSensorPosition;
      double expected_position_after_catch = (full_range / 2) * direction;
      double error_from_expected_position = fabs(sensed - expected_position_after_catch);
      if (error_from_expected_position < 0.03) {
        break;
      }
      delay(0.01 * 1000);
    }
  }
  else {
//      print("CAUGHT IT");
  }


  double start_current = 15;
  motor->setMaximumMotorCurrent(start_current, start_current);   // let's make the motor super weak so it can no longer push the ball up against gravity
//  print(f"Set the current to {start_current}");

  motor->goToPosition((START_POSITION_ROTATIONS + WIND_UP_ROTATIONS) * direction, 0.1);

  int n_steps = 40;
  for (int i = 0; i < n_steps; i++) {
    double final_current = start_current * 3;
    double current_step = (final_current - start_current) / n_steps;
    double current_at_this_step = (i + 1) * current_step + start_current;
//      print(f"Setting current to {current_at_this_step}");
    motor->setMaximumMotorCurrent(current_at_this_step, current_at_this_step);   // let's make the motor super weak so it can no longer push the ball up against gravity
    delay(0.01 * 1000);
  }
  //motor->trapezoidMove(CATCH_ANGLE / 360, CATCH_TIME) # we will move the motor as the ball is coming down to ease it into the catch
  return 0;
}


int go_to_middle(Servomotor *motor)
{
  motor->goToPosition(0.0, 1.5);
  return 0;
}

void initialize_motor(Servomotor &motor, double *full_range)
{
  // Use units: rotations for position, seconds for time
  motor.setPositionUnit(PositionUnit::SHAFT_ROTATIONS);
  motor.setTimeUnit(TimeUnit::SECONDS);
  motor.setCurrentUnit(CurrentUnit::INTERNAL_CURRENT_UNITS);
  motor.setVelocityUnit(VelocityUnit::ROTATIONS_PER_SECOND);
  motor.setAccelerationUnit(AccelerationUnit::ROTATIONS_PER_SECOND_SQUARED);

  motor.enableMosfets();                      // enable MOSFETs
  motor.setMaximumMotorCurrent(50, 50);   // let's make the motor very weak first, and then do homing
  motor.setPidConstants(3000, 2, 175000);  // set the PID constants
  motor.goToClosedLoop();                   // go to closed loop position control mode
  delay(0.2 * 1000);

  motor.homing(1, MAX_HOMING_TIME);                       // do homing
  // wait until homing is done
  while (1) {
    getStatusResponse status_response = motor.getStatus();
    uint16_t status_flags = status_response.statusFlags;
    if ((status_flags & (1 << 4)) == 0) {
      break;
    }
    delay(0.5 * 1000);
  }
  getComprehensivePositionResponseConverted comprehensive_position_response = motor.getComprehensivePosition();
//  print(f"Initial positions: commanded={commanded}, sensed={sensed}")
  double rightmost_positon = comprehensive_position_response.hallSensorPosition;

  motor.homing(-1, MAX_HOMING_TIME);                       // do homing
  // wait until homing is done
  while (1) {
    getStatusResponse status_response = motor.getStatus();
    uint16_t status_flags = status_response.statusFlags;
    if ((status_flags & (1 << 4)) == 0) {
      break;
    }
    delay(0.5 * 1000);
  }
  comprehensive_position_response = motor.getComprehensivePosition();
//  print(f"Initial positions: commanded={commanded}, sensed={sensed}")
  double leftmost_positon = comprehensive_position_response.hallSensorPosition;

  // we will now calculate the center position between the two extreme positions
  *full_range = rightmost_positon - leftmost_positon;
//  print(f"The full range of motion is {*full_range} rotations:")
  double center_position = (leftmost_positon + rightmost_positon) / 2;
//  print("The center position between the two extreme positions is:", center_position)
  // and travel to that position
  motor.goToPosition(center_position, 0.5);
  delay(1.2 * 1000);
  // zero the positon at the center position
  motor.zeroPosition();
  motor.setMaximumAcceleration(THROW_ACCELERATION); // set the maximum acceleration of the throw
  motor.setMaximumVelocity(THROW_VELOCITY); // set the maximum velocity of the throw
}


void setup()
{
  Serial.begin(500000); // Console serial for debugging
  Serial.println("Starting the demo...");
  motor1.systemReset();
  delay(100);
  motor2.systemReset();
  delay(100);
  motor3.systemReset();
  delay(1000); // wait for all the motors to finish resetting
  initialize_motor(motor1, &full_range1);
  initialize_motor(motor2, &full_range2);  
  initialize_motor(motor3, &full_range3);  
}

/*
void loop_early_demo()
{
//  Serial.println("Doing a throw to the right");
//  throw_a_ball(&motor1, full_range1, 1, THROW_ANGLE1);
//  Serial.println("Catching the ball on the right");
//  catch_a_ball(&motor1, full_range1, 1, THROW_ANGLE1);
//  Serial.println("Doing a throw to the right");
//  throw_a_ball(&motor2, full_range2, 1, THROW_ANGLE1);
//  Serial.println("Catching the ball on the right");
//  catch_a_ball(&motor2, full_range2, 1, THROW_ANGLE1);
//  Serial.println("Doing a throw to the left");
//  throw_a_ball(&motor1, full_range1, -1, THROW_ANGLE2);
//  Serial.println("Catching the ball on the left");
//  catch_a_ball(&motor1, full_range1, -1, THROW_ANGLE2);
//  Serial.println("Doing a throw to the left");
//  throw_a_ball(&motor2, full_range2, -1, THROW_ANGLE2);
//  Serial.println("Catching the ball on the left");
//  catch_a_ball(&motor2, full_range2, -1, THROW_ANGLE2);
}

void loop_two_arms()
{
  throw_a_ball(&motor1, full_range1, 1, THROW_ANGLE1); // X - the right side
  catch_a_ball(&motor2, full_range2, -1, THROW_ANGLE2, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor1);
  throw_a_ball(&motor2, full_range2, 1, THROW_ANGLE1);
  catch_a_ball(&motor2, full_range2, 1, THROW_ANGLE1, CATCH_ANGLE_WHEN_THROWING_TO_SELF, CATCH_CURRENT_WHEN_THROWING_TO_SELF, false);
  throw_a_ball(&motor2, full_range2, -1, THROW_ANGLE2);
  catch_a_ball(&motor1, full_range1, 1, THROW_ANGLE2, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor2);
  throw_a_ball(&motor1, full_range1, -1, THROW_ANGLE1);
  catch_a_ball(&motor1, full_range1, -1, THROW_ANGLE1, CATCH_ANGLE_WHEN_THROWING_TO_SELF, CATCH_CURRENT_WHEN_THROWING_TO_SELF, false);
}
*/

void loop() // three arms
{
  throw_a_ball(&motor1, full_range1, 1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, THROW_TIME_WHEN_THROWING_TO_OTHER); // X - the right side
  catch_a_ball(&motor2, full_range2, -1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor1);
  throw_a_ball(&motor2, full_range2, 1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, THROW_TIME_WHEN_THROWING_TO_OTHER);
  catch_a_ball(&motor3, full_range3, -1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor2);
  throw_a_ball(&motor3, full_range2, 1, THROW_ANGLE_WHEN_THROWING_TO_SELF, THROW_TIME_WHEN_THROWING_TO_SELF);
  catch_a_ball(&motor3, full_range2, 1, THROW_ANGLE_WHEN_THROWING_TO_SELF, CATCH_ANGLE_WHEN_THROWING_TO_SELF, CATCH_CURRENT_WHEN_THROWING_TO_SELF, false);
  throw_a_ball(&motor3, full_range2, -1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, THROW_TIME_WHEN_THROWING_TO_OTHER);
  catch_a_ball(&motor2, full_range2, 1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor3);
  throw_a_ball(&motor2, full_range2, -1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, THROW_TIME_WHEN_THROWING_TO_OTHER);
  catch_a_ball(&motor1, full_range1, 1, THROW_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_ANGLE_WHEN_THROWING_TO_OTHER, CATCH_CURRENT_WHEN_THROWING_TO_OTHER, true);
  go_to_middle(&motor2);
  throw_a_ball(&motor1, full_range1, -1, THROW_ANGLE_WHEN_THROWING_TO_SELF, THROW_TIME_WHEN_THROWING_TO_SELF);
  catch_a_ball(&motor1, full_range1, -1, THROW_ANGLE_WHEN_THROWING_TO_SELF, CATCH_ANGLE_WHEN_THROWING_TO_SELF, CATCH_CURRENT_WHEN_THROWING_TO_SELF, false);
}
