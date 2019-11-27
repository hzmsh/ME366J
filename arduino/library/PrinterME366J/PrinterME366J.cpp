#define NUM 3 

#include <Arduino.h>
#include <PrinterME366J.h>

PolarPrinter::PolarPrinter()
{
	pinMode(r_ena_pin, OUTPUT);
	pinMode(r_step_pin, OUTPUT);
	pinMode(r_dir_pin, OUTPUT);
	pinMode(t_ena_pin, OUTPUT);
	pinMode(t_step_pin, OUTPUT);
	pinMode(t_dir_pin, OUTPUT);
	pinMode(z_ena_pin, OUTPUT);
	pinMode(z_step_pin, OUTPUT);
	pinMode(z_dir_pin, OUTPUT);
	pinMode(e_ena_pin, OUTPUT);
	pinMode(e_step_pin, OUTPUT);
	pinMode(e_dir_pin, OUTPUT);

	pinMode(r_end_stop, INPUT);
	pinMode(z_end_stop, INPUT);

	digitalWrite(r_ena_pin, LOW);
	digitalWrite(t_ena_pin, LOW);
	digitalWrite(z_ena_pin, LOW);
	digitalWrite(e_ena_pin, LOW);

	digitalWrite(r_dir_pin, r_dir);
	digitalWrite(t_dir_pin, t_dir);
	digitalWrite(z_dir_pin, z_dir);
	digitalWrite(e_dir_pin, e_dir);
}

void PolarPrinter::calibrate()
{
	digitalWrite(z_dir_pin, HIGH);
	for (int i=0; i<6400; i++)
	{
		z_pulse = !z_pulse;
		digitalWrite(z_step_pin, z_pulse);      
		delayMicroseconds(250);
	}

	//Calibrate R
	digitalWrite(r_dir_pin, LOW);
	bool cal_complete = false;
	int l1 = 0;
	int l2 = 0;
	while (not cal_complete)
	{
		r_pulse = !r_pulse;
		digitalWrite(r_step_pin, r_pulse);
		l2 = l1;
		l1 = digitalRead(r_end_stop);
		delayMicroseconds(500);
		if (l1 == 1 & l2 == 1) 
		{
			delay(100);
			digitalWrite(r_dir_pin, HIGH);
			for (int i=0; i<400; i++)
			{
				r_pulse = !r_pulse;
				digitalWrite(r_step_pin, r_pulse);
				delayMicroseconds(500);
			}
			cal_complete = true;
		}
	}

	R_ = 0;

	//Calibrate Theta
	if (Theta_Step_Count_ != 0)
	{
		while (Theta_Step_Count_ > 6400) Theta_Step_Count_ -= 6400;
		while (Theta_Step_Count_ < 0) Theta_Step_Count_ += 6400;
		if (Theta_Step_Count_ < 3200)
		{
			digitalWrite(t_dir_pin, LOW);
			while (Theta_Step_Count_ > 0)
			{
				digitalWrite(t_step_pin, HIGH);
				delayMicroseconds(500);
				digitalWrite(t_step_pin, LOW);
				delayMicroseconds(500);
				Theta_Step_Count_ -= 1;
			}
		}
		else 
		{
			digitalWrite(t_dir_pin, HIGH);
			while (Theta_Step_Count_ < 6400)
			{
				digitalWrite(t_step_pin, HIGH);
				delayMicroseconds(500);
				digitalWrite(t_step_pin, LOW);
				delayMicroseconds(500);
				Theta_Step_Count_ += 1;
			}
		}
	}	
	Theta_ = 0;
	Theta_Step_Count_ = 0;

	digitalWrite(z_dir_pin, LOW);
	for (int i=0; i<6400; i++)
	{
		z_pulse = !z_pulse;
		digitalWrite(z_step_pin, z_pulse);      
		delayMicroseconds(250);
	}
}

void PolarPrinter::resetPolarFunction()
{
	PolarFunction blank_term;
	for(int i=0; i<10; i++)
	{

		polar_function_[i] = blank_term;
		
	}
	polar_function_array_size_ = 0;
}

void PolarPrinter::setFunctionTerm(PolarFunction term, int f)
{
	Serial.print("Setting Function: ");
	Serial.println(f);
	polar_function_[f] = term;
	polar_function_array_size_ = f+1;

	Serial.println(polar_function_[f].amplitude);
}

void PolarPrinter::print(PolarFunction *pf, int size, int layers)
{
	Serial.println("Starting Print");
	Serial.println(polar_function_array_size_);
	scheduler[0] = 0;
	scheduler[1] = 0;
	scheduler[2] = 0;
	for (int z=0; z<layers; z++)
	{
		for (int i=0; i<size; i++)
		{	
			PolarFunction t;
			t = pf[i];
			// t = polar_function_[i];
			// Serial.println(polar_function_[i].amplitude);
			float dt;
			float dr;
			float inside;
			float r;
			float theta = t.left_bound;
			int goal[3];
			unsigned long int_t;
			unsigned long ellapse;
			int flip_count = 0; 

			long iterations = (t.right_bound - t.left_bound) / theta_resolution_;
			Serial.println(t.right_bound);
			Serial.println(t.left_bound);
			Serial.println(iterations);

			calibrate();
			for (int j = 0; j < iterations; j++)
			{
				int_t = micros();
				//Calculate R
				inside = t.frequency*(theta-t.time_shift);
				// r = t.amplitude*(fabs(sin(inside))+cos(inside));
				
				switch (t.function_type)
				{
					case(0):
						r = t.amplitude;
						break;
					case(1):
						r = t.amplitude*inside;
						break;
					case(2):
						r = t.amplitude*sin(inside);
						break;
					case(3):
						r = t.amplitude*fabs(sin(inside));
						break;
					case(4):
						r = t.amplitude*cos(inside);
						break;
					case(5):
						r = t.amplitude*fabs(cos(inside));
						break;
				}

				bool new_r_sign = r >= 0;
				r = fabs(r);
				if (new_r_sign != R_SIGN_)
				{
					flip180();
					flip_count ++;
					R_SIGN_ = new_r_sign;

				}
				if (j == 0) jogToStart(theta, r);
				else
				{
					//Get delta values
					dr = r - R_;
					dt = theta - Theta_;
					//Convert to steps & load goal
					goal[0] = round((dr / pulley_radius_)*3200/M_PI);
					goal[1] = round(dt*3200/M_PI);
					goal[2] = goal[1];
					setNextGoal(goal);
					executeGoal();
				}

				ellapse = micros() - int_t;
				// Serial.println(ellapse);
				Theta_ = theta;
				R_ = r;
				theta += theta_resolution_;

			}
			Theta_ += flip_count * M_PI;
			
		}
		digitalWrite(z_dir_pin, HIGH);
		for (int i=0; i<3200; i++)
		{
			z_pulse = !z_pulse;
			digitalWrite(z_step_pin, z_pulse);      
			delayMicroseconds(500);
		}
	}
	Serial.println("Print Finished");
}

void PolarPrinter::flip180()
{
	digitalWrite(e_dir_pin, LOW);
	digitalWrite(z_dir_pin, HIGH);
	for (int i=0; i<100; i++)
	{
		e_pulse = !e_pulse;
		digitalWrite(e_step_pin, e_pulse);      
		delayMicroseconds(5000);
	}
	for (int i=0; i<3200; i++)
	{
		z_pulse = !z_pulse;
		digitalWrite(z_step_pin, z_pulse);      
		delayMicroseconds(1000);
	}
	digitalWrite(t_dir_pin, HIGH);
	for (int i=0; i<6400; i++)
	{
		t_pulse = !t_pulse;
		digitalWrite(t_step_pin, t_pulse);      
		delayMicroseconds(500);
	}
	Theta_Step_Count_ += 3200;
	digitalWrite(e_dir_pin, HIGH);
	digitalWrite(z_dir_pin, LOW);
	for (int i=0; i<100; i++)
	{
		e_pulse = !e_pulse;
		digitalWrite(e_step_pin, e_pulse);      
		delayMicroseconds(5000);
	}
	for (int i=0; i<3200; i++)
	{
		z_pulse = !z_pulse;
		digitalWrite(z_step_pin, z_pulse);      
		delayMicroseconds(1000);
	}

}

void PolarPrinter::jogToStart(float t0, float r0)
{
	float dt = t0 - Theta_;
	float dr = r0 - R_;
	if (dt != 0 || dr != 0)
	{
		//Convert to steps & load goal
		int goal[3];
		goal[0] = round((dr / pulley_radius_)*3200/M_PI);
		goal[1] = round(dt*3200/M_PI);
		goal[2] = 0;
		setNextGoal(goal);

		digitalWrite(e_dir_pin, LOW);
		digitalWrite(z_dir_pin, HIGH);
		for (int i=0; i<100; i++)
		{
			e_pulse = !e_pulse;
			digitalWrite(e_step_pin, e_pulse);      
			delayMicroseconds(5000);
		}
		for (int i=0; i<3200; i++)
		{
			z_pulse = !z_pulse;
			digitalWrite(z_step_pin, z_pulse);      
			delayMicroseconds(250);
		}
		executeGoal();
		digitalWrite(e_dir_pin, HIGH);
		digitalWrite(z_dir_pin, LOW);
		for (int i=0; i<100; i++)
		{
			e_pulse = !e_pulse;
			digitalWrite(e_step_pin, e_pulse);      
			delayMicroseconds(5000);
		}
		for (int i=0; i<3200; i++)
		{
			z_pulse = !z_pulse;
			digitalWrite(z_step_pin, z_pulse);      
			delayMicroseconds(250);
		}
	}
}

void PolarPrinter::setNextGoal(int goal[3])
{
	//Set goals
	//and set direction
	step_goal[0] = fabs(goal[0]);
	if (goal[0] > 0) digitalWrite(r_dir_pin, HIGH);
	else digitalWrite(r_dir_pin, LOW);
	step_goal[1] = fabs(goal[1]);
	if (goal[1] > 0) digitalWrite(t_dir_pin, HIGH);
	else digitalWrite(t_dir_pin, LOW);
	step_goal[2] = fabs(goal[2]);
	if (goal[2] > 0) digitalWrite(e_dir_pin, HIGH);
	else digitalWrite(e_dir_pin, LOW);

	//going to hard code for a constant extuder speed
	//this will result in variable line thickness
	//FIX LATER
	if (step_goal[2] != 0)
	{
		unsigned long extruder_delay = 12000;
		if (R_ > 5)
		{
			extruder_delay -= 30*R_;
		}
		unsigned long step_delay_const = extruder_delay * step_goal[2];
		// //Serial.println(step_goal[2]);
		// //Serial.println(step_delay_const);

		step_delay[0] = step_delay_const / step_goal[0];
		step_delay[1] = step_delay_const / step_goal[1];
		step_delay[2] = extruder_delay;
	}
	else
	{
		
		step_delay[0] = 750;
		step_delay[1] = 500;
		step_delay[2] = 0;
	}

	// Serial.println(step_goal[0]);
	// Serial.println(step_goal[1]);
	// Serial.println(step_goal[2]);
	// Serial.println(step_delay[0]);
	// Serial.println(step_delay[1]);
	// Serial.println(step_delay[2]);
}

void PolarPrinter::executeGoal()
{

	scheduler[0] = 0;
	scheduler[1] = 0;
	scheduler[2] = 0;
	step_manager[0] = 0;
	step_manager[1] = 0;
	step_manager[2] = 0;

	digitalWrite(e_dir_pin, HIGH);
	bool goal_complete = false;
	unsigned long start_time = micros();
	while (not goal_complete)
	{
		for (int i=0; i<3; i++)
		{
			unsigned long ellapse = micros() - start_time;
			if(ellapse > scheduler[i])
			{
				if (step_goal[i] > step_manager[i])
				{
					switch(i)
					{
						case(0):
							r_pulse = !r_pulse;
							digitalWrite(r_step_pin, r_pulse); 
							break;
						case(1):  
							digitalWrite(t_step_pin, t_pulse);      
							t_pulse = !t_pulse;
							break;
						case(2):  
							digitalWrite(e_step_pin, e_pulse);      
							e_pulse = !e_pulse;
						break; 

					}
					scheduler[i] += step_delay[i];
					step_manager[i] += 1;
				}
			}
		}
		for (int i=0; i<3; i++)
		{
			if (step_goal[i] <= step_manager[i])
			{
				goal_complete = true;
				if (i == 1)
				{
					Theta_Step_Count_ += step_manager[i]/2;
				}
			}
			else
			{
				goal_complete = false;
				break;
			}
		} 
	}
}