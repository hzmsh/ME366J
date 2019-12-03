#define NUM 3 

#include <Arduino.h>
#include <SerialME366J.h>
  
void StepperSerialCom::readSerialIn()
{
  //Serial.println("Triggered");  
  char x = char(Serial.read());

  // NOTE: the order of these IF clauses is significant

  //If input char marks the end of the data input message
  if (x == read_mark_end_) 
  {
    read_in_progress_ = false;
    //Reset the input buffer string and send data message to be parsed
    input_buffer[bytes_read_] = 0;
    parseDataIn();
  }

  //If the spin is currently receiving an input message
  if(read_in_progress_) 
  { 
    //Add the char to the end of the buffer and increase the buffer index
    input_buffer[bytes_read_] = x;
    bytes_read_ ++;
    if (bytes_read_ == buff_size_) 
    {
      bytes_read_ = buff_size_ - 1;
    }
  }

  //If input char marks the beginging of an input message
  if (x == read_mark_start_)
  { 
    bytes_read_ = 0; 
    read_in_progress_ = true;
  }
}

bool StepperSerialCom::getReadProgress() 
{
  return read_in_progress_;
}

bool StepperSerialCom::getSerialCmdState() 
{
  return fresh_cmd_;
}

SerialCmd<NUM> StepperSerialCom::getSerialCmd()
{
  fresh_cmd_ = false;
  return serial_cmd_;
}

void StepperSerialCom::parseDataIn()
{
  //MSG PARSER GENERAL APPLICATION
  //------------------------------
  char * msg_pointer;
  String msg_list[10];
  msg_pointer = strtok(input_buffer, ":");
  char msg[buff_size_] = {0};
  int msg_index = 0;
  while(msg_pointer != NULL)
  {
    strcpy(msg, msg_pointer);
    msg_list[msg_index] = msg;
    msg_index ++;
    msg_pointer = strtok(NULL, ":");
  }
  //------------------------------
  //CONVERT TO CMD
  //Serial.println(msg_list[0]);
  serial_cmd_.cmd_type = msg_list[0].toInt();
  
  if (serial_cmd_.cmd_type == 2)
  {
    for (int i=0; i<8; i++)
    {
      serial_cmd_.function_data[i] = msg_list[i+1].toFloat();
    }
  }
  fresh_cmd_ = true;
}