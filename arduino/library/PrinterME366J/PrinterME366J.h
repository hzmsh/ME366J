#ifndef PrinterME366J_h
#define PrinterME366J_h

#define r_ena_pin 38
#define r_step_pin 54
#define r_dir_pin 55
#define t_ena_pin 56
#define t_step_pin 60
#define t_dir_pin 61
#define z_ena_pin 62
#define z_step_pin 46
#define z_dir_pin 48
#define e_ena_pin 24
#define e_step_pin 26
#define e_dir_pin 28

#define r_end_stop 3
#define z_end_stop 2

struct PolarFunction
{
	int function_type;
	float amplitude;
	float frequency;
	float time_shift;
	float vertical_shift;
	float left_bound;
	float right_bound;
	int layer;
	};

class PolarPrinter
{
public:
	PolarPrinter();
	void calibrate();
	void resetPolarFunction();
	void setFunctionTerm(PolarFunction term, int f);
	void print(PolarFunction *t, int size);
	void toggleE();
	void toggleZ();
private:
	void setNextGoal(int goal[3]);
	void executeGoal();
	void jogToStart(float t0, float r0);
	void flip180();
	void nextLayer();
	void retract(int p);

	//Arrays for setting / managing goal
	//0 -> r
	//1 -> t
	//2 -> e
	unsigned long scheduler[3];
	int step_goal[3];
	long step_delay[3];
	int step_manager[3];

	//Stepper Booleans
	bool r_pulse = LOW;
	bool t_pulse = LOW;
	bool z_pulse = LOW;
	bool e_pulse = LOW;

	bool r_dir = LOW;
	bool t_dir = LOW;
	bool z_dir = LOW;
	bool e_dir = LOW;

	bool r_ena = LOW;
	bool t_ena = LOW;
	bool z_ena = LOW;
	bool e_ena = LOW;

	//Polar Function
	//[0][0] -> function 0 term 0
	//[0][1] -> function 0 term 1
	PolarFunction polar_function_[10];
	int polar_function_array_size_;
  	float theta_resolution_ = 2*M_PI/1600;
	//Printer Coor
	float R_ = 0;
	bool R_SIGN_ = HIGH; 
	float Theta_ = 0;
	int Theta_Step_Count_ = 0;
	int Z_;
	//Printer Properties
	float pulley_radius_ = 8;
	int retract_frequency_ = 80;
};

#endif