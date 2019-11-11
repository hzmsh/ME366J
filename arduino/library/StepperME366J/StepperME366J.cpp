#include <Arduino.h>
#include <StepperME366J.h>

//--------------------------------------------
//DRIVER TB6600 ------------------------------
//--------------------------------------------
DriverTB6600::DriverTB6600(int spr, int *pins)
{
  pinMode(pins[0], OUTPUT);
  ena_pin_ = pins[0];
  pinMode(pins[1], OUTPUT);
  dir_pin_ = pins[1];
  pinMode(pins[2], OUTPUT);
  pul_pin_ = pins[2];

  pulse_state_ = HIGH;
}

void DriverTB6600::stepMotor(int steps, int time_delay)
{
   Serial.print("TB6600: ");
   Serial.println(steps);

   //Enable Driver
   digitalWrite(ena_pin_, LOW);
   //Set Direction
   if (steps < 0) 
   {
    digitalWrite(dir_pin_, HIGH);
   }
   else if (steps > 0)
   {
    digitalWrite(dir_pin_, LOW);
   }
   //Step Motor
   for (int i=0; i<fabs(steps); i++)
   {
      digitalWrite(pul_pin_, HIGH);
      delayMicroseconds(time_delay);
      digitalWrite(pul_pin_, LOW);
      delayMicroseconds(time_delay);

   }
}

bool DriverTB6600::syncStep(bool dir)
{
  //Execute half of a step, return pulse state to allow stepper motor
  //class to determine and count completion of full steps
  //Enable Driver
  digitalWrite(ena_pin_, LOW);
  //Set Direction
  if (dir) 
  {
  digitalWrite(dir_pin_, HIGH);
  }
  else
  {
  digitalWrite(dir_pin_, LOW);
  }
  pulse_state_ = !pulse_state_;
  digitalWrite(pul_pin_, pulse_state_);
  return pulse_state_;
}

// int ena_pin_;
// int dir_pin;
// int pul_pin;
// int pulse_state_;

//--------------------------------------------
// DRIVER DVR8825 ----------------------------
//--------------------------------------------
DriverDVR8825::DriverDVR8825(int spr, int *pins)
{
  step_pin_ = pins[0];
  dir_pin_ = pins[1];
  pulse_state_ = HIGH;
}

bool DriverDVR8825::syncStep(bool dir)
{
  //Execute half of a step, return pulse state to allow stepper motor
  //class to determine and count completion of full steps
  //Set Direction
  if (dir) 
  {
  digitalWrite(dir_pin_, HIGH);
  }
  else
  {
  digitalWrite(dir_pin_, LOW);
  }
  pulse_state_ = !pulse_state_;
  digitalWrite(step_pin_, pulse_state_);
  return pulse_state_;
}