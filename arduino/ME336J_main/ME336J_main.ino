#define NUM 3
#include <PrinterME366J.h>
#include <SerialME366J.h>

PolarPrinter printer;
PolarFunction polar_function[30];
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
        printer.print(polar_function, function_index);
        Serial.println("<Done>");
        break;
      case(4):
        //flip e enable pin
        printer.toggleE();
        break;
      case(5):
        //flip z enable pin
        printer.toggleZ();
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
        t.time_shift = s.function_data[3];
        t.vertical_shift = s.function_data[4];
        t.left_bound = s.function_data[5];
        t.right_bound = s.function_data[6];
        t.layer = s.function_data[7];
        Serial.println(t.amplitude);
        Serial.println(t.frequency);
        Serial.println(t.time_shift);
        Serial.println(t.vertical_shift);
        Serial.println(t.left_bound);
        Serial.println(t.right_bound);
        Serial.println(t.layer);
        //<1><2:1:10:1:0:0:0:1:0><3>
        //<1><2:3:50:1:0:0:0:6.28:0><1><2:3:50:1:0:0:0:6.28:1><3>
        //<1><2:3:50:2:0:0:0:6.28:0><1><2:3:50:2:0:0:0:6.28:1><1><2:3:50:2:0:0:0:6.28:2><3>
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
