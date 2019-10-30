#define NUM 2

#include <SerialME366J.h>
#include <StepperME366J.h>
#include <math.h>


//DEFINE MOTOR VARIABLES
//----------------------
//ENA, DIR, PUL
int pin0[] = {49, 51, 53};
int pin1[] = {48, 50, 52};
int pin2[] = {43, 45, 47};
int pin3[] = {42, 44, 46};
StepperMotor<DriverTB6600> s0(800,pin0);
StepperMotor<DriverTB6600> s1(800,pin1);
StepperMotor<DriverTB6600> s2(800,pin2);
StepperMotor<DriverTB6600> s3(800,pin3);

//DEFINE SERIAL COM / CMD VARIABLES
//---------------------------
StepperSerialCom com;
StepperCmd<NUM> queue; //queue of 1
bool new_cmd = false;
bool active_sync_task = false;

void setup()
{
  Serial.begin(9600);
  //s1.setAngleGoal(10);
  
}

void loop()
{
  if (active_sync_task)
  {
    iterateSync();
  }
  else
  {
    if (new_cmd) cmdHandler(queue);
  }
  if (com.getStepperCmdState())
  {
    new_cmd = true;
    queue = com.getStepperCmd();
  }
  if (Serial.available()) com.readSerialIn();
  Serial.println();
}

void cmdHandler(StepperCmd<NUM> cmd)
{
  new_cmd = false;
  if (cmd.cmd_type == 0)
  {
    active_sync_task = true;

    //MOTOR 0
    if (cmd.delta_angle[0] != 0) s0.setAngleGoal(cmd.delta_angle[0]);
    //MOTOR 1 
    if (NUM >= 2)
    {
      if (cmd.delta_angle[1] != 0) s1.setAngleGoal(cmd.delta_angle[1]);
    }
    //MOTOR 2 
    if (NUM >= 3)
    {
      if (cmd.delta_angle[2] != 0) s2.setAngleGoal(cmd.delta_angle[2]);
    }
    //MOTOR 3
    if (NUM >= 4)
    {
      if (cmd.delta_angle[3] != 0) s3.setAngleGoal(cmd.delta_angle[3]);
    }
  }
  else if (cmd.cmd_type == 1)
  {
    Serial.println("SETTING THE SPEED");
    //MOTOR 0
    s0.setTimeDelay(cmd.step_speed[0]);
    //MOTOR 1 
    if (NUM >= 2) s1.setTimeDelay(cmd.step_speed[1]);
    //MOTOR 2 
    if (NUM >= 3) s2.setTimeDelay(cmd.step_speed[2]);
    //MOTOR 3
    if (NUM >= 4) s3.setTimeDelay(cmd.step_speed[3]);
  }
}
void iterateSync()
{
  int completion_count = 0;
  //MOTOR 0
  if (s0.getTaskState()) s0.executeSyncGoalStep();
  else completion_count ++;
  //MOTOR 1 
  if (NUM >= 2)
  {
    if (s1.getTaskState()) s1.executeSyncGoalStep();
    else completion_count ++;
  }
  //MOTOR 2 
  if (NUM >= 3)
  {
    if (s2.getTaskState()) s2.executeSyncGoalStep();
    else completion_count ++;
  }
  //MOTOR 3
  if (NUM >= 4)
  {
    if (s3.getTaskState()) s3.executeSyncGoalStep();
    else completion_count ++;
  }
  //Check for task completion
  if (completion_count == NUM)
  {
    active_sync_task = false;
  }
}

int compScheduleTime(unsigned long *t)
{
  unsigned long minimum = t[0];
  int index = 0;
  for (int i=1; i<NUM; i++)
  {
    if (t[i] < minimum & t[i] > 0)
    {
      minimum = t[i];
      index = i;
    }
  }
  return index;
}
