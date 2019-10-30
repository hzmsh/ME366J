#ifndef SerialComME366J_h
#define SerialComME366J_h


template <int n>
struct StepperCmd
{
  int cmd_type;
  float delta_angle[n];
  int step_speed[n];
};

class StepperSerialCom
{
public:
  StepperSerialCom(){}

  void readSerialIn();
  bool getReadProgress();
  bool getStepperCmdState();
  StepperCmd<NUM> getStepperCmd();

private:
  void parseDataIn();
  //SERIAL PARAMETERS
  const byte buff_size_ = 40;
  char input_buffer[40];
  const char read_mark_start_ = '<';
  const char read_mark_end_ = '>';
  byte bytes_read_ = 0;
  bool read_in_progress_ = false;
  //CMD VARIABLES
  StepperCmd<NUM> stepper_cmd_;
  bool fresh_cmd_ = false;
};
#endif