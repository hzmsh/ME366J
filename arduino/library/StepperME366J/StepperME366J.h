#ifndef StepperComME366J_h
#define StepperComME366J_h

class DriverTB6600
{
public:
  DriverTB6600(int spr, int *pins);

  void stepMotor(int steps, int time_delay);
  bool syncStep(bool dir);

private:
  int ena_pin;
  int dir_pin;
  int pul_pin;
  int pulse_state_;
};

class DriverL298N
{
public:
  DriverL298N();
  void setupDriver(int *pins);
  
  void stepMotor(int steps);
  bool syncStep(bool dir);
};

template <class DriverType>
class StepperMotor: public DriverType
{
public:
  StepperMotor(int spr, int *pins):
    DriverType(spr, pins), steps_per_rev_(spr){}

  void cmdAngle(float a)
  {
    //Turn the motor by a desired angle
    
    //Convert angle into steps
    //steps = angle/(2pi) * spr
    float theoretical = 0.5*a*steps_per_rev_/M_PI;
    int steps = round(theoretical);
    //Get error
    float error = 2*M_PI*(theoretical - steps)/steps_per_rev_;

    DriverType::stepMotor(steps, time_delay_);
  }

  int setAngleGoal(float a)
  {
    //SET GOAL FOR STEPPER
    //-------------------
    //This function will...
    //-> return the number of steps needed to complete goal
    //-> save the goal and error
    
    //Convert angle into steps
    //steps = angle/(2pi) * spr
    float angle_goal = a + error_;
    float theoretical = 0.5*angle_goal*steps_per_rev_/M_PI;
    goal_steps_ = round(theoretical);
    //Get error
    error_ = 2*M_PI*(theoretical - goal_steps_)/steps_per_rev_;
    return goal_steps_;
  }

  bool executeGoal(int execute_steps = 1)
  {
    if (signbit(goal_steps_))
    {
      execute_steps = -execute_steps;
    }
    if (fabs(execute_steps) < fabs(goal_steps_))
    {
      DriverType::stepMotor(execute_steps, time_delay_);
      goal_steps_ = goal_steps_ - execute_steps;
      return false;
    }
    else
    {
      DriverType::stepMotor(goal_steps_, time_delay_);
      goal_steps_ = 0;
      return true;
    }
  }

  void executeSyncGoalStep()
  {
    if (fabs(goal_steps_) > 0)
    {
      bool complete = false;
      bool step_cycle = false;
      bool dir = signbit(goal_steps_);
      while (!complete) //NOTE: Consider including exception or timeout
      {
        if (schedule_time_ < micros())
        {
          //pulse alternates high/low for one complete step
          //example:
          //  1st call: syncStep(dir) -> High
          //  2nd call: syncStep(dir) -> Low
          step_cycle = DriverType::syncStep(dir); 
          schedule_time_ += time_delay_;
          complete = true;
        }
      }
      //Check for completed motor step
      if (step_cycle)
      {
        if (signbit(goal_steps_)) goal_steps_ ++;
        else goal_steps_ --;
      }
    }
  }

  bool getTaskState()
  {
    if (fabs(goal_steps_) > 0) return true;
    else return false;
  }

private:
int steps_per_rev_;
int goal_steps_;
float error_;
int time_delay_ = 500;
unsigned long schedule_time_ = 0;

};
#endif