#define NUM 3
#include <PrinterME366J.h>
#include <SerialME366J.h>

PolarPrinter printer;
PolarFunction polar_function[10];
StepperSerialCom com;
int function_index = 0;

void setup()
{
  Serial.begin(9600);
  delay(1000);
//  printer.calibrate();
}

void loop()
{
  if (com.getSerialCmdState())
  {
    //GET NEW CMD
    SerialCmd<NUM> cmd;
    cmd = com.getSerialCmd();

    //HANDLE CMD BASED ON TYPE
    switch(cmd.cmd_type)
    {
      case(0):
        printer.calibrate();
        break;
      case(1):
        printer.resetPolarFunction();
        downloadPolarFunction();
        break;
      case(2):
        Serial.println("ERROR: Received function term w/o prompt to download");
        break;
      case(3):
        //Start Print
        printer.print(polar_function, function_index, cmd.cmd_data);
        break;
    }
  }
  if (Serial.available()) com.readSerialIn();
}

void downloadPolarFunction()
{
  Serial.println("Download"); 
  bool download_complete = false;
  PolarFunction t;
  while (not download_complete)
  {
    if (com.getSerialCmdState())
    {
      SerialCmd<NUM> s;
      s = com.getSerialCmd();
      if (s.cmd_type == 2)
      {
        Serial.println("Setting Term");
        t.function_type = s.function_data[0];
        t.amplitude = s.function_data[1];
        t.frequency = s.function_data[2];
        t.power = s.function_data[3];
        t.time_shift = s.function_data[4];
        t.vertical_shift = s.function_data[5];
        t.left_bound = s.function_data[6];
        t.right_bound = s.function_data[7];
        Serial.println(t.amplitude);
        Serial.println(t.frequency);
        Serial.println(t.power);
        Serial.println(t.time_shift);
        Serial.println(t.vertical_shift);
        Serial.println(t.left_bound);
        Serial.println(t.right_bound);
        //<1:1><2:0:100:1:1:0:0:0:6.29><3>
        //<1:1><2:3:100:2:1:0:0:0:6.29><1:1><2:0:125:1:1:0:0:0:6.29><3:3>
        //<1:1><2:3:80:5:1:0:0:0:6.29><1:1><2:5:140:2:1:0:0:0:6.29><3:2>

        //printer.setFunctionTerm(t, function_index);
        download_complete = true;
      }
    }
    if (Serial.available()) com.readSerialIn();
  }
  polar_function[function_index] = t;
  function_index ++;
  Serial.println("Download Finished");
}
