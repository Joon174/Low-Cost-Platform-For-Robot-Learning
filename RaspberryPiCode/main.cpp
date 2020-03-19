/*  I** Please make sure to update the doxygen manuals according to standards pls
 *
 * Intellecutal Property of Monash Univeristy Australia
 *
 * Version 1.0
 *
 * This software is licensed under the MIT license associated at https://linktosmthn.com
 *
 */

/** @brief Initial Code to be used for Raspberry Pi.
  * 
  * @author Joon You Tan <jtan0026@student.monash.edu>
  *
  */
#include "wiringPi.h"
#include <stdio.h>

namespace hexapod
{
	class Actuation
	{
		public:
			Actuation();
			~Actuation();
		
		private:
			bool actuateLeg(int leg_GPIO, int duty_cycle);
			
		protected:
			
	};
	/*class SensorData
	{
		public:
			SensorData():
			~SensorData();
		
		private:
			void imageData();
			void imuData();
		
		protected:
			
	};
	class RobotLearning
	{
		public:
			RobotLearning();
			~RobotLearning();
			
		private:
			void uploadModel();
			void trainModel();
			
		protected:
		
	};*/
	void run()
	{
	}
}// namespace hexapod
using namespace hexapod;

void run()
{
	/* Continue to run the code until interrupt keyboard event.*/
}

bool Acutation::actuateLeg(int leg_GPIO, int duty_cycle)
{
	if(GPIO is available)
	{
		wiringPi.pwmSignal(leg_GPIO, duty_cycle);
	}s
}

int main()
{
	while(1)
	{
		hexapod::run();
	}
	return 0;
}