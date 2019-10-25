#include <Arduino.h>
#include <StepperME366J.h>

//--------------------------------------------
//DRIVER TB6600 ------------------------------
//--------------------------------------------
DriverTB6600::DriverTB6600(int spr, int *pins)
{
  pinMode(pins[0], OUTPUT);
  ena_pin = pins[0];
  pinMode(pins[1], OUTPUT);
  dir_pin = pins[1];
  pinMode(pins[2], OUTPUT);
  pul_pin = pins[2];

  pulse_state_ = HIGH;
}

void DriverTB6600::stepMotor(int steps, int time_delay)
{
   Serial.print("TB6600: ");
   Serial.println(steps);

   //Enable Driver
   digitalWrite(ena_pin, LOW);
   //Set Direction
   if (steps < 0) 
   {
    digitalWrite(dir_pin, HIGH);
   }
   else if (steps > 0)
   {
    digitalWrite(dir_pin, LOW);
   }
   //Step Motor
   for (int i=0; i<fabs(steps); i++)
   {
      digitalWrite(pul_pin, HIGH);
      delayMicroseconds(time_delay);
      digitalWrite(pul_pin, LOW);
      delayMicroseconds(time_delay);

   }
}

bool DriverTB6600::syncStep(bool dir)
{
  //Execute half of a step, return pulse state to allow stepper motor
  //class to determine and count completion of full steps
  //Enable Driver
  digitalWrite(ena_pin, LOW);
  //Set Direction
  if (dir) 
  {
  digitalWrite(dir_pin, HIGH);
  }
  else
  {
  digitalWrite(dir_pin, LOW);
  }
  pulse_state_ = !pulse_state_;
  digitalWrite(pul_pin, pulse_state_);
  return pulse_state_;
}

int ena_pin;
int dir_pin;
int pul_pin;
int pulse_state_;

//--------------------------------------------
//DRIVER L298N -------------------------------
//--------------------------------------------
DriverL298N::DriverL298N(){}
void setupDriver(int *pins)
{
}

void DriverL298N::stepMotor(int steps)
{
  Serial.println("L298N");
  Serial.println(steps);
}
bool DriverL298N::syncStep(bool dir)
{
  return false;
}
