
struct blink_cmd
{
  bool *states;
  int msec;
  
};

blink_cmd _cmd;
bool _new_cmd = false;
unsigned long _schedule_time = 0;

const byte _buff_size = 40;
char _input_buffer[40];
const char _read_mark_start = '<';
const char _read_mark_end = '>';
byte _bytes_read = 0;
boolean _read_in_progress = false;

void setup() 
{
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
}

void loop() 
{
  if (_new_cmd && _schedule_time <= millis())
  {
    Serial.println(millis());
    blinkTaskHandler(_cmd);
    _new_cmd = false;
    Serial.println("send_msg");
  }

  //Check Buffer for input data
  if(Serial.available() > 0) 
  {
    readSerialIn();
  }

}

void readSerialIn()
{
  char x = char(Serial.read());
  //Serial.println(x);

  // NOTE: the order of these IF clauses is significant

  //If input char marks the end of the data input message
  if (x == _read_mark_end) 
  {
    _read_in_progress = false;
    //Reset the input buffer string and send data message to be parsed
    _input_buffer[_bytes_read] = 0;
    parseDataIn();
  }

  //If the spin is currently receiving an input message
  if(_read_in_progress) 
  { 
    //Add the char to the end of the buffer and increase the buffer index
    _input_buffer[_bytes_read] = x;
    _bytes_read ++;
    if (_bytes_read == _buff_size) 
    {
      _bytes_read = _buff_size - 1;
    }
  }

  //If input char marks the beginging of an input message
  if (x == _read_mark_start)
  { 
    _bytes_read = 0; 
    _read_in_progress = true;
  }
}
void parseDataIn()
{
  int numberOfMsg = 4;
  //MSG PARSER GENERAL APPLICATION
  //------------------------------
  //Serial.println("Parsing the DATA");
  //Serial.println(_input_buffer);
  char * msg_pointer;
  String msg_list[numberOfMsg];
  msg_pointer = strtok(_input_buffer, ":");
  char msg[_buff_size] = {0};
  int msg_index = 0;
  while(msg_pointer != NULL)
  {
    strcpy(msg, msg_pointer);
    msg_list[msg_index] = msg;
    //Serial.println(msg);
    msg_index ++;
    msg_pointer = strtok(NULL, ":");
  }
  //------------------------------
  
  //MSG PARSER BLINK APPLICATION
  bool states[3];
  int msec;
  
  for (int i=0; i < 3; i++)
  {
    states[i] = msg_list[i].toInt();
  }
  msec = msg_list[3].toInt();
  //Serial.println(msec);

  _cmd.states = states;
  _cmd.msec = msec;
  _new_cmd = true;
}

void blinkTaskHandler(blink_cmd cmd)
{
  digitalWrite(2, cmd.states[0]);
  digitalWrite(3, cmd.states[1]);
  digitalWrite(4, cmd.states[2]);

  _schedule_time = millis() + long(cmd.msec);
  //Serial.println(cmd.msec);
  //Serial.println(_schedule_time);
  //Serial.println(millis());
}
