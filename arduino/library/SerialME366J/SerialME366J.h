#ifndef SerialComME366J_h
#define SerialComME366J_h


template <int n>
struct SerialCmd
{
  int cmd_type;
  int cmd_data;
  int stepper_data[n];
  float function_data[8];
};


class StepperSerialCom
{
public:
  StepperSerialCom(){}

  void readSerialIn();

  bool getReadProgress();
  bool getSerialCmdState();
  SerialCmd<NUM> getSerialCmd();

private:
  void parseDataIn();
  //SERIAL PARAMETERS
  const byte buff_size_ = 50;
  char input_buffer[50];
  const char read_mark_start_ = '<';
  const char read_mark_end_ = '>';
  byte bytes_read_ = 0;
  bool read_in_progress_ = false;
  //CMD VARIABLES
  SerialCmd<NUM> serial_cmd_;
  bool fresh_cmd_ = false;

};
#endif